
# replay_worker/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import psycopg2, os
from datetime import datetime

app = FastAPI(title="Replay Worker")

PG_DSN = os.getenv("PG_DSN", "postgresql://user:pass@localhost:5432/fraud")

class EnqueueRequest(BaseModel):
    event_ids: List[str]
    schema_version: int
    reason: str

def get_conn():
    return psycopg2.connect(PG_DSN)

@app.post("/enqueue_replay")
def enqueue_replay(req: EnqueueRequest):
    with get_conn() as conn, conn.cursor() as cur:
        for eid in req.event_ids:
            cur.execute(
                "INSERT INTO replay_queue (event_id, schema_version, reason) VALUES (%s,%s,%s)",
                (eid, req.schema_version, req.reason)
            )
    return {"status": "ok", "count": len(req.event_ids)}

def score_event(payload: dict) -> dict:
    # TODO: call your rules + model service; never LLM
    return {"risk_score": 0.1, "decision": "allow", "reasons": ["stub"]}

def record_decision(conn, event_id: str, decision: dict):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO decisions(event_id, decided_at, decision, reasons, model_version, rule_versions) VALUES (%s, now(), %s, %s, %s, %s)",
            (event_id, decision["decision"], decision.get("reasons", []), "model_v0", ["ruleset_v0"])
        )

def fetch_next_batch(conn, limit=100):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM replay_queue WHERE status='pending' ORDER BY id LIMIT %s", (limit,))
        ids = [r[0] for r in cur.fetchall()]
        if not ids: 
            return []
        cur.execute("UPDATE replay_queue SET status='processing' WHERE id = ANY(%s) RETURNING id, event_id, schema_version", (ids,))
        rows = cur.fetchall()
    return rows

@app.post("/run_once")
def run_once(limit: int = 100):
    processed = 0
    with get_conn() as conn:
        rows = fetch_next_batch(conn, limit=limit)
        for rid, eid, sv in rows:
            with conn.cursor() as cur:
                cur.execute("SELECT payload FROM events WHERE event_id=%s AND schema_version=%s", (eid, sv))
                row = cur.fetchone()
            if not row:
                with conn.cursor() as cur:
                    cur.execute("UPDATE replay_queue SET status='missing' WHERE id=%s", (rid,))
                continue
            payload = row[0]
            decision = score_event(payload)
            record_decision(conn, eid, decision)
            with conn.cursor() as cur:
                cur.execute("UPDATE replay_queue SET status='done' WHERE id=%s", (rid,))
            processed += 1
    return {"processed": processed}
