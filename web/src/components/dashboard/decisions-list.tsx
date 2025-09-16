import React from "react"
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

interface Decision {
  id: string
  event_id: string
  outcome: string
  score?: number
  reasons: string[]
  decided_at: string
}

interface DecisionsListProps {
  decisions: Decision[]
}

export function DecisionsList({ decisions }: DecisionsListProps) {
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  const getOutcomeBadge = (outcome: string) => {
    const variants = {
      allow: "success",
      deny: "danger",
      review: "warning"
    } as const
    
    return variants[outcome as keyof typeof variants] || "default"
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Recent Decisions</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Outcome</TableHead>
            <TableHead>Score</TableHead>
            <TableHead>Reasons</TableHead>
            <TableHead>Event ID</TableHead>
            <TableHead>Decided At</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {decisions.map((decision) => (
            <TableRow key={decision.id}>
              <TableCell>
                <Badge variant={getOutcomeBadge(decision.outcome)}>
                  {decision.outcome}
                </Badge>
              </TableCell>
              <TableCell>{decision.score || "-"}</TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-1">
                  {decision.reasons.map((reason, index) => (
                    <Badge key={index} variant="info" className="text-xs">
                      {reason}
                    </Badge>
                  ))}
                </div>
              </TableCell>
              <TableCell>
                <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                  {decision.event_id.slice(0, 8)}...
                </code>
              </TableCell>
              <TableCell>{formatTimestamp(decision.decided_at)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
