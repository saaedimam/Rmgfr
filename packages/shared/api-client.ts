/**
 * Unified API client for Anti-Fraud Platform
 * Bridges web and mobile apps with backend using shared types
 */

import { 
  EventCreate, 
  EventResponse, 
  EventProcessingResult,
  EventListResponse,
  EventStats,
  DecisionAction,
  ApiClientConfig,
  ApiRequestOptions,
  ApiResponse,
  PaginationParams,
  EventFilters
} from './api-types';

export class ApiClient {
  private baseUrl: string;
  private apiKey: string;
  private projectId: string;
  private defaultOptions: ApiRequestOptions;

  constructor(config: ApiClientConfig) {
    this.baseUrl = config.baseUrl;
    this.apiKey = config.apiKey;
    this.projectId = config.projectId;
    this.defaultOptions = {
      timeout: 10000,
      retries: 3,
      ...config
    };
  }

  /**
   * Make authenticated API request
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit & { timeout?: number } = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    const controller = new AbortController();
    
    // Set timeout
    const timeout = options.timeout || this.defaultOptions.timeout;
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': this.apiKey,
          'X-Project-ID': this.projectId,
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `API Error: ${response.status} ${response.statusText}`
        );
      }

      const data = await response.json();
      return {
        data,
        success: true,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      
      return {
        data: null as T,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Events API
   */
  async createEvent(eventData: EventCreate): Promise<ApiResponse<EventProcessingResult>> {
    return this.request<EventProcessingResult>('/v2/events/', {
      method: 'POST',
      body: JSON.stringify(eventData),
    });
  }

  async getEvent(eventId: string): Promise<ApiResponse<EventResponse>> {
    return this.request<EventResponse>(`/v2/events/${eventId}?project_id=${this.projectId}`);
  }

  async listEvents(
    params: PaginationParams & EventFilters = {}
  ): Promise<ApiResponse<EventListResponse>> {
    const searchParams = new URLSearchParams({
      project_id: this.projectId,
      page: String(params.page || 1),
      limit: String(params.limit || 100),
    });

    // Add optional filters
    if (params.event_type) searchParams.set('event_type', params.event_type);
    if (params.decision) searchParams.set('decision', params.decision);
    if (params.profile_id) searchParams.set('profile_id', params.profile_id);
    if (params.date_from) searchParams.set('date_from', params.date_from);
    if (params.date_to) searchParams.set('date_to', params.date_to);
    if (params.risk_score_min) searchParams.set('risk_score_min', String(params.risk_score_min));
    if (params.risk_score_max) searchParams.set('risk_score_max', String(params.risk_score_max));

    return this.request<EventListResponse>(`/v2/events/?${searchParams.toString()}`);
  }

  async getEventStats(hours: number = 24): Promise<ApiResponse<EventStats>> {
    return this.request<EventStats>(
      `/v2/events/stats/summary?project_id=${this.projectId}&hours=${hours}`
    );
  }

  /**
   * Health API
   */
  async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: string; version: string }>> {
    return this.request<{ status: string; timestamp: string; version: string }>('/health');
  }

  /**
   * Test event creation (for development)
   */
  async testEvent(eventType: string = 'test'): Promise<ApiResponse<EventProcessingResult>> {
    const testEvent: EventCreate = {
      event_type: eventType as any,
      event_data: {
        test: true,
        timestamp: new Date().toISOString(),
      },
      profile_id: 'test-user',
      session_id: 'test-session',
      device_fingerprint: 'test-device-123',
      ip_address: '127.0.0.1',
      user_agent: 'Test Client/1.0',
    };

    return this.createEvent(testEvent);
  }
}

/**
 * Factory for creating API clients
 */
export class ApiClientFactory {
  private static instances: Map<string, ApiClient> = new Map();

  static create(config: ApiClientConfig): ApiClient {
    const key = `${config.baseUrl}:${config.projectId}`;
    
    if (!this.instances.has(key)) {
      this.instances.set(key, new ApiClient(config));
    }
    
    return this.instances.get(key)!;
  }

  static getInstance(baseUrl: string, projectId: string): ApiClient | null {
    const key = `${baseUrl}:${projectId}`;
    return this.instances.get(key) || null;
  }

  static clearInstances(): void {
    this.instances.clear();
  }
}

/**
 * React hook for API client
 */
export function useApiClient(config: ApiClientConfig): ApiClient {
  return ApiClientFactory.create(config);
}

/**
 * Default configuration
 */
export const DEFAULT_API_CONFIG: Partial<ApiClientConfig> = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
  retries: 3,
};
