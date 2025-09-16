#!/usr/bin/env bash
# Quick start script for Anti-Fraud Platform

set -euo pipefail

echo "🚀 Anti-Fraud Platform Quick Start"
echo "=================================="

# Check if .cursorops-prime exists
if [ ! -f ".cursorops-prime" ]; then
    echo "❌ .cursorops-prime not found. Please run the setup first."
    exit 1
fi

# Make it executable
chmod +x .cursorops-prime

# Run the appropriate command
case "${1:-dev}" in
    "dev")
        echo "🛠️  Starting development environment..."
        ./scripts/dev.sh
        ;;
    "test")
        echo "🧪 Running tests..."
        ./scripts/test.sh
        ;;
    "deploy")
        echo "🚀 Deploying to production..."
        ./scripts/deploy.sh
        ;;
    "setup")
        echo "⚙️  Running full setup..."
        ./.cursorops-prime run all
        ;;
    *)
        echo "Usage: $0 {dev|test|deploy|setup}"
        ;;
esac
