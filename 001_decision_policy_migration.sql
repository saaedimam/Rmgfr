
-- 001_decision_policy_migration.sql
BEGIN;

-- Enum for actions
DO $$ BEGIN
    CREATE TYPE decision AS ENUM ('allow','step_up','deny','review');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS decision_matrix (
  event_type TEXT NOT NULL,
  risk_band TEXT NOT NULL,
  customer_segment TEXT NOT NULL,
  action decision NOT NULL,
  max_fpr FLOAT NOT NULL,
  notes TEXT DEFAULT '',
  updated_by TEXT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (event_type, risk_band, customer_segment)
);

CREATE TABLE IF NOT EXISTS segment_metrics (
  date DATE NOT NULL,
  customer_segment TEXT NOT NULL,
  fpr FLOAT NOT NULL,
  tpr FLOAT NOT NULL,
  throughput INT NOT NULL,
  UNIQUE(date, customer_segment)
);

CREATE TABLE IF NOT EXISTS events (
  ingest_id UUID PRIMARY KEY,
  event_id TEXT NOT NULL,
  schema_version INT NOT NULL,
  event_type TEXT NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  payload JSONB NOT NULL,
  idempotency_key TEXT NOT NULL,
  UNIQUE(event_id, schema_version)
);

CREATE TABLE IF NOT EXISTS replay_queue (
  id BIGSERIAL PRIMARY KEY,
  event_id TEXT NOT NULL,
  schema_version INT NOT NULL,
  reason TEXT NOT NULL,
  enqueued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS feature_specs (
  name TEXT PRIMARY KEY,
  owner TEXT NOT NULL,
  calc TEXT NOT NULL,
  null_policy TEXT NOT NULL,
  max_psi FLOAT NOT NULL DEFAULT 0.2,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS feature_health (
  feature TEXT REFERENCES feature_specs(name),
  window_start TIMESTAMPTZ,
  psi FLOAT NOT NULL,
  null_rate FLOAT NOT NULL,
  p50 FLOAT, p95 FLOAT,
  status TEXT GENERATED ALWAYS AS (
    CASE WHEN psi > (SELECT max_psi FROM feature_specs fs WHERE fs.name = feature) THEN 'drop' ELSE 'ok' END
  ) STORED,
  PRIMARY KEY (feature, window_start)
);

COMMIT;
