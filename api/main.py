import os, hashlib, json, asyncpg
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, constr
import sentry_sdk
from typing import Optional, List
from api.admin import router as admin_router
from api.admin_rules import router_rules
from api.flags_admin import router_flags
from api.notify.router import router_notify
from api.rules.engine import evaluate_rules
from obs import init_obs
from flags_middleware import ReleaseChannelFlags
from api.slo import record_latency, router_slo
from api.incident.router import router_inc
from api.audit.router import router_audit
from api.stabilize import router_stab, is_stabilized, clamp_rps, cb_errs, deprioritized
from time import perf_counter
from collections import deque
from fastapi import Response, Depends
from fastapi_limiter.depends import RateLimiter
from rate_limit import setup_rate_limit

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN_API"))

DB_DSN = os.getenv("SUPABASE_DB_URL")

app = FastAPI(title="Platform API", version="1.1.0")
app.add_middleware(ReleaseChannelFlags)
init_obs()

# --- SLO Metrics Middleware ---
@app.middleware("http")
async def metrics_mw(request, call_next):
    start = perf_counter()
    try:
        resp = await call_next(request)
        ok = resp.status_code < 500
    except Exception:
        ok = False
        raise
    finally:
        path = request.url.path
        if path in ("/v1/events","/v1/decisions","/health"):
            ms = (perf_counter() - start) * 1000.0
            record_latency(path, ms, ok)
    return resp

# --- Stabilize Mode Middleware ---
# simple token bucket for RPS clamp (global for demo)
_bucket = deque()
BUCKET_SEC = 1.0

@app.middleware("http")
async def stabilize_mw(request, call_next):
    start = perf_counter()
    # Clamp RPS
    if is_stabilized():
        now = perf_counter()
        while _bucket and now - _bucket[0] > BUCKET_SEC:
            _bucket.popleft()
        if len(_bucket) >= clamp_rps():
            return Response("stabilize: throttled", status_code=503)
        _bucket.append(now)
    # Deprioritize queues (example header for workers)
    request.state.deprioritized = deprioritized() if is_stabilized() else set()
    # Tighten circuit breaker knobs via header hints (downstream aware)
    request.state.cb_consecutive_errors = cb_errs() if is_stabilized() else 5
    resp = await call_next(request)
    return resp

# --- CORS (tighten as needed) ---
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# --- DB Pool ---
_pool: asyncpg.Pool | None = None
async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        if not DB_DSN:
            raise RuntimeError("SUPABASE_DB_URL not set")
        _pool = await asyncpg.create_pool(dsn=DB_DSN, min_size=1, max_size=10)
    return _pool

# --- Models ---
class EventIn(BaseModel):
    type: constr(strip_whitespace=True, to_lower=True) = Field(pattern="^(login|signup|checkout|custom)$")
    actor_user_id: Optional[constr(max_length=200)] = None
    ip: Optional[constr(max_length=100)] = None
    device_hash: Optional[constr(max_length=200)] = None
    payload: dict = Field(default_factory=dict)

class DecisionIn(BaseModel):
    event_id: constr(min_length=1)
    outcome: constr(strip_whitespace=True, to_lower=True) = Field(pattern="^(allow|deny|review)$")
    score: Optional[int] = Field(default=None)
    reasons: Optional[List[constr(max_length=100)]] = Field(default=None)

# --- Helpers ---
MAX_PAYLOAD = 16 * 1024  # 16KB soft limit

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

async def resolve_project_id(conn: asyncpg.Connection, api_key: str) -> str:
    # Constant-time check by hashing input and comparing to stored hashes
    key_hash = sha256_hex(api_key)
    row = await conn.fetchrow("select project_id from api_keys where key_hash=$1", key_hash)
    if not row:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return str(row["project_id"])

# --- Middleware: rate limit stub (per-IP token bucket in-memory) ---
from time import time
from collections import defaultdict, deque

RATE_LIMIT = 60  # tokens per minute
_BUCKET = defaultdict(lambda: deque())

@app.middleware("http")
async def ratelimit_mw(request: Request, call_next):
    ip = request.headers.get("x-forwarded-for") or request.client.host or "unknown"
    now = time()
    q = _BUCKET[ip]
    # purge entries older than 60s
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= RATE_LIMIT:
        raise HTTPException(429, "Rate limit")
    q.append(now)
    return await call_next(request)

@app.get("/health")
async def health():
    return {"status": "ok", "version": app.version}

@app.get("/v1/events")
async def list_events(request: Request, page: int = 1, page_size: int = 50):
    api_key = request.headers.get("x-api-key")
    if not api_key: raise HTTPException(401, "Missing X-API-Key")
    if page_size > 200: raise HTTPException(400, "page_size too large")
    pool = await get_pool()
    async with pool.acquire() as conn:
        project_id = await resolve_project_id(conn, api_key)
        rows = await conn.fetch(
            "select id, type, actor_user_id, ip, device_hash, event_ts from events where project_id=$1 order by event_ts desc limit $2 offset $3",
            project_id, page_size, (page-1)*page_size
        )
        return [dict(r) for r in rows]

@app.get("/v1/decisions")
async def list_decisions(request: Request, page: int = 1, page_size: int = 50):
    api_key = request.headers.get("x-api-key")
    if not api_key: raise HTTPException(401, "Missing X-API-Key")
    if page_size > 200: raise HTTPException(400, "page_size too large")
    pool = await get_pool()
    async with pool.acquire() as conn:
        project_id = await resolve_project_id(conn, api_key)
        rows = await conn.fetch(
            "select id, event_id, outcome, score, reasons, decided_at from decisions where project_id=$1 order by decided_at desc limit $2 offset $3",
            project_id, page_size, (page-1)*page_size
        )
        return [dict(r) for r in rows]

# --- Endpoints ---
@app.post("/v1/events")
async def create_event(request: Request):
    # 1) Validate payload size
    raw = await request.body()
    if len(raw) > MAX_PAYLOAD:
        raise HTTPException(413, "Payload too large")
    try:
        body = EventIn(**json.loads(raw or b"{}"))
    except ValidationError as e:
        raise HTTPException(400, f"Invalid body: {e.errors()}")

    api_key = request.headers.get("x-api-key")
    if not api_key:
        raise HTTPException(401, "Missing X-API-Key")

    idem_key = request.headers.get("x-idempotency-key")
    idem_hash = sha256_hex(idem_key) if idem_key else None

    pool = await get_pool()
    async with pool.acquire() as conn:
        project_id = await resolve_project_id(conn, api_key)

        # If idempotency: find existing
        if idem_hash:
            existing = await conn.fetchrow(
                "select id from events where idempotency_key=$1 and project_id=$2",
                idem_hash, project_id
            )
            if existing:
                return {"event_id": str(existing["id"]), "accepted": True, "dedup": True}

        row = await conn.fetchrow(
            """
            insert into events (project_id, type, actor_user_id, ip, device_hash, payload, idempotency_key)
            values ($1, $2, $3, $4, $5, $6, $7)
            returning id
            """,
            project_id, body.type, body.actor_user_id, body.ip, body.device_hash, json.dumps(body.payload), idem_hash
        )
        return {"event_id": str(row["id"]), "accepted": True, "dedup": False}

@app.post("/v1/decisions")
async def create_decision(request: Request):
    raw = await request.body()
    if len(raw) > MAX_PAYLOAD:
        raise HTTPException(413, "Payload too large")
    try:
        body = DecisionIn(**json.loads(raw or b"{}"))
    except ValidationError as e:
        raise HTTPException(400, f"Invalid body: {e.errors()}")

    api_key = request.headers.get("x-api-key")
    if not api_key:
        raise HTTPException(401, "Missing X-API-Key")

    pool = await get_pool()
    async with pool.acquire() as conn:
        project_id = await resolve_project_id(conn, api_key)

        # Ensure event belongs to same project
        ev = await conn.fetchrow("select id from events where id=$1 and project_id=$2", body.event_id, project_id)
        if not ev:
            raise HTTPException(404, "Event not found for project")

        # auto-evaluate rules if score is not provided
        outcome = body.outcome
        score = body.score
        reasons = body.reasons or []
        if score is None:
            rr = await evaluate_rules(conn, project_id, body.event_id)
            # If client asked ALLOW but rules suggest stronger action, escalate to max(outcome, rr)
            # Simple precedence: deny > review > allow
            precedence = {"allow":0,"review":1,"deny":2}
            if precedence[rr.outcome] > precedence[outcome]:
                outcome = rr.outcome
            score = rr.score
            reasons = list(set(reasons + rr.reasons))
        row = await conn.fetchrow(
            "insert into decisions (project_id,event_id,outcome,score,reasons) values ($1,$2,$3,$4,$5) returning id,outcome,score,reasons,decided_at",
            project_id, body.event_id, outcome, score, json.dumps(reasons)
        )
        return {"decision_id": str(row["id"]), "outcome": row["outcome"], "score": row["score"],
                "reasons": row["reasons"], "decided_at": row["decided_at"].isoformat()}

@app.get("/v1/cases")
async def list_cases(request: Request, status: Optional[str] = None, page: int = 1, page_size: int = 50):
    api_key = request.headers.get("x-api-key")
    if not api_key:
        raise HTTPException(401, "Missing X-API-Key")
    if page_size > 200:
        raise HTTPException(400, "page_size too large")

    pool = await get_pool()
    async with pool.acquire() as conn:
        project_id = await resolve_project_id(conn, api_key)
        params = [project_id]
        q = "select id, status, title, created_at from cases where project_id=$1"
        if status:
            q += " and status=$2"
            params.append(status)
        q += " order by created_at desc limit $3 offset $4"
        params.extend([page_size, (page - 1) * page_size])
        rows = await conn.fetch(q, *params)
        return [dict(r) for r in rows]

# --- mount admin router ---
app.include_router(admin_router)
app.include_router(router_rules)
app.include_router(router_flags)
app.include_router(router_notify)
app.include_router(router_slo)
app.include_router(router_inc)
app.include_router(router_audit)
app.include_router(router_stab)

# --- Rate Limiting Setup ---
@app.on_event("startup")
async def on_startup():
    await setup_rate_limit()

# --- Rate Limited Health Endpoint ---
@app.get("/health", dependencies=[Depends(RateLimiter(times=60, seconds=60))])
async def health(): return {"ok": True}
