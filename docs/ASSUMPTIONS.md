# Assumptions (v1) — overwrite as facts become available

- **Regions**: US + EU; EU data processed and stored in EU region of Supabase/Vercel.
- **Compliance**: GDPR definite; PCI handled by not storing PAN (tokenized via PSP).
- **Team**: 4 engineers (2 full-stack, 1 backend, 1 mobile).
- **Traffic**: MVP target 100k events/day; peak 5×; latency budgets as per STRATEGY.md.
- **Integrations**: Payments PSP already tokenizes card data; we never ingest raw PAN.
- **Auth**: Clerk for org/project; API keys per project; RLS for tenant isolation.
- **Budget**: $50k–$150k Y1 infra + services.
- **Security posture**: Least-privilege DB roles, no secrets in code, rotation every 90 days.

> When any assumption changes, update this file and reference it in PR description.
