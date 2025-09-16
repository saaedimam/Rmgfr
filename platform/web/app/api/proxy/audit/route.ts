import { NextRequest, NextResponse } from 'next/server';
import { API_BASE, PROJECT_API_KEY } from '@/lib/serverEnv';

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get('q') ?? '';
  const r = await fetch(`${API_BASE}/v1/audit/search?q=${encodeURIComponent(q)}`, {
    headers: { 'X-API-Key': PROJECT_API_KEY }, cache: 'no-store'
  });
  return NextResponse.json(await r.json(), { status: r.status });
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const r = await fetch(`${API_BASE}/v1/audit/ingest`, {
    method:'POST', headers:{ 'Content-Type':'application/json','X-API-Key': PROJECT_API_KEY },
    body: JSON.stringify(body)
  });
  return NextResponse.json(await r.json(), { status: r.status });
}
