// Server action proxy to update rule configs via admin endpoint
import { NextRequest, NextResponse } from 'next/server';

const API_BASE = process.env.API_BASE || 'http://localhost:8000';
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || '';

export async function POST(req: NextRequest) {
  if (!ADMIN_TOKEN) return NextResponse.json({ error: 'ADMIN_TOKEN not set' }, { status: 500 });
  
  const body = await req.json();
  const r = await fetch(`${API_BASE}/admin/rules/upsert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Admin-Token': ADMIN_TOKEN },
    body: JSON.stringify(body),
    cache: 'no-store'
  });
  
  const data = await r.json().catch(()=>({}));
  return NextResponse.json(data, { status: r.status });
}
