#!/bin/bash

# Cloud SQL Proxy Setup Script
# Allows local services to connect to Cloud SQL securely

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
REGION="${REGION:-us-central1}"
INSTANCE_NAME="${INSTANCE_NAME:-notes-app-db}"
LOCAL_PORT="${LOCAL_PORT:-5432}"

echo "🔗 Starting Cloud SQL Proxy for local development"
echo "Project: $PROJECT_ID"
echo "Instance: $INSTANCE_NAME"
echo "Local Port: $LOCAL_PORT"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI is not installed"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "❌ Not authenticated with Google Cloud"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Check if Cloud SQL Admin API is enabled
echo "🔍 Checking if Cloud SQL Admin API is enabled..."
if ! gcloud services list --enabled --filter="name:sqladmin.googleapis.com" --format="value(name)" | grep -q "sqladmin.googleapis.com"; then
    echo "⚠️ Cloud SQL Admin API is not enabled. Enabling it now..."
    gcloud services enable sqladmin.googleapis.com
    echo "✅ Cloud SQL Admin API enabled"
fi

# Check if instance exists
echo "🔍 Checking if Cloud SQL instance exists..."
if ! gcloud sql instances describe $INSTANCE_NAME --quiet &>/dev/null; then
    echo "❌ Cloud SQL instance '$INSTANCE_NAME' not found"
    echo "Please run the GCP setup script first: ./scripts/gcp-setup.sh"
    exit 1
fi

# Install Cloud SQL Proxy if not present
PROXY_PATH="./cloud-sql-proxy"
if [ ! -f "$PROXY_PATH" ]; then
    echo "📦 Downloading Cloud SQL Proxy..."
    
    # Detect OS and architecture
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    case $ARCH in
        x86_64) ARCH="amd64" ;;
        arm64|aarch64) ARCH="arm64" ;;
        *) echo "❌ Unsupported architecture: $ARCH"; exit 1 ;;
    esac
    
    case $OS in
        linux) OS="linux" ;;
        darwin) OS="darwin" ;;
        mingw*|msys*|cygwin*) OS="windows"; PROXY_PATH="./cloud-sql-proxy.exe" ;;
        *) echo "❌ Unsupported OS: $OS"; exit 1 ;;
    esac
    
    DOWNLOAD_URL="https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.7.0/cloud-sql-proxy.${OS}.${ARCH}"
    if [[ $OS == "windows" ]]; then
        DOWNLOAD_URL="${DOWNLOAD_URL}.exe"
    fi
    
    echo "📥 Downloading from: $DOWNLOAD_URL"
    curl -o "$PROXY_PATH" "$DOWNLOAD_URL"
    chmod +x "$PROXY_PATH"
    echo "✅ Cloud SQL Proxy downloaded"
fi

# Start the proxy
CONNECTION_NAME="$PROJECT_ID:$REGION:$INSTANCE_NAME"
echo "🚀 Starting Cloud SQL Proxy..."
echo "Connection: $CONNECTION_NAME"
echo "Local port: $LOCAL_PORT"
echo ""
echo "💡 Keep this terminal open while developing"
echo "💡 In another terminal, run: make dev-gcp"
echo "💡 To stop: Press Ctrl+C"
echo ""

# Run the proxy
$PROXY_PATH --port $LOCAL_PORT $CONNECTION_NAME

echo "🛑 Cloud SQL Proxy stopped"