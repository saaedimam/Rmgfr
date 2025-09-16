.PHONY: db/migrate db/seed db/setup worker/run validator/ok validator/bad db-migrate db-rollback-002 load-smoke

PG_DSN ?= postgresql://user:pass@localhost:5432/fraud

db/migrate:
	psql "$(PG_DSN)" -f 001_decision_policy_migration.sql
	psql "$(PG_DSN)" -f 002_decisions_table.sql

db/seed:
	psql "$(PG_DSN)" -c "\\copy decision_matrix FROM 'decision_matrix_seed.csv' CSV HEADER"
	psql "$(PG_DSN)" -c "\\copy segment_metrics  FROM 'segment_metrics_seed.csv'  CSV HEADER"

db/setup: db/migrate db/seed

worker/run:
	PG_DSN=$(PG_DSN) uvicorn main:app --reload --port 8082

validator/ok:
	node llm_validator.js sample_case_summary.json && echo "OK"

validator/bad:
	node llm_validator.js bad_case_summary.json || echo "Expected failure"

# New Event Intake API targets
db-migrate:
ifneq ($(SUPABASE_DB_URL),)
	for f in infra/db/*.sql; do echo "Applying $$f"; psql "$(SUPABASE_DB_URL)" -v "ON_ERROR_STOP=1" -f "$$f"; done
else
	@echo "SUPABASE_DB_URL not set. Use Supabase SQL editor to run infra/db/*.sql"
endif

db-rollback-002:
ifneq ($(SUPABASE_DB_URL),)
	psql "$(SUPABASE_DB_URL)" -v "ON_ERROR_STOP=1" -f infra/db/002_events_down.sql
else
	@echo "SUPABASE_DB_URL not set. Run 002_events_down.sql in Supabase SQL editor"
endif

load-smoke:
	k6 run infra/load/k6_smoke.js || echo "Install k6: https://k6.io/docs/get-started/installation/"
