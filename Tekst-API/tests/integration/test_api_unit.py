import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_unit(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts", "nodes", "resources"))["texts"][0]
    user_data = await register_test_user()
    session_cookie = await get_session_cookie(user_data)

    # create new resource (because only owner can update(write))
    payload = {
        "title": "Foo Bar Baz",
        "textId": text_id,
        "level": 0,
        "resourceType": "plaintext",
        "ownerId": user_data.get("id"),
    }
    resp = await test_client.post("/resources", json=payload, cookies=session_cookie)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    resource_data = resp.json()
    assert "id" in resource_data
    assert "ownerId" in resource_data
    assert resource_data["ownerId"] == user_data["id"]

    # get ID of existing test node
    resp = await test_client.get(
        "/nodes", params={"textId": text_id, "level": 0}, cookies=session_cookie
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert "id" in resp.json()[0]
    node_id = resp.json()[0]["id"]

    # create plaintext resource unit
    payload = {
        "resourceId": resource_data["id"],
        "resourceType": "plaintext",
        "nodeId": node_id,
        "text": "Ein Raabe geht im Feld spazieren.",
        "comment": "This is a comment",
    }
    resp = await test_client.post("/units", json=payload, cookies=session_cookie)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["text"] == payload["text"]
    assert resp.json()["comment"] == payload["comment"]
    assert "id" in resp.json()
    unit_id = resp.json()["id"]

    # fail to create duplicate
    resp = await test_client.post("/units", json=payload, cookies=session_cookie)
    assert resp.status_code == 409, status_fail_msg(409, resp)

    # get unit
    resp = await test_client.get(f"/units/{unit_id}", cookies=session_cookie)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["text"] == payload["text"]
    assert resp.json()["comment"] == payload["comment"]

    # fail to get unit with invalid ID
    resp = await test_client.get(
        "/units/637b9ad396d541a505e5439b", cookies=session_cookie
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # update unit
    resp = await test_client.patch(
        f"/units/{unit_id}",
        json={"resourceType": "plaintext", "text": "FOO BAR"},
        cookies=session_cookie,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == unit_id
    assert resp.json()["text"] == "FOO BAR"

    # fail to update unit with invalid ID
    resp = await test_client.patch(
        "/units/637b9ad396d541a505e5439b",
        json={"resourceType": "plaintext", "text": "FOO BAR"},
        cookies=session_cookie,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)

    # find all units
    resp = await test_client.get(
        "/units", params={"limit": 100}, cookies=session_cookie
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
