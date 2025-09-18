-- PostgreSQL bootstrap for Anti-Fraud Platform
-- Safe to run multiple times (uses IF NOT EXISTS)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS tenants (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  email citext UNIQUE,
  role text NOT NULL DEFAULT 'analyst',
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cases (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  title text NOT NULL,
  status text NOT NULL DEFAULT 'open',
  risk_score numeric NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS events (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  case_id uuid REFERENCES cases(id) ON DELETE SET NULL,
  kind text NOT NULL,
  payload jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_cases_tenant_status ON cases(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_events_tenant_kind ON events(tenant_id, kind);
CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id);

-- Row Level Security
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Simple tenant isolation policy by tenant_id
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE polname = 'tenant_isolation_cases') THEN
    CREATE POLICY tenant_isolation_cases ON cases
      USING (tenant_id::text = current_setting('app.tenant_id', true));
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE polname = 'tenant_isolation_events') THEN
    CREATE POLICY tenant_isolation_events ON events
      USING (tenant_id::text = current_setting('app.tenant_id', true));
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE polname = 'tenant_isolation_users') THEN
    CREATE POLICY tenant_isolation_users ON users
      USING (tenant_id::text = current_setting('app.tenant_id', true));
  END IF;
END$$;

-- Demo data (idempotent inserts)
INSERT INTO tenants (id, name)
SELECT '00000000-0000-0000-0000-000000000001', 'demo'
WHERE NOT EXISTS (SELECT 1 FROM tenants WHERE id = '00000000-0000-0000-0000-000000000001');

INSERT INTO users (tenant_id, email, role)
SELECT '00000000-0000-0000-0000-000000000001', 'analyst@demo.local', 'analyst'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email='analyst@demo.local');

INSERT INTO cases (tenant_id, title, status, risk_score)
SELECT '00000000-0000-0000-0000-000000000001', 'Test Case', 'open', 42
WHERE NOT EXISTS (SELECT 1 FROM cases WHERE title='Test Case');