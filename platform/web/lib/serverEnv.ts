// Runtime env validation. Import once at server boot.
// If variables are missing, the process will exit with a helpful error.

import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("production"),
  DATABASE_URL: z.string().min(1, "DATABASE_URL is required"),
  REDIS_URL: z.string().optional(),
  SECRET_KEY: z.string().optional(),
  SENTRY_DSN: z.string().optional(),

  // Public (sent to browser in Next.js or similar)
  NEXT_PUBLIC_API_URL: z.string().optional(),
  NEXT_PUBLIC_APP_URL: z.string().optional(),
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: z.string().optional(),

  // Server-side auth keys
  CLERK_SECRET_KEY: z.string().optional(),

  // Legacy mobile proxy vars
  API_BASE: z.string().optional(),
  PROJECT_API_KEY: z.string().optional(),
  ADMIN_TOKEN: z.string().optional(),
});

const parsed = EnvSchema.safeParse({
  NODE_ENV: process.env.NODE_ENV,
  DATABASE_URL: process.env.DATABASE_URL,
  REDIS_URL: process.env.REDIS_URL,
  SECRET_KEY: process.env.SECRET_KEY,
  SENTRY_DSN: process.env.SENTRY_DSN,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
  CLERK_SECRET_KEY: process.env.CLERK_SECRET_KEY,
  API_BASE: process.env.API_BASE,
  PROJECT_API_KEY: process.env.PROJECT_API_KEY,
  ADMIN_TOKEN: process.env.ADMIN_TOKEN,
});

if (!parsed.success) {
  // Pretty-print errors and exit
  console.error("❌ Invalid or missing environment variables:\n");
  for (const issue of parsed.error.issues) {
    console.error(`- ${issue.path.join(".")}: ${issue.message}`);
  }
  process.exit(1);
}

export const ENV = parsed.data;

// Legacy exports for backward compatibility
export const API_BASE = ENV.API_BASE || 'http://localhost:8000';
export const PROJECT_API_KEY = ENV.PROJECT_API_KEY || '';
export const ADMIN_TOKEN = ENV.ADMIN_TOKEN || '';
