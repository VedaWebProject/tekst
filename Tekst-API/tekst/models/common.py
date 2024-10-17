from datetime import datetime
from types import UnionType
from typing import (  # noqa: UP035
    Annotated,
    Any,
    Literal,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from beanie import (
    Document,
    PydanticObjectId,
)
from humps import camelize, decamelize
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    conlist,
    create_model,
)
from pydantic.aliases import PydanticUndefined
from pydantic.fields import FieldInfo
from typing_extensions import TypeAliasType, TypedDict


# type alias for available locale/language setting identifiers
_platform_locales = ("deDE", "enUS")
LocaleKey = TypeAliasType("LocaleKey", Literal[_platform_locales])
TranslationLocaleKey = TypeAliasType(
    "TranslationLocaleKey", Literal[_platform_locales + ("*",)]
)


class ExcludeFromModelVariants:
    """
    Class to be used as type annotation metadata for fields that
    should not be included in certain model types
    """

    def __init__(
        self,
        *,
        create: bool = False,
        update: bool = False,
    ):
        self.create = create
        self.update = update


# These FieldInfo instances are to be used as type annotation metadata for fields
# that should be marked as optional in hte JSON schema. By default, any field
# with a default value is "optional", but the generator we use to generate the
# TypeScript types for the client is configured to transform fields with default
# values as required to make working with response models easier. In turn, we have to
# explicitly mark optional fields (especially for request models) as optinal in some way
# for the generators to understand which fields to treat as optional.
SchemaOptionalNullable = Field(json_schema_extra={"optionalNullable": True})
SchemaOptionalNonNullable = Field(json_schema_extra={"optionalNullable": False})


class TranslationBase(TypedDict):
    locale: TranslationLocaleKey


T = TypeVar("T", bound=TranslationBase)
Translations = conlist(
    T,
    max_length=len(get_args(TranslationLocaleKey.__value__)),
)


class ModelTransformerMixin:
    @classmethod
    def model_from(cls, obj: BaseModel) -> BaseModel:
        return cls.model_validate(obj, from_attributes=True)


class ModelBase(ModelTransformerMixin, BaseModel):
    _exclude_from_updates = {"id", "_id"}
    model_config = ConfigDict(
        alias_generator=camelize,
        populate_by_name=True,
        from_attributes=True,
    )

    @classmethod
    def _field_excluded_from_model_variant(
        cls, field_name: str, model_variant: Literal["create", "update"]
    ) -> bool:
        """
        Returns `True` if the field with the given name should be excluded from the
        model variant with the given name. This is the case if the field is annotated
        with `ExcludeFromModelVariants` with the given model variant set to `True`.
        """
        for meta in cls.model_fields[field_name].metadata:
            if isinstance(
                meta,
                ExcludeFromModelVariants,
            ) and getattr(
                meta,
                model_variant,
                False,
            ):
                return True
        return False


class DocumentBase(ModelTransformerMixin, Document):
    """Base model for all Tekst ODMs"""

    class Settings:
        validate_on_save = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **decamelize(kwargs))

    async def insert(self, **kwargs):
        self.id = None  # reset ID for new document in case one is already set
        return await super().insert(**kwargs)

    async def apply_updates(
        self,
        updates_model: ModelBase,
        *,
        replace: bool = True,
    ):
        """
        Custom method to apply updates to the document, excluding any fields that are
        - in the `exclude` set
        - not set in `updates_model`
        - equal to the default value of the respective field in `updates_model`
        """
        for field in updates_model.model_fields_set:
            # we have to always preserve `resource_type`, so skip updating it
            if field == "resource_type":
                continue
            # make sure we ignore None values that sneaked in because
            # the update models allow them but the original model does not
            if getattr(updates_model, field) is None and not isinstance(
                None, self.model_fields[field].annotation
            ):
                continue
            setattr(self, field, getattr(updates_model, field))

        if replace:
            return await self.replace()
        else:
            return self


class CreateBase(BaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        for name, field in list(cls.model_fields.items()):
            if cls._field_excluded_from_model_variant(name, "create"):
                field.default = PydanticUndefined
                del cls.model_fields[name]

        cls.model_rebuild(force=True)


class ReadBase(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: PydanticObjectId


class UpdateBase(BaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        for name, field in list(cls.model_fields.items()):
            if cls._field_excluded_from_model_variant(name, "update"):
                del cls.model_fields[name]

        cls.model_rebuild(force=True)


class ModelFactoryMixin:
    _document_model: type[DocumentBase] = None
    _create_model: type[ModelBase] = None
    _read_model: type[ReadBase] = None
    _update_model: type[ModelBase] = None

    @classmethod
    def _is_origin_cls(cls, attr: str) -> bool:
        for clazz in cls.mro():
            if attr in vars(clazz):
                return clazz == cls
        raise AttributeError(
            f"Attribute '{attr}' not found in class '{cls.__name__}'"
        )  # pragma: no cover

    @classmethod
    def _to_bases_tuple(cls, bases: type | tuple[type]):
        return (bases,) if type(bases) is not tuple else bases

    @classmethod
    def document_model(cls, bases: type | tuple[type] = DocumentBase) -> type:
        if not cls._document_model or not cls._is_origin_cls("_document_model"):
            cls._document_model = create_model(
                f"{cls.__name__}Document",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__module__,
            )
        return cls._document_model

    @classmethod
    def create_model(cls, bases: type | tuple[type] = CreateBase) -> type[ModelBase]:
        if not cls._create_model or not cls._is_origin_cls("_create_model"):
            cls._create_model = create_model(
                f"{cls.__name__}Create",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__module__,
            )
        return cls._create_model

    @classmethod
    def read_model(cls, bases: type | tuple[type] = ReadBase) -> type[ReadBase]:
        if not cls._read_model or not cls._is_origin_cls("_read_model"):
            cls._read_model = create_model(
                f"{cls.__name__}Read",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__module__,
            )
        return cls._read_model

    @classmethod
    def update_model(cls, bases: type | tuple[type] = UpdateBase) -> type[ModelBase]:
        if not cls._update_model or not cls._is_origin_cls("_update_model"):
            field_overrides = {}
            for name, field in cls.model_fields.items():
                if not str(name).endswith("_type"):
                    type_annos = (
                        (field.annotation,)
                        if get_origin(field.annotation) not in (Union, UnionType)
                        else get_args(field.annotation)
                    )
                    extra_field_infos = []
                    if not (None in type_annos or type(None) in type_annos):
                        # None isn't present in the type annotation, so we add it
                        type_annos += (type(None),)
                        # mark that this prop wasn't originally nullable
                        extra_field_infos.append(SchemaOptionalNonNullable)
                    else:
                        # mark that this prop was originally nullable
                        extra_field_infos.append(SchemaOptionalNullable)
                    # merge with original field info
                    fi = FieldInfo.merge_field_infos(
                        field,
                        *extra_field_infos,
                        # set the type annotation to a union of the composed types
                        annotation=Union[type_annos],  # noqa: UP007
                        # we always default to None on these update model fields
                        default=None,
                    )
                    # add to field overrides
                    field_overrides[name] = (fi.annotation, fi)
            cls._update_model = create_model(
                f"{cls.__name__}Update",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__module__,
                **field_overrides,
            )
        return cls._update_model


class PrecomputedDataDocument(ModelBase, DocumentBase):
    """Base model for precomputed data"""

    class Settings(DocumentBase.Settings):
        name = "precomputed"
        indexes = [
            "precomputed_type",
            "ref_id",
        ]

    ref_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the resource this precomputed data refers to",
        ),
    ]

    precomputed_type: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=64,
            strip_whitespace=True,
        ),
        Field(
            description="String identifying the type of precomputed data",
        ),
    ]

    created_at: Annotated[
        datetime,
        Field(
            description="The time this data was created",
        ),
    ] = datetime.utcnow()

    data: Annotated[
        Any | None,
        Field(
            description="The precomputed data",
        ),
    ] = None
