import { NextRequest, NextResponse } from 'next/server';
import { API_BASE, PROJECT_API_KEY } from '@/lib/serverEnv';

export async function POST(req: NextRequest) {
  const body = await req.json();
  const r = await fetch(`${API_BASE}/v1/mobile/register-push-token`, {
    method: 'POST',
    headers: { 'Content-Type':'application/json', 'X-API-Key': PROJECT_API_KEY },
    body: JSON.stringify(body)
  });
  const data = await r.json().catch(()=>({}));
  return NextResponse.json(data, { status: r.status });
}
