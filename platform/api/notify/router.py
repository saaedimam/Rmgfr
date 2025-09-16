import asyncpg, os
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from .expo import send_expo_push
from ..main import get_pool, resolve_project_id  # reuse from main

router_notify = APIRouter(prefix="/v1/mobile", tags=["mobile"])

class RegisterTokenIn(BaseModel):
    expo_push_token: str
    user_id: str | None = None
    device_hash: str | None = None
    platform: str | None = None

@router_notify.post("/register-push-token")
async def register_push_token(request: Request, body: RegisterTokenIn):
    key = request.headers.get("x-api-key")
    if not key: raise HTTPException(401, "Missing X-API-Key")
    pool = await get_pool()
    async with pool.acquire() as conn:
        project_id = await resolve_project_id(conn, key)
        await conn.execute(
            "insert into mobile_push_tokens(project_id,user_id,device_hash,expo_push_token,platform) values ($1,$2,$3,$4,$5) on conflict (project_id,expo_push_token) do nothing",
            project_id, body.user_id, body.device_hash, body.expo_push_token, body.platform
        )
    return {"ok": True}

class PushIn(BaseModel):
    expo_push_token: str
    title: str
    body: str
    data: dict | None = None

@router_notify.post("/push")
async def push(request: Request, body: PushIn):
    key = request.headers.get("x-api-key")
    if not key: raise HTTPException(401, "Missing X-API-Key")
    status, resp = await send_expo_push(body.expo_push_token, body.title, body.body, body.data)
    return {"status": status, "resp": resp}
