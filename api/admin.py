import os, secrets, hashlib, asyncpg
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from .main import get_pool  # reuse pool from main.py

router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

async def require_admin(x_admin_token: str = Header(default="")):
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "Unauthorized (admin)")
    return True

class BootstrapIn(BaseModel):
    org_name: str
    project_name: str

@router.post("/bootstrap")
async def bootstrap_tenant(body: BootstrapIn, ok: bool = Depends(require_admin)):
    """
    Creates org + project, mints an API key (plaintext returned ONCE),
    stores hash in projects.api_key_hash and api_keys.key_hash.
    """
    api_key_plain = f"prj_{secrets.token_urlsafe(24)}"
    api_key_hash = sha256_hex(api_key_plain)

    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            org_id = await conn.fetchval(
                "insert into orgs(name) values($1) returning id", body.org_name
            )
            project_id = await conn.fetchval(
                "insert into projects(org_id, name, api_key_hash) values($1,$2,$3) returning id",
                org_id, body.project_name, api_key_hash
            )
            await conn.execute(
                "insert into api_keys(project_id, key_hash) values($1,$2)",
                project_id, api_key_hash
            )
    return {
        "org_id": str(org_id),
        "project_id": str(project_id),
        "api_key": api_key_plain,  # show ONCE; you will store safely
        "note": "Store this API key securely. It will not be shown again."
    }
