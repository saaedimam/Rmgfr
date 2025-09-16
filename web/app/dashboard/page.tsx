import React from "react"
import { StatsCards } from "@/components/dashboard/stats-cards"
import { EventsList } from "@/components/dashboard/events-list"
import { DecisionsList } from "@/components/dashboard/decisions-list"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

async function getStats() {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:3000"}/api/stats`, {
      cache: "no-store"
    })
    if (!response.ok) throw new Error("Failed to fetch stats")
    return await response.json()
  } catch (error) {
    console.error("Error fetching stats:", error)
    return { totalEvents: 0, totalDecisions: 0, allowRate: 0, denyRate: 0, reviewRate: 0 }
  }
}

async function getEvents() {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:3000"}/api/events`, {
      cache: "no-store"
    })
    if (!response.ok) throw new Error("Failed to fetch events")
    return await response.json()
  } catch (error) {
    console.error("Error fetching events:", error)
    return []
  }
}

async function getDecisions() {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:3000"}/api/decisions`, {
      cache: "no-store"
    })
    if (!response.ok) throw new Error("Failed to fetch decisions")
    return await response.json()
  } catch (error) {
    console.error("Error fetching decisions:", error)
    return []
  }
}

export default async function DashboardPage() {
  const [stats, events, decisions] = await Promise.all([
    getStats(),
    getEvents(),
    getDecisions()
  ])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Fraud Detection Dashboard</h1>
          <p className="mt-2 text-gray-600">Real-time monitoring of events and fraud decisions</p>
        </div>

        <div className="space-y-8">
          <StatsCards
            totalEvents={stats.totalEvents}
            totalDecisions={stats.totalDecisions}
            allowRate={stats.allowRate}
            denyRate={stats.denyRate}
            reviewRate={stats.reviewRate}
          />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card>
              <CardHeader>
                <CardTitle>Recent Events</CardTitle>
              </CardHeader>
              <CardContent>
                <EventsList events={events.slice(0, 10)} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Decisions</CardTitle>
              </CardHeader>
              <CardContent>
                <DecisionsList decisions={decisions.slice(0, 10)} />
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
