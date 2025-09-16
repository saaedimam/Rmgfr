.PHONY: help install dev test deploy clean

# Default target
help:
	@echo "Anti-Fraud Platform - Available commands:"
	@echo "  install     - Install all dependencies"
	@echo "  dev         - Start all services in development"
	@echo "  test        - Run all tests"
	@echo "  deploy      - Deploy all services"
	@echo "  clean       - Clean all build artifacts"

# Install dependencies
install:
	@echo "Installing dependencies..."
	cd web && npm install
	cd api && pip install -r requirements.txt
	cd mobile && npm install
	@echo "✓ All dependencies installed"

# Development
dev:
	@echo "Starting development servers..."
	@echo "Web: http://localhost:3000"
	@echo "API: http://localhost:8000"
	@echo "Mobile: Run 'cd mobile && npm start' in another terminal"
	@echo "Press Ctrl+C to stop all services"
	@trap 'kill %1 %2' INT; \
	cd web && npm run dev & \
	cd api && uvicorn src.main:app --reload --port 8000 &

# Testing
test:
	@echo "Running all tests..."
	cd web && npm run test
	cd api && pytest
	cd mobile && npm run test
	@echo "✓ All tests passed"

test-web:
	cd web && npm run test

test-api:
	cd api && pytest

test-mobile:
	cd mobile && npm run test

# Deployment
deploy:
	@echo "Deploying all services..."
	@echo "Web: Deploying to Vercel..."
	cd web && vercel --prod
	@echo "API: Deploying to Vercel..."
	cd api && vercel --prod
	@echo "Mobile: Building with EAS..."
	cd mobile && eas build --platform all
	@echo "✓ All services deployed"

deploy-web:
	cd web && vercel --prod

deploy-api:
	cd api && vercel --prod

deploy-mobile:
	cd mobile && eas build --platform all

# Database
db-setup:
	@echo "Setting up database..."
	@echo "Run: supabase db reset"
	@echo "Then: supabase db push"

db-migrate:
	@echo "Running migrations..."
	supabase db push

db-rollback:
	@echo "Rolling back database..."
	supabase db reset

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	cd web && rm -rf .next node_modules
	cd api && rm -rf __pycache__ .pytest_cache
	cd mobile && rm -rf node_modules .expo
	@echo "✓ Cleanup complete"

# Security
security-check:
	@echo "Running security checks..."
	cd web && npm audit
	cd api && safety check
	cd mobile && npm audit
	@echo "✓ Security checks complete"

# Format code
format:
	@echo "Formatting code..."
	cd web && npm run lint:fix
	cd api && black . && ruff --fix .
	cd mobile && npm run lint:fix
	@echo "✓ Code formatted"