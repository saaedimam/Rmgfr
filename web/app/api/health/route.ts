// file: web/app/api/health/route.ts
import { NextResponse } from "next/server"
export async function GET() {
  return NextResponse.json({ status: "ok", ts: Date.now() })
}
