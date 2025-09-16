# Anti-Fraud Platform API Makefile

.PHONY: help install dev test lint format clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Start development server
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	pytest tests/ -v

lint: ## Run linter
	black --check src/
	isort --check-only src/
	mypy src/

format: ## Format code
	black src/
	isort src/

clean: ## Clean up
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
