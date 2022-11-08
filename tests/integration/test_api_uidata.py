import pytest
from httpx import AsyncClient
from textrig import pkg_meta


@pytest.mark.anyio
async def test_uidata(root_path, test_client: AsyncClient):
    endpoint = f"{root_path}/uidata"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"response status {resp.status_code} != 200"
    assert resp.json()["platform"]["version"] == pkg_meta["version"]
