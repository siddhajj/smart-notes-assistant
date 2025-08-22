#!/bin/bash

# GCP Setup Script for Notes App
# Run this script to set up all required GCP infrastructure

set -e

# Configuration - Update these values for your project
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
REGION="${REGION:-us-central1}"
DB_INSTANCE_NAME="${DB_INSTANCE_NAME:-notes-app-db}"
DB_NAME="${DB_NAME:-notesapp}"
DB_USER="${DB_USER:-notesapp_user}"
SERVICE_ACCOUNT_NAME="notes-app-sa"

echo "🚀 Setting up GCP infrastructure for Notes App"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Set the project
gcloud config set project $PROJECT_ID

echo "📋 Enabling required APIs..."
gcloud services enable \
  cloudsql-admin.googleapis.com \
  run.googleapis.com \
  container.googleapis.com \
  aiplatform.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  compute.googleapis.com

echo "🗄️ Creating Cloud SQL PostgreSQL instance..."
if ! gcloud sql instances describe $DB_INSTANCE_NAME --quiet 2>/dev/null; then
  gcloud sql instances create $DB_INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --cpu=1 \
    --memory=3840MB \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --authorized-networks=0.0.0.0/0
  
  echo "⏳ Waiting for Cloud SQL instance to be ready..."
  sleep 30
else
  echo "Cloud SQL instance $DB_INSTANCE_NAME already exists"
fi

echo "🔐 Creating database and user..."
if ! gcloud sql databases describe $DB_NAME --instance=$DB_INSTANCE_NAME --quiet 2>/dev/null; then
  gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE_NAME
fi

# Generate secure password
DB_PASSWORD=$(openssl rand -base64 32)

# Create or update user
gcloud sql users set-password $DB_USER \
  --instance=$DB_INSTANCE_NAME \
  --password="$DB_PASSWORD" \
  --quiet || \
gcloud sql users create $DB_USER \
  --instance=$DB_INSTANCE_NAME \
  --password="$DB_PASSWORD"

echo "👤 Creating service account..."
if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --quiet 2>/dev/null; then
  gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --description="Service account for Notes App" \
    --display-name="Notes App Service Account"
fi

echo "🔑 Granting IAM permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "🔒 Storing secrets in Secret Manager..."
# Store database password
echo -n "$DB_PASSWORD" | gcloud secrets create db-password --data-file=- --quiet || \
echo -n "$DB_PASSWORD" | gcloud secrets versions add db-password --data-file=-

# Store JWT secret
JWT_SECRET=$(openssl rand -base64 64)
echo -n "$JWT_SECRET" | gcloud secrets create jwt-secret --data-file=- --quiet || \
echo -n "$JWT_SECRET" | gcloud secrets versions add jwt-secret --data-file=-

# Get connection string
CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE_NAME --format="value(connectionName)")
DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@/$DB_NAME?host=/cloudsql/$CONNECTION_NAME"

# Store database URL
echo -n "$DATABASE_URL" | gcloud secrets create database-url --data-file=- --quiet || \
echo -n "$DATABASE_URL" | gcloud secrets versions add database-url --data-file=-

echo "✅ GCP Infrastructure setup complete!"
echo ""
echo "📝 Important information:"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Database Instance: $DB_INSTANCE_NAME"
echo "Database Name: $DB_NAME"
echo "Database User: $DB_USER"
echo "Connection Name: $CONNECTION_NAME"
echo ""
echo "🔐 Secrets stored in Secret Manager:"
echo "- db-password: Database password"
echo "- jwt-secret: JWT signing secret"
echo "- database-url: Complete database connection string"
echo ""
echo "🚀 Next steps:"
echo "1. Update your environment variables"
echo "2. Deploy services to Cloud Run"
echo "3. Configure networking"