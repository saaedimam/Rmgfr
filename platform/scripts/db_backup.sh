#!/usr/bin/env bash
set -euo pipefail
TS=$(date -u +%Y%m%d-%H%M%S)
pg_dump --no-owner --format=custom "$SUPABASE_DB_URL" > backups/db-$TS.dump
echo "Backup: backups/db-$TS.dump"
