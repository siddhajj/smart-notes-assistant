#!/bin/bash

# Setup Application Load Balancer for Notes App
# This script creates a load balancer with SSL termination and routes traffic to Cloud Run services

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
REGION="${REGION:-us-central1}"
DOMAIN="${DOMAIN:-your-domain.com}"

echo "🌐 Setting up Application Load Balancer for Notes App"
echo "Project ID: $PROJECT_ID"
echo "Domain: $DOMAIN"

# Set the project
gcloud config set project $PROJECT_ID

# Create a global external IP address
echo "🌍 Creating global external IP address..."
gcloud compute addresses create notes-app-ip --global --quiet || echo "IP address already exists"

# Get the IP address
EXTERNAL_IP=$(gcloud compute addresses describe notes-app-ip --global --format="value(address)")
echo "External IP: $EXTERNAL_IP"

# Create SSL certificate (managed)
echo "🔒 Creating managed SSL certificate..."
gcloud compute ssl-certificates create notes-app-ssl \
    --domains=$DOMAIN \
    --global \
    --quiet || echo "SSL certificate already exists"

# Create URL map with backend services
echo "🗺️ Creating URL map..."

# First, we need to create backend services for each Cloud Run service
echo "📡 Creating backend services..."

# Get Cloud Run service URLs
USER_SERVICE_URL=$(gcloud run services describe user-service --platform managed --region $REGION --format "value(status.url)" | sed 's|https://||')
NOTES_SERVICE_URL=$(gcloud run services describe notes-service --platform managed --region $REGION --format "value(status.url)" | sed 's|https://||')
TASKS_SERVICE_URL=$(gcloud run services describe tasks-service --platform managed --region $REGION --format "value(status.url)" | sed 's|https://||')
AI_SERVICE_URL=$(gcloud run services describe ai-service --platform managed --region $REGION --format "value(status.url)" | sed 's|https://||')

# Create Network Endpoint Groups for Cloud Run services
gcloud compute network-endpoint-groups create user-service-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=user-service \
    --quiet || echo "user-service NEG already exists"

gcloud compute network-endpoint-groups create notes-service-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=notes-service \
    --quiet || echo "notes-service NEG already exists"

gcloud compute network-endpoint-groups create tasks-service-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=tasks-service \
    --quiet || echo "tasks-service NEG already exists"

gcloud compute network-endpoint-groups create ai-service-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=ai-service \
    --quiet || echo "ai-service NEG already exists"

# Create backend services
gcloud compute backend-services create user-service-backend \
    --global \
    --load-balancing-scheme=EXTERNAL \
    --protocol=HTTPS \
    --quiet || echo "user-service backend already exists"

gcloud compute backend-services create notes-service-backend \
    --global \
    --load-balancing-scheme=EXTERNAL \
    --protocol=HTTPS \
    --quiet || echo "notes-service backend already exists"

gcloud compute backend-services create tasks-service-backend \
    --global \
    --load-balancing-scheme=EXTERNAL \
    --protocol=HTTPS \
    --quiet || echo "tasks-service backend already exists"

gcloud compute backend-services create ai-service-backend \
    --global \
    --load-balancing-scheme=EXTERNAL \
    --protocol=HTTPS \
    --quiet || echo "ai-service backend already exists"

# Add NEGs to backend services
gcloud compute backend-services add-backend user-service-backend \
    --global \
    --network-endpoint-group=user-service-neg \
    --network-endpoint-group-region=$REGION \
    --quiet || echo "user-service backend already configured"

gcloud compute backend-services add-backend notes-service-backend \
    --global \
    --network-endpoint-group=notes-service-neg \
    --network-endpoint-group-region=$REGION \
    --quiet || echo "notes-service backend already configured"

gcloud compute backend-services add-backend tasks-service-backend \
    --global \
    --network-endpoint-group=tasks-service-neg \
    --network-endpoint-group-region=$REGION \
    --quiet || echo "tasks-service backend already configured"

gcloud compute backend-services add-backend ai-service-backend \
    --global \
    --network-endpoint-group=ai-service-neg \
    --network-endpoint-group-region=$REGION \
    --quiet || echo "ai-service backend already configured"

# Create URL map
gcloud compute url-maps create notes-app-url-map \
    --default-service=notes-service-backend \
    --global \
    --quiet || echo "URL map already exists"

# Add path matchers
gcloud compute url-maps add-path-matcher notes-app-url-map \
    --path-matcher-name=api-matcher \
    --default-service=notes-service-backend \
    --path-rules="/api/users/*=user-service-backend,/api/notes/*=notes-service-backend,/api/tasks/*=tasks-service-backend,/api/ai/*=ai-service-backend" \
    --global \
    --quiet || echo "Path matcher already exists"

# Create target HTTPS proxy
gcloud compute target-https-proxies create notes-app-https-proxy \
    --ssl-certificates=notes-app-ssl \
    --url-map=notes-app-url-map \
    --global \
    --quiet || echo "HTTPS proxy already exists"

# Create forwarding rule
gcloud compute forwarding-rules create notes-app-https-forwarding-rule \
    --address=notes-app-ip \
    --global \
    --target-https-proxy=notes-app-https-proxy \
    --ports=443 \
    --quiet || echo "Forwarding rule already exists"

# Create HTTP to HTTPS redirect
gcloud compute url-maps create notes-app-redirect-map \
    --global \
    --quiet || echo "Redirect map already exists"

gcloud compute url-maps edit notes-app-redirect-map \
    --global <<EOF
defaultUrlRedirect:
  httpsRedirect: true
  redirectResponseCode: MOVED_PERMANENTLY_DEFAULT
name: notes-app-redirect-map
EOF

gcloud compute target-http-proxies create notes-app-http-proxy \
    --url-map=notes-app-redirect-map \
    --global \
    --quiet || echo "HTTP proxy already exists"

gcloud compute forwarding-rules create notes-app-http-forwarding-rule \
    --address=notes-app-ip \
    --global \
    --target-http-proxy=notes-app-http-proxy \
    --ports=80 \
    --quiet || echo "HTTP forwarding rule already exists"

echo "✅ Load balancer setup complete!"
echo ""
echo "📋 Configuration:"
echo "External IP: $EXTERNAL_IP"
echo "Domain: $DOMAIN"
echo "SSL Certificate: notes-app-ssl"
echo ""
echo "🔗 API Endpoints:"
echo "Users API: https://$DOMAIN/api/users/"
echo "Notes API: https://$DOMAIN/api/notes/"
echo "Tasks API: https://$DOMAIN/api/tasks/"
echo "AI API: https://$DOMAIN/api/ai/"
echo ""
echo "⚠️ Important:"
echo "1. Point your domain '$DOMAIN' to IP: $EXTERNAL_IP"
echo "2. SSL certificate provisioning may take 10-60 minutes"
echo "3. Test the endpoints after DNS propagation"