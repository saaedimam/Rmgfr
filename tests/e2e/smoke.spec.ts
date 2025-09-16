import { test, expect } from '@playwright/test';

test.describe('Anti-Fraud Platform E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
  });

  test('should display home page with sign in/up buttons', async ({ page }) => {
    await expect(page).toHaveTitle(/Anti-Fraud Platform/);
    await expect(page.getByText('Anti-Fraud Platform')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign Up' })).toBeVisible();
  });

  test('should show features section', async ({ page }) => {
    await expect(page.getByText('Real-time Detection')).toBeVisible();
    await expect(page.getByText('Risk Assessment')).toBeVisible();
    await expect(page.getByText('Case Management')).toBeVisible();
  });

  test('should have working navigation', async ({ page }) => {
    // This test would require authentication setup
    // For now, just verify the page loads
    await expect(page).toHaveURL('http://localhost:3000/');
  });
});

test.describe('API Health Checks', () => {
  test('should return healthy status from API', async ({ request }) => {
    const response = await request.get('http://localhost:8000/health');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.version).toBe('1.0.0');
  });

  test('should return API root information', async ({ request }) => {
    const response = await request.get('http://localhost:8000/');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.message).toBe('Anti-Fraud Platform API');
    expect(data.version).toBe('1.0.0');
  });
});

test.describe('Events API', () => {
  test('should create event successfully', async ({ request }) => {
    const eventData = {
      event_type: 'checkout',
      event_data: { amount: 100.0, currency: 'USD' },
      profile_id: 'test_user_123',
      session_id: 'test_session_456'
    };

    const response = await request.post(
      'http://localhost:8000/v1/events/?project_id=test-project-123',
      { data: eventData }
    );

    expect(response.status()).toBe(201);
    
    const data = await response.json();
    expect(data.event_type).toBe('checkout');
    expect(data.profile_id).toBe('test_user_123');
    expect(data.session_id).toBe('test_session_456');
    expect(data.id).toBeDefined();
  });

  test('should list events', async ({ request }) => {
    const response = await request.get(
      'http://localhost:8000/v1/events/?project_id=test-project-123'
    );

    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.events).toBeDefined();
    expect(data.total).toBeDefined();
    expect(data.page).toBe(1);
    expect(data.limit).toBe(100);
  });
});

test.describe('Decisions API', () => {
  test('should create decision successfully', async ({ request }) => {
    const decisionData = {
      decision: 'allow',
      risk_score: 0.2,
      reasons: ['Low risk profile'],
      rules_fired: ['velocity_check']
    };

    const response = await request.post(
      'http://localhost:8000/v1/decisions/?project_id=test-project-123',
      { data: decisionData }
    );

    expect(response.status()).toBe(201);
    
    const data = await response.json();
    expect(data.decision).toBe('allow');
    expect(data.risk_score).toBe(0.2);
    expect(data.reasons).toEqual(['Low risk profile']);
    expect(data.id).toBeDefined();
  });

  test('should list decisions', async ({ request }) => {
    const response = await request.get(
      'http://localhost:8000/v1/decisions/?project_id=test-project-123'
    );

    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.decisions).toBeDefined();
    expect(data.total).toBeDefined();
    expect(data.page).toBe(1);
    expect(data.limit).toBe(100);
  });
});

test.describe('Cases API', () => {
  test('should list cases', async ({ request }) => {
    const response = await request.get(
      'http://localhost:8000/v1/cases/?project_id=test-project-123'
    );

    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.cases).toBeDefined();
    expect(data.total).toBeDefined();
    expect(data.page).toBe(1);
    expect(data.limit).toBe(100);
  });
});
