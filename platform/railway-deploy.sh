#!/usr/bin/env bash
set -euo pipefail

step(){ printf "\n==> %s\n" "$*"; }
fail(){ printf "❌ %s\n" "$*" >&2; exit 1; }

: "${RAILWAY_TOKEN:?RAILWAY_TOKEN env var is required}"

# 1) Ensure CLI (prefer global, else npx)
if command -v railway >/dev/null 2>&1; then
  RW=railway
else
  RW="npx -y @railway/cli"
  $RW --version >/dev/null
fi

# 2) Login browserless
step "Logging into Railway"
# shellcheck disable=SC2086
$RW login --browserless --token "$RAILWAY_TOKEN" >/dev/null

# 3) Vars
SERVICE="${SERVICE:-}"
PROJECT="${PROJECT:-}"

# 4) Push env vars
if [[ -n "${DATABASE_URL:-}" ]]; then
  step "Setting DATABASE_URL"
  # shellcheck disable=SC2086
  $RW variables set DATABASE_URL="$DATABASE_URL" >/dev/null
fi

# 5) Deploy
step "Deploying"
if [[ -n "$SERVICE" ]]; then
  # shellcheck disable=SC2086
  $RW up --service "$SERVICE"
else
  # shellcheck disable=SC2086
  $RW up
fi

# 6) Optional DB bootstrap
if [[ -n "${DATABASE_URL:-}" && -f "platform/railway-db-setup.sql" ]]; then
  step "Bootstrapping PostgreSQL schema"
  if command -v psql >/dev/null 2>&1; then
    psql "$DATABASE_URL" -f platform/railway-db-setup.sql
  else
    echo "psql not found; skipping DB bootstrap."
  fi
fi

echo
echo "✅ Railway deploy complete"