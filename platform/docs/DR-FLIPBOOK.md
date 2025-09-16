# Disaster Recovery Flipbook

**Trigger**: Region outage or DB corruption
**RPO**: ≤ 5 min | **RTO**: ≤ 15 min

## 1. Declare incident (SEV1) and Enter **Stabilize Mode** (Step 11).

## 2. Promote standby DB:
- If managed: click "Promote Replica" in provider console.
- Else: run `pg_ctl promote` on replica; update primary connection string.

## 3. Update API secrets:
- `SUPABASE_DB_URL=<replica-uri>`
- Restart API (`fly deploy` or `render redeploy`).

## 4. Web switch:
- Update `API_BASE` env in Vercel to standby API; redeploy instant.

## 5. Validate:
- Read/write tests; run smoke suite; SLOs green.

## 6. Communicate:
- Status page; regulator note template `templates/regulators/dr-exec.md`.

## 7. Post:
- Backfill WAL; re-establish replication; mark RESOLVED; schedule RCA.
