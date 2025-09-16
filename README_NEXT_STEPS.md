# Next Steps Runbook (fast lane)

## 0) Env
export PG_DSN='postgresql://user:pass@localhost:5432/fraud'
export TZ='Asia/Dhaka'

## 1) DB setup (migrations + seed)
# Option A: one-liner
./run_db_setup.sh

# Option B: Make targets
make PG_DSN=$PG_DSN db/setup

## 2) Replay worker (FastAPI skeleton)
# Ensure you have uvicorn + psycopg2 installed in your venv
make PG_DSN=$PG_DSN worker/run
# Then in another shell:
curl -X POST localhost:8082/enqueue_replay -H 'content-type: application/json' -d '{"event_ids":["evt_1","evt_2"],"schema_version":1,"reason":"rule_change:rule_42@v7"}'
curl -X POST "localhost:8082/run_once?limit=100"

## 3) LLM strict JSON validator
npm i zod
make validator/ok       # should print OK
make validator/bad      # should print 'Expected failure'

## 4) Server decision gate (drop-in)
// TypeScript:
// function decide(k, matrixMap, latestFpr) { ... } (see chat for snippet)
// Cache decision_matrix in-memory; refresh on admin writes.

## Dhaka-first defaults
- Set TZ at process boot (already exported above).
- Render dates/numbers with bn-BD locale in the UI; ensure screen-reader labels & keyboard focus are present on Alerts/Case pages.

## Where to edit seeds
- decision_matrix_seed.csv → actions & max_fpr by event/risk/segment
- segment_metrics_seed.csv → placeholders until live telemetry writes

