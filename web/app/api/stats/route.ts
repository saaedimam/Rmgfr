import { NextRequest, NextResponse } from "next/server"

const API_BASE = process.env.API_BASE_URL || "http://localhost:8000"
const API_KEY = process.env.DEMO_API_KEY || ""

export async function GET(request: NextRequest) {
  try {
    if (!API_KEY) {
      return NextResponse.json({ error: "Demo API key not configured" }, { status: 500 })
    }

    // Fetch events and decisions in parallel
    const [eventsResponse, decisionsResponse] = await Promise.all([
      fetch(`${API_BASE}/v1/events`, {
        headers: {
          "X-API-Key": API_KEY,
          "Content-Type": "application/json"
        }
      }),
      fetch(`${API_BASE}/v1/decisions`, {
        headers: {
          "X-API-Key": API_KEY,
          "Content-Type": "application/json"
        }
      })
    ])

    if (!eventsResponse.ok || !decisionsResponse.ok) {
      throw new Error("Failed to fetch data from API")
    }

    const events = await eventsResponse.json()
    const decisions = await decisionsResponse.json()

    // Calculate stats
    const totalEvents = events.length
    const totalDecisions = decisions.length
    
    const allowCount = decisions.filter((d: any) => d.outcome === "allow").length
    const denyCount = decisions.filter((d: any) => d.outcome === "deny").length
    const reviewCount = decisions.filter((d: any) => d.outcome === "review").length
    
    const allowRate = totalDecisions > 0 ? (allowCount / totalDecisions) * 100 : 0
    const denyRate = totalDecisions > 0 ? (denyCount / totalDecisions) * 100 : 0
    const reviewRate = totalDecisions > 0 ? (reviewCount / totalDecisions) * 100 : 0

    return NextResponse.json({
      totalEvents,
      totalDecisions,
      allowRate,
      denyRate,
      reviewRate
    })
  } catch (error) {
    console.error("Error fetching stats:", error)
    return NextResponse.json({ error: "Failed to fetch stats" }, { status: 500 })
  }
}
