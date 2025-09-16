import { NextRequest, NextResponse } from 'next/server';
import { API_BASE, PROJECT_API_KEY } from '@/lib/serverEnv';

export async function POST(req: NextRequest) {
  const body = await req.json();
  const r = await fetch(`${API_BASE}/v1/incident/${body.action}`, {
    method: 'POST',
    headers: { 'Content-Type':'application/json','X-API-Key': PROJECT_API_KEY },
    body: JSON.stringify(body.payload || {})
  });
  return NextResponse.json(await r.json().catch(()=>({})), { status: r.status });
}
