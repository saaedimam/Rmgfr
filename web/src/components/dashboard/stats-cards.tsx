"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from "lucide-react";

interface StatsCardsProps {
  totalEvents?: number
  totalDecisions?: number
  allowRate?: number
  denyRate?: number
  reviewRate?: number
}

export function StatsCards({ 
  totalEvents = 12543,
  totalDecisions = 234,
  allowRate = 15,
  denyRate = 8,
  reviewRate = 3
}: StatsCardsProps = {}) {
  const stats = [
    {
      title: "Total Events",
      value: totalEvents.toLocaleString(),
      change: "+12%",
      trend: "up" as const,
      icon: TrendingUp,
    },
    {
      title: "Fraud Detected",
      value: totalDecisions.toLocaleString(),
      change: `-${denyRate}%`,
      trend: "down" as const,
      icon: AlertTriangle,
    },
    {
      title: "Approved",
      value: (totalEvents - totalDecisions).toLocaleString(),
      change: `+${allowRate}%`,
      trend: "up" as const,
      icon: CheckCircle,
    },
    {
      title: "Review Cases",
      value: Math.floor(totalEvents * 0.03).toLocaleString(),
      change: `+${reviewRate}%`,
      trend: "up" as const,
      icon: AlertTriangle,
    },
  ];
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat) => {
        const Icon = stat.icon;
        return (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {stat.title}
              </CardTitle>
              <Icon className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-gray-500 flex items-center mt-1">
                <span
                  className={`inline-flex items-center ${
                    stat.trend === "up" ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {stat.change}
                </span>
                <span className="ml-1">from last month</span>
              </p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
