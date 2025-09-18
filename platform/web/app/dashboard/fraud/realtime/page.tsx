'use client';

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Activity,
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  RefreshCw,
  Play,
  Pause,
  Square
} from 'lucide-react';

interface RealtimeEvent {
  id: string;
  event_type: string;
  profile_id: string;
  ip_address: string;
  risk_score: number;
  decision: string;
  reasons: string[];
  rules_fired: string[];
  created_at: string;
  processing_time_ms: number;
}

interface RealtimeStats {
  total_events: number;
  allowed_events: number;
  denied_events: number;
  review_events: number;
  avg_risk_score: number;
  events_per_minute: number;
}

export default function RealtimePage() {
  const [events, setEvents] = useState<RealtimeEvent[]>([]);
  const [stats, setStats] = useState<RealtimeStats | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const eventSourceRef = useRef<EventSource | null>(null);
  const statsIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const projectId = "550e8400-e29b-41d4-a716-446655440001";

  const startStreaming = () => {
    if (isStreaming) return;

    setIsStreaming(true);
    setError(null);

    // Simulate real-time events (in production, this would be WebSocket or SSE)
    const simulateEvent = () => {
      const eventTypes = ['login', 'signup', 'payment', 'checkout'];
      const decisions = ['allow', 'deny', 'review', 'step_up'];
      const reasons = [
        'High risk score',
        'Unusual location',
        'Velocity check failed',
        'Device anomaly detected',
        'Behavioral pattern mismatch'
      ];
      const rules = [
        'risk_band_high',
        'velocity_check',
        'geo_anomaly',
        'device_fingerprint',
        'behavioral_analysis'
      ];

      const newEvent: RealtimeEvent = {
        id: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        event_type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
        profile_id: `user_${Math.floor(Math.random() * 1000)}`,
        ip_address: `192.168.1.${Math.floor(Math.random() * 254) + 1}`,
        risk_score: Math.random(),
        decision: decisions[Math.floor(Math.random() * decisions.length)],
        reasons: reasons.slice(0, Math.floor(Math.random() * 3) + 1),
        rules_fired: rules.slice(0, Math.floor(Math.random() * 3) + 1),
        created_at: new Date().toISOString(),
        processing_time_ms: Math.random() * 100 + 10
      };

      setEvents(prev => [newEvent, ...prev.slice(0, 49)]); // Keep last 50 events
      setLastUpdate(new Date());
    };

    // Simulate events every 2-5 seconds
    const eventInterval = setInterval(simulateEvent, Math.random() * 3000 + 2000);

    // Update stats every 10 seconds
    const updateStats = async () => {
      try {
        const response = await fetch(`/api/dashboard/stats?project_id=${projectId}&hours=1`);
        if (response.ok) {
          const data = await response.json();
          setStats({
            total_events: data.total_events,
            allowed_events: data.allowed_events,
            denied_events: data.denied_events,
            review_events: data.review_events,
            avg_risk_score: data.avg_risk_score,
            events_per_minute: Math.floor(data.total_events / 60)
          });
        }
      } catch (err) {
        console.error('Error updating stats:', err);
      }
    };

    statsIntervalRef.current = setInterval(updateStats, 10000);
    updateStats(); // Initial load

    // Store interval for cleanup
    (eventInterval as any).__cleanup = () => clearInterval(eventInterval);
  };

  const stopStreaming = () => {
    setIsStreaming(false);

    // Clean up intervals
    if (statsIntervalRef.current) {
      clearInterval(statsIntervalRef.current);
      statsIntervalRef.current = null;
    }
  };

  const clearEvents = () => {
    setEvents([]);
  };

  const getDecisionColor = (decision: string) => {
    switch (decision) {
      case 'allow': return 'bg-green-100 text-green-800';
      case 'deny': return 'bg-red-100 text-red-800';
      case 'review': return 'bg-yellow-100 text-yellow-800';
      case 'step_up': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case 'allow': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'deny': return <Shield className="h-4 w-4 text-red-600" />;
      case 'review': return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'step_up': return <AlertTriangle className="h-4 w-4 text-blue-600" />;
      default: return <Activity className="h-4 w-4 text-gray-600" />;
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

  useEffect(() => {
    return () => {
      stopStreaming();
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Real-time Monitoring</h1>
          <p className="text-muted-foreground">
            Live fraud detection events and analytics
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            onClick={clearEvents}
            variant="outline"
            size="sm"
            disabled={events.length === 0}
          >
            Clear Events
          </Button>
          {isStreaming ? (
            <Button onClick={stopStreaming} variant="destructive" size="sm">
              <Square className="h-4 w-4 mr-2" />
              Stop
            </Button>
          ) : (
            <Button onClick={startStreaming} variant="default" size="sm">
              <Play className="h-4 w-4 mr-2" />
              Start
            </Button>
          )}
        </div>
      </div>

      {/* Status */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isStreaming ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
          <span className="text-sm font-medium">
            {isStreaming ? 'Streaming' : 'Stopped'}
          </span>
        </div>
        <div className="text-sm text-muted-foreground">
          Last update: {lastUpdate.toLocaleTimeString()}
        </div>
        <div className="text-sm text-muted-foreground">
          Events: {events.length}
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
                {stats.events_per_minute} events/min
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

      {/* Live Events */}
      <Card>
        <CardHeader>
          <CardTitle>Live Events</CardTitle>
          <CardDescription>
            Real-time fraud detection events (last 50)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {events.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                {isStreaming ? 'Waiting for events...' : 'Click Start to begin monitoring'}
              </div>
            ) : (
              events.map((event) => {
                const riskLevel = getRiskLevel(event.risk_score);
                return (
                  <div key={event.id} className="flex items-center justify-between p-3 border rounded-lg bg-gray-50">
                    <div className="flex items-center space-x-4">
                      {getDecisionIcon(event.decision)}
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
                        {event.processing_time_ms.toFixed(1)}ms
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
