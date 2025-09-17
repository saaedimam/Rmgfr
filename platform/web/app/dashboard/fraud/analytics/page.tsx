'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import FraudNav from '@/components/FraudNav';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  Activity,
  Shield,
  Clock,
  RefreshCw
} from 'lucide-react';

interface AnalyticsData {
  total_events: number;
  allowed_events: number;
  denied_events: number;
  review_events: number;
  avg_risk_score: number;
  trends: Array<{
    timestamp: string;
    total_events: number;
    allowed_events: number;
    denied_events: number;
    review_events: number;
    avg_risk_score: number;
  }>;
  top_rules: Array<{
    rule_name: string;
    fire_count: number;
    deny_count: number;
    allow_count: number;
    review_count: number;
  }>;
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('24');
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const projectId = "550e8400-e29b-41d4-a716-446655440001";

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsRes, trendsRes, rulesRes] = await Promise.all([
        fetch(`/api/dashboard/stats?project_id=${projectId}&hours=${timeRange}`),
        fetch(`/api/dashboard/trends?project_id=${projectId}&hours=${timeRange}&interval_minutes=60`),
        fetch(`/api/dashboard/top-rules?project_id=${projectId}&hours=${timeRange}&limit=10`)
      ]);

      if (!statsRes.ok || !trendsRes.ok || !rulesRes.ok) {
        throw new Error('Failed to fetch analytics data');
      }

      const [stats, trends, rules] = await Promise.all([
        statsRes.json(),
        trendsRes.json(),
        rulesRes.json()
      ]);

      setData({
        total_events: stats.total_events,
        allowed_events: stats.allowed_events,
        denied_events: stats.denied_events,
        review_events: stats.review_events,
        avg_risk_score: stats.avg_risk_score,
        trends,
        top_rules: rules
      });

      setLastRefresh(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const getTrendDirection = (current: number, previous: number) => {
    if (current > previous) return { direction: 'up', color: 'text-red-600' };
    if (current < previous) return { direction: 'down', color: 'text-green-600' };
    return { direction: 'flat', color: 'text-gray-600' };
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString();
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading analytics...</span>
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
          <h1 className="text-3xl font-bold">Analytics</h1>
          <p className="text-muted-foreground">
            Fraud detection analytics and insights
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">Last Hour</SelectItem>
              <SelectItem value="24">Last 24h</SelectItem>
              <SelectItem value="168">Last 7d</SelectItem>
              <SelectItem value="720">Last 30d</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={fetchAnalytics} disabled={loading} variant="outline" size="sm">
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Summary Cards */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Events</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{data.total_events.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                Last {timeRange}h
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {data.total_events > 0 ? 
                  ((data.allowed_events / data.total_events) * 100).toFixed(1) : 0}%
              </div>
              <p className="text-xs text-muted-foreground">
                {data.allowed_events} allowed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Block Rate</CardTitle>
              <Shield className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {data.total_events > 0 ? 
                  ((data.denied_events / data.total_events) * 100).toFixed(1) : 0}%
              </div>
              <p className="text-xs text-muted-foreground">
                {data.denied_events} denied
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Review Rate</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {data.total_events > 0 ? 
                  ((data.review_events / data.total_events) * 100).toFixed(1) : 0}%
              </div>
              <p className="text-xs text-muted-foreground">
                {data.review_events} under review
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Risk Score Analysis */}
      {data && (
        <Card>
          <CardHeader>
            <CardTitle>Risk Score Analysis</CardTitle>
            <CardDescription>
              Average risk score: {data.avg_risk_score.toFixed(3)}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Risk Distribution</span>
                <span className="text-sm text-muted-foreground">
                  {data.total_events} total events
                </span>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Low Risk (0.0 - 0.3)</span>
                  <span className="text-sm font-medium">
                    {data.total_events > 0 ? 
                      Math.round((data.allowed_events / data.total_events) * 100) : 0}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full" 
                    style={{ 
                      width: `${data.total_events > 0 ? 
                        (data.allowed_events / data.total_events) * 100 : 0}%` 
                    }}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Medium Risk (0.3 - 0.6)</span>
                  <span className="text-sm font-medium">
                    {data.total_events > 0 ? 
                      Math.round(((data.total_events - data.allowed_events - data.denied_events - data.review_events) / data.total_events) * 100) : 0}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-yellow-500 h-2 rounded-full" 
                    style={{ 
                      width: `${data.total_events > 0 ? 
                        ((data.total_events - data.allowed_events - data.denied_events - data.review_events) / data.total_events) * 100 : 0}%` 
                    }}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">High Risk (0.6 - 0.8)</span>
                  <span className="text-sm font-medium">
                    {data.total_events > 0 ? 
                      Math.round((data.review_events / data.total_events) * 100) : 0}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-orange-500 h-2 rounded-full" 
                    style={{ 
                      width: `${data.total_events > 0 ? 
                        (data.review_events / data.total_events) * 100 : 0}%` 
                    }}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Critical Risk (0.8 - 1.0)</span>
                  <span className="text-sm font-medium">
                    {data.total_events > 0 ? 
                      Math.round((data.denied_events / data.total_events) * 100) : 0}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-red-500 h-2 rounded-full" 
                    style={{ 
                      width: `${data.total_events > 0 ? 
                        (data.denied_events / data.total_events) * 100 : 0}%` 
                    }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Trends */}
      {data && data.trends.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Event Trends</CardTitle>
            <CardDescription>
              Event volume and risk trends over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.trends.slice(0, 10).map((trend, index) => (
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
      )}

      {/* Top Rules */}
      {data && data.top_rules.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Top Firing Rules</CardTitle>
            <CardDescription>
              Most frequently triggered rules
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.top_rules.map((rule, index) => (
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
      )}

      {/* Last Updated */}
      <div className="text-center text-sm text-muted-foreground">
        Last updated: {lastRefresh.toLocaleString()}
      </div>
    </div>
  );
}
