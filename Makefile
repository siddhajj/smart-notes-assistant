# Notes App - Development Makefile
# Provides convenient commands for local development

.PHONY: help install dev-setup clean test lint format type-check
.PHONY: dev-user dev-notes dev-tasks dev-ai dev-search dev-web
.PHONY: build-user build-notes build-tasks build-ai build-search build-web
.PHONY: docker-up docker-down docker-logs
.PHONY: setup-pgvector check-pgvector

# Default target
help:
	@echo "Notes App - Available Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install      - Install project dependencies"
	@echo "  dev-setup    - Complete development environment setup"
	@echo "  clean        - Clean build artifacts and cache"
	@echo ""
	@echo "Development Commands (Local SQLite):"
	@echo "  dev-user     - Run user service (port 8003)"
	@echo "  dev-notes    - Run notes service (port 8000)"
	@echo "  dev-tasks    - Run tasks service (port 8002)"
	@echo "  dev-ai       - Run AI service (port 8001) - mock AI"
	@echo "  dev-search   - Run search service (port 8004)"
	@echo "  dev-web      - Run web frontend (port 3000)"
	@echo ""
	@echo "Development Commands (GCP Integration):"
	@echo "  setup-gcp-dev        - Setup local dev with GCP services"
	@echo "  check-gcp-dev        - Check GCP development setup"
	@echo "  start-cloud-sql-proxy - Start Cloud SQL Proxy"
	@echo "  dev-gcp-user         - Run user service with Cloud SQL"
	@echo "  dev-gcp-notes        - Run notes service with Cloud SQL + AI"
	@echo "  dev-gcp-tasks        - Run tasks service with Cloud SQL"
	@echo "  dev-gcp-ai           - Run AI service with REAL Vertex AI"
	@echo "  dev-gcp-search       - Run search service with Cloud SQL"
	@echo "  dev-gcp-web          - Run web frontend"
	@echo ""
	@echo "Quality Commands:"
	@echo "  test         - Run all tests"
	@echo "  test-watch   - Run tests in watch mode"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black + isort)"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  security     - Run security checks (bandit + safety)"
	@echo ""
	@echo "Database Commands:"
	@echo "  setup-pgvector   - Setup pgvector extension for PostgreSQL"
	@echo "  check-pgvector   - Check pgvector extension status"
	@echo ""
	@echo "Docker Commands:"
	@echo "  build-user   - Build user service Docker image"
	@echo "  build-notes  - Build notes service Docker image"
	@echo "  build-tasks  - Build tasks service Docker image"
	@echo "  build-ai     - Build AI service Docker image"
	@echo "  build-search - Build search service Docker image"
	@echo "  build-web    - Build web app Docker image"
	@echo "  docker-up    - Start all services with docker-compose"
	@echo "  docker-down  - Stop all services"
	@echo "  docker-logs  - View service logs"

# Setup Commands
install:
	pip install -e ".[api-common,user-service,notes-service,tasks-service,ai-service,web,dev]"

dev-setup:
	chmod +x scripts/setup-dev.sh
	./scripts/setup-dev.sh

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Development Services (Local SQLite)
dev-user:
	cd apps/api/user-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8003

dev-notes:
	cd apps/api/notes-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-tasks:
	cd apps/api/tasks-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

dev-ai:
	cd apps/api/ai-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

dev-search:
	cd apps/api/search-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8004

dev-web:
	cd apps/web && reflex run --env dev

# Development Services (GCP Integration)
# Note: Requires .env file with GCP configuration and Cloud SQL Proxy running
setup-gcp-dev:
	chmod +x scripts/setup-local-gcp.sh
	./scripts/setup-local-gcp.sh

check-gcp-dev:
	chmod +x scripts/check-gcp-dev.sh
	./scripts/check-gcp-dev.sh

start-cloud-sql-proxy:
	chmod +x scripts/start-cloud-sql-proxy.sh
	./scripts/start-cloud-sql-proxy.sh

dev-gcp-user:
	@echo "🚀 Starting User Service with GCP integration..."
	@echo "Ensure Cloud SQL Proxy is running: make start-cloud-sql-proxy"
	set -a && [ -f .env ] && . .env && set +a && cd apps/api/user-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8003

dev-gcp-notes:
	@echo "🚀 Starting Notes Service with GCP integration..."
	@echo "Ensure Cloud SQL Proxy is running: make start-cloud-sql-proxy"
	set -a && [ -f .env ] && . .env && set +a && cd apps/api/notes-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-gcp-tasks:
	@echo "🚀 Starting Tasks Service with GCP integration..."
	@echo "Ensure Cloud SQL Proxy is running: make start-cloud-sql-proxy"
	set -a && [ -f .env ] && . .env && set +a && cd apps/api/tasks-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

dev-gcp-ai:
	@echo "🚀 Starting AI Service with FULL Vertex AI integration..."
	@echo "This will use real Vertex AI - ensure you have proper GCP credentials"
	set -a && [ -f .env ] && . .env && set +a && cd apps/api/ai-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

dev-gcp-search:
	@echo "🚀 Starting Search Service with GCP integration..."
	@echo "Ensure Cloud SQL Proxy is running: make start-cloud-sql-proxy"
	set -a && [ -f .env ] && . .env && set +a && cd apps/api/search-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8004

dev-gcp-web:
	@echo "🚀 Starting Web Frontend..."
	set -a && [ -f .env ] && . .env && set +a && cd apps/web && reflex run --env dev

# Quality Commands
test:
	pytest tests/ -v --cov=apps --cov-report=term-missing

test-watch:
	pytest-watch -- tests/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

lint:
	flake8 apps/ tests/
	black --check apps/ tests/
	isort --check-only apps/ tests/

format:
	black apps/ tests/
	isort apps/ tests/

type-check:
	mypy apps/

security:
	bandit -r apps/
	safety check

# Database Commands
setup-pgvector:
	@echo "🔧 Setting up pgvector extension..."
	python scripts/setup-pgvector.py

check-pgvector:
	@echo "🔍 Checking pgvector extension status..."
	python scripts/setup-pgvector.py check

# Docker Build Commands
build-user:
	docker build -t notes-app/user-service -f apps/api/user-service/Dockerfile .

build-notes:
	docker build -t notes-app/notes-service -f apps/api/notes-service/Dockerfile .

build-tasks:
	docker build -t notes-app/tasks-service -f apps/api/tasks-service/Dockerfile .

build-ai:
	docker build -t notes-app/ai-service -f apps/api/ai-service/Dockerfile .

build-search:
	docker build -t notes-app/search-service -f apps/api/search-service/Dockerfile .

build-web:
	docker build -t notes-app/web -f apps/web/Dockerfile .

build-all: build-user build-notes build-tasks build-ai build-search build-web

# Docker Compose Commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

# Database Commands
db-init:
	python -m alembic upgrade head

db-migrate:
	python -m alembic revision --autogenerate -m "$(MSG)"

db-upgrade:
	python -m alembic upgrade head

db-downgrade:
	python -m alembic downgrade -1

# Deployment Commands
deploy-local:
	chmod +x scripts/build-and-deploy.sh
	./scripts/build-and-deploy.sh

deploy-gcp:
	chmod +x scripts/gcp-setup.sh
	./scripts/gcp-setup.sh
	chmod +x scripts/build-and-deploy.sh
	./scripts/build-and-deploy.sh

# Documentation
docs-build:
	mkdocs build

docs-serve:
	mkdocs serve

docs-deploy:
	mkdocs gh-deploy