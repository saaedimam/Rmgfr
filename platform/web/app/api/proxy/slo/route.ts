import { NextResponse } from 'next/server';
import { API_BASE, PROJECT_API_KEY } from '@/lib/serverEnv';

export async function GET() {
  const r = await fetch(`${API_BASE}/v1/slo/snapshot`, { headers: { 'X-API-Key': PROJECT_API_KEY }, cache: 'no-store' });
  return NextResponse.json(await r.json(), { status: r.status });
}
