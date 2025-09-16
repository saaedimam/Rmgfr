
-- 002_decisions_table.sql
CREATE TABLE IF NOT EXISTS decisions (
  id BIGSERIAL PRIMARY KEY,
  event_id TEXT NOT NULL,
  decided_at TIMESTAMPTZ NOT NULL,
  decision decision NOT NULL,
  reasons TEXT[] NOT NULL DEFAULT '{}',
  model_version TEXT,
  rule_versions TEXT[]
);
