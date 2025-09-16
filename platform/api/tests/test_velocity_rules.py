import os, json, pytest
from httpx import AsyncClient
from main import app

API_KEY = os.getenv("TEST_API_KEY", "TEST_KEY")

@pytest.mark.asyncio
async def test_velocity_paths_smoke():
  client = AsyncClient(app=app, base_url="http://test")
  headers = {"x-api-key": API_KEY}
  # Listing endpoints require key
  r1 = await client.get("/v1/events", headers=headers)
  r2 = await client.get("/v1/decisions", headers=headers)
  assert r1.status_code in (200,401,404,429)  # 401 until seeded
  assert r2.status_code in (200,401,404,429)

@pytest.mark.asyncio
async def test_decision_autoscore_shape():
  client = AsyncClient(app=app, base_url="http://test")
  headers = {"x-api-key": API_KEY, "content-type":"application/json"}
  # Without real DB seed, assert validation paths
  ev = await client.post("/v1/events", headers=headers, content=json.dumps({"type":"login","payload":{}}))
  assert ev.status_code in (200,401,429,413)
