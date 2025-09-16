#!/usr/bin/env bash
set -euo pipefail

echo "🧪 Running Anti-Fraud Platform Tests"

# API tests
echo "🔬 Running API tests..."
cd platform/api && python -m pytest tests/ -v --cov=src

# E2E tests
echo "🎭 Running E2E tests..."
cd ../.. && npx playwright test

# Mobile tests
echo "📱 Running mobile tests..."
cd platform/mobile && pnpm test

echo "✅ All tests completed!"
