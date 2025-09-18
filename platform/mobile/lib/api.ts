/**
 * API client for Anti-Fraud Mobile app
 */

import {
  EventResponse,
  DecisionAction,
  EventCreate,
  ApiClientConfig,
  ApiRequestOptions
} from '@antifraud/shared';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

// Re-export shared types for convenience
export type Event = EventResponse;
export type EventCreateData = EventCreate;
export type Decision = DecisionAction;

export interface Case {
  id: string;
  decision_id: string;
  status: 'open' | 'reviewed' | 'closed';
  assigned_to?: string;
  resolution?: 'approved' | 'rejected' | 'escalated';
  notes?: string;
  created_at: string;
  updated_at: string;
}

class ApiClient {
  private baseUrl: string;
  private projectId: string;

  constructor(projectId: string) {
    this.baseUrl = API_BASE_URL;
    this.projectId = projectId;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Events API
  async createEvent(eventData: EventCreateData): Promise<Event> {
    return this.request<Event>(`/v1/events/?project_id=${this.projectId}`, {
      method: 'POST',
      body: JSON.stringify(eventData),
    });
  }

  async getEvents(page = 1, limit = 100, eventType?: string): Promise<{
    events: Event[];
    total: number;
    page: number;
    limit: number;
  }> {
    const params = new URLSearchParams({
      project_id: this.projectId,
      page: page.toString(),
      limit: limit.toString(),
      ...(eventType && { event_type: eventType }),
    });

    return this.request(`/v1/events/?${params}`);
  }

  // Decisions API
  async createDecision(decisionData: Omit<Decision, 'id' | 'created_at'>): Promise<Decision> {
    return this.request<Decision>(`/v1/decisions/?project_id=${this.projectId}`, {
      method: 'POST',
      body: JSON.stringify(decisionData),
    });
  }

  async getDecisions(page = 1, limit = 100, decision?: string): Promise<{
    decisions: Decision[];
    total: number;
    page: number;
    limit: number;
  }> {
    const params = new URLSearchParams({
      project_id: this.projectId,
      page: page.toString(),
      limit: limit.toString(),
      ...(decision && { decision }),
    });

    return this.request(`/v1/decisions/?${params}`);
  }

  // Cases API
  async getCases(page = 1, limit = 100, status?: string): Promise<{
    cases: Case[];
    total: number;
    page: number;
    limit: number;
  }> {
    const params = new URLSearchParams({
      project_id: this.projectId,
      page: page.toString(),
      limit: limit.toString(),
      ...(status && { status }),
    });

    return this.request(`/v1/cases/?${params}`);
  }

  async updateCase(caseId: string, updates: Partial<Case>): Promise<Case> {
    return this.request<Case>(`/v1/cases/${caseId}?project_id=${this.projectId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request('/health');
  }
}

export const createApiClient = (projectId: string) => new ApiClient(projectId);
