import os, json, asyncpg
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from .main import get_pool
from .admin import ADMIN_TOKEN
from .audit.router import ingest

router_flags = APIRouter(prefix="/admin/flags", tags=["admin"])

class FlagUpsertIn(BaseModel):
    project_id: str
    key: str
    enabled: bool
    description: str | None = None

async def require_admin(x_admin_token: str = Header(default="")):
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "Unauthorized (admin)")
    return True

@router_flags.post("/upsert")
async def upsert_flag(body: FlagUpsertIn, ok = await require_admin()):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("select upsert_flag($1,$2,$3,$4)", body.project_id, body.key, body.enabled, body.description)
        # Emit audit event
        await ingest(type("Obj",(object,),{"headers":{"x-api-key":"admin"}})(), type("Obj",(object,),{
          "source":"flags","kind":"flag_set","subject":body.key,"actor":"admin",
          "payload":{"enabled":body.enabled,"description":body.description}
        })())
    return {"ok": True}

@router_flags.get("/{project_id}")
async def list_flags(project_id: str, ok = await require_admin()):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("select id, key, enabled, description, updated_at from feature_flags where project_id=$1 order by key", project_id)
        return [dict(r) for r in rows]
