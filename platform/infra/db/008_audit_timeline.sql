create table if not exists audit_events (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  at timestamptz not null default now(),
  source text not null check (source in ('incident','sentry','deploy','flags','policy','stabilize')),
  kind text not null,
  subject text,                 -- e.g., release id, flag key, incident id
  actor text,                   -- system/user
  payload jsonb not null default '{}'
);
create index if not exists idx_audit_project_time on audit_events(project_id, at desc);
