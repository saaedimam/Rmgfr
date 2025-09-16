Perfect—here’s the **next step** and the roadmap status.

* **We’re following a 12-step track.**
* You’ve completed: **Steps 1–10**.
* **Remaining:** **Step 11 (now)** and **Step 12 (final launch & hardening)**.
* So: **2 steps total remain** (including this one). After Step 11, only **1** step left.

---

# STEP 11: Searchable Audit Timeline + Runbooks + One-Click “Stabilize Mode”

You’ll get: a **single, searchable audit timeline** that stitches together **Incidents + Sentry events + Deploys + Feature Flags changes**; **paste-ready runbooks** surfaced in the UI for common faults; and a **stabilize mode** switch that clamps RPS, de-prioritizes non-critical work, tightens circuit breakers, and turns off expensive/fragile features—**without downtime**.

---

## 1) Commands (repo root)

```bash
mkdir -p infra/db api/audit web/app/dashboard/audit web/app/api/proxy/audit api/runbooks

# DB migration
cat > infra/db/008_audit_timeline.sql <<'SQL'
create table if not exists audit_events (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  at timestamptz not null default now(),
  source text not null check (source in ('incident','sentry','deploy','flags','policy','stabilize')),
  kind text not null,
  subject text,                 -- e.g., release id, flag key, incident id
  actor text,                   -- system/user
  payload jsonb not null default '{}'
);
create index if not exists idx_audit_project_time on audit_events(project_id, at desc);
SQL

psql "$SUPABASE_DB_URL" -v "ON_ERROR_STOP=1" -f infra/db/008_audit_timeline.sql
```

---

## 2) API: Audit collector + Stabilize Mode switch

**2.1 Audit ingestion & query router**

```py
# api/audit/router.py
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from .utils import get_pool, resolve_project_id

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
```

**2.2 Stabilize Mode policy**

```py
# api/stabilize.py
import os, time
from fastapi import APIRouter, Request, HTTPException
from .utils import get_pool, resolve_project_id
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
```

**2.3 Wire Stabilize Mode into middleware & circuit breaker**

```py
# api/main.py (additions)
from api.stabilize import router_stab, is_stabilized, clamp_rps, cb_errs, deprioritized
from collections import deque
from time import perf_counter
from fastapi import Response

app.include_router(router_stab)

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
```

*(If you already have Istio/Envoy, map `is_stabilized` to stricter DestinationRule thresholds instead.)*

---

## 3) Web: Audit Timeline UI + Stabilize toggle

**3.1 Server proxies**

```ts
// web/app/api/proxy/audit/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { API_BASE, PROJECT_API_KEY } from '@/lib/serverEnv';

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get('q') ?? '';
  const r = await fetch(`${API_BASE}/v1/audit/search?q=${encodeURIComponent(q)}`, {
    headers: { 'X-API-Key': PROJECT_API_KEY }, cache: 'no-store'
  });
  return NextResponse.json(await r.json(), { status: r.status });
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const r = await fetch(`${API_BASE}/v1/audit/ingest`, {
    method:'POST', headers:{ 'Content-Type':'application/json','X-API-Key': PROJECT_API_KEY },
    body: JSON.stringify(body)
  });
  return NextResponse.json(await r.json(), { status: r.status });
}
```

```ts
// web/app/api/proxy/stabilize/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { API_BASE, PROJECT_API_KEY } from '@/lib/serverEnv';
export async function POST(req: NextRequest) {
  const { action } = await req.json();
  const url = `${API_BASE}/v1/stabilize/${action}`; // enter|exit
  const r = await fetch(url, { method:'POST', headers:{ 'X-API-Key': PROJECT_API_KEY }});
  return NextResponse.json(await r.json(), { status: r.status });
}
```

**3.2 UI pages**

```tsx
// web/app/dashboard/audit/page.tsx
'use client';
import { useEffect, useState } from 'react';

type Item = { at:string; source:string; kind:string; subject?:string; actor?:string; payload:any };

export default function AuditPage(){
  const [q,setQ] = useState('');
  const [items,setItems] = useState<Item[]>([]);
  const load = async () => {
    const r = await fetch(`/api/proxy/audit?q=${encodeURIComponent(q)}`, { cache:'no-store' });
    const j = await r.json();
    setItems(j.items || []);
  };
  useEffect(()=>{ load(); const id=setInterval(load,10000); return ()=>clearInterval(id); },[]);
  return (
    <main style={{padding:24}}>
      <h1>Audit Timeline</h1>
      <div style={{display:'flex',gap:8,marginBottom:12}}>
        <input placeholder="search: release, flag, incident…" value={q} onChange={e=>setQ(e.target.value)} />
        <button onClick={load}>Search</button>
      </div>
      <table style={{width:'100%',borderCollapse:'collapse'}}>
        <thead><tr><th>Time</th><th>Source</th><th>Kind</th><th>Subject</th><th>Actor</th><th>Payload</th></tr></thead>
        <tbody>
          {items.map((it,idx)=>(
            <tr key={idx}>
              <td>{new Date(it.at).toLocaleString()}</td>
              <td>{it.source}</td><td>{it.kind}</td>
              <td>{it.subject||''}</td><td>{it.actor||''}</td>
              <td><code style={{fontSize:12}}>{JSON.stringify(it.payload)}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
```

```tsx
// web/app/dashboard/audit/stabilize/page.tsx
'use client';
import { useState } from 'react';

export default function StabilizePage(){
  const [state,setState] = useState<string>('idle');
  const call = async (action:'enter'|'exit')=>{
    setState('…');
    const r = await fetch('/api/proxy/stabilize', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ action }) });
    const j = await r.json();
    setState(JSON.stringify(j));
  };
  return (
    <main style={{padding:24, display:'grid', gap:12}}>
      <h1>Stabilize Mode</h1>
      <div style={{display:'flex', gap:8}}>
        <button onClick={()=>call('enter')}>Enter Stabilize</button>
        <button onClick={()=>call('exit')}>Exit Stabilize</button>
      </div>
      <pre style={{background:'#f8fafc',padding:12,borderRadius:8}}>{state}</pre>
      <p style={{color:'#64748b'}}>When enabled: RPS clamped, circuit breakers tighten, non-critical queues de-prioritized. All changes are audited.</p>
    </main>
  );
}
```

---

## 4) Wire other systems to audit

Add calls to `/v1/audit/ingest` wherever meaningful:

* **Incidents** (when opened/updated) → already emitted via Step 10? Add here too.
* **Deploys** (CI step) → POST `{source:'deploy', kind:'release', subject:'web@<sha>'}`.
* **Sentry** (server error sample) → Sentry webhook → small receiver that forwards to audit.
* **Flags** (admin changes) → after any flag change in API, emit `{source:'flags', kind:'flag_set', subject:'<flag>'}`.

*(Optional: add a tiny Next.js API route to receive Sentry webhooks and forward.)*

---

## 5) Runbooks (paste-ready)

```md
<!-- api/runbooks/README.md -->
# Runbooks

## RB-001: Error Rate Spike
- Check SLO dashboard. If error_rate > 1% and p99.9 > 400ms:
  1) Enter Stabilize Mode (`/dashboard/audit/stabilize`)
  2) Verify auto-rollback result in audit timeline
  3) If persists: disable `beta_ui` & `experimental_rules` flags
  4) Page on-call; attach Sentry issue link and latest deploy id

## RB-002: Database Saturation
- Actions:
  1) Enable Stabilize
  2) Raise read replicas / reduce pool by 20%
  3) Turn off heavy jobs: `reports`, `analytics`
  4) Add index if hotspot (temporary); plan long-term fix

## RB-003: Push Failure Storm
- Actions:
  1) Deprioritize `emails,reports` queues
  2) Reduce push batch size to 50
  3) Switch to fallback provider
```

(Expose a docs page linking to these in your dashboard’s sidebar if desired.)

---

## 6) Git

```bash
git add infra/db/008_audit_timeline.sql api/audit/router.py api/stabilize.py web/app/api/proxy/audit/route.ts \
        web/app/api/proxy/stabilize/route.ts web/app/dashboard/audit/page.tsx web/app/dashboard/audit/stabilize/page.tsx \
        api/runbooks/README.md api/main.py
git commit -m "feat(audit+stabilize): unified audit timeline, stabilize mode (RPS clamp, CB tighten, queue deprioritize), runbooks"
```

---

## 7) Verify

1. **Enter stabilize** at `/dashboard/audit/stabilize` → see **stabilize: enter** in **/dashboard/audit**.
2. Run a quick bombardment (e.g., your k6 script) and verify 503 throttling occurs while stabilized.
3. Trigger a small deploy (web or api) and POST a deploy audit record from CI—confirm appears in the timeline.
4. Flip a feature flag in your admin — confirm **flags/flag\_set** entries appear.
5. Exit stabilize — confirm **stabilize: exit** audit event.

---

## Pro Tips

* Replace audit table with **OpenTelemetry** + **ClickHouse** for long-term, cheap retention & fast queries.
* Add **subscriptions** (e.g., Slack webhook) for new SEV1/SEV2 audit items.
* Gate **stabilize** with RBAC and dual-auth if needed (break-glass).
* Store the **reason** when entering stabilize (form in UI).
* In production, prefer **Envoy/Istio** for rate limiting & outlier detection; your middleware simply toggles policies.

---

## What’s next?

* **Step 12 (FINAL):** Production hardening + launch handoff

  * WAF/rate-limit presets, backups & PITR drills, DR flipbook, cost guardrails, data retention & PII scrubbing, final checklists (ops, security, mobile stores), and “Day-30 optimization plan.”

Want me to proceed to **STEP 12** now?
