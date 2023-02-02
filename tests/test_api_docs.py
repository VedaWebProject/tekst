import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_load_openapi_schema(config, root_path, test_client: AsyncClient):
    endpoint = f"{root_path}{config.doc.openapi_url}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"


@pytest.mark.anyio
async def test_load_swaggerui(config, root_path, test_client: AsyncClient):
    endpoint = f"{root_path}{config.doc.swaggerui_url}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"


@pytest.mark.anyio
async def test_load_redoc(config, root_path, test_client: AsyncClient):
    endpoint = f"{root_path}{config.doc.redoc_url}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"
