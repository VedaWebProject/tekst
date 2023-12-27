import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts", "nodes"))["texts"][0]
    user_data = await register_test_user()
    await get_session_cookie(user_data)
    payload = {
        "title": "A test resource",
        "description": [
            {
                "locale": "*",
                "translation": "This is     a string with \n some space    chars",
            }
        ],
        "textId": text_id,
        "level": 0,
        "resourceType": "plaintext",
        "ownerId": user_data["id"],
    }

    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert "id" in resp.json()
    assert resp.json()["title"] == "A test resource"
    assert (
        resp.json()["description"][0]["translation"]
        == "This is a string with some space chars"
    )
    assert resp.json()["ownerId"] == user_data.get("id")


@pytest.mark.anyio
async def test_create_resource_invalid(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    await insert_sample_data("texts", "nodes")
    user_data = await register_test_user()
    await get_session_cookie(user_data)

    payload = {
        "title": "A test resource",
        "textId": "5eb7cfb05e32e07750a1756a",
        "level": 0,
        "resourceType": "plaintext",
    }

    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_update_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts", "nodes", "resources"))["texts"][0]
    user_data = await register_test_user()
    await get_session_cookie(user_data)
    # create new resource (because only owner can update(write))
    payload = {
        "title": "Foo Bar Baz",
        "textId": text_id,
        "level": 0,
        "resourceType": "plaintext",
        "public": True,
    }
    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    resource_data = resp.json()
    assert "id" in resource_data
    assert "ownerId" in resource_data
    assert resource_data.get("public") is False
    # update resource
    updates = {"title": "This Title Changed", "resourceType": "plaintext"}
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(resource_data["id"])
    assert resp.json()["title"] == updates["title"]
    # check if updating public/proposed has no effect (as intended)
    updates = {"public": True, "proposed": True, "resourceType": "plaintext"}
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["public"] is False
    assert resp.json()["proposed"] is False
    # logout
    resp = await test_client.post("/auth/cookie/logout")
    assert resp.status_code == 204, status_fail_msg(204, resp)
    # update resource unauthorized
    updates = {"title": "This Title Changed Again", "resourceType": "plaintext"}
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert resp.status_code == 401, status_fail_msg(401, resp)


@pytest.mark.anyio
async def test_create_resource_with_forged_owner_id(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts", "nodes"))["texts"][0]
    user_data = await register_test_user()
    await get_session_cookie(user_data)
    # create new resource with made up owner ID
    payload = {
        "title": "Foo Bar Baz",
        "textId": text_id,
        "level": 0,
        "resourceType": "plaintext",
        "ownerId": "643d3cdc21efd6c46ae1527e",
    }
    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert resp.json()["ownerId"] != payload["ownerId"]


@pytest.mark.anyio
async def test_get_resource(
    test_client: AsyncClient, insert_sample_data, status_fail_msg
):
    text_id = (await insert_sample_data("texts", "nodes", "resources"))["texts"][0]
    # get existing resource id
    resp = await test_client.get("/resources", params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert isinstance(resp.json()[0], dict)
    assert "id" in resp.json()[0]
    resource = resp.json()[0]
    resource_id = resource["id"]
    # get resource by id
    resp = await test_client.get(f"/resources/{resource_id}")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == resource_id


@pytest.mark.anyio
async def test_access_private_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources")
    text_id = inserted_ids["texts"][0]
    resource_id = inserted_ids["resources"][0]
    # get all accessible resources
    resp = await test_client.get("/resources", params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    accessible_unauthorized = len(resp.json())
    # register test superuser
    user_data = await register_test_user(is_superuser=True)
    await get_session_cookie(user_data)
    # unpublish
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    # logout
    resp = await test_client.post("/auth/cookie/logout")
    assert resp.status_code == 204, status_fail_msg(204, resp)
    # get all accessible resources again, unauthorized
    resp = await test_client.get("/resources", params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) < accessible_unauthorized  # this should be less now


@pytest.mark.anyio
async def test_get_resources(
    test_client: AsyncClient, insert_sample_data, status_fail_msg
):
    text_id = (await insert_sample_data("texts", "nodes", "resources"))["texts"][0]
    resp = await test_client.get(
        "/resources",
        params={"textId": text_id, "level": 1, "resourceType": "plaintext"},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert isinstance(resp.json()[0], dict)
    assert "id" in resp.json()[0]

    resource_id = resp.json()[0]["id"]

    resp = await test_client.get(f"/resources/{resource_id}")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "resourceType" in resp.json()

    # request invalid ID
    resp = await test_client.get("/resources/foo")
    assert resp.status_code == 422, status_fail_msg(422, resp)


@pytest.mark.anyio
async def test_propose_unpropose_publish_unpublish_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts", "nodes", "resources"))["texts"][0]
    user_data = await register_test_user()
    await get_session_cookie(user_data)
    # create new resource (because only owner can update(write))
    payload = {
        "title": "Foo Bar Baz",
        "textId": text_id,
        "level": 0,
        "resourceType": "plaintext",
        "ownerId": user_data.get("id"),
    }
    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    resource_data = resp.json()
    assert "id" in resource_data
    assert "ownerId" in resource_data
    # become superuser
    user_data = await register_test_user(is_superuser=True, alternative=True)
    await get_session_cookie(user_data)
    # publish unproposed resource
    resp = await test_client.post(
        f"/resources/{resource_data['id']}/publish",
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)
    # propose resource
    resp = await test_client.post(
        f"/resources/{resource_data['id']}/propose",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    # get all accessible resources, check if ours is proposed
    resp = await test_client.get("/resources", params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    for resource in resp.json():
        if resource["id"] == resource_data["id"]:
            assert resource["proposed"]
    # propose resource again (should just go through)
    resp = await test_client.post(
        f"/resources/{resource_data['id']}/propose",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    # publish resource
    resp = await test_client.post(
        f"/resources/{resource_data['id']}/publish",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    # unpublish resource
    resp = await test_client.post(
        f"/resources/{resource_data['id']}/unpublish",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    # unpublish resource again (should just go through)
    resp = await test_client.post(
        f"/resources/{resource_data['id']}/unpublish",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    # propose resource again
    resp = await test_client.post(
        f"/resources/{resource_data['id']}/propose",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    # unpropose resource
    resp = await test_client.post(
        f"/resources/{resource_data['id']}/unpropose",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)


@pytest.mark.anyio
async def test_delete_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources")
    text_id = inserted_ids["texts"][0]
    resource_id = inserted_ids["resources"][0]
    # get all accessible resources
    resp = await test_client.get("/resources", params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    resources_count = len(resp.json())
    # register test superuser
    user_data = await register_test_user(is_superuser=True)
    await get_session_cookie(user_data)
    # delete resource
    resp = await test_client.delete(
        f"/resources/{resource_id}",
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)
    # unpublish resource
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )
    # delete resource
    resp = await test_client.delete(
        f"/resources/{resource_id}",
    )
    assert resp.status_code == 204, status_fail_msg(204, resp)
    # get all accessible resources again
    resp = await test_client.get("/resources", params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == resources_count - 1


@pytest.mark.anyio
async def test_transfer_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources")
    resource_id = inserted_ids["resources"][0]
    # register regular test user
    user_data = await register_test_user(is_superuser=False)
    # register test superuser
    superuser_data = await register_test_user(alternative=True, is_superuser=True)
    await get_session_cookie(superuser_data)
    # transfer resource that is still public to test user
    resp = await test_client.post(
        f"/resources/{resource_id}/transfer",
        json=user_data["id"],
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)
    # unpublish resource
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    # transfer resource to test user
    resp = await test_client.post(
        f"/resources/{resource_id}/transfer",
        json=user_data["id"],
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["ownerId"] == user_data["id"]


@pytest.mark.anyio
async def test_get_resource_template(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources")
    resource_id = inserted_ids["resources"][0]
    # register regular test user
    user_data = await register_test_user(is_superuser=False)
    await get_session_cookie(user_data)
    # get resource template
    resp = await test_client.get(
        f"/resources/{resource_id}/template",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)