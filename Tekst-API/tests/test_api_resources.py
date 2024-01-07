import pytest

from httpx import AsyncClient
from tekst.models.resource import ResourceBaseDocument


@pytest.mark.anyio
async def test_create_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    text_id = (await insert_sample_data("texts", "nodes"))["texts"][0]
    user = await login()
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
        "ownerId": user["id"],
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
    assert resp.json()["ownerId"] == user.get("id")


@pytest.mark.anyio
async def test_create_resource_w_invalid_level(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    text_id = (await insert_sample_data("texts", "nodes"))["texts"][0]
    user = await login()
    resp = await test_client.post(
        "/resources",
        json={
            "title": "A test resource",
            "description": [
                {
                    "locale": "*",
                    "translation": "This is     a string with \n some space    chars",
                }
            ],
            "textId": text_id,
            "level": 4,
            "resourceType": "plaintext",
            "ownerId": user["id"],
        },
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_create_resource_w_wrong_text_id(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
    wrong_id,
):
    await insert_sample_data("texts", "nodes")
    await login()

    payload = {
        "title": "A test resource",
        "textId": wrong_id,
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
    login,
    register_test_user,
    wrong_id,
    logout,
):
    text_id = (await insert_sample_data("texts", "nodes", "resources"))["texts"][0]
    superuser = await login(is_superuser=True)
    other_user = await register_test_user()

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
    assert resource_data["ownerId"] == superuser.get("id")
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

    # update resource w/ wrong ID
    updates = {"title": "This Title Changed", "resourceType": "plaintext"}
    resp = await test_client.patch(
        f"/resources/{wrong_id}",
        json=updates,
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # update resource's read shares
    updates = {"sharedRead": [other_user["id"]], "resourceType": "plaintext"}
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["sharedRead"][0] == other_user["id"]

    # update resource's read/write shares
    updates = {
        "sharedRead": [],
        "sharedWrite": [other_user["id"]],
        "resourceType": "plaintext",
    }
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["sharedRead"]) == 0
    assert resp.json()["sharedWrite"][0] == other_user["id"]

    # update resource's write shares using wrong user ID
    updates = {"sharedWrite": [wrong_id], "resourceType": "plaintext"}
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)

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

    # update resource unauthenticated
    await logout()
    updates = {"title": "This Title Changed Again", "resourceType": "plaintext"}
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert resp.status_code == 401, status_fail_msg(401, resp)

    # update resource shares as non-owner/non-admin
    await login(user=other_user)
    updates = {"sharedRead": [wrong_id], "resourceType": "plaintext"}
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert wrong_id not in resp.json()["sharedRead"]  # bc API should ignore the update!


@pytest.mark.anyio
async def test_set_shares_for_public_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
    register_test_user,
    wrong_id,
):
    resource_id = (await insert_sample_data("texts", "nodes", "resources"))[
        "resources"
    ][0]
    await login(is_superuser=True)
    other_user = await register_test_user()

    # set resource public
    res = await ResourceBaseDocument.get(resource_id, with_children=True)
    await res.set({ResourceBaseDocument.public: True})

    # update shares
    updates = {"sharedRead": [other_user["id"]], "resourceType": "plaintext"}
    resp = await test_client.patch(
        f"/resources/{resource_id}",
        json=updates,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["public"] is True
    assert len(resp.json()["sharedRead"]) == 0  # bc API should clear shares updates!


@pytest.mark.anyio
async def test_create_resource_with_forged_owner_id(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    text_id = (await insert_sample_data("texts", "nodes"))["texts"][0]
    await login()

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
    test_client: AsyncClient, insert_sample_data, status_fail_msg, wrong_id, login
):
    resource_id = (await insert_sample_data("texts", "nodes", "resources"))[
        "resources"
    ][0]

    # get resource by ID
    resp = await test_client.get(f"/resources/{resource_id}")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == resource_id

    # fail to get resource by wrong ID
    resp = await test_client.get(f"/resources/{wrong_id}")
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # fail to get resource without read permissions
    await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id, with_children=True
    ).set({ResourceBaseDocument.public: False})
    await login(is_superuser=False)
    resp = await test_client.get(f"/resources/{wrong_id}")
    assert resp.status_code == 404, status_fail_msg(404, resp)


@pytest.mark.anyio
async def test_access_private_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
    logout,
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
    await login(is_superuser=True)

    # unpublish
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # get all accessible resources again, unauthenticated
    await logout()
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
    test_client: AsyncClient, insert_sample_data, status_fail_msg, login, wrong_id
):
    text_id = (await insert_sample_data("texts", "nodes", "resources"))["texts"][0]
    owner = await login(is_superuser=True)

    # create new resource (because only owner can update(write))
    payload = {
        "title": "Foo Bar Baz",
        "textId": text_id,
        "level": 0,
        "resourceType": "plaintext",
        "ownerId": owner.get("id"),
    }
    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    resource_data = resp.json()
    assert "id" in resource_data
    assert "ownerId" in resource_data
    resource_id = resource_data["id"]

    # publish unproposed resource
    resp = await test_client.post(
        f"/resources/{resource_id}/publish",
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)

    # propose resource
    resp = await test_client.post(
        f"/resources/{resource_id}/propose",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # propose resource w/ wrong ID
    resp = await test_client.post(
        f"/resources/{wrong_id}/propose",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # get all accessible resources, check if ours is proposed
    resp = await test_client.get("/resources", params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    for resource in resp.json():
        if resource["id"] == resource_id:
            assert resource["proposed"]

    # propose resource again (should just go through)
    resp = await test_client.post(
        f"/resources/{resource_id}/propose",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # publish resource w/ wrong ID
    resp = await test_client.post(
        f"/resources/{wrong_id}/publish",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # publish resource
    resp = await test_client.post(
        f"/resources/{resource_id}/publish",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # propose public resource
    resp = await test_client.post(
        f"/resources/{resource_id}/propose",
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)

    # unpublish resource w/ wrong ID
    resp = await test_client.post(
        f"/resources/{wrong_id}/unpublish",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # unpublish resource
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # unpublish resource again (should just go through)
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # propose resource again
    resp = await test_client.post(
        f"/resources/{resource_id}/propose",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # unpropose resource w/ wrong ID
    resp = await test_client.post(
        f"/resources/{wrong_id}/unpropose",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # unpropose resource
    resp = await test_client.post(
        f"/resources/{resource_id}/unpropose",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # propose resource unauthorized
    other_user = await login()
    resp = await test_client.post(
        f"/resources/{resource_id}/propose",
    )
    assert resp.status_code == 403, status_fail_msg(403, resp)

    # propose resource again
    await login(user=owner)
    resp = await test_client.post(
        f"/resources/{resource_id}/propose",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # unpropose resource unauthorized
    await login(user=other_user)
    resp = await test_client.post(
        f"/resources/{resource_id}/unpropose",
    )
    assert resp.status_code == 403, status_fail_msg(403, resp)


@pytest.mark.anyio
async def test_delete_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
    wrong_id,
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources")
    text_id = inserted_ids["texts"][0]
    resource_id = inserted_ids["resources"][0]

    # get all accessible resources
    resp = await test_client.get("/resources", params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    resources_count = len(resp.json())

    # register test users
    user = await login(is_superuser=True)

    # unpublish resource
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )

    # try to delete resource w/ wrong ID
    resp = await test_client.delete(
        f"/resources/{wrong_id}",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # become non-owner/non-superuser
    await login()

    # try to delete resource as non-owner/non-superuser
    resp = await test_client.delete(
        f"/resources/{resource_id}",
    )
    assert resp.status_code == 403, status_fail_msg(403, resp)

    # become superuser again
    await login(user=user)

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
async def test_delete_public_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources")
    resource_id = inserted_ids["resources"][0]
    await login(is_superuser=True)

    # ensure resource is public
    resp = await test_client.post(f"/resources/{resource_id}/unpublish")
    resp = await test_client.post(f"/resources/{resource_id}/propose")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["proposed"] is True
    resp = await test_client.post(f"/resources/{resource_id}/publish")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["public"] is True

    # delete public resource (should not be possible)
    resp = await test_client.delete(
        f"/resources/{resource_id}",
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_delete_proposed_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources")
    resource_id = inserted_ids["resources"][0]
    await login(is_superuser=True)

    # ensure resource is not public
    resp = await test_client.post(f"/resources/{resource_id}/unpublish")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["public"] is False

    # ensure resource is proposed
    resp = await test_client.post(f"/resources/{resource_id}/propose")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["proposed"] is True

    # delete proposed resource (should not be possible)
    resp = await test_client.delete(
        f"/resources/{resource_id}",
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_transfer_resource(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
    register_test_user,
    wrong_id,
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources")
    resource_id = inserted_ids["resources"][0]

    # register regular test user
    user = await register_test_user(is_superuser=False)
    # register test superuser
    superuser = await login(is_superuser=True)

    # transfer resource that is still public to test user
    resp = await test_client.post(
        f"/resources/{resource_id}/transfer",
        json=user["id"],
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)

    # unpublish resource
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # transfer resource w/ wrong ID
    resp = await test_client.post(
        f"/resources/{wrong_id}/transfer",
        json=user["id"],
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # transfer resource to user w/ wrong ID
    resp = await test_client.post(
        f"/resources/{resource_id}/transfer",
        json=wrong_id,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)

    # transfer resource without permission
    await login(user=user)
    resp = await test_client.post(
        f"/resources/{resource_id}/transfer",
        json=user["id"],
    )
    assert resp.status_code == 403, status_fail_msg(403, resp)

    # transfer resource to test user
    await login(user=superuser)
    resp = await test_client.post(
        f"/resources/{resource_id}/transfer",
        json=user["id"],
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["ownerId"] == user["id"]

    # ....and do that again
    resp = await test_client.post(
        f"/resources/{resource_id}/transfer",
        json=user["id"],
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["ownerId"] == user["id"]


@pytest.mark.anyio
async def test_get_resource_template(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
    wrong_id,
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources")
    resource_id = inserted_ids["resources"][0]

    # register regular test user
    await login(is_superuser=False)

    # get resource template
    resp = await test_client.get(
        f"/resources/{resource_id}/template",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)

    # get resource template w/ wrong ID
    resp = await test_client.get(
        f"/resources/{wrong_id}/template",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)