import { NextRequest, NextResponse } from 'next/server';
import { API_BASE, PROJECT_API_KEY } from '@/lib/serverEnv';
export async function POST(req: NextRequest) {
  const { action } = await req.json();
  const url = `${API_BASE}/v1/stabilize/${action}`; // enter|exit
  const r = await fetch(url, { method:'POST', headers:{ 'X-API-Key': PROJECT_API_KEY }});
  return NextResponse.json(await r.json(), { status: r.status });
}
