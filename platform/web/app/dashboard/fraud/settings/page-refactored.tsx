'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import FraudNav from '@/components/FraudNav';
import {
  Settings,
  Save,
  RefreshCw,
  AlertTriangle,
  Shield,
  Activity,
  Clock,
  DollarSign,
  CheckCircle
} from 'lucide-react';

import { useFraudSettings } from '@/hooks/useFraudSettings';
import { validateFraudSettings, getFieldErrorMessage, hasFieldError } from '@/lib/settings-validation';

export default function SettingsPageRefactored() {
  const {
    settings,
    saving,
    error,
    success,
    handleSettingChange,
    handleSave,
    handleReset
  } = useFraudSettings();

  // Validate settings
  const validation = validateFraudSettings(settings);

  // Guard clause: show error if validation fails
  if (!validation.isValid) {
    return (
      <div className="space-y-6">
        <FraudNav />
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Settings validation failed. Please fix the following errors:
            <ul className="mt-2 list-disc list-inside">
              {validation.errors.map((error, index) => (
                <li key={index}>{error.field}: {error.message}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
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
      <GeneralSettingsCard
        settings={settings}
        onSettingChange={handleSettingChange}
        validation={validation}
      />

      {/* Risk Thresholds */}
      <RiskThresholdsCard
        settings={settings}
        onSettingChange={handleSettingChange}
        validation={validation}
      />

      {/* Velocity Limits */}
      <VelocityLimitsCard
        settings={settings}
        onSettingChange={handleSettingChange}
        validation={validation}
      />

      {/* Payment Settings */}
      <PaymentSettingsCard
        settings={settings}
        onSettingChange={handleSettingChange}
        validation={validation}
      />

      {/* Notification Settings */}
      <NotificationSettingsCard
        settings={settings}
        onSettingChange={handleSettingChange}
        validation={validation}
      />
    </div>
  );
}

// Extracted component for general settings
function GeneralSettingsCard({
  settings,
  onSettingChange,
  validation
}: {
  settings: any;
  onSettingChange: (path: string, value: any) => void;
  validation: any;
}) {
  return (
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
            onCheckedChange={(checked) => onSettingChange('enabled', checked)}
          />
        </div>
      </CardContent>
    </Card>
  );
}

// Extracted component for risk thresholds
function RiskThresholdsCard({
  settings,
  onSettingChange,
  validation
}: {
  settings: any;
  onSettingChange: (path: string, value: any) => void;
  validation: any;
}) {
  return (
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
              onChange={(e) => onSettingChange('risk_thresholds.low', parseFloat(e.target.value))}
              className={hasFieldError('risk_thresholds.low', validation.errors) ? 'border-red-500' : ''}
            />
            {getFieldErrorMessage('risk_thresholds.low', validation.errors) && (
              <p className="text-sm text-red-500 mt-1">
                {getFieldErrorMessage('risk_thresholds.low', validation.errors)}
              </p>
            )}
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
              onChange={(e) => onSettingChange('risk_thresholds.medium', parseFloat(e.target.value))}
              className={hasFieldError('risk_thresholds.medium', validation.errors) ? 'border-red-500' : ''}
            />
            {getFieldErrorMessage('risk_thresholds.medium', validation.errors) && (
              <p className="text-sm text-red-500 mt-1">
                {getFieldErrorMessage('risk_thresholds.medium', validation.errors)}
              </p>
            )}
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
              onChange={(e) => onSettingChange('risk_thresholds.high', parseFloat(e.target.value))}
              className={hasFieldError('risk_thresholds.high', validation.errors) ? 'border-red-500' : ''}
            />
            {getFieldErrorMessage('risk_thresholds.high', validation.errors) && (
              <p className="text-sm text-red-500 mt-1">
                {getFieldErrorMessage('risk_thresholds.high', validation.errors)}
              </p>
            )}
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
              onChange={(e) => onSettingChange('risk_thresholds.critical', parseFloat(e.target.value))}
              className={hasFieldError('risk_thresholds.critical', validation.errors) ? 'border-red-500' : ''}
            />
            {getFieldErrorMessage('risk_thresholds.critical', validation.errors) && (
              <p className="text-sm text-red-500 mt-1">
                {getFieldErrorMessage('risk_thresholds.critical', validation.errors)}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Extracted component for velocity limits
function VelocityLimitsCard({
  settings,
  onSettingChange,
  validation
}: {
  settings: any;
  onSettingChange: (path: string, value: any) => void;
  validation: any;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Activity className="h-5 w-5 mr-2" />
          Velocity Limits
        </CardTitle>
        <CardDescription>
          Configure maximum events per time period
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="events_per_minute">Events per Minute</Label>
            <Input
              id="events_per_minute"
              type="number"
              min="1"
              value={settings.velocity_limits.max_events_per_minute}
              onChange={(e) => onSettingChange('velocity_limits.max_events_per_minute', parseInt(e.target.value))}
              className={hasFieldError('velocity_limits.max_events_per_minute', validation.errors) ? 'border-red-500' : ''}
            />
            {getFieldErrorMessage('velocity_limits.max_events_per_minute', validation.errors) && (
              <p className="text-sm text-red-500 mt-1">
                {getFieldErrorMessage('velocity_limits.max_events_per_minute', validation.errors)}
              </p>
            )}
          </div>
          <div>
            <Label htmlFor="events_per_hour">Events per Hour</Label>
            <Input
              id="events_per_hour"
              type="number"
              min="1"
              value={settings.velocity_limits.max_events_per_hour}
              onChange={(e) => onSettingChange('velocity_limits.max_events_per_hour', parseInt(e.target.value))}
              className={hasFieldError('velocity_limits.max_events_per_hour', validation.errors) ? 'border-red-500' : ''}
            />
            {getFieldErrorMessage('velocity_limits.max_events_per_hour', validation.errors) && (
              <p className="text-sm text-red-500 mt-1">
                {getFieldErrorMessage('velocity_limits.max_events_per_hour', validation.errors)}
              </p>
            )}
          </div>
          <div>
            <Label htmlFor="events_per_day">Events per Day</Label>
            <Input
              id="events_per_day"
              type="number"
              min="1"
              value={settings.velocity_limits.max_events_per_day}
              onChange={(e) => onSettingChange('velocity_limits.max_events_per_day', parseInt(e.target.value))}
              className={hasFieldError('velocity_limits.max_events_per_day', validation.errors) ? 'border-red-500' : ''}
            />
            {getFieldErrorMessage('velocity_limits.max_events_per_day', validation.errors) && (
              <p className="text-sm text-red-500 mt-1">
                {getFieldErrorMessage('velocity_limits.max_events_per_day', validation.errors)}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Extracted component for payment settings
function PaymentSettingsCard({
  settings,
  onSettingChange,
  validation
}: {
  settings: any;
  onSettingChange: (path: string, value: any) => void;
  validation: any;
}) {
  return (
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
            <Label htmlFor="min_amount">Minimum Amount</Label>
            <Input
              id="min_amount"
              type="number"
              step="0.01"
              min="0"
              value={settings.payment_settings.min_amount}
              onChange={(e) => onSettingChange('payment_settings.min_amount', parseFloat(e.target.value))}
              className={hasFieldError('payment_settings.min_amount', validation.errors) ? 'border-red-500' : ''}
            />
            {getFieldErrorMessage('payment_settings.min_amount', validation.errors) && (
              <p className="text-sm text-red-500 mt-1">
                {getFieldErrorMessage('payment_settings.min_amount', validation.errors)}
              </p>
            )}
          </div>
          <div>
            <Label htmlFor="max_amount">Maximum Amount</Label>
            <Input
              id="max_amount"
              type="number"
              step="0.01"
              min="0"
              value={settings.payment_settings.max_amount}
              onChange={(e) => onSettingChange('payment_settings.max_amount', parseFloat(e.target.value))}
              className={hasFieldError('payment_settings.max_amount', validation.errors) ? 'border-red-500' : ''}
            />
            {getFieldErrorMessage('payment_settings.max_amount', validation.errors) && (
              <p className="text-sm text-red-500 mt-1">
                {getFieldErrorMessage('payment_settings.max_amount', validation.errors)}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Extracted component for notification settings
function NotificationSettingsCard({
  settings,
  onSettingChange,
  validation
}: {
  settings: any;
  onSettingChange: (path: string, value: any) => void;
  validation: any;
}) {
  return (
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
            onCheckedChange={(checked) => onSettingChange('notification_settings.email_alerts', checked)}
          />
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
            onChange={(e) => onSettingChange('notification_settings.alert_threshold', parseFloat(e.target.value))}
            className={hasFieldError('notification_settings.alert_threshold', validation.errors) ? 'border-red-500' : ''}
          />
          {getFieldErrorMessage('notification_settings.alert_threshold', validation.errors) && (
            <p className="text-sm text-red-500 mt-1">
              {getFieldErrorMessage('notification_settings.alert_threshold', validation.errors)}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
