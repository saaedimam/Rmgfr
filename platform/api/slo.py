import os, time, statistics as stats
from fastapi import APIRouter, Request, HTTPException
from ..main import get_pool, resolve_project_id

router_slo = APIRouter(prefix="/v1/slo", tags=["slo"])

# simplistic in-memory meters (swap with Prometheus in prod)
WINDOW_SEC = 3600
_hist = {"/v1/events": [], "/v1/decisions": [], "/health": []}
_errs = {k: 0 for k in _hist}

def record_latency(path: str, ms: float, ok: bool):
    now = time.time()
    _hist[path].append((now, ms))
    if not ok: _errs[path] += 1
    # evict old
    cutoff = now - WINDOW_SEC
    _hist[path] = [(t,v) for (t,v) in _hist[path] if t >= cutoff]

def p99_9(samples):
    if not samples: return None
    xs = sorted(samples)
    idx = int(round(0.999*(len(xs)-1)))
    return xs[idx]

@router_slo.get("/snapshot")
async def snapshot(request: Request):
    key = request.headers.get("x-api-key")
    if not key: raise HTTPException(401, "Missing key")
    pool = await get_pool()
    async with pool.acquire() as conn:
        project_id = await resolve_project_id(conn, key)

    out = []
    for ep, series in _hist.items():
        latencies = [v for _,v in series]
        p999 = p99_9(latencies) or 0.0
        total = max(len(latencies), 1)
        errs = _errs[ep]
        err_rate = min(1.0, errs / total)
        uptime = 1.0 - err_rate
        # simple error budget: target 99.9% (0.001 allowed)
        budget_remaining = max(0.0, 1.0 - max(0.0, uptime - 0.999) / 0.001) if total>100 else 1.0
        out.append({"endpoint": ep, "latency_p99_9": p999, "error_rate": err_rate, "uptime": uptime, "budget_remaining": budget_remaining})
    return {"window":"1h","snapshots":out}
