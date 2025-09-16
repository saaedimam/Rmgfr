#!/usr/bin/env bash
set -euo pipefail
DUMP=${1:?dump file}
pg_restore --clean --if-exists --no-owner --dbname "$SUPABASE_DB_URL" "$DUMP"
