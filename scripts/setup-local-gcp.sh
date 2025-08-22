#!/bin/bash

# Setup Local Development with GCP Services
# This script configures your local environment to connect to GCP services

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT}"
SERVICE_ACCOUNT_NAME="notes-app-sa"

echo "🔧 Setting up local development with GCP services"

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo "❌ GOOGLE_CLOUD_PROJECT environment variable not set"
    echo "Please set it with your GCP project ID:"
    echo "export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

echo "Project ID: $PROJECT_ID"

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI is not installed"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "❌ Not authenticated with Google Cloud"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Setup Application Default Credentials
echo "🔐 Setting up Application Default Credentials..."
gcloud auth application-default login

# Download service account key for local development
echo "🔑 Setting up service account key..."
SA_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe $SA_EMAIL --quiet &>/dev/null; then
    echo "📥 Downloading service account key..."
    gcloud iam service-accounts keys create ./gcp-service-account.json \
        --iam-account=$SA_EMAIL \
        --quiet || echo "⚠️ Key might already exist or you may not have permission"
    
    if [ -f "./gcp-service-account.json" ]; then
        echo "✅ Service account key saved to ./gcp-service-account.json"
        chmod 600 ./gcp-service-account.json
    fi
else
    echo "⚠️ Service account not found. Please run ./scripts/gcp-setup.sh first"
fi

# Copy environment template
echo "📝 Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.local-gcp .env
    echo "✅ Created .env file from template"
    echo "⚠️ Please update .env with your specific configuration"
else
    echo "⚠️ .env file already exists. You may want to merge settings from .env.local-gcp"
fi

# Update .env with project ID
if [ -f ".env" ]; then
    # Replace placeholder with actual project ID
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-project-id/$PROJECT_ID/g" .env
    else
        # Linux
        sed -i "s/your-project-id/$PROJECT_ID/g" .env
    fi
    echo "✅ Updated .env with project ID: $PROJECT_ID"
fi

# Get database password from Secret Manager
echo "🔒 Retrieving database password from Secret Manager..."
if gcloud secrets describe db-password --quiet &>/dev/null; then
    DB_PASSWORD=$(gcloud secrets versions access latest --secret="db-password" --format="value(payload.data)" | base64 --decode)
    
    # Update .env with database password
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-password/$DB_PASSWORD/g" .env
    else
        # Linux
        sed -i "s/your-password/$DB_PASSWORD/g" .env
    fi
    echo "✅ Database password retrieved and added to .env"
else
    echo "⚠️ Database password secret not found. You may need to run ./scripts/gcp-setup.sh first"
fi

# Get Cloud SQL instance IP
echo "🗄️ Getting Cloud SQL instance information..."
if gcloud sql instances describe notes-app-db --quiet &>/dev/null; then
    INSTANCE_IP=$(gcloud sql instances describe notes-app-db --format="value(ipAddresses[0].ipAddress)")
    echo "Cloud SQL Instance IP: $INSTANCE_IP"
    
    # Update .env with instance IP
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-cloud-sql-ip/$INSTANCE_IP/g" .env
    else
        # Linux
        sed -i "s/your-cloud-sql-ip/$INSTANCE_IP/g" .env
    fi
    echo "✅ Cloud SQL IP added to .env"
else
    echo "⚠️ Cloud SQL instance not found. Please run ./scripts/gcp-setup.sh first"
fi

# Make scripts executable
chmod +x scripts/*.sh

echo "✅ Local GCP development setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Review and update .env file with any custom settings"
echo "2. Start Cloud SQL Proxy: ./scripts/start-cloud-sql-proxy.sh"
echo "3. In another terminal, start services: make dev-gcp"
echo ""
echo "📋 Available development commands:"
echo "  make dev-gcp        - Start all services with GCP connectivity"
echo "  make dev-gcp-user   - Start user service with GCP"
echo "  make dev-gcp-notes  - Start notes service with GCP"
echo "  make dev-gcp-tasks  - Start tasks service with GCP"
echo "  make dev-gcp-ai     - Start AI service with GCP (full Vertex AI)"
echo "  make dev-gcp-web    - Start web frontend"
echo ""
echo "🔗 Service URLs:"
echo "  Web Interface: http://localhost:3000"
echo "  Notes API: http://localhost:8000/docs"
echo "  AI Service: http://localhost:8001/docs"