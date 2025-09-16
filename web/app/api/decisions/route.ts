import { NextRequest, NextResponse } from "next/server"

const API_BASE = process.env.API_BASE_URL || "http://localhost:8000"
const API_KEY = process.env.DEMO_API_KEY || ""

export async function GET(request: NextRequest) {
  try {
    if (!API_KEY) {
      return NextResponse.json({ error: "Demo API key not configured" }, { status: 500 })
    }

    const response = await fetch(`${API_BASE}/v1/decisions`, {
      headers: {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
      }
    })

    if (!response.ok) {
      throw new Error(`API responded with ${response.status}`)
    }

    const decisions = await response.json()
    return NextResponse.json(decisions)
  } catch (error) {
    console.error("Error fetching decisions:", error)
    return NextResponse.json({ error: "Failed to fetch decisions" }, { status: 500 })
  }
}
