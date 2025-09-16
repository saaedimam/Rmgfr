# MVP Scope (explicit checklists)

## API & Data
- [ ] POST /v1/events (login, signup, checkout, custom)
- [ ] POST /v1/decisions (idempotent; allow/deny/review + reasons)
- [ ] GET  /v1/cases?status=open|closed
- [ ] Tables: profiles, items, orgs, projects, api_keys, events, decisions, cases
- [ ] RLS policies per org/project; unit tests for RLS

## Rules v1
- [ ] Rate limit per IP, per user, per device
- [ ] Velocity checks (N events / Δt)
- [ ] Device fingerprint capture hook (no PII; hash only)
- [ ] Rules config per project with safe defaults

## Dashboard v0
- [ ] Approvals/denials timeline, top rules firing
- [ ] Latency/error charts (Sentry + basic OTel)
- [ ] Case queue view (open/reviewed/closed)

## Ops
- [ ] k6 load test @ 2× peak
- [ ] Error budget policy + rollback commands
- [ ] Status page + SEV templates
