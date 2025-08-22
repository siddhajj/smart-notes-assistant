#!/bin/bash

# Build and Deploy Script for Notes App to Cloud Run
# This script builds Docker images and deploys all services to Cloud Run

set -e

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
REGION="${REGION:-us-central1}"
REGISTRY="gcr.io"

echo "🚀 Building and deploying Notes App to Cloud Run"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Set the project
gcloud config set project $PROJECT_ID

# Function to build and deploy a service
deploy_service() {
    local service_name=$1
    local service_path=$2
    local service_port=${3:-8000}
    local memory=${4:-512Mi}
    local cpu=${5:-1}
    
    echo "📦 Building $service_name..."
    
    # Build and push Docker image with proper context
    # Build from project root with service-specific Dockerfile
    gcloud builds submit \
        --tag $REGISTRY/$PROJECT_ID/$service_name \
        --file $service_path/Dockerfile \
        .
    
    echo "🚀 Deploying $service_name to Cloud Run..."
    
    # Deploy to Cloud Run
    gcloud run deploy $service_name \
        --image $REGISTRY/$PROJECT_ID/$service_name \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --port $service_port \
        --memory $memory \
        --cpu $cpu \
        --min-instances 0 \
        --max-instances 10 \
        --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,REGION=$REGION,INSTANCE_NAME=notes-app-db,DB_NAME=notesapp,DB_USER=notesapp_user \
        --service-account notes-app-sa@$PROJECT_ID.iam.gserviceaccount.com
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $service_name --platform managed --region $REGION --format "value(status.url)")
    echo "✅ $service_name deployed at: $SERVICE_URL"
    
    # Store URL as environment variable for other services
    export "${service_name^^}_URL"="$SERVICE_URL"
}

echo "🔨 Building all services..."

# Deploy User Service
deploy_service "user-service" "./apps/api/user-service" 8000 "512Mi" "1"

# Deploy Notes Service
deploy_service "notes-service" "./apps/api/notes-service" 8000 "512Mi" "1"

# Deploy Tasks Service  
deploy_service "tasks-service" "./apps/api/tasks-service" 8000 "512Mi" "1"

# Deploy AI Service with more resources
deploy_service "ai-service" "./apps/api/ai-service" 8000 "1Gi" "1"

echo "🔄 Updating AI service with service URLs..."

# Update AI service with other service URLs
gcloud run services update ai-service \
    --platform managed \
    --region $REGION \
    --set-env-vars NOTES_SERVICE_URL=$NOTES_SERVICE_URL,TASKS_SERVICE_URL=$TASKS_SERVICE_URL,USER_SERVICE_URL=$USER_SERVICE_URL

echo "🔄 Updating other services with AI service URL..."

# Update Notes service with AI service URL
gcloud run services update notes-service \
    --platform managed \
    --region $REGION \
    --set-env-vars AI_SERVICE_URL=$AI_SERVICE_URL

echo "✅ All services deployed successfully!"
echo ""
echo "📋 Service URLs:"
echo "User Service: $USER_SERVICE_URL"
echo "Notes Service: $NOTES_SERVICE_URL"  
echo "Tasks Service: $TASKS_SERVICE_URL"
echo "AI Service: $AI_SERVICE_URL"
echo ""
echo "🔗 Next steps:"
echo "1. Configure load balancer and custom domain"
echo "2. Set up monitoring and logging"
echo "3. Deploy frontend application"