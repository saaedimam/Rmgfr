/**
 * Custom hook for fraud settings management
 * Extracted from complex settings page component
 */

import { useState, useCallback } from 'react';

export interface FraudSettings {
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

const DEFAULT_SETTINGS: FraudSettings = {
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
};

export interface UseFraudSettingsReturn {
  settings: FraudSettings;
  loading: boolean;
  saving: boolean;
  error: string | null;
  success: string | null;
  handleSettingChange: (path: string, value: any) => void;
  handleSave: () => Promise<void>;
  handleReset: () => void;
  clearMessages: () => void;
}

export function useFraudSettings(): UseFraudSettingsReturn {
  const [settings, setSettings] = useState<FraudSettings>(DEFAULT_SETTINGS);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  const handleSettingChange = useCallback((path: string, value: any) => {
    setSettings(prev => {
      const newSettings = { ...prev };
      const keys = path.split('.');
      let current = newSettings;

      // Navigate to the nested property
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) {
          current[keys[i]] = {};
        }
        current = current[keys[i]];
      }

      // Set the final value
      current[keys[keys.length - 1]] = value;
      return newSettings;
    });
  }, []);

  const handleSave = useCallback(async () => {
    if (saving) return; // Guard clause: prevent double saves

    setSaving(true);
    clearMessages();

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
  }, [saving, clearMessages]);

  const handleReset = useCallback(() => {
    if (saving) return; // Guard clause: prevent reset while saving

    setSettings({ ...DEFAULT_SETTINGS });
    clearMessages();
  }, [saving, clearMessages]);

  return {
    settings,
    loading,
    saving,
    error,
    success,
    handleSettingChange,
    handleSave,
    handleReset,
    clearMessages
  };
}
