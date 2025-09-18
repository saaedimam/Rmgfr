'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import FraudNav from '@/components/FraudNav';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Activity,
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Users,
  DollarSign,
  Eye,
  RefreshCw
} from 'lucide-react';

interface DashboardStats {
  total_events: number;
  allowed_events: number;
  denied_events: number;
  review_events: number;
  avg_risk_score: number;
  max_risk_score: number;
  min_risk_score: number;
  time_period_hours: number;
  last_updated: string;
}

interface EventTrend {
  timestamp: string;
  total_events: number;
  allowed_events: number;
  denied_events: number;
  review_events: number;
  avg_risk_score: number;
}

interface RecentEvent {
  id: string;
  event_type: string;
  profile_id: string;
  ip_address: string;
  risk_score: number;
  decision: string;
  reasons: string[];
  rules_fired: string[];
  created_at: string;
}

interface TopRule {
  rule_name: string;
  fire_count: number;
  deny_count: number;
  allow_count: number;
  review_count: number;
}

export default function FraudDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [trends, setTrends] = useState<EventTrend[]>([]);
  const [recentEvents, setRecentEvents] = useState<RecentEvent[]>([]);
  const [topRules, setTopRules] = useState<TopRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const projectId = "550e8400-e29b-41d4-a716-446655440001"; // Default test project

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all dashboard data in parallel
      const [statsRes, trendsRes, eventsRes, rulesRes] = await Promise.all([
        fetch(`/api/dashboard/stats?project_id=${projectId}&hours=24`),
        fetch(`/api/dashboard/trends?project_id=${projectId}&hours=24&interval_minutes=60`),
        fetch(`/api/dashboard/recent-events?project_id=${projectId}&limit=50`),
        fetch(`/api/dashboard/top-rules?project_id=${projectId}&hours=24&limit=10`)
      ]);

      if (!statsRes.ok || !trendsRes.ok || !eventsRes.ok || !rulesRes.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const [statsData, trendsData, eventsData, rulesData] = await Promise.all([
        statsRes.json(),
        trendsRes.json(),
        eventsRes.json(),
        rulesRes.json()
      ]);

      setStats(statsData);
      setTrends(trendsData);
      setRecentEvents(eventsData);
      setTopRules(rulesData);
      setLastRefresh(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();

    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getDecisionColor = (decision: string) => {
    switch (decision) {
      case 'allow': return 'bg-green-100 text-green-800';
      case 'deny': return 'bg-red-100 text-red-800';
      case 'review': return 'bg-yellow-100 text-yellow-800';
      case 'step_up': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskLevel = (score: number) => {
    if (score < 0.3) return { level: 'Low', color: 'text-green-600' };
    if (score < 0.6) return { level: 'Medium', color: 'text-yellow-600' };
    if (score < 0.8) return { level: 'High', color: 'text-orange-600' };
    return { level: 'Critical', color: 'text-red-600' };
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString();
  };

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Navigation */}
      <FraudNav />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Fraud Detection Dashboard</h1>
          <p className="text-muted-foreground">
            Real-time monitoring and analytics
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            onClick={fetchDashboardData}
            disabled={loading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <span className="text-sm text-muted-foreground">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Events</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_events.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                Last {stats.time_period_hours} hours
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Allowed</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {stats.allowed_events.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                {stats.total_events > 0 ?
                  ((stats.allowed_events / stats.total_events) * 100).toFixed(1) : 0}% of total
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Denied</CardTitle>
              <Shield className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {stats.denied_events.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                {stats.total_events > 0 ?
                  ((stats.denied_events / stats.total_events) * 100).toFixed(1) : 0}% of total
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Under Review</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {stats.review_events.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                {stats.total_events > 0 ?
                  ((stats.review_events / stats.total_events) * 100).toFixed(1) : 0}% of total
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Risk Score Overview */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Risk Score Overview</CardTitle>
            <CardDescription>
              Average risk score: {stats.avg_risk_score.toFixed(3)}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {stats.min_risk_score.toFixed(3)}
                </div>
                <p className="text-sm text-muted-foreground">Minimum Risk</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {stats.avg_risk_score.toFixed(3)}
                </div>
                <p className="text-sm text-muted-foreground">Average Risk</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {stats.max_risk_score.toFixed(3)}
                </div>
                <p className="text-sm text-muted-foreground">Maximum Risk</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="events" className="space-y-4">
        <TabsList>
          <TabsTrigger value="events">Recent Events</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="rules">Top Rules</TabsTrigger>
        </TabsList>

        {/* Recent Events Tab */}
        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Events</CardTitle>
              <CardDescription>
                Latest {recentEvents.length} events processed
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentEvents.map((event) => {
                  const riskLevel = getRiskLevel(event.risk_score);
                  return (
                    <div key={event.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex flex-col">
                          <span className="font-medium">{event.event_type}</span>
                          <span className="text-sm text-muted-foreground">
                            {event.profile_id} • {event.ip_address}
                          </span>
                        </div>
                        <Badge className={getDecisionColor(event.decision)}>
                          {event.decision}
                        </Badge>
                        <div className="flex flex-col">
                          <span className={`text-sm font-medium ${riskLevel.color}`}>
                            Risk: {event.risk_score.toFixed(3)}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {riskLevel.level}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">
                          {formatTime(event.created_at)}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {formatDate(event.created_at)}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Trends Tab */}
        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Event Trends</CardTitle>
              <CardDescription>
                Event volume and risk trends over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {trends.map((trend, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="text-sm font-medium">
                        {formatTime(trend.timestamp)}
                      </div>
                      <div className="flex space-x-4">
                        <span className="text-green-600">
                          ✓ {trend.allowed_events}
                        </span>
                        <span className="text-red-600">
                          ✗ {trend.denied_events}
                        </span>
                        <span className="text-yellow-600">
                          ⏳ {trend.review_events}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        {trend.total_events} total
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Avg risk: {trend.avg_risk_score.toFixed(3)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Top Rules Tab */}
        <TabsContent value="rules" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Top Firing Rules</CardTitle>
              <CardDescription>
                Most frequently triggered rules
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topRules.map((rule, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="text-sm font-medium">
                        {rule.rule_name}
                      </div>
                      <div className="flex space-x-2">
                        <Badge variant="outline">
                          {rule.fire_count} fires
                        </Badge>
                        <Badge className="bg-green-100 text-green-800">
                          {rule.allow_count} allow
                        </Badge>
                        <Badge className="bg-red-100 text-red-800">
                          {rule.deny_count} deny
                        </Badge>
                        <Badge className="bg-yellow-100 text-yellow-800">
                          {rule.review_count} review
                        </Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        {rule.fire_count} total
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {rule.deny_count + rule.review_count} flagged
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
