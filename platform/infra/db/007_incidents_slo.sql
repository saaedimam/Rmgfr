create table if not exists incidents (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  severity text not null check (severity in ('SEV1','SEV2','SEV3','SEV4')),
  title text not null,
  status text not null check (status in ('OPEN','MITIGATED','RESOLVED','CANCELLED')) default 'OPEN',
  started_at timestamptz not null default now(),
  mitigated_at timestamptz,
  resolved_at timestamptz,
  commander text,
  summary text
);

create table if not exists incident_events (
  id uuid primary key default gen_random_uuid(),
  incident_id uuid not null references incidents(id) on delete cascade,
  at timestamptz not null default now(),
  kind text not null,
  payload jsonb not null default '{}'
);

create table if not exists slo_snapshots (
  id bigserial primary key,
  project_id uuid not null references projects(id) on delete cascade,
  window text not null default '1h',
  endpoint text not null,
  latency_p99_9 numeric,
  error_rate numeric,         -- 0..1
  uptime numeric,             -- 0..1
  budget_remaining numeric,   -- 0..1 (error budget)
  taken_at timestamptz not null default now()
);

-- quick helpers
create index if not exists idx_incidents_project_status on incidents(project_id, status);
create index if not exists idx_slo_snapshots_project_time on slo_snapshots(project_id, taken_at desc);
