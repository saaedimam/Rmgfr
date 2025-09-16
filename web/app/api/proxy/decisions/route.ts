import { NextRequest, NextResponse } from 'next/server';
import { API_BASE, PROJECT_API_KEY } from '../../../lib/serverEnv';

export async function GET(req: NextRequest) {
  if (!PROJECT_API_KEY) return NextResponse.json({ error: 'Server API key not set' }, { status: 500 });
  const { searchParams } = new URL(req.url);
  const page = searchParams.get('page') || '1';
  const page_size = searchParams.get('page_size') || '20';
  const r = await fetch(`${API_BASE}/v1/decisions?page=${page}&page_size=${page_size}`, {
    headers: { 'X-API-Key': PROJECT_API_KEY }
  });
  const data = await r.json();
  return NextResponse.json(data, { status: r.status });
}
