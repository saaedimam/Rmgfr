import { NextRequest, NextResponse } from 'next/server';

const API_BASE = process.env.API_BASE || 'http://localhost:8000';
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || '';

export async function GET(req: NextRequest) {
  if (!ADMIN_TOKEN) return NextResponse.json({ error: 'ADMIN_TOKEN not set' }, { status: 500 });
  const projectId = new URL(req.url).searchParams.get('project_id');
  if (!projectId) return NextResponse.json({ error: 'project_id required' }, { status: 400 });
  const r = await fetch(`${API_BASE}/admin/flags/${projectId}`, {
    headers: { 'X-Admin-Token': ADMIN_TOKEN },
    cache: 'no-store'
  });
  return NextResponse.json(await r.json(), { status: r.status });
}

export async function POST(req: NextRequest) {
  if (!ADMIN_TOKEN) return NextResponse.json({ error: 'ADMIN_TOKEN not set' }, { status: 500 });
  const body = await req.json();
  const r = await fetch(`${API_BASE}/admin/flags/upsert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Admin-Token': ADMIN_TOKEN },
    body: JSON.stringify(body)
  });
  return NextResponse.json(await r.json().catch(()=>({})), { status: r.status });
}
