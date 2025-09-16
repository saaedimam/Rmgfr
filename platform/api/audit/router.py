from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from ..main import get_pool, resolve_project_id

router_audit = APIRouter(prefix="/v1/audit", tags=["audit"])

class AuditIn(BaseModel):
    source: str   # incident|sentry|deploy|flags|policy|stabilize
    kind: str     # opened|update|error|release|flag_set|budget_burn|enter|exit ...
    subject: str | None = None
    actor: str | None = "system"
    payload: dict = {}

@router_audit.post("/ingest")
async def ingest(request: Request, body: AuditIn):
    key = request.headers.get("x-api-key")
    if not key: raise HTTPException(401, "Missing key")
    async with (await get_pool()).acquire() as conn:
        project_id = await resolve_project_id(conn, key)
        await conn.execute(
          "insert into audit_events(project_id,source,kind,subject,actor,payload) values ($1,$2,$3,$4,$5,$6)",
          project_id, body.source, body.kind, body.subject, body.actor, body.payload
        )
    return {"ok": True}

@router_audit.get("/search")
async def search(request: Request, q: str = "", limit: int = 200):
    key = request.headers.get("x-api-key")
    if not key: raise HTTPException(401, "Missing key")
    async with (await get_pool()).acquire() as conn:
        project_id = await resolve_project_id(conn, key)
        rows = await conn.fetch(
          """select at,source,kind,subject,actor,payload
             from audit_events
             where project_id=$1 and (subject ilike $2 or kind ilike $2 or source ilike $2)
             order by at desc limit $3""",
          project_id, f"%{q}%", min(500, max(50, limit))
        )
    return {"items":[dict(r) for r in rows]}
