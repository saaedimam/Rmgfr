import os, hashlib, json, asyncpg
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, constr
import sentry_sdk
from typing import Optional, List
from api.admin import router as admin_router

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN_API"))

DB_DSN = os.getenv("SUPABASE_DB_URL")

app = FastAPI(title="Platform API", version="1.1.0")

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

        row = await conn.fetchrow(
            """
            insert into decisions (project_id, event_id, outcome, score, reasons)
            values ($1,$2,$3,$4,$5)
            returning id, outcome, score, reasons, decided_at
            """,
            project_id, body.event_id, body.outcome, body.score, json.dumps(body.reasons or [])
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
