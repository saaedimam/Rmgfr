import React from "react"
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

interface Event {
  id: string
  type: string
  actor_user_id?: string
  ip?: string
  event_ts: string
  payload: Record<string, any>
}

interface EventsListProps {
  events: Event[]
}

export function EventsList({ events }: EventsListProps) {
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  const getEventTypeBadge = (type: string) => {
    const variants = {
      login: "info",
      signup: "success", 
      checkout: "warning",
      custom: "default"
    } as const
    
    return variants[type as keyof typeof variants] || "default"
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Recent Events</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Type</TableHead>
            <TableHead>User ID</TableHead>
            <TableHead>IP</TableHead>
            <TableHead>Timestamp</TableHead>
            <TableHead>Payload</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {events.map((event) => (
            <TableRow key={event.id}>
              <TableCell>
                <Badge variant={getEventTypeBadge(event.type)}>
                  {event.type}
                </Badge>
              </TableCell>
              <TableCell>{event.actor_user_id || "-"}</TableCell>
              <TableCell>{event.ip || "-"}</TableCell>
              <TableCell>{formatTimestamp(event.event_ts)}</TableCell>
              <TableCell>
                <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                  {JSON.stringify(event.payload).slice(0, 50)}...
                </code>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
