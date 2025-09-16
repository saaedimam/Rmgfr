#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting Anti-Fraud Platform Development Environment"

# Check dependencies
command -v pnpm >/dev/null || { echo "❌ pnpm not found. Install with: npm install -g pnpm"; exit 1; }
command -v python3 >/dev/null || { echo "❌ Python 3 not found"; exit 1; }

# Install dependencies
echo "📦 Installing dependencies..."
pnpm install
cd platform/api && pip install -r requirements.txt && cd ../..
cd platform/mobile && pnpm install && cd ../..

# Start services
echo "🌐 Starting web app..."
cd web && pnpm dev &
WEB_PID=$!

echo "🚀 Starting API server..."
cd platform/api && python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "📱 Starting mobile app..."
cd platform/mobile && pnpm start &
MOBILE_PID=$!

echo "✅ All services started!"
echo "🌐 Web: http://localhost:3000"
echo "🚀 API: http://localhost:8000"
echo "📱 Mobile: Check terminal for Expo QR code"

# Cleanup function
cleanup() {
    echo "🛑 Shutting down services..."
    kill $WEB_PID $API_PID $MOBILE_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for services
wait
