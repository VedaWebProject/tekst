import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_texts(
    test_client: AsyncClient, insert_sample_data, status_assertion
):
    await insert_sample_data("texts")
    resp = await test_client.get("/texts")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    text_id = resp.json()[0]["id"]
    # get one by specific id
    resp = await test_client.get(f"/texts/{text_id}")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["id"] == text_id
    # get one by non-existent id
    resp = await test_client.get("/texts/637b9ad396d541a505e5439b")
    assert status_assertion(404, resp)


@pytest.mark.anyio
async def test_create_text(
    test_client: AsyncClient,
    status_assertion,
    login,
):
    await login(is_superuser=True)
    payload = {
        "title": "Just a Test",
        "slug": "justatest",
        "levels": [[{"locale": "enUS", "translation": "foo"}]],
    }
    resp = await test_client.post(
        "/texts",
        json=payload,
    )
    assert status_assertion(201, resp)
    assert "id" in resp.json()
    assert "slug" in resp.json()
    assert resp.json()["slug"] == "justatest"
    # create duplicate
    resp = await test_client.post(
        "/texts",
        json=payload,
    )
    assert status_assertion(409, resp)


@pytest.mark.anyio
async def test_create_text_unauthorized(
    test_client: AsyncClient,
    status_assertion,
    login,
):
    await login()  # not a superuser (=unauthorized)!
    payload = {"title": "Meow", "slug": "meow", "levels": ["meow"]}
    resp = await test_client.post(
        "/texts",
        json=payload,
    )
    assert status_assertion(403, resp)


@pytest.mark.anyio
async def test_create_text_unauthenticated(
    test_client: AsyncClient,
    status_assertion,
):
    payload = {"title": "Meow", "slug": "meow", "levels": ["meow"]}
    resp = await test_client.post("/texts", json=payload)
    assert status_assertion(401, resp)


@pytest.mark.anyio
async def test_update_text(
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    login,
    wrong_id,
):
    await insert_sample_data("texts")

    # get text from db
    resp = await test_client.get("/texts")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    text = resp.json()[0]

    # update text unauthenticated
    text_update = {"title": "Unauthenticated text update"}
    resp = await test_client.patch(f"/texts/{text['id']}", json=text_update)
    assert status_assertion(401, resp)

    # log in as superuser
    await login(is_superuser=True)

    # update text
    text_update = {"title": "Another text"}
    resp = await test_client.patch(
        f"/texts/{text['id']}",
        json=text_update,
    )
    assert status_assertion(200, resp)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(text["id"])
    assert "title" in resp.json()
    assert resp.json()["title"] == "Another text"

    # update unchanged text
    resp = await test_client.patch(
        f"/texts/{text['id']}",
        json=text_update,
    )
    assert status_assertion(200, resp)

    # update invalid text
    text_update = {"title": "Yet another text"}
    resp = await test_client.patch(
        f"/texts/{wrong_id}",
        json=text_update,
    )
    assert status_assertion(404, resp)


@pytest.mark.anyio
async def test_delete_text(
    test_client: AsyncClient, insert_sample_data, status_assertion, login, wrong_id
):
    inserted_ids = await insert_sample_data("texts", "locations")
    text_id = inserted_ids["texts"][1]

    # log in as superuser
    await login(is_superuser=True)

    # try to delete text with wrong ID
    resp = await test_client.delete(
        f"/texts/{wrong_id}",
    )
    assert status_assertion(404, resp)

    # delete text
    resp = await test_client.delete(
        f"/texts/{text_id}",
    )
    assert status_assertion(204, resp)

    # try to delete all texts (must fail because last text cannot be deleted)
    for text_id in inserted_ids["texts"]:
        resp = await test_client.delete(
            f"/texts/{text_id}",
        )
        delete_failed = resp.status_code == 400
        if delete_failed:
            break
    assert delete_failed


@pytest.mark.anyio
async def test_download_structure_template(
    test_client: AsyncClient, insert_sample_data, status_assertion, login, wrong_id
):
    inserted_ids = await insert_sample_data("texts", "locations")
    text_id = inserted_ids["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # download template
    resp = await test_client.get(
        f"/texts/{text_id}/template",
    )
    assert status_assertion(200, resp)

    # download template w/ wrong ID
    resp = await test_client.get(
        f"/texts/{wrong_id}/template",
    )
    assert status_assertion(404, resp)


@pytest.mark.anyio
async def test_insert_level(
    test_client: AsyncClient, insert_sample_data, status_assertion, login, wrong_id
):
    await insert_sample_data("texts", "locations")

    # log in as superuser
    await login(is_superuser=True)

    # get text from db
    resp = await test_client.get("/texts")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    text = resp.json()[0]
    assert len(text["levels"]) == 3

    # prepare new level data
    level_data = [
        {"locale": "enUS", "translation": "A level"},
        {"locale": "deDE", "translation": "Eine Ebene"},
    ]

    # insert new level 0
    resp = await test_client.post(
        f"/texts/{text['id']}/level/0",
        json=level_data,
    )
    assert status_assertion(200, resp)
    assert "id" in resp.json()
    assert len(resp.json()["levels"]) == 4

    # insert new level 1
    resp = await test_client.post(
        f"/texts/{text['id']}/level/1",
        json=level_data,
    )
    assert status_assertion(200, resp)
    assert "id" in resp.json()
    assert len(resp.json()["levels"]) == 5

    # insert new level for wrong text ID
    resp = await test_client.post(
        f"/texts/{wrong_id}/level/0",
        json=level_data,
    )
    assert status_assertion(404, resp)

    # insert new level at invalid index
    resp = await test_client.post(
        f"/texts/{text['id']}/level/12",
        json=level_data,
    )
    assert status_assertion(400, resp)


@pytest.mark.anyio
async def test_delete_top_level(
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    login,
):
    inserted_ids = await insert_sample_data("texts", "locations")
    text_id = inserted_ids["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # delete level 0
    resp = await test_client.delete(
        f"/texts/{text_id}/level/0",
    )
    assert status_assertion(200, resp)
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_delete_bottom_level(
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    login,
):
    inserted_ids = await insert_sample_data("texts", "locations")
    text_id = inserted_ids["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # delete level 1
    resp = await test_client.delete(
        f"/texts/{text_id}/level/1",
    )
    assert status_assertion(200, resp)
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_delete_middle_level(
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    login,
):
    inserted_ids = await insert_sample_data("texts", "locations")
    text_id = inserted_ids["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # create extra level
    resp = await test_client.post(
        f"/texts/{text_id}/level/2",
        json=[{"locale": "*", "translation": "Some Level"}],
    )
    assert status_assertion(200, resp)
    assert "id" in resp.json()

    # delete level 1
    resp = await test_client.delete(
        f"/texts/{text_id}/level/1",
    )
    assert status_assertion(200, resp)
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_fail_delete_level(
    test_client: AsyncClient, insert_sample_data, status_assertion, login, wrong_id
):
    inserted_ids = await insert_sample_data("texts", "locations")
    text_id = inserted_ids["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # delete level for wrong text ID
    resp = await test_client.delete(
        f"/texts/{wrong_id}/level/0",
    )
    assert status_assertion(404, resp)

    # delete level at invalid index
    resp = await test_client.delete(
        f"/texts/{text_id}/level/12",
    )
    assert status_assertion(400, resp)


@pytest.mark.anyio
async def test_import_text_structure(
    test_client: AsyncClient,
    insert_sample_data,
    get_sample_data_path,
    status_assertion,
    login,
    wrong_id,
):
    text_id = (await insert_sample_data("texts"))["texts"][0]
    await login(is_superuser=True)
    sample_data_path = get_sample_data_path("import/structure_fdhdgg.json")

    # upload invalid structure definition file (give wrong MIME type)
    with open(sample_data_path, "rb") as f:
        resp = await test_client.post(
            f"/texts/{text_id}/structure",
            files={"file": (f.name, f, "text/plain")},
        )
        assert status_assertion(400, resp)

    # upload invalid structure definition file (invalid JSON)
    resp = await test_client.post(
        f"/texts/{text_id}/structure",
        files={"file": ("fdhdgg.json", r"{foo: bar}", "application/json")},
    )
    assert status_assertion(422, resp)

    # upload structure definition file for wrong text ID
    with open(sample_data_path, "rb") as f:
        resp = await test_client.post(
            f"/texts/{wrong_id}/structure",
            files={"file": (f.name, f, "application/json")},
        )
        assert status_assertion(404, resp)

    # upload valid structure definition file
    with open(sample_data_path, "rb") as f:
        resp = await test_client.post(
            f"/texts/{text_id}/structure",
            files={"file": (f.name, f, "application/json")},
        )
        assert status_assertion(201, resp)

    # try it again (should fail because text now already has locations)
    with open(sample_data_path, "rb") as f:
        resp = await test_client.post(
            f"/texts/{text_id}/structure",
            files={"file": (f.name, f, "application/json")},
        )
        assert status_assertion(409, resp)


@pytest.mark.anyio
async def test_update_text_structure(
    test_client: AsyncClient,
    insert_sample_data,
    get_sample_data_path,
    status_assertion,
    login,
    wrong_id,
    wait_for_task_success,
):
    text_id = (await insert_sample_data("texts", "locations"))["texts"][0]
    await login(is_superuser=True)
    sample_data_path = get_sample_data_path("import/structure_fdhdgg_updates.json")

    # upload invalid locations updates file (give wrong MIME type)
    with open(sample_data_path, "rb") as f:
        resp = await test_client.patch(
            f"/texts/{text_id}/structure",
            files={"file": (f.name, f, "text/plain")},
        )
        assert status_assertion(400, resp)

    # upload invalid locations updates file (invalid JSON)
    resp = await test_client.patch(
        f"/texts/{text_id}/structure",
        files={"file": ("fdhdgg.json", r"{foo: bar}", "application/json")},
    )
    assert status_assertion(400, resp)

    # upload invalid locations updates file (not a list/array)
    resp = await test_client.patch(
        f"/texts/{text_id}/structure",
        files={"file": ("fdhdgg.json", '{"foo": "bar"}', "application/json")},
    )
    assert status_assertion(422, resp)

    # upload locations updates file for wrong text ID
    with open(sample_data_path, "rb") as f:
        resp = await test_client.patch(
            f"/texts/{wrong_id}/structure",
            files={"file": (f.name, f, "application/json")},
        )
        assert status_assertion(404, resp)

    # upload valid locations updates file
    with open(sample_data_path, "rb") as f:
        resp = await test_client.patch(
            f"/texts/{text_id}/structure",
            files={"file": (f.name, f, "application/json")},
        )
        assert status_assertion(202, resp)
        assert "id" in resp.json()
        assert await wait_for_task_success(resp.json()["id"])
