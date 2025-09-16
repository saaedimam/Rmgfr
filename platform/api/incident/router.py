import os, json, asyncpg, time
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from ..main import get_pool, resolve_project_id
from ..audit.router import ingest

router_inc = APIRouter(prefix="/v1/incident", tags=["incident"])

class IncidentOpenIn(BaseModel):
    severity: str
    title: str
    commander: str | None = None
    summary: str | None = None

class IncidentEventIn(BaseModel):
    incident_id: str
    kind: str
    payload: dict = {}

class IncidentUpdateIn(BaseModel):
    incident_id: str
    status: str
    summary: str | None = None

async def _project(conn, key): return await resolve_project_id(conn, key)

@router_inc.post("/open")
async def open_incident(request: Request, body: IncidentOpenIn):
    key = request.headers.get("x-api-key"); 
    if not key: raise HTTPException(401, "Missing key")
    async with (await get_pool()).acquire() as conn:
        project_id = await _project(conn, key)
        row = await conn.fetchrow("""insert into incidents(project_id,severity,title,commander,summary)
                                     values($1,$2,$3,$4,$5) returning id, started_at""",
                                     project_id, body.severity, body.title, body.commander, body.summary)
        # Emit audit event
        await ingest(request, type("Obj",(object,),{
          "source":"incident","kind":"opened","subject":str(row["id"]),"actor":body.commander or "system",
          "payload":{"severity":body.severity,"title":body.title}
        })())
        return {"id": str(row["id"]), "started_at": row["started_at"]}

@router_inc.post("/event")
async def add_event(request: Request, body: IncidentEventIn):
    key = request.headers.get("x-api-key")
    if not key: raise HTTPException(401, "Missing key")
    async with (await get_pool()).acquire() as conn:
        await conn.execute("insert into incident_events(incident_id,kind,payload) values ($1,$2,$3)",
                           body.incident_id, body.kind, json.dumps(body.payload))
    return {"ok": True}

@router_inc.post("/update")
async def update_incident(request: Request, body: IncidentUpdateIn):
    key = request.headers.get("x-api-key")
    if not key: raise HTTPException(401, "Missing key")
    status = body.status.upper()
    if status not in ("OPEN","MITIGATED","RESOLVED","CANCELLED"): 
        raise HTTPException(400, "bad status")
    async with (await get_pool()).acquire() as conn:
        sets, vals = ["status=$1"], [status]
        if status == "MITIGATED": sets.append("mitigated_at=now()")
        if status == "RESOLVED":  sets.append("resolved_at=now()")
        if body.summary: 
            sets.append("summary=$2"); vals.append(body.summary)
        q = f"update incidents set {', '.join(sets)} where id=$3"
        vals.append(body.incident_id)
        await conn.execute(q, *vals)
    return {"ok": True}
