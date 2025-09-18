# Environment & Variables

## Required (server)
- `NODE_ENV` (`production` recommended)
- `DATABASE_URL` (Postgres)
- Optional: `REDIS_URL`, `SECRET_KEY`, `SENTRY_DSN`, `CLERK_SECRET_KEY`

## Public (sent to browser)
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_APP_URL`
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`

## Local Workflow
```bash
cp .env.example .env
# fill values
npm run env:check
```

## Push to Railway

```bash
# PowerShell
$env:RAILWAY_TOKEN="..."        # required for browserless CLI
$env:DATABASE_URL="postgres://..."
$env:NEXT_PUBLIC_APP_URL="https://your-app.up.railway.app"
npm run env:push
```

## Environment Variable Reference

### Core Variables
- **NODE_ENV**: Environment mode (`development`, `test`, `production`)
- **DATABASE_URL**: PostgreSQL connection string (required)
- **REDIS_URL**: Redis connection string (optional)
- **SECRET_KEY**: Application secret key (optional)
- **SENTRY_DSN**: Sentry error tracking DSN (optional)

### Public Variables (sent to browser)
- **NEXT_PUBLIC_API_URL**: API base URL for client-side requests
- **NEXT_PUBLIC_APP_URL**: Application base URL
- **NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY**: Clerk authentication public key

### Server-only Variables
- **CLERK_SECRET_KEY**: Clerk authentication secret key

### Legacy Variables (for backward compatibility)
- **API_BASE**: Legacy API base URL
- **PROJECT_API_KEY**: Project API key
- **ADMIN_TOKEN**: Admin authentication token

## Validation

The application uses Zod for runtime environment variable validation. If required variables are missing or invalid, the application will exit with clear error messages.

## Railway Deployment

Environment variables are automatically validated on startup. Use the provided scripts to manage variables:

```bash
# Check local environment
npm run env:check

# Push variables to Railway
npm run env:push
```

## Security Notes

- Never commit `.env` files to version control
- Use `.env.example` as a template
- Public variables (NEXT_PUBLIC_*) are exposed to the browser
- Server-only variables are kept secure on the server
