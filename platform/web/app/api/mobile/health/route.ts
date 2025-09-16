import { NextResponse } from 'next/server';
import { API_BASE, PROJECT_API_KEY } from '@/lib/serverEnv';

export async function GET() {
  const r = await fetch(`${API_BASE}/health`, { headers: { 'X-API-Key': PROJECT_API_KEY } });
  const data = await r.json();
  return NextResponse.json({ ok: true, api: data });
}
