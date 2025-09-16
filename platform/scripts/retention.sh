#!/usr/bin/env bash
set -euo pipefail
psql "$SUPABASE_DB_URL" <<'SQL'
with moved as (
  insert into events_archive select * from events where created_at < now() - interval '400 days' returning id
) delete from events e using moved m where e.id=m.id;
SQL
