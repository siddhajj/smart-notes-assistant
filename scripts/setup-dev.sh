#!/bin/bash

# Development Environment Setup Script
# Sets up the Notes App for local development using pyproject.toml

set -e

echo "🚀 Setting up Notes App development environment"

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [[ $(echo "$python_version >= $required_version" | bc -l) -eq 0 ]]; then
    echo "❌ Python 3.11+ is required. Found: $python_version"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install the project in development mode
echo "📚 Installing project dependencies..."
pip install -e ".[api-common,user-service,notes-service,tasks-service,ai-service,web,dev]"

# Set up pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# Development Environment Variables
DATABASE_URL=sqlite:///./dev.db
JWT_SECRET_KEY=dev-secret-key-change-in-production
GOOGLE_CLOUD_PROJECT=your-dev-project-id
REGION=us-central1
INSTANCE_NAME=notes-app-db
DB_NAME=notesapp
DB_USER=notesapp_user

# AI Service URLs (for local development)
AI_SERVICE_URL=http://localhost:8001
NOTES_SERVICE_URL=http://localhost:8000/notes
TASKS_SERVICE_URL=http://localhost:8002/tasks
USER_SERVICE_URL=http://localhost:8003/users

# Development flags
DEBUG=true
DB_ECHO=false
LOG_LEVEL=INFO
EOF
    echo "✅ Created .env file with development defaults"
    echo "⚠️ Please update the values in .env for your specific setup"
else
    echo "✅ .env file already exists"
fi

# Create local database
echo "🗄️ Setting up local database..."
if [ ! -f "dev.db" ]; then
    echo "Creating SQLite database for development..."
    python3 -c "
from apps.api.user_service.app.database import init_user_db
from apps.api.notes_service.app.database import init_notes_db
from apps.api.tasks_service.app.database import init_tasks_db

try:
    init_user_db()
    init_notes_db()
    init_tasks_db()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'⚠️ Database initialization failed: {e}')
    print('You may need to initialize the database manually')
"
else
    echo "✅ Database already exists"
fi

echo "✅ Development environment setup complete!"
echo ""
echo "🔧 Available commands:"
echo "  make dev-user     - Run user service (port 8003)"
echo "  make dev-notes    - Run notes service (port 8000)"
echo "  make dev-tasks    - Run tasks service (port 8002)"
echo "  make dev-ai       - Run AI service (port 8001)"
echo "  make dev-web      - Run web frontend (port 3000)"
echo "  make test         - Run tests"
echo "  make lint         - Run code linting"
echo "  make format       - Format code"
echo ""
echo "🚀 To get started:"
echo "  1. Activate virtual environment: source .venv/bin/activate"
echo "  2. Update .env file with your configuration"
echo "  3. Run services: make dev-<service-name>"
echo "  4. Open http://localhost:3000 for the web interface"