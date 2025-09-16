import React from "react"
import { Card, CardContent } from "@/components/ui/card"

interface StatsCardsProps {
  totalEvents: number
  totalDecisions: number
  allowRate: number
  denyRate: number
  reviewRate: number
}

export function StatsCards({ totalEvents, totalDecisions, allowRate, denyRate, reviewRate }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      <Card>
        <CardContent className="p-4">
          <div className="text-2xl font-bold text-gray-900">{totalEvents}</div>
          <div className="text-sm text-gray-500">Total Events</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4">
          <div className="text-2xl font-bold text-gray-900">{totalDecisions}</div>
          <div className="text-sm text-gray-500">Total Decisions</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4">
          <div className="text-2xl font-bold text-green-600">{allowRate.toFixed(1)}%</div>
          <div className="text-sm text-gray-500">Allow Rate</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4">
          <div className="text-2xl font-bold text-red-600">{denyRate.toFixed(1)}%</div>
          <div className="text-sm text-gray-500">Deny Rate</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4">
          <div className="text-2xl font-bold text-yellow-600">{reviewRate.toFixed(1)}%</div>
          <div className="text-sm text-gray-500">Review Rate</div>
        </CardContent>
      </Card>
    </div>
  )
}
