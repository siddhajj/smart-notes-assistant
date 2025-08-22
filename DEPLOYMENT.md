# Smart Notes Assistant - GCP Deployment Guide

This guide provides step-by-step instructions to deploy the Smart Notes Assistant to Google Cloud Platform using Cloud Run, Cloud SQL, and Vertex AI.

## Prerequisites

1. **Google Cloud Platform Account** with billing enabled
2. **Google Cloud CLI** installed and configured
3. **Domain** (optional, for custom domain setup)
4. **GitHub repository** with the code

## Quick Start

### 1. Environment Setup

```bash
# Set your project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"
export REGION="us-central1"

# Authenticate with GCP
gcloud auth login
gcloud config set project $GOOGLE_CLOUD_PROJECT
```

### 2. Infrastructure Setup

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run infrastructure setup
./scripts/gcp-setup.sh
```

This script will:
- Enable required GCP APIs
- Create Cloud SQL PostgreSQL instance
- Set up service accounts and IAM permissions
- Configure Secret Manager
- Store database credentials securely

### 3. Deploy Services

```bash
# Deploy all microservices to Cloud Run
./scripts/build-and-deploy.sh
```

This will build and deploy:
- User Service (Authentication)
- Notes Service (Notes CRUD + AI integration)
- Tasks Service (Task management)
- AI Service (Vertex AI + Gemini integration)

### 4. Configure Load Balancer (Optional)

```bash
# Set up Application Load Balancer with SSL
export DOMAIN="your-domain.com"
./scripts/setup-load-balancer.sh
```

### 5. Set up Monitoring

```bash
# Configure monitoring, logging, and alerting
export ADMIN_EMAIL="admin@your-domain.com"
./scripts/setup-monitoring.sh
```

## Detailed Configuration

### Environment Variables

Set these in GitHub Actions secrets for CI/CD:

| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_ID` | Your Google Cloud Project ID |
| `GCP_SA_KEY` | Service account key JSON |

### Required GCP APIs

The setup script enables these APIs automatically:
- Cloud SQL Admin API
- Cloud Run API
- Container Registry API
- Vertex AI API
- Secret Manager API
- Cloud Build API

### Service Architecture

```
┌─────────────────┐    ┌──────────────────┐
│   Load Balancer │────│    Cloud Run     │
│   (HTTPS/SSL)   │    │   Microservices  │
└─────────────────┘    └──────────────────┘
                                │
                       ┌─────────────────┐
                       │   Cloud SQL     │
                       │  (PostgreSQL)   │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Vertex AI     │
                       │  (Gemini API)   │
                       └─────────────────┘
```

### Service Endpoints

After deployment, services will be available at:

- **User Service**: `https://user-service-[hash]-[region].a.run.app`
- **Notes Service**: `https://notes-service-[hash]-[region].a.run.app`
- **Tasks Service**: `https://tasks-service-[hash]-[region].a.run.app`
- **AI Service**: `https://ai-service-[hash]-[region].a.run.app`

### Database Configuration

All services connect to a shared Cloud SQL PostgreSQL instance:
- **Instance**: `notes-app-db`
- **Database**: `notesapp` 
- **Connection**: Via Cloud SQL Python Connector
- **Authentication**: Service account with Cloud SQL Client role

### AI Integration

The AI service uses Vertex AI with:
- **Model**: Gemini 1.5 Flash
- **Capabilities**: 
  - Intelligent title generation for notes
  - Natural language query processing
  - Structured data extraction from user queries

## CI/CD Pipeline

### GitHub Actions Workflow

The pipeline (`.github/workflows/gcp-deploy.yaml`) automatically:

1. **Test**: Run unit tests on PR/push
2. **Build**: Create Docker images for each service
3. **Deploy**: Deploy to Cloud Run with proper configuration
4. **Update**: Configure inter-service communication URLs

### Manual Deployment

For manual deployment without CI/CD:

```bash
# Build and deploy individual services
gcloud builds submit --tag gcr.io/$PROJECT_ID/user-service ./apps/api/user-service
gcloud run deploy user-service --image gcr.io/$PROJECT_ID/user-service --platform managed --region $REGION

# Repeat for other services...
```

## Monitoring and Logging

### Cloud Monitoring

- **Custom Metrics**: Notes created, tasks created, AI requests
- **System Metrics**: CPU, memory, request latency, error rates
- **Alerts**: High error rate, high latency, resource exhaustion

### Error Reporting

- Automatic error collection from all services
- Stack trace analysis
- Error grouping and notification

### Logging

- Centralized logging in Cloud Logging
- Structured logs with JSON format
- Log-based metrics for business KPIs

## Security

### Authentication & Authorization

- JWT-based authentication
- Service account authentication for GCP services
- Secret Manager for credential storage

### Network Security

- HTTPS-only communication
- Private service-to-service communication
- Cloud SQL private IP (optional)

### Data Protection

- Encrypted data at rest (Cloud SQL)
- Encrypted data in transit (TLS)
- Secret rotation via Secret Manager

## Scaling Configuration

### Auto-scaling Settings

| Service | Min Instances | Max Instances | Memory | CPU |
|---------|---------------|---------------|---------|-----|
| User Service | 0 | 10 | 512Mi | 1 |
| Notes Service | 0 | 10 | 512Mi | 1 |
| Tasks Service | 0 | 10 | 512Mi | 1 |
| AI Service | 0 | 5 | 1Gi | 2 |

### Database Scaling

- **Development**: db-f1-micro (shared CPU, 0.6GB RAM)
- **Production**: db-n1-standard-1 (1 vCPU, 3.75GB RAM)
- **High Availability**: Enable regional persistent disks

## Cost Optimization

### Cloud Run

- **Cold starts**: Minimized with optimized containers
- **Concurrency**: 80 requests per instance
- **Timeout**: 300s (600s for AI service)

### Cloud SQL

- **Automatic scaling**: Enable for variable workloads
- **Backups**: Automated daily backups with 7-day retention
- **Maintenance**: Automated during low-traffic windows

### Vertex AI

- **Model selection**: Gemini 1.5 Flash for cost efficiency
- **Request optimization**: Batch requests when possible
- **Caching**: Implement response caching for common queries

## Troubleshooting

### Common Issues

1. **Service Communication Errors**
   ```bash
   # Check service URLs are correctly configured
   gcloud run services list --platform managed --region $REGION
   ```

2. **Database Connection Issues**
   ```bash
   # Verify Cloud SQL instance status
   gcloud sql instances describe notes-app-db
   ```

3. **AI Service Errors**
   ```bash
   # Check Vertex AI API is enabled and service account has permissions
   gcloud services list --enabled | grep aiplatform
   ```

### Logs and Debugging

```bash
# View service logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=user-service" --limit 50

# Check service health
curl -f https://[service-url]/
```

## Production Checklist

- [ ] Set strong JWT secret in Secret Manager
- [ ] Configure custom domain with SSL certificate
- [ ] Set up monitoring alerts with appropriate thresholds
- [ ] Enable audit logging for compliance
- [ ] Configure backup and disaster recovery
- [ ] Set up staging environment for testing
- [ ] Document incident response procedures
- [ ] Configure rate limiting and DDoS protection

## Support

For issues or questions:
1. Check the monitoring dashboard for service health
2. Review application logs in Cloud Logging
3. Consult the error reporting dashboard
4. Check this documentation for troubleshooting steps

## Next Steps

1. **Frontend Deployment**: Deploy the Reflex web application
2. **Custom Domain**: Configure your domain with the load balancer
3. **Enhanced Monitoring**: Set up custom dashboards and SLIs
4. **Performance Testing**: Load test the application
5. **Security Audit**: Review and enhance security configurations