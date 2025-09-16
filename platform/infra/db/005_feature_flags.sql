-- Project-scoped feature flags with server enforcement
create table if not exists feature_flags (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  key text not null,
  enabled boolean not null default false,
  description text,
  constraints flags_unique unique (project_id, key),
  updated_at timestamptz not null default now()
);

alter table feature_flags enable row level security;
create policy flags_rw on feature_flags for all using (
  current_jwt_project_id() is not null and project_id = current_jwt_project_id()
);

-- helper to upsert flag
create or replace function upsert_flag(p_project uuid, p_key text, p_enabled boolean, p_desc text)
returns void language sql as $$
  insert into feature_flags(project_id, key, enabled, description)
  values (p_project, p_key, p_enabled, p_desc)
  on conflict (project_id, key) do update
  set enabled = excluded.enabled,
      description = excluded.description,
      updated_at = now();
$$;
