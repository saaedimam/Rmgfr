/**
 * Unified configuration management
 * Bridges environment variables across web, mobile, and API
 */

import { z } from 'zod';

// Base configuration schema
const BaseConfigSchema = z.object({
  // API Configuration
  apiUrl: z.string().url().default('http://localhost:8000'),
  apiKey: z.string().min(1),
  projectId: z.string().min(1),
  
  // Environment
  environment: z.enum(['development', 'staging', 'production']).default('development'),
  
  // Features
  features: z.object({
    enableAnalytics: z.boolean().default(true),
    enableNotifications: z.boolean().default(true),
    enableDebugMode: z.boolean().default(false),
  }).default({}),
  
  // Security
  security: z.object({
    enableCSP: z.boolean().default(true),
    enableHSTS: z.boolean().default(true),
    maxRequestSize: z.number().default(1024 * 1024), // 1MB
  }).default({}),
});

// Web-specific configuration
const WebConfigSchema = BaseConfigSchema.extend({
  // Clerk Authentication
  clerkPublishableKey: z.string().optional(),
  clerkSecretKey: z.string().optional(),
  
  // Next.js specific
  nextPublicApiUrl: z.string().url().optional(),
  nextPublicAppUrl: z.string().url().optional(),
  
  // Sentry
  sentryDsn: z.string().url().optional(),
});

// Mobile-specific configuration
const MobileConfigSchema = BaseConfigSchema.extend({
  // Expo
  expoPublicApiUrl: z.string().url().optional(),
  
  // Push Notifications
  expoPushToken: z.string().optional(),
  
  // Device
  deviceId: z.string().optional(),
});

// API-specific configuration
const ApiConfigSchema = BaseConfigSchema.extend({
  // Database
  databaseUrl: z.string().url(),
  redisUrl: z.string().url().optional(),
  
  // Authentication
  jwtSecret: z.string().min(32),
  
  // External Services
  sentryDsn: z.string().url().optional(),
  
  // Rate Limiting
  rateLimit: z.object({
    windowMs: z.number().default(15 * 60 * 1000), // 15 minutes
    maxRequests: z.number().default(100),
  }).default({}),
});

export type BaseConfig = z.infer<typeof BaseConfigSchema>;
export type WebConfig = z.infer<typeof WebConfigSchema>;
export type MobileConfig = z.infer<typeof MobileConfigSchema>;
export type ApiConfig = z.infer<typeof ApiConfigSchema>;

/**
 * Configuration manager with environment-specific loading
 */
export class ConfigManager {
  private static instance: ConfigManager;
  private config: BaseConfig;

  private constructor() {
    this.config = this.loadConfig();
  }

  static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  private loadConfig(): BaseConfig {
    const env = process.env.NODE_ENV || 'development';
    
    // Load environment-specific configuration
    const config = {
      apiUrl: process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      apiKey: process.env.API_KEY || process.env.NEXT_PUBLIC_API_KEY || 'dev-key',
      projectId: process.env.PROJECT_ID || process.env.NEXT_PUBLIC_PROJECT_ID || 'dev-project',
      environment: env,
      features: {
        enableAnalytics: process.env.ENABLE_ANALYTICS !== 'false',
        enableNotifications: process.env.ENABLE_NOTIFICATIONS !== 'false',
        enableDebugMode: env === 'development',
      },
      security: {
        enableCSP: process.env.ENABLE_CSP !== 'false',
        enableHSTS: process.env.ENABLE_HSTS !== 'false',
        maxRequestSize: parseInt(process.env.MAX_REQUEST_SIZE || '1048576'),
      },
    };

    try {
      return BaseConfigSchema.parse(config);
    } catch (error) {
      console.error('Configuration validation failed:', error);
      throw new Error('Invalid configuration');
    }
  }

  getConfig(): BaseConfig {
    return { ...this.config };
  }

  get<K extends keyof BaseConfig>(key: K): BaseConfig[K] {
    return this.config[key];
  }

  isDevelopment(): boolean {
    return this.config.environment === 'development';
  }

  isProduction(): boolean {
    return this.config.environment === 'production';
  }

  isFeatureEnabled(feature: keyof BaseConfig['features']): boolean {
    return this.config.features[feature];
  }
}

/**
 * Web-specific configuration loader
 */
export class WebConfigManager extends ConfigManager {
  private webConfig: WebConfig;

  constructor() {
    super();
    this.webConfig = this.loadWebConfig();
  }

  private loadWebConfig(): WebConfig {
    const baseConfig = this.getConfig();
    
    const webConfig = {
      ...baseConfig,
      clerkPublishableKey: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
      clerkSecretKey: process.env.CLERK_SECRET_KEY,
      nextPublicApiUrl: process.env.NEXT_PUBLIC_API_URL,
      nextPublicAppUrl: process.env.NEXT_PUBLIC_APP_URL,
      sentryDsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
    };

    try {
      return WebConfigSchema.parse(webConfig);
    } catch (error) {
      console.error('Web configuration validation failed:', error);
      throw new Error('Invalid web configuration');
    }
  }

  getWebConfig(): WebConfig {
    return { ...this.webConfig };
  }
}

/**
 * Mobile-specific configuration loader
 */
export class MobileConfigManager extends ConfigManager {
  private mobileConfig: MobileConfig;

  constructor() {
    super();
    this.mobileConfig = this.loadMobileConfig();
  }

  private loadMobileConfig(): MobileConfig {
    const baseConfig = this.getConfig();
    
    const mobileConfig = {
      ...baseConfig,
      expoPublicApiUrl: process.env.EXPO_PUBLIC_API_URL,
      expoPushToken: process.env.EXPO_PUSH_TOKEN,
      deviceId: process.env.EXPO_DEVICE_ID,
    };

    try {
      return MobileConfigSchema.parse(mobileConfig);
    } catch (error) {
      console.error('Mobile configuration validation failed:', error);
      throw new Error('Invalid mobile configuration');
    }
  }

  getMobileConfig(): MobileConfig {
    return { ...this.mobileConfig };
  }
}

/**
 * API-specific configuration loader
 */
export class ApiConfigManager extends ConfigManager {
  private apiConfig: ApiConfig;

  constructor() {
    super();
    this.apiConfig = this.loadApiConfig();
  }

  private loadApiConfig(): ApiConfig {
    const baseConfig = this.getConfig();
    
    const apiConfig = {
      ...baseConfig,
      databaseUrl: process.env.DATABASE_URL || process.env.SUPABASE_DB_URL || '',
      redisUrl: process.env.REDIS_URL,
      jwtSecret: process.env.JWT_SECRET || process.env.SECRET_KEY || '',
      sentryDsn: process.env.SENTRY_DSN,
      rateLimit: {
        windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000'),
        maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100'),
      },
    };

    try {
      return ApiConfigSchema.parse(apiConfig);
    } catch (error) {
      console.error('API configuration validation failed:', error);
      throw new Error('Invalid API configuration');
    }
  }

  getApiConfig(): ApiConfig {
    return { ...this.apiConfig };
  }
}

/**
 * Environment-specific configuration factory
 */
export function createConfigManager(platform: 'web' | 'mobile' | 'api'): ConfigManager {
  switch (platform) {
    case 'web':
      return new WebConfigManager();
    case 'mobile':
      return new MobileConfigManager();
    case 'api':
      return new ApiConfigManager();
    default:
      return new ConfigManager();
  }
}

/**
 * Configuration validation utilities
 */
export class ConfigValidator {
  static validateEnvironment(requiredVars: string[]): void {
    const missing = requiredVars.filter(varName => !process.env[varName]);
    
    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
  }

  static validateUrl(url: string, name: string): void {
    try {
      new URL(url);
    } catch {
      throw new Error(`Invalid ${name} URL: ${url}`);
    }
  }

  static validateApiKey(apiKey: string): void {
    if (!apiKey || apiKey.length < 8) {
      throw new Error('API key must be at least 8 characters long');
    }
  }
}

// Export default instances
export const config = ConfigManager.getInstance();
export const webConfig = new WebConfigManager();
export const mobileConfig = new MobileConfigManager();
export const apiConfig = new ApiConfigManager();
