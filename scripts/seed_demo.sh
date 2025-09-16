#!/usr/bin/env bash
set -euo pipefail
: "${ADMIN_TOKEN:?Need ADMIN_TOKEN in env}"
API_BASE="${API_BASE:-http://localhost:8000}"

echo "➡️ Bootstrapping demo org/project…"
BOOT=$(curl -s -X POST "$API_BASE/admin/bootstrap" \
  -H "X-Admin-Token: $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"org_name":"DemoCo","project_name":"Demo Risk"}')

echo "$BOOT"
API_KEY=$(echo "$BOOT" | sed -n 's/.*"api_key":"\([^"]*\)".*/\1/p')
[ -z "${API_KEY}" ] && { echo "Failed to mint API key"; exit 1; }

echo "➡️ Creating sample events…"
for i in 1 2 3; do
  curl -s -X POST "$API_BASE/v1/events" \
    -H "X-API-Key: $API_KEY" \
    -H "X-Idempotency-Key: idem-demo-$i" \
    -H "Content-Type: application/json" \
    -d '{"type":"login","actor_user_id":"user'$i'","payload":{"demo":'$i'}}' | jq .
done

echo "✅ Demo seed complete. API_KEY (store securely): $API_KEY"
