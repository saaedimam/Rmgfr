#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${PG_DSN:-}" ]]; then
  echo "PG_DSN is not set. Example: export PG_DSN='postgresql://user:pass@localhost:5432/fraud'"
  exit 1
fi

echo "Running migrations..."
psql "$PG_DSN" -f 001_decision_policy_migration.sql
if [[ -f 002_decisions_table.sql ]]; then
  psql "$PG_DSN" -f 002_decisions_table.sql
fi

echo "Seeding CSVs..."
# These paths assume you're running from the same folder as this script.
\copy decision_matrix FROM 'decision_matrix_seed.csv' CSV HEADER
\copy segment_metrics  FROM 'segment_metrics_seed.csv'  CSV HEADER

echo "Done."
