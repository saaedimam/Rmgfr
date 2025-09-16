"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const recentDecisions = [
  {
    id: "dec_123",
    eventId: "evt_123",
    decision: "allow",
    riskScore: 0.2,
    timestamp: "2024-01-15T10:30:00Z",
    reasons: ["Low risk profile", "Normal transaction pattern"],
  },
  {
    id: "dec_124",
    eventId: "evt_124",
    decision: "deny",
    riskScore: 0.9,
    timestamp: "2024-01-15T10:25:00Z",
    reasons: ["High velocity", "Suspicious device"],
  },
  {
    id: "dec_125",
    eventId: "evt_125",
    decision: "allow",
    riskScore: 0.1,
    timestamp: "2024-01-15T10:20:00Z",
    reasons: ["New user signup", "Clean profile"],
  },
  {
    id: "dec_126",
    eventId: "evt_126",
    decision: "review",
    riskScore: 0.6,
    timestamp: "2024-01-15T10:15:00Z",
    reasons: ["Medium risk", "Unusual amount"],
  },
];

export function DecisionsList() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Decisions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recentDecisions.map((decision) => (
            <div
              key={decision.id}
              className="flex items-center justify-between p-3 border rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <div
                  className={`w-2 h-2 rounded-full ${
                    decision.decision === "allow"
                      ? "bg-green-500"
                      : decision.decision === "deny"
                      ? "bg-red-500"
                      : "bg-yellow-500"
                  }`}
                />
                <div>
                  <p className="font-medium text-sm">
                    {decision.decision.toUpperCase()}
                  </p>
                  <p className="text-xs text-gray-500">
                    Risk: {(decision.riskScore * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
              <div className="text-right">
                <Badge
                  variant={
                    decision.decision === "allow"
                      ? "default"
                      : decision.decision === "deny"
                      ? "destructive"
                      : "secondary"
                  }
                >
                  {decision.decision}
                </Badge>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(decision.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
