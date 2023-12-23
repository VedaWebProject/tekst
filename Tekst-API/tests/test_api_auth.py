import pytest

from httpx import AsyncClient
from tekst.auth import create_initial_superuser, create_sample_users


@pytest.mark.anyio
async def test_register(test_client: AsyncClient, get_fake_user, status_fail_msg):
    payload = get_fake_user()
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_register_invalid_pw(
    test_client: AsyncClient, get_fake_user, status_fail_msg
):
    payload = get_fake_user()

    payload["username"] = "uuuuhhh"
    payload["password"] = "foo"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "aaaa"
    payload["password"] = "foooooooooooo"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "bbbb"
    payload["password"] = "Fooooooooooo"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "cccc"
    payload["password"] = "Foo1234"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"


@pytest.mark.anyio
async def test_register_username_exists(
    test_client: AsyncClient, get_fake_user, status_fail_msg
):
    payload = get_fake_user()

    payload["username"] = "someuser"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 201, status_fail_msg(201, resp)

    payload["email"] = "hello@hello.com"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_register_email_exists(
    test_client: AsyncClient, get_fake_user, status_fail_msg
):
    payload = get_fake_user()

    payload["email"] = "first@test.com"
    payload["username"] = "first"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 201, status_fail_msg(201, resp)

    payload["username"] = "second"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"] == "REGISTER_USER_ALREADY_EXISTS"


@pytest.mark.anyio
async def test_login(
    config,
    register_test_user,
    test_client: AsyncClient,
    status_fail_msg,
):
    user_data = await register_test_user()
    payload = {"username": user_data["email"], "password": user_data["password"]}
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert resp.status_code == 204, status_fail_msg(204, resp)
    assert resp.cookies.get(config.security_auth_cookie_name)


@pytest.mark.anyio
async def test_login_fail_bad_pw(
    config,
    register_test_user,
    test_client: AsyncClient,
    status_fail_msg,
):
    user_data = await register_test_user()
    payload = {"username": user_data["username"], "password": "XoiPOI09871"}
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"] == "LOGIN_BAD_CREDENTIALS"


@pytest.mark.anyio
async def test_login_fail_unverified(
    config,
    register_test_user,
    test_client: AsyncClient,
    status_fail_msg,
):
    user_data = await register_test_user(is_verified=False)
    payload = {"username": user_data["email"], "password": user_data["password"]}
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"] == "LOGIN_USER_NOT_VERIFIED"


@pytest.mark.anyio
async def test_user_updates_self(
    config,
    register_test_user,
    get_session_cookie,
    test_client: AsyncClient,
    status_fail_msg,
):
    user_data = await register_test_user()
    session_cookie = await get_session_cookie(user_data)
    # get user data from /users/me
    resp = await test_client.get(
        "/users/me",
        cookies=session_cookie,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    # update own first name
    user_id = resp.json()["id"]
    updates = {"name": "Bird Person"}
    resp = await test_client.patch(
        "/users/me",
        json=updates,
        cookies=session_cookie,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["id"] == user_id
    assert resp.json()["name"] == "Bird Person"


@pytest.mark.anyio
async def test_user_deletes_self(
    config,
    register_test_user,
    get_session_cookie,
    test_client: AsyncClient,
    status_fail_msg,
):
    user_data = await register_test_user()
    session_cookie = await get_session_cookie(user_data)
    # delete self
    resp = await test_client.delete(
        "/users/me",
        cookies=session_cookie,
    )
    assert resp.status_code == 204, status_fail_msg(204, resp)


@pytest.mark.anyio
async def test_create_sample_users():
    await create_sample_users()


@pytest.mark.anyio
async def test_create_initial_superuser():
    await create_initial_superuser()  # will abort because of dev mode
    await create_initial_superuser(force=True)  # forced despite dev mode
