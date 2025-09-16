#!/usr/bin/env bash
# Deploy Anti-Fraud Platform to Cursor Server

set -euo pipefail

echo "🚀 Deploying Anti-Fraud Platform to Cursor Server"
echo "================================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Not in project root directory"
    exit 1
fi

# Check dependencies
command -v pnpm >/dev/null || { echo "❌ pnpm not found. Install with: npm install -g pnpm"; exit 1; }
command -v python3 >/dev/null || { echo "❌ Python 3 not found"; exit 1; }

echo "📦 Installing dependencies..."

# Install all dependencies
pnpm install

# Install API dependencies
cd platform/api
pip install -r requirements.txt
cd ../..

# Install mobile dependencies
cd platform/mobile
pnpm install
cd ../..

echo "🔧 Building applications..."

# Build web app
echo "🌐 Building web application..."
cd web
pnpm run build
cd ..

# Build API (prepare for deployment)
echo "🚀 Preparing API for deployment..."
cd platform/api
# Create a simple deployment package
mkdir -p ../deploy
cp -r src ../deploy/
cp requirements.txt ../deploy/
cp *.py ../deploy/ 2>/dev/null || true
cd ../..

echo "📱 Preparing mobile app..."
cd platform/mobile
# Create build configuration
npx expo export --platform web
cd ../..

echo "🗄️  Setting up database..."
# Run database migrations if available
if [ -f "run_db_setup.sh" ]; then
    chmod +x run_db_setup.sh
    ./run_db_setup.sh
fi

echo "🔒 Setting up production environment..."

# Create production environment file
cat > .env.production << 'EOF'
# Production Environment Variables
NODE_ENV=production
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}
SECRET_KEY=${SECRET_KEY}
SENTRY_DSN=${SENTRY_DSN}
NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
NEXT_PUBLIC_APP_URL=${NEXT_PUBLIC_APP_URL}
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
CLERK_SECRET_KEY=${CLERK_SECRET_KEY}
EOF

echo "📋 Creating deployment manifest..."
cat > deploy-manifest.json << 'EOF'
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
EOF

echo "📦 Creating deployment package..."
# Create deployment archive
tar -czf antifraud-platform-deploy.tar.gz \
    web/.next \
    platform/api/src \
    platform/api/*.py \
    platform/api/requirements.txt \
    platform/mobile/dist \
    platform/infra/db \
    scripts \
    .env.production \
    deploy-manifest.json \
    package.json \
    pnpm-lock.yaml

echo "✅ Deployment package created: antifraud-platform-deploy.tar.gz"

echo "🌐 Starting services..."

# Start web server
echo "🌐 Starting web server on port 3000..."
cd web
pnpm start &
WEB_PID=$!
cd ..

# Start API server
echo "🚀 Starting API server on port 8000..."
cd platform/api
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
cd ../..

# Start mobile server
echo "📱 Starting mobile server on port 19006..."
cd platform/mobile
pnpm start &
MOBILE_PID=$!
cd ../..

echo "✅ All services started!"
echo ""
echo "🌐 Web App: http://localhost:3000"
echo "🚀 API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "📱 Mobile: http://localhost:19006"
echo ""
echo "📋 Health Checks:"
echo "  - Web: curl http://localhost:3000"
echo "  - API: curl http://localhost:8000/health"
echo "  - Mobile: curl http://localhost:19006"
echo ""
echo "🛑 To stop all services: kill $WEB_PID $API_PID $MOBILE_PID"

# Keep script running
wait
