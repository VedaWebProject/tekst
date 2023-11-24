from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Path, Query, status

from tekst.auth import OptionalUserDep, SuperuserDep, UserDep
from tekst.layer_types import (
    AnyLayerCreateBody,
    AnyLayerDocument,
    AnyLayerRead,
    AnyLayerReadBody,
    AnyLayerUpdateBody,
    layer_types_mgr,
)
from tekst.models.layer import LayerBaseDocument
from tekst.models.text import TextDocument
from tekst.models.unit import UnitBaseDocument
from tekst.models.user import UserDocument, UserRead, UserReadPublic


router = APIRouter(
    prefix="/layers",
    tags=["layers"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
    },
)


async def _process_layer_results(
    layer_docs: AnyLayerDocument | list[AnyLayerDocument],
    *,
    user: UserRead | None = None,
    include_owners: bool = False,
    include_writable: bool = False,
) -> AnyLayerRead | list[AnyLayerRead]:
    # remember if a list has been passed
    is_list = isinstance(layer_docs, list)
    # convert single layer document to list
    if not is_list:
        layer_docs = [layer_docs]
    # convert layer documents to layer type's read instances
    layers = [
        layer_types_mgr.get(layer_doc.layer_type)
        .layer_model()
        .read_model()(
            **layer_doc.model_dump(
                exclude=layer_doc.restricted_fields(user and user.id)
            )
        )
        for layer_doc in layer_docs
    ]
    # include writable flag (if applicable)
    if include_writable and user:
        for layer in layers:
            layer.writable = (
                user.is_superuser
                or user.id == layer.owner_id
                or user.id in layer.shared_write
            )
    # include owner user data in each layer model (if an owner id is set)
    if include_owners:
        for layer in layers:
            if layer.owner_id:
                layer.owner = UserReadPublic.model_from(
                    await UserDocument.get(layer.owner_id)
                )
    return layers if is_list else layers[0]


@router.post("", response_model=AnyLayerReadBody, status_code=status.HTTP_201_CREATED)
async def create_layer(layer: AnyLayerCreateBody, user: UserDep) -> AnyLayerDocument:
    if not await TextDocument.get(layer.text_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Layer refers to non-existent text '{layer.text_id}'",
        )
    # force some values on creation
    layer.owner_id = user.id
    layer.proposed = False
    layer.public = False
    # find document model for this layer type, instantiate, create
    return (
        await layer_types_mgr.get(layer.layer_type)
        .layer_model()
        .document_model()
        .model_from(layer)
        .create()
    )


@router.patch("/{id}", response_model=AnyLayerReadBody, status_code=status.HTTP_200_OK)
async def update_layer(
    id: PydanticObjectId, updates: AnyLayerUpdateBody, user: UserDep
) -> AnyLayerDocument:
    if not await LayerBaseDocument.find_one(
        LayerBaseDocument.id == id,
        LayerBaseDocument.allowed_to_write(user),
        with_children=True,
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Layer {id} doesn't exist or requires extra permissions",
        )
    layer_doc = (
        await layer_types_mgr.get(updates.layer_type)
        .layer_model()
        .document_model()
        .find_one(LayerBaseDocument.id == id, LayerBaseDocument.allowed_to_write(user))
    )
    return await layer_doc.apply(
        updates.model_dump(
            exclude_unset=True,
            exclude={"public", "proposed", "text_id", "owner_id"}
            if not user.is_superuser
            else None,
        )
    )


@router.get("", response_model=list[AnyLayerReadBody], status_code=status.HTTP_200_OK)
async def find_layers(
    user: OptionalUserDep,
    text_id: Annotated[PydanticObjectId, Query(alias="textId")],
    level: int = None,
    layer_type: Annotated[str, Query(alias="layerType")] = None,
    limit: int = 1000,
    include_owners: Annotated[
        bool, Query(alias="owners", description="Include owners' user data, if any")
    ] = False,
    include_writable: Annotated[
        bool,
        Query(
            alias="writable",
            description="Add flag indicating write permissions for requesting user",
        ),
    ] = False,
) -> list[AnyLayerRead]:
    """
    Returns a list of all data layers matching the given criteria.

    As the resulting list of data layers may contain layers of different types, the
    returned layer objects cannot be typed to their precise layer type.
    """
    example = {"text_id": text_id}

    # add to example
    if level is not None:
        example["level"] = level
    if layer_type:
        example["layer_type"] = layer_type

    # query for layers the user is allowed to read and that belong to active texts
    layer_docs = (
        await LayerBaseDocument.find(
            example, await LayerBaseDocument.allowed_to_read(user), with_children=True
        )
        .limit(limit)
        .to_list()
    )

    return await _process_layer_results(
        layer_docs,
        user=user,
        include_owners=include_owners,
        include_writable=include_writable,
    )


#
#   TODO: rebuild template endpoint using beanie logic
#

# @router.get("/template", status_code=status.HTTP_200_OK)
# async def get_layer_template(layer_id: str, db_io: DbIO = Depends(get_db_io)) -> dict:
#     layer_data = await db_io.find_one("layers", layer_id)

#     if not layer_data:
#         raise HTTPException(
#             status.HTTP_400_BAD_REQUEST,
#             detail=f"Layer with ID {layer_id} doesn't exist",
#         )
#
#     layer_types_mgr = layer_types_mgr

#     # decode layer data: Usually, this is handled automatically by our models, but
#     # in this case we're returning a raw dict/JSON, so we have to manually make sure
#     # that a) the ID field is called "id" and b) the DocumentId is encoded as str.
#     layer_read_model = layer_types_mgr \
#       .get(layer_data["layerType"]).get_layer_read_model()
#     layer_data = layer_read_model(**layer_data).model_dump()

#     # import unit type for the requested layer
#     template = layer_types_mgr \
#       .get(layer_data["layerType"]).prepare_import_template()
#     # apply data from layer instance
#     template["layerId"] = str(layer_data["id"])
#     template["_level"] = layer_data["level"]
#     template["_title"] = layer_data["title"]
#     template["_description"] = layer_data.get("description", None)

#     # generate unit template
#     node_template = {key: None for key in template["_unitSchema"].keys()}

#     # get IDs of all nodes on this structure level as a base for unit templates
#     nodes = await db_io.find(
#         "nodes",
#         example={"textSlug": layer_data["textSlug"], "level": layer_data["level"]},
#         projection={"_id", "label"},
#         limit=0,
#     )

#     # fill in unit templates with IDs
#     template["units"] = [
#         model_dump(nodeId=str(node["_id"]), **node_template) for node in nodes
#     ]

#     # create temporary file and stream it as a file response
#     tempfile = NamedTemporaryFile(mode="w")
#     tempfile.write(json.dumps(template, indent=2))
#     tempfile.flush()

#     # prepare headers
#     filename = (
#         f"{layer_data['textSlug']}_layer_{safe_name(template['layerId'])}"
#         "_template.json"
#     )
#     headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

#     log.debug(f"Serving layer template as temporary file {tempfile.name}")
#     return FileResponse(
#         tempfile.name,
#         headers=headers,
#         media_type="application/json",
#         background=BackgroundTask(tempfile.close),
#     )


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=AnyLayerReadBody)
async def get_layer(
    user: OptionalUserDep,
    layer_id: Annotated[PydanticObjectId, Path(alias="id")],
    include_owner: Annotated[
        bool, Query(alias="owner", description="Include owner's user data, if any")
    ] = False,
    include_writable: Annotated[
        bool,
        Query(
            alias="writable",
            description="Add flag indicating write permissions for requesting user",
        ),
    ] = False,
) -> AnyLayerRead:
    layer_doc = await LayerBaseDocument.find_one(
        LayerBaseDocument.id == layer_id,
        await LayerBaseDocument.allowed_to_read(user),
        with_children=True,
    )
    if not layer_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No layer with ID {layer_id}"
        )
    return await _process_layer_results(
        layer_doc,
        user=user,
        include_owners=include_owner,
        include_writable=include_writable,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_layer(
    user: UserDep, layer_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> None:
    layer_doc = await LayerBaseDocument.get(layer_id, with_children=True)
    if not layer_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No layer with ID {layer_id}"
        )
    if not user.is_superuser and user.id != layer_doc.owner_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if layer_doc.public:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a published layer",
        )
    if layer_doc.proposed:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a proposed layer",
        )
    # all fine
    # delete units
    await UnitBaseDocument.find(
        UnitBaseDocument.layer_id == layer_id,
        with_children=True,
    ).delete()
    # delete layer
    await LayerBaseDocument.find_one(
        LayerBaseDocument.id == layer_id,
        with_children=True,
    ).delete()


@router.post("/{id}/propose", status_code=status.HTTP_204_NO_CONTENT)
async def propose_layer(
    user: UserDep, layer_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> None:
    layer_doc = await LayerBaseDocument.get(layer_id, with_children=True)
    if not layer_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No layer with ID {layer_id}"
        )
    if not user.is_superuser and user.id != layer_doc.owner_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if layer_doc.public:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Layer with ID {layer_id} is already public",
        )
    if layer_doc.proposed:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Layer with ID {layer_id} is already proposed for publication",
        )
    # all fine, propose layer
    await LayerBaseDocument.find_one(
        LayerBaseDocument.id == layer_id,
        with_children=True,
    ).set({LayerBaseDocument.proposed: True})


@router.post("/{id}/unpropose", status_code=status.HTTP_204_NO_CONTENT)
async def unpropose_layer(
    user: UserDep, layer_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> None:
    layer_doc = await LayerBaseDocument.get(layer_id, with_children=True)
    if not layer_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No layer with ID {layer_id}"
        )
    if not user.is_superuser and user.id != layer_doc.owner_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if not layer_doc.proposed:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Layer with ID {layer_id} is not proposed for publication",
        )
    # all fine, unpropose layer
    await LayerBaseDocument.find_one(
        LayerBaseDocument.id == layer_id,
        with_children=True,
    ).set(
        {
            LayerBaseDocument.proposed: False,
            LayerBaseDocument.public: False,
        }
    )


@router.post("/{id}/publish", status_code=status.HTTP_204_NO_CONTENT)
async def publish_layer(
    user: SuperuserDep, layer_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> None:
    layer_doc = await LayerBaseDocument.get(layer_id, with_children=True)
    if not layer_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No layer with ID {layer_id}"
        )
    if layer_doc.public:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Layer with ID {layer_id} is already public",
        )
    if not layer_doc.proposed:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Layer with ID {layer_id} is not proposed for publication",
        )
    # all fine, publish layer
    await LayerBaseDocument.find_one(
        LayerBaseDocument.id == layer_id,
        with_children=True,
    ).set(
        {
            LayerBaseDocument.public: True,
            LayerBaseDocument.proposed: False,
            LayerBaseDocument.owner_id: None,
            LayerBaseDocument.shared_read: [],
            LayerBaseDocument.shared_write: [],
        }
    )


@router.post("/{id}/unpublish", status_code=status.HTTP_204_NO_CONTENT)
async def unpublish_layer(
    user: SuperuserDep, layer_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> None:
    layer_doc = await LayerBaseDocument.get(layer_id, with_children=True)
    if not layer_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No layer with ID {layer_id}"
        )
    if not layer_doc.public:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Layer with ID {layer_id} is not public",
        )
    # all fine, unpublish layer
    await LayerBaseDocument.find_one(
        LayerBaseDocument.id == layer_id,
        with_children=True,
    ).set(
        {
            LayerBaseDocument.public: False,
            LayerBaseDocument.proposed: False,
        }
    )
