-- Rules v1 config + helper indexes
create table if not exists rule_configs (
  project_id uuid primary key references projects(id) on delete cascade,
  -- per 5-minute window defaults (tune per project)
  max_events_per_ip int not null default 60,
  max_events_per_user int not null default 60,
  max_events_per_device int not null default 120,
  -- global velocity (all events)
  max_events_global int not null default 5000,
  window_seconds int not null default 300,              -- 5 min
  updated_at timestamptz not null default now()
);

-- helpful composite indexes
create index if not exists idx_events_ts_ip on events(event_ts desc, ip);
create index if not exists idx_events_ts_user on events(event_ts desc, actor_user_id);
create index if not exists idx_events_ts_device on events(event_ts desc, device_hash);
create index if not exists idx_events_project on events(project_id, event_ts desc);

-- upsert convenience function for admin/API
create or replace function upsert_rule_config(
  p_project_id uuid,
  p_ip int, p_user int, p_device int, p_global int, p_window int)
returns void language sql as $$
  insert into rule_configs(project_id, max_events_per_ip, max_events_per_user, max_events_per_device, max_events_global, window_seconds)
  values (p_project_id, p_ip, p_user, p_device, p_global, p_window)
  on conflict (project_id) do update
  set max_events_per_ip = excluded.max_events_per_ip,
      max_events_per_user = excluded.max_events_per_user,
      max_events_per_device = excluded.max_events_per_device,
      max_events_global = excluded.max_events_global,
      window_seconds = excluded.window_seconds,
      updated_at = now();
$$;
