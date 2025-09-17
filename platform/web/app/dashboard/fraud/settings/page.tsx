'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import FraudNav from '@/components/FraudNav';
import { 
  Settings, 
  Save, 
  RefreshCw, 
  AlertTriangle,
  Shield,
  Activity,
  Clock,
  DollarSign
} from 'lucide-react';

interface FraudSettings {
  enabled: boolean;
  risk_thresholds: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  decision_matrix: {
    [key: string]: {
      [key: string]: string;
    };
  };
  velocity_limits: {
    max_events_per_minute: number;
    max_events_per_hour: number;
    max_events_per_day: number;
  };
  geo_settings: {
    enable_vpn_detection: boolean;
    enable_location_consistency: boolean;
    max_location_changes: number;
  };
  device_settings: {
    enable_fingerprinting: boolean;
    enable_user_agent_analysis: boolean;
    suspicious_patterns: string[];
  };
  payment_settings: {
    max_amount: number;
    min_amount: number;
    suspicious_amounts: number[];
    enable_round_number_detection: boolean;
  };
  notification_settings: {
    email_alerts: boolean;
    webhook_url: string;
    alert_threshold: number;
  };
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<FraudSettings>({
    enabled: true,
    risk_thresholds: {
      low: 0.3,
      medium: 0.6,
      high: 0.8,
      critical: 0.9
    },
    decision_matrix: {
      'low': { 'new_user': 'allow', 'returning': 'allow' },
      'medium': { 'new_user': 'review', 'returning': 'allow' },
      'high': { 'new_user': 'deny', 'returning': 'review' },
      'critical': { 'new_user': 'deny', 'returning': 'deny' }
    },
    velocity_limits: {
      max_events_per_minute: 10,
      max_events_per_hour: 100,
      max_events_per_day: 1000
    },
    geo_settings: {
      enable_vpn_detection: true,
      enable_location_consistency: true,
      max_location_changes: 3
    },
    device_settings: {
      enable_fingerprinting: true,
      enable_user_agent_analysis: true,
      suspicious_patterns: ['bot', 'crawler', 'spider', 'scraper']
    },
    payment_settings: {
      max_amount: 10000,
      min_amount: 0.01,
      suspicious_amounts: [1, 10, 100, 1000, 10000],
      enable_round_number_detection: true
    },
    notification_settings: {
      email_alerts: true,
      webhook_url: '',
      alert_threshold: 0.8
    }
  });

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSettingChange = (path: string, value: any) => {
    setSettings(prev => {
      const newSettings = { ...prev };
      const keys = path.split('.');
      let current = newSettings;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newSettings;
    });
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess('Settings saved successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    // Reset to default settings
    setSettings({
      enabled: true,
      risk_thresholds: {
        low: 0.3,
        medium: 0.6,
        high: 0.8,
        critical: 0.9
      },
      decision_matrix: {
        'low': { 'new_user': 'allow', 'returning': 'allow' },
        'medium': { 'new_user': 'review', 'returning': 'allow' },
        'high': { 'new_user': 'deny', 'returning': 'review' },
        'critical': { 'new_user': 'deny', 'returning': 'deny' }
      },
      velocity_limits: {
        max_events_per_minute: 10,
        max_events_per_hour: 100,
        max_events_per_day: 1000
      },
      geo_settings: {
        enable_vpn_detection: true,
        enable_location_consistency: true,
        max_location_changes: 3
      },
      device_settings: {
        enable_fingerprinting: true,
        enable_user_agent_analysis: true,
        suspicious_patterns: ['bot', 'crawler', 'spider', 'scraper']
      },
      payment_settings: {
        max_amount: 10000,
        min_amount: 0.01,
        suspicious_amounts: [1, 10, 100, 1000, 10000],
        enable_round_number_detection: true
      },
      notification_settings: {
        email_alerts: true,
        webhook_url: '',
        alert_threshold: 0.8
      }
    });
  };

  return (
    <div className="space-y-6">
      {/* Navigation */}
      <FraudNav />
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Fraud Detection Settings</h1>
          <p className="text-muted-foreground">
            Configure fraud detection rules and thresholds
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button onClick={handleReset} variant="outline" size="sm">
            Reset
          </Button>
          <Button onClick={handleSave} disabled={saving} size="sm">
            {saving ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Settings
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* General Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            General Settings
          </CardTitle>
          <CardDescription>
            Basic fraud detection configuration
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="enabled">Enable Fraud Detection</Label>
              <p className="text-sm text-muted-foreground">
                Turn fraud detection on or off
              </p>
            </div>
            <Switch
              id="enabled"
              checked={settings.enabled}
              onCheckedChange={(checked) => handleSettingChange('enabled', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Risk Thresholds */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Shield className="h-5 w-5 mr-2" />
            Risk Thresholds
          </CardTitle>
          <CardDescription>
            Configure risk score thresholds for different risk levels
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <Label htmlFor="low_threshold">Low Risk</Label>
              <Input
                id="low_threshold"
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={settings.risk_thresholds.low}
                onChange={(e) => handleSettingChange('risk_thresholds.low', parseFloat(e.target.value))}
              />
            </div>
            <div>
              <Label htmlFor="medium_threshold">Medium Risk</Label>
              <Input
                id="medium_threshold"
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={settings.risk_thresholds.medium}
                onChange={(e) => handleSettingChange('risk_thresholds.medium', parseFloat(e.target.value))}
              />
            </div>
            <div>
              <Label htmlFor="high_threshold">High Risk</Label>
              <Input
                id="high_threshold"
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={settings.risk_thresholds.high}
                onChange={(e) => handleSettingChange('risk_thresholds.high', parseFloat(e.target.value))}
              />
            </div>
            <div>
              <Label htmlFor="critical_threshold">Critical Risk</Label>
              <Input
                id="critical_threshold"
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={settings.risk_thresholds.critical}
                onChange={(e) => handleSettingChange('risk_thresholds.critical', parseFloat(e.target.value))}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Velocity Limits */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="h-5 w-5 mr-2" />
            Velocity Limits
          </CardTitle>
          <CardDescription>
            Configure maximum event frequency limits
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="max_per_minute">Max Events per Minute</Label>
              <Input
                id="max_per_minute"
                type="number"
                min="1"
                value={settings.velocity_limits.max_events_per_minute}
                onChange={(e) => handleSettingChange('velocity_limits.max_events_per_minute', parseInt(e.target.value))}
              />
            </div>
            <div>
              <Label htmlFor="max_per_hour">Max Events per Hour</Label>
              <Input
                id="max_per_hour"
                type="number"
                min="1"
                value={settings.velocity_limits.max_events_per_hour}
                onChange={(e) => handleSettingChange('velocity_limits.max_events_per_hour', parseInt(e.target.value))}
              />
            </div>
            <div>
              <Label htmlFor="max_per_day">Max Events per Day</Label>
              <Input
                id="max_per_day"
                type="number"
                min="1"
                value={settings.velocity_limits.max_events_per_day}
                onChange={(e) => handleSettingChange('velocity_limits.max_events_per_day', parseInt(e.target.value))}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Payment Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <DollarSign className="h-5 w-5 mr-2" />
            Payment Settings
          </CardTitle>
          <CardDescription>
            Configure payment-specific fraud detection rules
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="max_amount">Maximum Amount</Label>
              <Input
                id="max_amount"
                type="number"
                step="0.01"
                min="0"
                value={settings.payment_settings.max_amount}
                onChange={(e) => handleSettingChange('payment_settings.max_amount', parseFloat(e.target.value))}
              />
            </div>
            <div>
              <Label htmlFor="min_amount">Minimum Amount</Label>
              <Input
                id="min_amount"
                type="number"
                step="0.01"
                min="0"
                value={settings.payment_settings.min_amount}
                onChange={(e) => handleSettingChange('payment_settings.min_amount', parseFloat(e.target.value))}
              />
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="round_number_detection">Detect Round Numbers</Label>
              <p className="text-sm text-muted-foreground">
                Flag transactions with round numbers (e.g., $100, $1000)
              </p>
            </div>
            <Switch
              id="round_number_detection"
              checked={settings.payment_settings.enable_round_number_detection}
              onCheckedChange={(checked) => handleSettingChange('payment_settings.enable_round_number_detection', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Device Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="h-5 w-5 mr-2" />
            Device Settings
          </CardTitle>
          <CardDescription>
            Configure device fingerprinting and analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="enable_fingerprinting">Enable Device Fingerprinting</Label>
              <p className="text-sm text-muted-foreground">
                Use device fingerprints for fraud detection
              </p>
            </div>
            <Switch
              id="enable_fingerprinting"
              checked={settings.device_settings.enable_fingerprinting}
              onCheckedChange={(checked) => handleSettingChange('device_settings.enable_fingerprinting', checked)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="enable_user_agent_analysis">Enable User Agent Analysis</Label>
              <p className="text-sm text-muted-foreground">
                Analyze user agents for suspicious patterns
              </p>
            </div>
            <Switch
              id="enable_user_agent_analysis"
              checked={settings.device_settings.enable_user_agent_analysis}
              onCheckedChange={(checked) => handleSettingChange('device_settings.enable_user_agent_analysis', checked)}
            />
          </div>
          
          <div>
            <Label htmlFor="suspicious_patterns">Suspicious User Agent Patterns</Label>
            <Textarea
              id="suspicious_patterns"
              value={settings.device_settings.suspicious_patterns.join(', ')}
              onChange={(e) => handleSettingChange('device_settings.suspicious_patterns', e.target.value.split(', ').filter(p => p.trim()))}
              placeholder="bot, crawler, spider, scraper"
              rows={3}
            />
            <p className="text-sm text-muted-foreground mt-1">
              Comma-separated list of patterns to flag
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Clock className="h-5 w-5 mr-2" />
            Notification Settings
          </CardTitle>
          <CardDescription>
            Configure alerts and notifications
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="email_alerts">Email Alerts</Label>
              <p className="text-sm text-muted-foreground">
                Send email notifications for high-risk events
              </p>
            </div>
            <Switch
              id="email_alerts"
              checked={settings.notification_settings.email_alerts}
              onCheckedChange={(checked) => handleSettingChange('notification_settings.email_alerts', checked)}
            />
          </div>
          
          <div>
            <Label htmlFor="webhook_url">Webhook URL</Label>
            <Input
              id="webhook_url"
              type="url"
              value={settings.notification_settings.webhook_url}
              onChange={(e) => handleSettingChange('notification_settings.webhook_url', e.target.value)}
              placeholder="https://your-webhook-url.com/fraud-alerts"
            />
            <p className="text-sm text-muted-foreground mt-1">
              URL to send webhook notifications
            </p>
          </div>
          
          <div>
            <Label htmlFor="alert_threshold">Alert Threshold</Label>
            <Input
              id="alert_threshold"
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={settings.notification_settings.alert_threshold}
              onChange={(e) => handleSettingChange('notification_settings.alert_threshold', parseFloat(e.target.value))}
            />
            <p className="text-sm text-muted-foreground mt-1">
              Risk score threshold for sending alerts
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
