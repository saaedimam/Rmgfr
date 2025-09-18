# Railway Deployment (Details)

- Cross-platform entry: `npm run deploy:railway` → runs `platform/deploy.js`
- Windows: `platform/railway-deploy.ps1`
- macOS/Linux: `platform/railway-deploy.sh`
- Env variables propagated to Railway via CLI:
  - `DATABASE_URL` (if present)
- Optional hints:
  - `SERVICE`, `PROJECT` for multi-service repos
- DB bootstrap uses `platform/railway-db-setup.sql` if `psql` is available.

**Troubleshooting**
- ❌ `Missing RAILWAY_TOKEN`: set it in your environment or CI.
- ❌ `psql not found`: install PostgreSQL client or skip DB bootstrap.
- ❌ Endpoint checks fail: confirm `BASE_URL` and service health route.