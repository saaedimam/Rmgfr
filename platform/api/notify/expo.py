import os, json, httpx
EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

async def send_expo_push(token: str, title: str, body: str, data: dict | None = None):
    payload = {"to": token, "title": title, "body": body, "data": data or {}}
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(EXPO_PUSH_URL, json=payload)
        return r.status_code, r.json()
