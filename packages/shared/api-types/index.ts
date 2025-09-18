/**
 * Generated TypeScript types from OpenAPI specification
 * Source: Anti-Fraud Platform API v1.0.0
 * Generated: 2025-01-19
 */

// Base types
export interface ErrorResponse {
  error: string;
  detail: string;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  database?: Record<string, any> | null;
}

// Event types
export type EventType = 'login' | 'signup' | 'checkout' | 'payment' | 'custom';

export interface EventCreate {
  event_type: EventType;
  event_data?: Record<string, any>;
  profile_id?: string | null;
  session_id?: string | null;
  device_fingerprint?: string | null;
  ip_address?: string | null;
  user_agent?: string | null;
  amount?: number | null;
  currency?: string | null;
}

export interface EventResponse {
  id: string;
  event_type: string;
  event_data: Record<string, any>;
  profile_id?: string | null;
  session_id?: string | null;
  device_fingerprint?: string | null;
  ip_address?: string | null;
  user_agent?: string | null;
  amount?: number | null;
  currency?: string | null;
  risk_score?: number | null;
  decision?: string | null;
  created_at: string;
}

export interface EventProcessingResult {
  event_id: string;
  risk_score: number;
  decision: string;
  reasons: string[];
  rules_fired: string[];
  processing_time_ms: number;
}

export interface EventListResponse {
  events: EventResponse[];
  total: number;
  page: number;
  limit: number;
}

export interface EventStats {
  total_events: number;
  allowed_events: number;
  denied_events: number;
  review_events: number;
  avg_risk_score: number;
  max_risk_score: number;
  min_risk_score: number;
  time_period_hours: number;
}

// Decision types
export type DecisionAction = 'allow' | 'deny' | 'review' | 'step_up';

export interface DecisionContext {
  event_type: string;
  risk_score: number;
  customer_segment: string;
  latest_fpr: number;
}

export interface DecisionResult {
  action: DecisionAction;
  confidence: number;
  reasons: string[];
}

export interface DecisionMatrix {
  event_type: string;
  risk_band: string;
  customer_segment: string;
  action: DecisionAction;
  max_fpr: number;
  notes: string;
}

// Risk scoring types
export type RiskBand = 'low' | 'med' | 'high' | 'critical';

export interface RiskFactors {
  velocity: number;
  device_anomaly: number;
  geolocation: number;
  behavioral: number;
  payment_risk: number;
}

export interface RiskWeights {
  velocity: number;
  device_anomaly: number;
  geolocation: number;
  behavioral: number;
  payment_risk: number;
}

// API client types
export interface ApiClientConfig {
  baseUrl: string;
  apiKey: string;
  projectId: string;
}

export interface ApiRequestOptions {
  headers?: Record<string, string>;
  timeout?: number;
  retries?: number;
}

// Common response wrapper
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
  timestamp: string;
}

// Pagination types
export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// Filter types
export interface EventFilters {
  event_type?: EventType;
  decision?: DecisionAction;
  profile_id?: string;
  session_id?: string;
  date_from?: string;
  date_to?: string;
  risk_score_min?: number;
  risk_score_max?: number;
}

// Export all types as a namespace for better organization
export namespace ApiTypes {
  export type { ErrorResponse, HealthResponse };
  export type { EventType, EventCreate, EventResponse, EventProcessingResult, EventListResponse, EventStats };
  export type { DecisionAction, DecisionContext, DecisionResult, DecisionMatrix };
  export type { RiskBand, RiskFactors, RiskWeights };
  export type { ApiClientConfig, ApiRequestOptions, ApiResponse, PaginationParams, PaginatedResponse, EventFilters };
}
