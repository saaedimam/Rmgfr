-- 002_events.sql — Event Intake / Decisions / Cases, multi-tenant with RLS
-- Assumptions:
-- - We will pass a JWT to Postgres with a claim "project_id" for server-to-DB calls,
--   OR use the Supabase service role for server-side enforcement. API also enforces project via API key.

-- === Types ===
do $$ begin
  create type event_type as enum ('login','signup','checkout','custom');
exception when duplicate_object then null; end $$;

do $$ begin
  create type decision_outcome as enum ('allow','deny','review');
exception when duplicate_object then null; end $$;

do $$ begin
  create type case_status as enum ('open','reviewed','closed');
exception when duplicate_object then null; end $$;

-- === Tenancy ===
create table if not exists orgs (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz default now()
);

create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  api_key_hash text unique,             -- store SHA-256 of API key (never plaintext)
  created_at timestamptz default now()
);

create table if not exists api_keys (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  key_hash text unique not null,        -- SHA-256
  created_at timestamptz default now()
);

-- === Core Data ===
create table if not exists events (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  type event_type not null,
  actor_user_id text,
  ip inet,
  device_hash text,
  payload jsonb not null default '{}'::jsonb,
  event_ts timestamptz not null default now(),
  idempotency_key text unique
);

create index if not exists idx_events_project_ts on events(project_id, event_ts desc);
create index if not exists idx_events_idem on events(idempotency_key);

create table if not exists decisions (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  event_id uuid not null references events(id) on delete cascade,
  outcome decision_outcome not null,
  score int,
  reasons jsonb,
  decided_at timestamptz default now()
);

create index if not exists idx_decisions_project_ts on decisions(project_id, decided_at desc);

create table if not exists cases (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  status case_status not null default 'open',
  title text not null check (char_length(title) <= 200),
  notes text,
  created_at timestamptz default now()
);

create index if not exists idx_cases_project_ts on cases(project_id, created_at desc);

-- === RLS Setup ===
alter table orgs enable row level security;
alter table projects enable row level security;
alter table api_keys enable row level security;
alter table events enable row level security;
alter table decisions enable row level security;
alter table cases enable row level security;

-- Helper to read project_id from JWT claim "project_id" if present
create or replace function current_jwt_project_id() returns uuid language sql stable as $$
  select nullif(coalesce(
    (current_setting('request.jwt.claims', true)::json ->> 'project_id'), ''), '')::uuid
$$;

-- Policies (defense-in-depth). Expect server to set a JWT with project_id OR use service role for admin ops.
-- orgs/projects/api_keys: readable only via service role or when project/org matches the JWT project scope.
create policy orgs_ro on orgs for select using (true);           -- typically service role only (restrict via role grants)
create policy projects_ro on projects for select using (
  current_jwt_project_id() is not null and id = current_jwt_project_id()
);
create policy api_keys_none on api_keys for all using (false);   -- not accessible directly (managed by backoffice)

-- events: project-scoped
create policy events_rw on events for all using (
  current_jwt_project_id() is not null and project_id = current_jwt_project_id()
);

-- decisions: project-scoped
create policy decisions_rw on decisions for all using (
  current_jwt_project_id() is not null and project_id = current_jwt_project_id()
);

-- cases: project-scoped
create policy cases_rw on cases for all using (
  current_jwt_project_id() is not null and project_id = current_jwt_project_id()
);

comment on table events is 'Tenant-scoped events; RLS expects JWT claim project_id OR service role.';
comment on table decisions is 'Fraud decisions linked to events; RLS mirrors events.';
comment on table cases is 'Lightweight review queue; RLS tenant-scoped.';

-- === ROLLBACK (reference only) ===
-- To rollback, see 002_events_down.sql
