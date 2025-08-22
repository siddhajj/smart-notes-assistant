# Local Development with GCP Services

This guide shows you how to run the Notes App locally while connecting to real Google Cloud Platform services like Cloud SQL and Vertex AI. This gives you the best of both worlds: fast local development with production-grade cloud services.

## 🎯 Why Use Local + GCP Development?

### Benefits
- **Fast Development**: Instant code reloads and debugging
- **Real AI Features**: Use actual Vertex AI instead of mocks
- **Production Database**: Test against real PostgreSQL with Cloud SQL
- **Cost Effective**: Only pay for cloud resources you use
- **Realistic Testing**: Catch integration issues early
- **Team Collaboration**: Share cloud resources across the team

### When to Use This Setup
- ✅ Developing AI features that need real LLM integration
- ✅ Testing database migrations and complex queries
- ✅ Debugging production issues locally
- ✅ Working with large datasets in Cloud SQL
- ✅ Validating GCP service integrations

### When to Use Pure Local Development
- ✅ Initial feature development and testing
- ✅ Working offline or with limited internet
- ✅ Quick prototyping and experimentation
- ✅ Running automated tests

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have:
- **GCP Project**: With billing enabled and APIs activated
- **GCP CLI**: Installed and authenticated (`gcloud auth login`)
- **Cloud Resources**: Already deployed via `./scripts/gcp-setup.sh`
- **Python Environment**: Set up with `make dev-setup`

### 2. One-Time Setup

```bash
# Set your GCP project
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Run the GCP development setup
make setup-gcp-dev
```

This script will:
- Configure Application Default Credentials
- Download service account keys
- Create `.env` file with GCP configuration
- Retrieve database passwords from Secret Manager
- Set up Cloud SQL connection details

### 3. Start Development

**Terminal 1** - Start Cloud SQL Proxy:
```bash
make start-cloud-sql-proxy
```
Keep this running - it creates a secure tunnel to Cloud SQL.

**Terminal 2** - Start your services:
```bash
# Option 1: Start individual services
make dev-gcp-notes  # Notes service with real AI
make dev-gcp-ai     # AI service with Vertex AI

# Option 2: Start all services (use multiple terminals)
make dev-gcp-user   # Terminal 3
make dev-gcp-tasks  # Terminal 4
make dev-gcp-web    # Terminal 5
```

### 4. Access Your App

- **Web Interface**: http://localhost:3000
- **Notes API**: http://localhost:8000/docs
- **AI Service**: http://localhost:8001/docs
- **User Service**: http://localhost:8003/docs
- **Tasks Service**: http://localhost:8002/docs

## 🔧 Configuration Details

### Environment Variables (.env)

Your `.env` file will contain:

```bash
# GCP Project Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./gcp-service-account.json

# Cloud SQL Configuration (via proxy)
DATABASE_URL=postgresql://notesapp_user:password@127.0.0.1:5432/notesapp
INSTANCE_NAME=notes-app-db
DB_NAME=notesapp
DB_USER=notesapp_user

# Vertex AI Configuration
VERTEX_AI_LOCATION=us-central1
MODEL_NAME=gemini-1.5-flash

# Local Service URLs
USER_SERVICE_URL=http://localhost:8003
NOTES_SERVICE_URL=http://localhost:8000/notes
TASKS_SERVICE_URL=http://localhost:8002/tasks
AI_SERVICE_URL=http://localhost:8001

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=local-gcp
```

### Cloud SQL Proxy

The Cloud SQL Proxy creates a secure connection to your Cloud SQL instance:

- **What it does**: Provides encrypted connection without opening firewall ports
- **How it works**: Creates a local socket that forwards to Cloud SQL
- **Security**: Uses IAM authentication, no IP allowlisting needed
- **Local address**: `127.0.0.1:5432` (standard PostgreSQL port)

### Service Account Authentication

For local development, you'll use:
- **Application Default Credentials**: For `gcloud` command authentication
- **Service Account Key**: JSON file for application authentication
- **IAM Permissions**: Same permissions as production deployment

## 🎯 Development Modes

### Mode 1: Hybrid Development (Recommended)

**What runs locally**: Your application code  
**What runs in GCP**: Database, AI services, monitoring

```bash
make dev-gcp-notes  # Local code + Cloud SQL + Vertex AI
```

**Benefits**:
- Fast code reloads
- Real AI responses
- Production database
- Realistic performance

### Mode 2: Full Local Development

**What runs locally**: Everything (SQLite, mock AI)

```bash
make dev-notes  # Local code + SQLite + mock AI
```

**Benefits**:
- Works offline
- Fast startup
- No cloud costs
- Simple debugging

### Mode 3: Full Cloud Development

**What runs in cloud**: Everything deployed to Cloud Run

```bash
./scripts/build-and-deploy.sh
```

**Benefits**:
- Production environment
- Team testing
- Performance testing
- Integration testing

## 🛠️ Common Development Tasks

### Connecting to Cloud SQL Directly

```bash
# Via Cloud SQL Proxy (recommended)
psql "postgresql://notesapp_user:password@127.0.0.1:5432/notesapp"

# Direct connection (requires firewall rules)
psql "postgresql://notesapp_user:password@CLOUD_SQL_IP:5432/notesapp"
```

### Testing AI Features

```bash
# Start AI service with real Vertex AI
make dev-gcp-ai

# Test title generation
curl -X POST http://localhost:8001/generate_title \
  -H "Content-Type: application/json" \
  -d '{"body": "Meeting notes from today about project planning"}'

# Test conversational AI
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "create a note about my vacation plans"}'
```

### Database Operations

```bash
# Run migrations
alembic upgrade head

# Check database connection
python -c "from apps.api.shared.database import engine; print(engine.connect())"

# View database logs
gcloud sql operations list --instance=notes-app-db
```

### Monitoring and Debugging

```bash
# View Cloud SQL connections
gcloud sql operations list --instance=notes-app-db --limit=10

# Check service account permissions
gcloud projects get-iam-policy $GOOGLE_CLOUD_PROJECT

# Monitor AI service usage
gcloud logging read "resource.type=aiplatform.googleapis.com/Model" --limit=10
```

## 🔍 Troubleshooting

### Cloud SQL Connection Issues

**Problem**: Can't connect to database
```bash
# Check proxy status
ps aux | grep cloud-sql-proxy

# Restart proxy
pkill cloud-sql-proxy
make start-cloud-sql-proxy
```

**Problem**: Authentication failed
```bash
# Refresh credentials
gcloud auth application-default login

# Check service account key
ls -la gcp-service-account.json
```

### Vertex AI Issues

**Problem**: AI service returns errors
```bash
# Check credentials
gcloud auth list

# Verify AI platform access
gcloud ai models list --region=us-central1

# Check quotas
gcloud compute project-info describe --project=$GOOGLE_CLOUD_PROJECT
```

### Environment Issues

**Problem**: Environment variables not loaded
```bash
# Check .env file exists
ls -la .env

# Manually load environment
set -a && source .env && set +a

# Verify variables
echo $GOOGLE_CLOUD_PROJECT
echo $DATABASE_URL
```

### Common Error Messages

| Error | Solution |
|-------|----------|
| `connection refused` | Start Cloud SQL Proxy |
| `permission denied` | Run `gcloud auth application-default login` |
| `instance not found` | Check instance name in .env |
| `quota exceeded` | Check GCP quotas and billing |
| `invalid credentials` | Regenerate service account key |

## 💰 Cost Management

### Estimated Costs (Daily Development)

| Service | Usage | Cost |
|---------|-------|------|
| Cloud SQL (db-f1-micro) | 8 hours active | ~$0.50 |
| Vertex AI (Gemini Flash) | 100 requests | ~$0.10 |
| Cloud Storage | Minimal | ~$0.01 |
| **Total** | **Full day development** | **~$0.61** |

### Cost Optimization Tips

1. **Use shared instances**: Team shares one Cloud SQL instance
2. **Stop when not developing**: Pause Cloud SQL during breaks
3. **Use efficient AI calls**: Cache AI responses locally
4. **Monitor usage**: Set up billing alerts

```bash
# Stop Cloud SQL instance (saves money)
gcloud sql instances patch notes-app-db --activation-policy=NEVER

# Start Cloud SQL instance
gcloud sql instances patch notes-app-db --activation-policy=ALWAYS
```

## 🚀 Advanced Configurations

### Custom Service Ports

Update `.env` file:
```bash
USER_SERVICE_PORT=8103
NOTES_SERVICE_PORT=8100
TASKS_SERVICE_PORT=8102
AI_SERVICE_PORT=8101
```

Then use custom commands:
```bash
cd apps/api/notes-service && uvicorn app.main:app --reload --port 8100
```

### Multiple Environments

Create environment-specific files:
- `.env.dev-gcp` - Development with GCP
- `.env.staging-gcp` - Staging environment
- `.env.local` - Pure local development

### Team Development

Share configurations:
```bash
# Team shared Cloud SQL instance
INSTANCE_NAME=team-notes-app-db

# Team shared GCP project
GOOGLE_CLOUD_PROJECT=team-notes-dev

# Individual developer databases
DB_NAME=notesapp_dev_alice
DB_NAME=notesapp_dev_bob
```

## 📋 Checklist

Before starting local GCP development:

- [ ] GCP project created and billing enabled
- [ ] Cloud SQL instance deployed (`./scripts/gcp-setup.sh`)
- [ ] Service account configured with proper permissions
- [ ] `gcloud` CLI installed and authenticated
- [ ] Application Default Credentials configured
- [ ] `.env` file created with GCP settings
- [ ] Cloud SQL Proxy downloaded and executable

During development:

- [ ] Cloud SQL Proxy running in background
- [ ] Service account key file present (`gcp-service-account.json`)
- [ ] Environment variables loaded
- [ ] Services started with `dev-gcp-*` commands

## 🎓 Best Practices

1. **Security**: Never commit service account keys to git
2. **Environment**: Use `.env` files for configuration
3. **Costs**: Monitor GCP usage and set billing alerts
4. **Testing**: Test locally first, then with GCP integration
5. **Collaboration**: Document any shared resource changes
6. **Backup**: Regularly backup important development data

This setup gives you a powerful development environment that combines the speed of local development with the realism of cloud services. Happy coding! 🚀