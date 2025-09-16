"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const recentEvents = [
  {
    id: "evt_123",
    type: "checkout",
    profileId: "user_456",
    timestamp: "2024-01-15T10:30:00Z",
    status: "processed",
  },
  {
    id: "evt_124",
    type: "login",
    profileId: "user_789",
    timestamp: "2024-01-15T10:25:00Z",
    status: "flagged",
  },
  {
    id: "evt_125",
    type: "signup",
    profileId: "user_101",
    timestamp: "2024-01-15T10:20:00Z",
    status: "processed",
  },
  {
    id: "evt_126",
    type: "checkout",
    profileId: "user_202",
    timestamp: "2024-01-15T10:15:00Z",
    status: "review",
  },
];

export function EventsList() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Events</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recentEvents.map((event) => (
            <div
              key={event.id}
              className="flex items-center justify-between p-3 border rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full" />
                <div>
                  <p className="font-medium text-sm">{event.type}</p>
                  <p className="text-xs text-gray-500">{event.profileId}</p>
                </div>
              </div>
              <div className="text-right">
                <Badge
                  variant={
                    event.status === "processed"
                      ? "default"
                      : event.status === "flagged"
                      ? "destructive"
                      : "secondary"
                  }
                >
                  {event.status}
                </Badge>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
