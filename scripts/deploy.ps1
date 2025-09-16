# Deploy Anti-Fraud Platform to Cursor Server
# PowerShell version for Windows

Write-Host "🚀 Deploying Anti-Fraud Platform to Cursor Server" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Not in project root directory" -ForegroundColor Red
    exit 1
}

# Check dependencies
try {
    pnpm --version | Out-Null
    Write-Host "✅ pnpm found" -ForegroundColor Green
} catch {
    Write-Host "❌ pnpm not found. Install with: npm install -g pnpm" -ForegroundColor Red
    exit 1
}

try {
    python --version | Out-Null
    Write-Host "✅ Python found" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow

# Install all dependencies
pnpm install

# Install API dependencies
Set-Location platform/api
pip install -r requirements.txt
Set-Location ../..

# Install mobile dependencies
Set-Location platform/mobile
pnpm install
Set-Location ../..

Write-Host "🔧 Building applications..." -ForegroundColor Yellow

# Build web app
Write-Host "🌐 Building web application..." -ForegroundColor Cyan
Set-Location web
pnpm run build
Set-Location ..

# Prepare API for deployment
Write-Host "🚀 Preparing API for deployment..." -ForegroundColor Cyan
if (-not (Test-Path "platform/deploy")) {
    New-Item -ItemType Directory -Path "platform/deploy" -Force
}
Copy-Item -Path "platform/api/src" -Destination "platform/deploy/" -Recurse -Force
Copy-Item -Path "platform/api/requirements.txt" -Destination "platform/deploy/" -Force
Copy-Item -Path "platform/api/*.py" -Destination "platform/deploy/" -Force

# Prepare mobile app
Write-Host "📱 Preparing mobile app..." -ForegroundColor Cyan
Set-Location platform/mobile
npx expo export --platform web
Set-Location ../..

Write-Host "🗄️  Setting up database..." -ForegroundColor Yellow
# Run database setup if available
if (Test-Path "run_db_setup.sh") {
    bash run_db_setup.sh
}

Write-Host "🔒 Setting up production environment..." -ForegroundColor Yellow

# Create production environment file
@"
# Production Environment Variables
NODE_ENV=production
DATABASE_URL=`${DATABASE_URL}
REDIS_URL=`${REDIS_URL}
SECRET_KEY=`${SECRET_KEY}
SENTRY_DSN=`${SENTRY_DSN}
NEXT_PUBLIC_API_URL=`${NEXT_PUBLIC_API_URL}
NEXT_PUBLIC_APP_URL=`${NEXT_PUBLIC_APP_URL}
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=`${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
CLERK_SECRET_KEY=`${CLERK_SECRET_KEY}
"@ | Out-File -FilePath ".env.production" -Encoding UTF8

Write-Host "📋 Creating deployment manifest..." -ForegroundColor Yellow
@"
{
  "name": "antifraud-platform",
  "version": "1.0.0",
  "description": "Anti-Fraud Platform - Comprehensive fraud detection and prevention",
  "type": "fullstack",
  "components": {
    "web": {
      "type": "nextjs",
      "build_dir": "web/.next",
      "start_command": "cd web && pnpm start",
      "port": 3000
    },
    "api": {
      "type": "fastapi",
      "build_dir": "platform/api",
      "start_command": "cd platform/api && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000",
      "port": 8000
    },
    "mobile": {
      "type": "expo",
      "build_dir": "platform/mobile/dist",
      "start_command": "cd platform/mobile && pnpm start",
      "port": 19006
    }
  },
  "database": {
    "type": "postgresql",
    "migrations": "platform/infra/db"
  },
  "monitoring": {
    "sentry": true,
    "health_checks": ["/health", "/api/health"]
  }
}
"@ | Out-File -FilePath "deploy-manifest.json" -Encoding UTF8

Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow
# Create deployment archive
Compress-Archive -Path @(
    "web/.next",
    "platform/deploy",
    "platform/mobile/dist",
    "platform/infra/db",
    "scripts",
    ".env.production",
    "deploy-manifest.json",
    "package.json",
    "pnpm-lock.yaml"
) -DestinationPath "antifraud-platform-deploy.zip" -Force

Write-Host "✅ Deployment package created: antifraud-platform-deploy.zip" -ForegroundColor Green

Write-Host "🌐 Starting services..." -ForegroundColor Yellow

# Start web server
Write-Host "🌐 Starting web server on port 3000..." -ForegroundColor Cyan
Set-Location web
Start-Process -NoNewWindow -FilePath "pnpm" -ArgumentList "start"
Set-Location ..

# Start API server
Write-Host "🚀 Starting API server on port 8000..." -ForegroundColor Cyan
Set-Location platform/api
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"
Set-Location ../..

# Start mobile server
Write-Host "📱 Starting mobile server on port 19006..." -ForegroundColor Cyan
Set-Location platform/mobile
Start-Process -NoNewWindow -FilePath "pnpm" -ArgumentList "start"
Set-Location ../..

Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Web App: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🚀 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "📱 Mobile: http://localhost:19006" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Health Checks:" -ForegroundColor Yellow
Write-Host "  - Web: curl http://localhost:3000" -ForegroundColor White
Write-Host "  - API: curl http://localhost:8000/health" -ForegroundColor White
Write-Host "  - Mobile: curl http://localhost:19006" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Deployment complete! Your Anti-Fraud Platform is now running on Cursor server." -ForegroundColor Green
