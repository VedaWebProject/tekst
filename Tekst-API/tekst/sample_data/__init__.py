from tekst.layer_types import LayerTypeABC, layer_type_manager
from tekst.logging import log
from tekst.models.common import PydanticObjectId
from tekst.models.text import NodeDocument, TextDocument
from tekst.sample_data._sample_data import LAYERS, TEXTS


_layer_types = layer_type_manager.get_all()


async def _create_sample_node(node_data: dict, text_id: str, parent_id: str = None):
    node_doc = NodeDocument(text_id=text_id, parent_id=parent_id, **node_data)
    node_id = str((await node_doc.create()).id)
    for node_doc in node_data.get("children", []):
        await _create_sample_node(node_doc, text_id, parent_id=node_id)
    return node_id


async def _create_sample_unit(
    layer_data: dict, unit_data: dict, layer_type: type[LayerTypeABC]
):
    # get node this unit belongs to
    node = await NodeDocument.find(
        NodeDocument.text_id == PydanticObjectId(layer_data.get("textId", "")),
        NodeDocument.level == layer_data.get("level", -1),
        NodeDocument.position == unit_data.get("sampleNodePosition", -1),
    ).first_or_none()
    if not node:
        log.error(f"Could not find target node for unit {unit_data}")
        return
    # create node
    unit_doc_model = layer_type.get_unit_model().get_document_model()
    unit_doc = unit_doc_model(
        layer_id=layer_data.get("id"), node_id=node.id, **unit_data
    )
    unit_id = str((await unit_doc.create()).id)
    return unit_id


async def _create_sample_layers(text_slug: str, text_id: str):
    for layer_data in LAYERS.get(text_slug, []):
        layer_type = _layer_types.get(layer_data.get("layerType"))
        layer_doc_model = layer_type.get_layer_model().get_document_model()
        if not layer_doc_model:
            raise RuntimeError(f"Layer type {layer_data.get('layerType')} not found.")
        layer_doc = layer_doc_model(text_id=text_id, **layer_data)
        await layer_doc.create()
        # units
        for unit_data in layer_data.get("units", []):
            await _create_sample_unit(layer_doc.model_dump(), unit_data, layer_type)


async def create_sample_texts():
    log.info("Creating sample texts...")
    if not (await TextDocument.find_one().exists()):
        for text_slug, text_data in TEXTS.items():
            text_doc = TextDocument(**text_data["text"])
            text_id = str((await text_doc.create()).id)
            log.debug(f"Created {text_slug} as {text_id}")
            # nodes
            for node in text_data["nodes"]:
                await _create_sample_node(node, text_id)
            # layers belonging to this text
            await _create_sample_layers(text_slug, text_id)
    else:
        log.warning("Found texts in the database. Skipping sample data creation.")
