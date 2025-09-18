# Railway Setup Guide

## Prereqs
- Node 18+
- Railway CLI (auto-installed by our scripts if missing)
- **Environment variables**:
  - `RAILWAY_TOKEN` (required)
  - `DATABASE_URL` (optional but recommended for DB bootstrap)
  - `SERVICE` and/or `PROJECT` (optional hints for multi-service apps)

## Recommended (Web UI)
1. Go to https://railway.app and sign in.
2. Create/Select your project.
3. Add `DATABASE_URL` in Variables.
4. Connect repo or deploy from the web.
5. Once your service URL is visible, run:
   ```bash
   BASE_URL="https://<your-app>.up.railway.app" npm run verify:deployment
   ```

## Automated (CLI)

```bash
# macOS/Linux
export RAILWAY_TOKEN=...    # required
export DATABASE_URL=...     # optional, enables DB bootstrap
export SERVICE=api          # optional
npm run deploy:railway

# Windows (PowerShell)
$env:RAILWAY_TOKEN="..."
$env:DATABASE_URL="..."
$env:SERVICE="api"
npm run deploy:railway
```

### Database bootstrap

If `DATABASE_URL` is present **and** `psql` is installed, the deploy scripts will run `platform/railway-db-setup.sql` automatically.

### Verify deployment

```bash
BASE_URL="https://<your-app>.up.railway.app" npm run verify:deployment
# or with custom endpoints:
ENDPOINTS_JSON='["/health","/metrics","/api/ping"]' BASE_URL="..." npm run verify:deployment
```