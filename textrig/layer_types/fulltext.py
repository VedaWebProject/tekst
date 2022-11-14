from pydantic import Field
from textrig.layer_types import LayerTypePluginABC, layer_type_impl


class Fulltext(LayerTypePluginABC):
    """A simple fulltext layer type"""

    class FulltextUnit(LayerTypePluginABC.UnitBase):
        text: str = Field(
            None,
            description="Text content of the fulltext unit",
            extra={"template": True},
        )

    @classmethod
    @layer_type_impl
    def get_name(cls) -> str:
        return "Fulltext"

    @classmethod
    @layer_type_impl
    def get_description(cls) -> str:
        return "A simple fulltext data layer"

    @classmethod
    @layer_type_impl
    def get_unit_model(cls) -> type[FulltextUnit]:
        return cls.FulltextUnit
