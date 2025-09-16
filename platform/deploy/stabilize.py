import os, time
from fastapi import APIRouter, Request, HTTPException
from .main import get_pool, resolve_project_id
from .audit.router import ingest

router_stab = APIRouter(prefix="/v1/stabilize", tags=["stabilize"])

# Defaults can be tuned via env
CLAMP_RPS = int(os.getenv("STAB_CLAMP_RPS", "200"))
CB_CONSEC_ERR = int(os.getenv("STAB_CB_ERR", "2"))
DEPRIORITIZE_QUEUES = os.getenv("STAB_DEPRIORITIZE", "emails,reports,analytics").split(",")

_state = {"enabled": False, "since": None}

@router_stab.post("/enter")
async def enter(request: Request):
    key = request.headers.get("x-api-key"); 
    if not key: raise HTTPException(401, "Missing key")
    if _state["enabled"]: return {"ok": True, "already": True}
    _state["enabled"] = True; _state["since"] = time.time()
    # Emit audit
    await ingest(request, type("Obj",(object,),{
      "source":"stabilize","kind":"enter","subject":"stabilize_mode","actor":"policy",
      "payload": {"clamp_rps":CLAMP_RPS,"cb_errors":CB_CONSEC_ERR,"deprioritized":DEPRIORITIZE_QUEUES}
    })())
    return {"ok": True, "state": _state}

@router_stab.post("/exit")
async def exit_(request: Request):
    key = request.headers.get("x-api-key"); 
    if not key: raise HTTPException(401, "Missing key")
    _state["enabled"] = False
    await ingest(request, type("Obj",(object,),{
      "source":"stabilize","kind":"exit","subject":"stabilize_mode","actor":"policy","payload":{}
    })())
    return {"ok": True, "state": _state}

def is_stabilized(): return bool(_state["enabled"])
def clamp_rps(): return CLAMP_RPS
def cb_errs(): return CB_CONSEC_ERR
def deprioritized(): return set(DEPRIORITIZE_QUEUES)
