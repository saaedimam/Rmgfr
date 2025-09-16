import os, pytest
from main import app
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_requires_key():
    client = AsyncClient(app=app, base_url="http://test")
    r = await client.get("/v1/events")
    assert r.status_code == 401
    r = await client.get("/v1/decisions")
    assert r.status_code == 401
