# Admin Bootstrap (Local & Prod)

## 1) Set admin token (server-side only)
Add `ADMIN_TOKEN` to your environment (Vercel/Fly.io/Render or local).
Never expose this to browsers/mobile.

## 2) Create org + project + API key
```bash
curl -s -X POST http://localhost:8000/admin/bootstrap \
  -H "X-Admin-Token: $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"org_name":"Acme Inc","project_name":"Checkout Risk"}'
```

**Response**

```json
{
  "org_id": "...",
  "project_id": "...",
  "api_key": "prj_... (copy once)"
}
```

## 3) Verify event intake (idempotent)

```bash
API_KEY="prj_....."
curl -s -X POST http://localhost:8000/v1/events \
  -H "X-API-Key: $API_KEY" \
  -H "X-Idempotency-Key: idem-123" \
  -H "Content-Type: application/json" \
  -d '{"type":"login","actor_user_id":"u1","payload":{"email_hash":"..."} }'
```

## 4) Create a decision

```bash
EVENT_ID="(from /v1/events response)"
curl -s -X POST http://localhost:8000/v1/decisions \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"event_id":"'$EVENT_ID'","outcome":"review","score":45,"reasons":["velocity"] }'
```
