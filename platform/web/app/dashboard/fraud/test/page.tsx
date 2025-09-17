'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Send, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle,
  Activity,
  Shield
} from 'lucide-react';

interface TestEvent {
  event_type: string;
  event_data: Record<string, any>;
  profile_id?: string;
  session_id?: string;
  device_fingerprint?: string;
  ip_address?: string;
  user_agent?: string;
  amount?: number;
  currency?: string;
}

interface EventResult {
  event_id: string;
  risk_score: number;
  decision: string;
  reasons: string[];
  rules_fired: string[];
  processing_time_ms: number;
  timestamp: string;
}

export default function FraudTestPage() {
  const [testEvent, setTestEvent] = useState<TestEvent>({
    event_type: 'login',
    event_data: {},
    profile_id: '',
    session_id: '',
    device_fingerprint: '',
    ip_address: '',
    user_agent: '',
    amount: undefined,
    currency: 'USD'
  });

  const [results, setResults] = useState<EventResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const eventTypes = [
    { value: 'login', label: 'Login' },
    { value: 'signup', label: 'Sign Up' },
    { value: 'checkout', label: 'Checkout' },
    { value: 'payment', label: 'Payment' },
    { value: 'custom', label: 'Custom' }
  ];

  const currencies = [
    { value: 'USD', label: 'USD' },
    { value: 'EUR', label: 'EUR' },
    { value: 'GBP', label: 'GBP' },
    { value: 'JPY', label: 'JPY' }
  ];

  const handleInputChange = (field: keyof TestEvent, value: any) => {
    setTestEvent(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleEventDataChange = (value: string) => {
    try {
      const parsed = JSON.parse(value);
      setTestEvent(prev => ({
        ...prev,
        event_data: parsed
      }));
    } catch {
      // Invalid JSON, keep as string for now
      setTestEvent(prev => ({
        ...prev,
        event_data: { raw: value }
      }));
    }
  };

  const sendTestEvent = async () => {
    setLoading(true);
    setError(null);

    try {
      // Clean up the event data
      const cleanedEvent: TestEvent = {
        ...testEvent,
        profile_id: testEvent.profile_id || undefined,
        session_id: testEvent.session_id || undefined,
        device_fingerprint: testEvent.device_fingerprint || undefined,
        ip_address: testEvent.ip_address || undefined,
        user_agent: testEvent.user_agent || undefined,
        amount: testEvent.amount || undefined,
        currency: testEvent.currency || undefined
      };

      const response = await fetch('/api/events/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cleanedEvent),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      const eventResult: EventResult = {
        ...result,
        timestamp: new Date().toISOString()
      };

      setResults(prev => [eventResult, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error sending test event:', err);
    } finally {
      setLoading(false);
    }
  };

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case 'allow': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'deny': return <XCircle className="h-4 w-4 text-red-600" />;
      case 'review': return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'step_up': return <Shield className="h-4 w-4 text-blue-600" />;
      default: return <AlertTriangle className="h-4 w-4 text-gray-600" />;
    }
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

  const getRiskLevel = (score: number) => {
    if (score < 0.3) return { level: 'Low', color: 'text-green-600' };
    if (score < 0.6) return { level: 'Medium', color: 'text-yellow-600' };
    if (score < 0.8) return { level: 'High', color: 'text-orange-600' };
    return { level: 'Critical', color: 'text-red-600' };
  };

  const clearResults = () => {
    setResults([]);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Fraud Detection Test</h1>
          <p className="text-muted-foreground">
            Test real-time fraud detection with custom events
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button onClick={clearResults} variant="outline" size="sm">
            Clear Results
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test Event Form */}
        <Card>
          <CardHeader>
            <CardTitle>Test Event</CardTitle>
            <CardDescription>
              Configure and send a test event to the fraud detection system
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="event_type">Event Type</Label>
                <Select
                  value={testEvent.event_type}
                  onValueChange={(value) => handleInputChange('event_type', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {eventTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="profile_id">Profile ID</Label>
                <Input
                  id="profile_id"
                  value={testEvent.profile_id || ''}
                  onChange={(e) => handleInputChange('profile_id', e.target.value)}
                  placeholder="user_123"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="session_id">Session ID</Label>
                <Input
                  id="session_id"
                  value={testEvent.session_id || ''}
                  onChange={(e) => handleInputChange('session_id', e.target.value)}
                  placeholder="session_456"
                />
              </div>
              <div>
                <Label htmlFor="device_fingerprint">Device Fingerprint</Label>
                <Input
                  id="device_fingerprint"
                  value={testEvent.device_fingerprint || ''}
                  onChange={(e) => handleInputChange('device_fingerprint', e.target.value)}
                  placeholder="device_hash_789"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="ip_address">IP Address</Label>
                <Input
                  id="ip_address"
                  value={testEvent.ip_address || ''}
                  onChange={(e) => handleInputChange('ip_address', e.target.value)}
                  placeholder="192.168.1.1"
                />
              </div>
              <div>
                <Label htmlFor="user_agent">User Agent</Label>
                <Input
                  id="user_agent"
                  value={testEvent.user_agent || ''}
                  onChange={(e) => handleInputChange('user_agent', e.target.value)}
                  placeholder="Mozilla/5.0..."
                />
              </div>
            </div>

            {(testEvent.event_type === 'payment' || testEvent.event_type === 'checkout') && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="amount">Amount</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    value={testEvent.amount || ''}
                    onChange={(e) => handleInputChange('amount', parseFloat(e.target.value) || undefined)}
                    placeholder="99.99"
                  />
                </div>
                <div>
                  <Label htmlFor="currency">Currency</Label>
                  <Select
                    value={testEvent.currency || 'USD'}
                    onValueChange={(value) => handleInputChange('currency', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {currencies.map((currency) => (
                        <SelectItem key={currency.value} value={currency.value}>
                          {currency.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}

            <div>
              <Label htmlFor="event_data">Event Data (JSON)</Label>
              <Textarea
                id="event_data"
                value={JSON.stringify(testEvent.event_data, null, 2)}
                onChange={(e) => handleEventDataChange(e.target.value)}
                placeholder='{"user_id": "123", "email": "test@example.com"}'
                rows={4}
              />
            </div>

            <Button 
              onClick={sendTestEvent} 
              disabled={loading}
              className="w-full"
            >
              {loading ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Send Test Event
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Results */}
        <Card>
          <CardHeader>
            <CardTitle>Test Results</CardTitle>
            <CardDescription>
              {results.length} event{results.length !== 1 ? 's' : ''} processed
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {results.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  No test events sent yet
                </div>
              ) : (
                results.map((result, index) => {
                  const riskLevel = getRiskLevel(result.risk_score);
                  return (
                    <div key={index} className="p-4 border rounded-lg space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          {getDecisionIcon(result.decision)}
                          <Badge className={getDecisionColor(result.decision)}>
                            {result.decision}
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {new Date(result.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium">Risk Score:</span>
                          <span className={`ml-2 ${riskLevel.color}`}>
                            {result.risk_score.toFixed(3)} ({riskLevel.level})
                          </span>
                        </div>
                        <div>
                          <span className="font-medium">Processing Time:</span>
                          <span className="ml-2">{result.processing_time_ms.toFixed(1)}ms</span>
                        </div>
                      </div>

                      {result.reasons.length > 0 && (
                        <div>
                          <span className="text-sm font-medium">Reasons:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {result.reasons.map((reason, i) => (
                              <Badge key={i} variant="outline" className="text-xs">
                                {reason}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {result.rules_fired.length > 0 && (
                        <div>
                          <span className="text-sm font-medium">Rules Fired:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {result.rules_fired.map((rule, i) => (
                              <Badge key={i} variant="secondary" className="text-xs">
                                {rule}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="text-xs text-muted-foreground">
                        Event ID: {result.event_id}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
