import pytest
from bson import ObjectId
from httpx import AsyncClient
from textrig.models.node import Node, NodeRead


@pytest.mark.anyio
async def test_create_node(
    root_path, test_client: AsyncClient, test_data, load_test_data_texts
):

    endpoint = f"{root_path}/nodes"
    nodes = test_data["nodes"]

    for node in nodes:
        resp = await test_client.post(endpoint, json=node)
        assert resp.status_code == 201, f"response status {resp.status_code} != 201"


@pytest.mark.anyio
async def test_child_node_io(
    root_path, test_client: AsyncClient, test_data, load_test_data_texts
):

    endpoint = f"{root_path}/nodes"
    node = test_data["nodes"][0]

    # create parent
    resp = await test_client.post(endpoint, json=node)
    assert resp.status_code == 201, f"response status {resp.status_code} != 201"
    parent: NodeRead = NodeRead(**resp.json())

    # create child
    child: Node = Node(**node)
    child.parent_id = str(parent.id)
    child.level = parent.level + 1
    child.index = 0
    resp = await test_client.post(endpoint, json=child.dict())
    child = NodeRead(**resp.json())
    assert "id" in resp.json()
    assert "parentId" in resp.json()
    assert resp.json()["parentId"] == str(child.parent_id)

    # find children by parent ID
    resp = await test_client.get(
        endpoint, params={"text_slug": parent.text_slug, "parent_id": str(parent.id)}
    )
    assert resp.status_code == 200, f"response status {resp.status_code} != 200"
    assert type(resp.json()) is list
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == str(child.id)


@pytest.mark.anyio
async def test_create_node_invalid_text_fail(
    root_path, test_client: AsyncClient, test_data, load_test_data_texts
):

    endpoint = f"{root_path}/nodes"
    node = test_data["nodes"][0]
    node["textSlug"] = "this_does_not_exist"

    resp = await test_client.post(endpoint, json=node)
    assert resp.status_code == 400, f"response status {resp.status_code} != 400"


@pytest.mark.anyio
async def test_create_node_duplicate_fail(
    root_path, test_client: AsyncClient, test_data, load_test_data_texts
):

    endpoint = f"{root_path}/nodes"
    node = test_data["nodes"][0]

    resp = await test_client.post(endpoint, json=node)
    assert resp.status_code == 201, f"response status {resp.status_code} != 201"

    resp = await test_client.post(endpoint, json=node)
    assert resp.status_code == 409, f"response status {resp.status_code} != 409"


@pytest.mark.anyio
async def test_get_nodes(
    root_path, test_client: AsyncClient, test_data, load_test_data
):

    endpoint = f"{root_path}/nodes"
    text = test_data["texts"][0]
    text_slug = text["slug"]
    nodes = [n for n in test_data["nodes"] if n["textSlug"] == text_slug]
    # level = 0
    # index = 0
    # parent_id = None
    # limit = 1000

    # test results length limit
    resp = await test_client.get(
        endpoint, params={"text_slug": text_slug, "level": 0, "limit": 2}
    )
    assert resp.status_code == 200, f"response status {resp.status_code} != 200"
    assert type(resp.json()) is list
    assert len(resp.json()) == 2

    # test empty results with status 200
    resp = await test_client.get(
        endpoint, params={"text_slug": "this_does_not_exist", "level": 0}
    )
    assert resp.status_code == 200, f"response status {resp.status_code} != 200"
    assert type(resp.json()) is list
    assert len(resp.json()) == 0

    # test results contain all nodes of level 0
    resp = await test_client.get(endpoint, params={"text_slug": text_slug, "level": 0})
    assert resp.status_code == 200, f"response status {resp.status_code} != 200"
    assert type(resp.json()) is list
    assert len(resp.json()) == len(nodes)

    # test returned nodes have IDs
    assert "id" in resp.json()[0]
    ObjectId(resp.json()[0]["id"])

    # test specific index
    resp = await test_client.get(
        endpoint, params={"text_slug": text_slug, "level": 0, "index": 0}
    )
    assert resp.status_code == 200, f"response status {resp.status_code} != 200"
    assert type(resp.json()) is list
    assert len(resp.json()) == 1
