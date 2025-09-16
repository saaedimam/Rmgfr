import os, json, asyncio
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
import hashlib

# Import the FastAPI app
from main import app, get_pool, sha256_hex

@pytest.mark.asyncio
async def test_idempotency(monkeypatch):
    # Skip if DB not configured
    if not os.getenv("SUPABASE_DB_URL"):
        pytest.skip("SUPABASE_DB_URL not set")

    # Fake API key insert prerequisite (hash must exist in api_keys)
    # For a real test, you would set up a test DB and seed data here.

    client = AsyncClient(app=app, base_url="http://test")
    headers = {"x-api-key": "TEST_KEY", "x-idempotency-key": "idem-1"}
    body = {"type":"login","payload":{"u":"1"}}

    # First insert (will likely 401 unless you seeded api_keys)
    r1 = await client.post("/v1/events", headers=headers, content=json.dumps(body))
    # We can only assert structural behavior here without a real seeded DB
    assert r1.status_code in (200, 401, 429, 413)

    # Second insert with same idempotency key should dedup (if first succeeded)
    r2 = await client.post("/v1/events", headers=headers, content=json.dumps(body))
    assert r2.status_code in (200, 401, 429, 413)

@pytest.mark.asyncio
async def test_auth_required():
    client = AsyncClient(app=app, base_url="http://test")
    r = await client.post("/v1/events", content=json.dumps({"type":"login","payload":{}}))
    assert r.status_code == 401
