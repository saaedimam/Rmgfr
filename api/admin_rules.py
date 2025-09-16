import os, json, asyncpg
from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel
from .main import get_pool
from .admin import ADMIN_TOKEN

router_rules = APIRouter(prefix="/admin/rules", tags=["admin"])

class RuleUpsertIn(BaseModel):
    project_id: str
    max_events_per_ip: int = 60
    max_events_per_user: int = 60
    max_events_per_device: int = 120
    max_events_global: int = 5000
    window_seconds: int = 300

async def require_admin(x_admin_token: str = Header(default="")):
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "Unauthorized (admin)")
    return True

@router_rules.post("/upsert")
async def upsert_rules(body: RuleUpsertIn, ok = Depends(require_admin)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "select upsert_rule_config($1,$2,$3,$4,$5,$6)",
            body.project_id, body.max_events_per_ip, body.max_events_per_user,
            body.max_events_per_device, body.max_events_global, body.window_seconds
        )
    return {"ok": True}
