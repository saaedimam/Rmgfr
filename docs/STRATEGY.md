# Anti-Fraud Platform — Strategic Alignment (v1)

## Value Proposition (1 sentence)
Real-time, developer-friendly fraud detection that cuts chargebacks and abuse by >50% while keeping user friction near zero and latency budgets intact (API p99.9 < 400 ms).

## Personas & Jobs-to-be-Done
1) **Merchant Ops Lead** — needs instant risk decisions, explainable reasons, and simple case workflows to refund/ban/appeal.
2) **Risk Analyst** — needs velocity/device/behavioral signals, tunable rules, alerting, and audit-ready evidence.
3) **Developer (Integrator)** — needs a 30-minute drop-in SDK + stable REST API + dashboard to observe traffic.

## MVP (ships in 12–16 weeks)
- **Event Intake API** (REST): login/signup/checkout events with idempotency.
- **Risk Rules v1**: rate limiting (per IP/user/device), velocity checks, device fingerprint capture hook.
- **Decision Service**: allow/deny/review with scores and reasons.
- **Case Basics**: queue with status + notes (no SLA workflows yet).
- **Dashboard v0**: live approvals/denials, top rules firing, latency/error charts.
- **Auth & RBAC**: org + project; roles: owner, analyst, viewer.
- **Observability**: Sentry, p95/p99 latency, error budgets.
- **RLS Security**: tenant isolation on Postgres; least-privilege API keys.

## V1+ (post-MVP, not now)
- **Graph features** (device → user → payment instrument links).
- **ML Scoring** (supervised model with feature store + drift checks).
- **Chargeback workflows** (disputes, evidence pack, SLA).
- **Partner Webhooks** (downstream updates).
- **Self-serve sandbox** (traffic replays, synthetic data).
- **Advanced RBAC** (scopes, audit exports).

## Non-Goals (now)
- No blockchain analysis, no KYC vendor integrations, no custom ML labeling UI.

## Success Metrics
- Business: chargeback rate ↓ 50% in pilot; auto-approve ≥ 90%; false-positive rate ≤ 1.0%.
- Product: D7 retention of integrators ≥ 60%; time-to-first-decision ≤ 30 min.
- Technical SLOs: API p99.9 < 400 ms; Web LCP < 2.5 s; uptime ≥ 99.9%; error budget ≤ 0.1%.
- Ops: median case resolution < 24 h; on-call pages ≤ 2/month.

## Hard Constraints & Compliance
- Regions: US & EU; data residency honored (EU data in EU).
- GDPR: consent/DSR endpoints; PCI-aware (no PAN storage; tokens only).
- Security: RLS enforced; secrets external; HTTPS only; rate limits at edge.

## Risk Register (top 6)
1) High false positives → tunable thresholds + review queue + A/B rules.
2) Latency regressions under load → k6 tests at 2× peak + circuit breakers.
3) Multi-tenant data leaks → RLS tests + per-org schema checks.
4) Vendor outages (Auth/DB) → graceful degradation + retry/backoff.
5) Secrets mishandling → centralized env, rotation playbook, no logs of secrets.
6) Scope creep → locked MVP; any change needs a written trade-off.

## Timeline (high level)
- Weeks 1–4: Event Intake + Rules v1 + Dashboard v0
- Weeks 5–8: Device FP hook + Decision Service + Case basics
- Weeks 9–12: Hardening, load tests, docs, pilot integration
- Weeks 13–16: Store submission (mobile) + GA launch improvements

## Architecture Guardrails (binds design)
- Next.js 14 (web), FastAPI (API), Supabase Postgres (RLS), Clerk (auth), Expo (mobile), GitHub Actions (CI), Sentry (obs).
- Ask ≤ 3 questions if critical info missing; otherwise proceed with safe defaults + update CHANGELOG.
