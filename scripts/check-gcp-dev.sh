#!/bin/bash

# Check Local GCP Development Setup
# Validates that all requirements are met for local development with GCP services

set -e

echo "🔍 Checking Local GCP Development Setup"
echo "======================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Status tracking
CHECKS_PASSED=0
CHECKS_TOTAL=0

# Helper function for check results
check_result() {
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}❌ $2${NC}"
        if [ ! -z "$3" ]; then
            echo -e "${YELLOW}   💡 $3${NC}"
        fi
    fi
}

echo ""
echo "📋 Prerequisites"
echo "---------------"

# Check if gcloud is installed
gcloud --version > /dev/null 2>&1
check_result $? "Google Cloud CLI installed" "Install from: https://cloud.google.com/sdk/docs/install"

# Check if authenticated
gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@" 2>/dev/null
check_result $? "Authenticated with Google Cloud" "Run: gcloud auth login"

# Check if project is set
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ ! -z "$PROJECT_ID" ]; then
    echo -e "${GREEN}✅ Project ID set: $PROJECT_ID${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}❌ Project ID not set${NC}"
    echo -e "${YELLOW}   💡 Run: gcloud config set project YOUR_PROJECT_ID${NC}"
fi
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))

# Check Application Default Credentials
gcloud auth application-default print-access-token > /dev/null 2>&1
check_result $? "Application Default Credentials configured" "Run: gcloud auth application-default login"

echo ""
echo "🗄️ Cloud SQL"
echo "------------"

# Check if Cloud SQL instance exists
if [ ! -z "$PROJECT_ID" ]; then
    gcloud sql instances describe notes-app-db --quiet > /dev/null 2>&1
    check_result $? "Cloud SQL instance 'notes-app-db' exists" "Run: ./scripts/gcp-setup.sh"
    
    # Check if database exists
    gcloud sql databases describe notesapp --instance=notes-app-db --quiet > /dev/null 2>&1
    check_result $? "Database 'notesapp' exists" "Run: ./scripts/gcp-setup.sh"
else
    echo -e "${YELLOW}⚠️ Skipping Cloud SQL checks (no project set)${NC}"
fi

echo ""
echo "🤖 Vertex AI"
echo "------------"

# Check if Vertex AI API is enabled
if [ ! -z "$PROJECT_ID" ]; then
    gcloud services list --enabled --filter="name:aiplatform.googleapis.com" --format="value(name)" | grep -q "aiplatform.googleapis.com" 2>/dev/null
    check_result $? "Vertex AI API enabled" "Run: gcloud services enable aiplatform.googleapis.com"
else
    echo -e "${YELLOW}⚠️ Skipping Vertex AI checks (no project set)${NC}"
fi

echo ""
echo "🔐 Local Configuration"
echo "--------------------"

# Check if .env file exists
[ -f ".env" ]
check_result $? ".env file exists" "Run: make setup-gcp-dev"

# Check if service account key exists
[ -f "./gcp-service-account.json" ]
check_result $? "Service account key file exists" "Run: make setup-gcp-dev"

# Check if Cloud SQL Proxy is downloaded
[ -f "./cloud-sql-proxy" ] || [ -f "./cloud-sql-proxy.exe" ]
check_result $? "Cloud SQL Proxy downloaded" "Will be downloaded automatically when needed"

echo ""
echo "🐍 Python Environment"
echo "--------------------"

# Check if virtual environment exists
[ -d ".venv" ]
check_result $? "Virtual environment exists" "Run: make dev-setup"

# Check if in virtual environment or packages installed
python -c "import fastapi, sqlalchemy, google.cloud.sql.connector" > /dev/null 2>&1
check_result $? "Required Python packages installed" "Run: make install"

echo ""
echo "🔄 Services Status"
echo "----------------"

# Check if Cloud SQL Proxy is running
if pgrep -f "cloud-sql-proxy" > /dev/null; then
    echo -e "${GREEN}✅ Cloud SQL Proxy is running${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠️ Cloud SQL Proxy not running${NC}"
    echo -e "${YELLOW}   💡 Start with: make start-cloud-sql-proxy${NC}"
fi
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))

# Check if any development services are running
SERVICES_RUNNING=0
for port in 8000 8001 8002 8003 3000; do
    if lsof -i :$port > /dev/null 2>&1; then
        SERVICES_RUNNING=$((SERVICES_RUNNING + 1))
    fi
done

if [ $SERVICES_RUNNING -gt 0 ]; then
    echo -e "${GREEN}✅ $SERVICES_RUNNING development service(s) running${NC}"
else
    echo -e "${YELLOW}⚠️ No development services running${NC}"
    echo -e "${YELLOW}   💡 Start with: make dev-gcp-notes, make dev-gcp-ai, etc.${NC}"
fi

echo ""
echo "📊 Summary"
echo "--------"

if [ $CHECKS_PASSED -eq $CHECKS_TOTAL ]; then
    echo -e "${GREEN}🎉 All checks passed! ($CHECKS_PASSED/$CHECKS_TOTAL)${NC}"
    echo -e "${GREEN}You're ready for local GCP development!${NC}"
    echo ""
    echo "🚀 Quick start commands:"
    echo "  make start-cloud-sql-proxy  # Terminal 1"
    echo "  make dev-gcp-notes          # Terminal 2"
    echo "  make dev-gcp-ai             # Terminal 3"
    echo ""
elif [ $CHECKS_PASSED -gt $((CHECKS_TOTAL * 70 / 100)) ]; then
    echo -e "${YELLOW}⚠️ Most checks passed ($CHECKS_PASSED/$CHECKS_TOTAL)${NC}"
    echo -e "${YELLOW}You can proceed with caution. Address failing checks if you encounter issues.${NC}"
else
    echo -e "${RED}❌ Several checks failed ($CHECKS_PASSED/$CHECKS_TOTAL)${NC}"
    echo -e "${RED}Please address the failing checks before proceeding.${NC}"
    echo ""
    echo "🛠️ Quick fix commands:"
    echo "  make setup-gcp-dev     # One-time GCP setup"
    echo "  make dev-setup         # Local environment setup"
fi

echo ""
echo "📖 For detailed instructions, see: LOCAL-GCP-DEVELOPMENT.md"