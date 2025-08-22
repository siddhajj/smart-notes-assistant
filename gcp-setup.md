# GCP Setup Instructions

## Prerequisites
1. Install Google Cloud CLI: `gcloud init`
2. Set up billing account and enable APIs
3. Create a new GCP project or use existing one

## Required GCP APIs
Enable these APIs in your GCP project:
```bash
gcloud services enable cloudsql-admin.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## Environment Variables
Set these in your environment:
```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export DB_INSTANCE_NAME="notes-app-db"
export DB_NAME="notesapp"
export DB_USER="notesapp_user"
export DB_PASSWORD="your-secure-password"
```

## Cloud SQL Setup
1. **Create PostgreSQL instance:**
```bash
gcloud sql instances create $DB_INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --cpu=1 \
    --memory=3840MB \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB
```

2. **Create database and user:**
```bash
gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE_NAME
gcloud sql users create $DB_USER --instance=$DB_INSTANCE_NAME --password=$DB_PASSWORD
```

3. **Get connection string:**
```bash
gcloud sql instances describe $DB_INSTANCE_NAME --format="value(connectionName)"
```

## Service Account Setup
1. **Create service account:**
```bash
gcloud iam service-accounts create notes-app-sa \
    --description="Service account for Smart Notes Assistant" \
    --display-name="Smart Notes Assistant Service Account"
```

2. **Grant permissions:**
```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:notes-app-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:notes-app-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:notes-app-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

3. **Create and download key:**
```bash
gcloud iam service-accounts keys create key.json \
    --iam-account=notes-app-sa@$PROJECT_ID.iam.gserviceaccount.com
```

## Cloud Run Configuration
Default settings for all services:
- CPU: 1
- Memory: 512Mi
- Min instances: 0
- Max instances: 10
- Concurrency: 80
- Timeout: 300s

## Security Setup
1. **Store database password in Secret Manager:**
```bash
echo -n "$DB_PASSWORD" | gcloud secrets create db-password --data-file=-
```

2. **Create connection string secret:**
```bash
CONNECTION_STRING="postgresql://$DB_USER:$DB_PASSWORD@/$DB_NAME?host=/cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE_NAME"
echo -n "$CONNECTION_STRING" | gcloud secrets create database-url --data-file=-
```

## Next Steps
1. Update application code with GCP configurations
2. Deploy services to Cloud Run
3. Configure networking and IAM
4. Set up monitoring and logging