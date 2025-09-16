import { NextRequest, NextResponse } from 'next/server';
import { API_BASE, PROJECT_API_KEY } from '@/lib/serverEnv';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    // Shape guard — only allow a few safe fields from mobile
    const payload = {
      type: String(body?.type || 'mobile_event'),
      actor_user_id: body?.actor_user_id ?? null,
      device_hash: body?.device_hash ?? null,
      payload: body?.payload ?? {},
    };
    const idem = req.headers.get('x-idempotency-key') || `mob-${Date.now()}-${Math.random()}`;
    const r = await fetch(`${API_BASE}/v1/events`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': PROJECT_API_KEY,
        'X-Idempotency-Key': idem,
      },
      body: JSON.stringify(payload),
      cache: 'no-store',
    });
    const data = await r.json();
    return NextResponse.json(data, { status: r.status });
  } catch (e:any) {
    return NextResponse.json({ error: e?.message || 'bad request' }, { status: 400 });
  }
}
