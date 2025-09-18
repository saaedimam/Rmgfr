/**
 * Validation utilities for fraud settings
 * Extracted complex validation logic into pure functions
 */

import { FraudSettings } from '@/hooks/useFraudSettings';

export interface ValidationError {
  field: string;
  message: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

/**
 * Validates risk thresholds
 */
export function validateRiskThresholds(thresholds: FraudSettings['risk_thresholds']): ValidationError[] {
  const errors: ValidationError[] = [];

  // Guard clause: check if thresholds exist
  if (!thresholds) {
    return [{ field: 'risk_thresholds', message: 'Risk thresholds are required' }];
  }

  const { low, medium, high, critical } = thresholds;

  // Validate individual thresholds
  if (low < 0 || low > 1) {
    errors.push({ field: 'risk_thresholds.low', message: 'Low threshold must be between 0 and 1' });
  }

  if (medium < 0 || medium > 1) {
    errors.push({ field: 'risk_thresholds.medium', message: 'Medium threshold must be between 0 and 1' });
  }

  if (high < 0 || high > 1) {
    errors.push({ field: 'risk_thresholds.high', message: 'High threshold must be between 0 and 1' });
  }

  if (critical < 0 || critical > 1) {
    errors.push({ field: 'risk_thresholds.critical', message: 'Critical threshold must be between 0 and 1' });
  }

  // Validate threshold ordering
  if (low >= medium) {
    errors.push({ field: 'risk_thresholds', message: 'Low threshold must be less than medium threshold' });
  }

  if (medium >= high) {
    errors.push({ field: 'risk_thresholds', message: 'Medium threshold must be less than high threshold' });
  }

  if (high >= critical) {
    errors.push({ field: 'risk_thresholds', message: 'High threshold must be less than critical threshold' });
  }

  return errors;
}

/**
 * Validates velocity limits
 */
export function validateVelocityLimits(limits: FraudSettings['velocity_limits']): ValidationError[] {
  const errors: ValidationError[] = [];

  // Guard clause: check if limits exist
  if (!limits) {
    return [{ field: 'velocity_limits', message: 'Velocity limits are required' }];
  }

  const { max_events_per_minute, max_events_per_hour, max_events_per_day } = limits;

  // Validate individual limits
  if (max_events_per_minute <= 0) {
    errors.push({ field: 'velocity_limits.max_events_per_minute', message: 'Events per minute must be greater than 0' });
  }

  if (max_events_per_hour <= 0) {
    errors.push({ field: 'velocity_limits.max_events_per_hour', message: 'Events per hour must be greater than 0' });
  }

  if (max_events_per_day <= 0) {
    errors.push({ field: 'velocity_limits.max_events_per_day', message: 'Events per day must be greater than 0' });
  }

  // Validate logical relationships
  if (max_events_per_minute > max_events_per_hour) {
    errors.push({ field: 'velocity_limits', message: 'Events per minute cannot exceed events per hour' });
  }

  if (max_events_per_hour > max_events_per_day) {
    errors.push({ field: 'velocity_limits', message: 'Events per hour cannot exceed events per day' });
  }

  return errors;
}

/**
 * Validates payment settings
 */
export function validatePaymentSettings(payment: FraudSettings['payment_settings']): ValidationError[] {
  const errors: ValidationError[] = [];

  // Guard clause: check if payment settings exist
  if (!payment) {
    return [{ field: 'payment_settings', message: 'Payment settings are required' }];
  }

  const { max_amount, min_amount, suspicious_amounts } = payment;

  // Validate amount ranges
  if (min_amount < 0) {
    errors.push({ field: 'payment_settings.min_amount', message: 'Minimum amount cannot be negative' });
  }

  if (max_amount <= 0) {
    errors.push({ field: 'payment_settings.max_amount', message: 'Maximum amount must be greater than 0' });
  }

  if (min_amount >= max_amount) {
    errors.push({ field: 'payment_settings', message: 'Minimum amount must be less than maximum amount' });
  }

  // Validate suspicious amounts
  if (!Array.isArray(suspicious_amounts)) {
    errors.push({ field: 'payment_settings.suspicious_amounts', message: 'Suspicious amounts must be an array' });
  } else {
    const invalidAmounts = suspicious_amounts.filter(amount =>
      typeof amount !== 'number' || amount < 0 || amount > max_amount
    );

    if (invalidAmounts.length > 0) {
      errors.push({
        field: 'payment_settings.suspicious_amounts',
        message: 'All suspicious amounts must be valid numbers between 0 and max amount'
      });
    }
  }

  return errors;
}

/**
 * Validates notification settings
 */
export function validateNotificationSettings(notifications: FraudSettings['notification_settings']): ValidationError[] {
  const errors: ValidationError[] = [];

  // Guard clause: check if notification settings exist
  if (!notifications) {
    return [{ field: 'notification_settings', message: 'Notification settings are required' }];
  }

  const { alert_threshold, webhook_url } = notifications;

  // Validate alert threshold
  if (alert_threshold < 0 || alert_threshold > 1) {
    errors.push({ field: 'notification_settings.alert_threshold', message: 'Alert threshold must be between 0 and 1' });
  }

  // Validate webhook URL if provided
  if (webhook_url && webhook_url.trim() !== '') {
    try {
      new URL(webhook_url);
    } catch {
      errors.push({ field: 'notification_settings.webhook_url', message: 'Webhook URL must be a valid URL' });
    }
  }

  return errors;
}

/**
 * Validates all fraud settings
 */
export function validateFraudSettings(settings: FraudSettings): ValidationResult {
  const errors: ValidationError[] = [
    ...validateRiskThresholds(settings.risk_thresholds),
    ...validateVelocityLimits(settings.velocity_limits),
    ...validatePaymentSettings(settings.payment_settings),
    ...validateNotificationSettings(settings.notification_settings)
  ];

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Gets a human-readable error message for a field
 */
export function getFieldErrorMessage(field: string, errors: ValidationError[]): string | null {
  const fieldError = errors.find(error => error.field === field);
  return fieldError?.message || null;
}

/**
 * Checks if a specific field has validation errors
 */
export function hasFieldError(field: string, errors: ValidationError[]): boolean {
  return errors.some(error => error.field === field);
}
