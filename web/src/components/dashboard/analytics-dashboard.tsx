"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Activity,
  Shield,
  Clock,
  Users,
  Smartphone,
  Globe
} from "lucide-react";

interface DashboardData {
  total_events: number;
  high_risk_events: number;
  medium_risk_events: number;
  low_risk_events: number;
  blocked_transactions: number;
  allowed_transactions: number;
  pending_review: number;
  avg_risk_score: number;
  fraud_detection_rate: number;
  false_positive_rate: number;
  response_time_avg: number;
  response_time_p95: number;
  response_time_p99: number;
  active_users: number;
  unique_devices: number;
  top_event_types: Array<{
    type: string;
    count: number;
    percentage: number;
  }>;
  top_risk_factors: Array<{
    factor: string;
    count: number;
    impact: string;
  }>;
  geographic_distribution: Array<{
    location: string;
    count: number;
    risk_level: string;
  }>;
  hourly_trends: Array<{
    hour: number;
    events: number;
    high_risk: number;
    avg_risk_score: number;
  }>;
}

interface Alert {
  type: string;
  title: string;
  message: string;
  timestamp: string;
  severity: string;
}

export default function AnalyticsDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/analytics/dashboard?project_id=demo');
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }
      const data = await response.json();
      setDashboardData(data.dashboard);
      setAlerts(data.alerts || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-600 p-4">
        <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
        <p>Error loading dashboard: {error}</p>
        <button 
          onClick={fetchDashboardData}
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!dashboardData) {
    return <div>No data available</div>;
  }

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'High': return 'bg-red-100 text-red-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'Low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Active Alerts</h3>
          {alerts.map((alert, index) => (
            <div key={index} className="p-4 border-l-4 border-red-500 bg-red-50">
              <div className="flex items-center">
                <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
                <div>
                  <h4 className="font-medium text-red-800">{alert.title}</h4>
                  <p className="text-red-700">{alert.message}</p>
                  <Badge className={`mt-1 ${getSeverityColor(alert.severity)}`}>
                    {alert.severity}
                  </Badge>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Events</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.total_events.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Last 24 hours
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High Risk Events</CardTitle>
            <Shield className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{dashboardData.high_risk_events}</div>
            <p className="text-xs text-muted-foreground">
              {((dashboardData.high_risk_events / dashboardData.total_events) * 100).toFixed(1)}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Fraud Detection Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {dashboardData.fraud_detection_rate.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Transactions blocked
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Clock className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.response_time_avg.toFixed(0)}ms</div>
            <p className="text-xs text-muted-foreground">
              P99: {dashboardData.response_time_p99.toFixed(0)}ms
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="text-sm">High Risk</span>
                </div>
                <span className="font-medium">{dashboardData.high_risk_events}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span className="text-sm">Medium Risk</span>
                </div>
                <span className="font-medium">{dashboardData.medium_risk_events}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Low Risk</span>
                </div>
                <span className="font-medium">{dashboardData.low_risk_events}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Transaction Outcomes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="text-sm">Blocked</span>
                </div>
                <span className="font-medium">{dashboardData.blocked_transactions}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Allowed</span>
                </div>
                <span className="font-medium">{dashboardData.allowed_transactions}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span className="text-sm">Pending Review</span>
                </div>
                <span className="font-medium">{dashboardData.pending_review}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Event Types */}
      <Card>
        <CardHeader>
          <CardTitle>Top Event Types</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {dashboardData.top_event_types.map((eventType, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm font-medium">{eventType.type}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full progress-bar" 
                      style={{ width: `${Math.min(eventType.percentage, 100)}%` }}
                      role="progressbar"
                      aria-valuenow={eventType.percentage}
                      aria-valuemin={0}
                      aria-valuemax={100}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-12 text-right">
                    {eventType.count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Risk Factors */}
      <Card>
        <CardHeader>
          <CardTitle>Top Risk Factors</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {dashboardData.top_risk_factors.map((factor, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm font-medium">{factor.factor}</span>
                <div className="flex items-center space-x-2">
                  <Badge className={getRiskLevelColor(factor.impact)}>
                    {factor.impact}
                  </Badge>
                  <span className="text-sm text-gray-600">{factor.count}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Geographic Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Geographic Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {dashboardData.geographic_distribution.map((location, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Globe className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">{location.location}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge className={getRiskLevelColor(location.risk_level)}>
                    {location.risk_level}
                  </Badge>
                  <span className="text-sm text-gray-600">{location.count}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* System Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.active_users}</div>
            <p className="text-xs text-muted-foreground">
              Last hour
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Unique Devices</CardTitle>
            <Smartphone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.unique_devices}</div>
            <p className="text-xs text-muted-foreground">
              Last 24 hours
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Risk Score</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(dashboardData.avg_risk_score * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Overall risk level
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
