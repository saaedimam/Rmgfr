create table if not exists mobile_push_tokens (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  user_id text,
  device_hash text,
  expo_push_token text not null,
  platform text,        -- ios|android
  created_at timestamptz not null default now(),
  unique (project_id, expo_push_token)
);
