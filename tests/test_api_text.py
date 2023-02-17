import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_texts(
    root_path, test_client: AsyncClient, insert_test_data, status_fail_msg
):
    await insert_test_data("texts")
    endpoint = f"{root_path}/texts"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    text_id = resp.json()[0]["id"]
    # get one by specific id
    resp = await test_client.get(f"{endpoint}/{text_id}")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) == dict
    assert resp.json()["id"] == text_id
    # get one by non-existent id
    resp = await test_client.get(f"{endpoint}/637b9ad396d541a505e5439b")
    assert resp.status_code == 404, status_fail_msg(404, resp)


@pytest.mark.anyio
async def test_create_text(root_path, test_client: AsyncClient, status_fail_msg):
    endpoint = f"{root_path}/texts"
    payload = {"title": "Just a Test", "slug": "justatest", "levels": ["foo"]}
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert "id" in resp.json()
    assert "slug" in resp.json()
    assert resp.json()["slug"] == "justatest"
    # create duplicate
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 409, status_fail_msg(409, resp)


@pytest.mark.anyio
async def test_update_text(
    root_path, test_client: AsyncClient, insert_test_data, status_fail_msg
):
    await insert_test_data("texts")
    # get text from db
    endpoint = f"{root_path}/texts"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    text = resp.json()[0]
    # update text
    endpoint = f"{root_path}/texts/{text['id']}"
    text_update = {"title": "Another text"}
    resp = await test_client.patch(endpoint, json=text_update)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(text["id"])
    assert "title" in resp.json()
    assert resp.json()["title"] == "Another text"
    # update unchanged text
    resp = await test_client.patch(endpoint, json=text_update)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    # update invalid text
    text_update = {"title": "Yet another text"}
    endpoint = f"{root_path}/texts/637b9ad396d541a505e5439b"
    resp = await test_client.patch(endpoint, json=text_update)
    assert resp.status_code == 400, status_fail_msg(400, resp)
