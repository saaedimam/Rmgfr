#requires -Version 5.1
$ErrorActionPreference = "Stop"

function Fail($msg){ Write-Host "❌ $msg" -ForegroundColor Red; exit 1 }
function Step($msg){ Write-Host "`n==> $msg" -ForegroundColor Cyan }

if (-not $env:RAILWAY_TOKEN) { Fail "RAILWAY_TOKEN env var is required" }

# 1) Ensure Railway CLI
Step "Checking Railway CLI"
$railway = (Get-Command railway -ErrorAction SilentlyContinue)
if (-not $railway) {
  Write-Host "Installing @railway/cli locally (npx fallback) ..."
  npx -y @railway/cli --version | Out-Null
}

# 2) Login (browserless)
Step "Logging into Railway (token auth)"
# Prefer global cli; fallback to npx
if (Get-Command railway -ErrorAction SilentlyContinue) {
  $loginCmd = "railway"
} else {
  $loginCmd = "npx @railway/cli"
}
# Set token and login
$env:RAILWAY_TOKEN = $env:RAILWAY_TOKEN
cmd /c "$loginCmd login --browserless" | Out-Null

# 3) Set project/service (optional)
$service = $env:SERVICE
$project = $env:PROJECT

# 4) Push env vars if provided
if ($env:DATABASE_URL) {
  Step "Setting DATABASE_URL variable"
  cmd /c "$loginCmd variables --set DATABASE_URL=$env:DATABASE_URL" | Out-Null
}

# 5) Deploy
Step "Deploying to Railway"
if ($service) {
  cmd /c "$loginCmd up --service `"$service`"" | Out-Null
} else {
  cmd /c "$loginCmd up" | Out-Null
}

# 6) Optional DB bootstrap (psql must be available)
if ($env:DATABASE_URL -and (Test-Path "platform\railway-db-setup.sql")) {
  Step "Bootstrapping PostgreSQL schema"
  $pg = (Get-Command psql -ErrorAction SilentlyContinue)
  if ($pg) {
    $env:PGPASSWORD = "" # rely on DATABASE_URL
    psql "$env:DATABASE_URL" -f "platform/railway-db-setup.sql"
  } else {
    Write-Host "psql not found; skip DB bootstrap. Install PostgreSQL client to auto-run."
  }
}

Write-Host "`n✅ Railway deploy complete"
