# Smart Notes Assistant - AI-Powered Notes and Tasks Management

A modern, AI-powered productivity application built with FastAPI microservices, Reflex frontend, and Google Cloud Platform integration.

## 🚀 Features

### **Core Functionality**
- **Smart Note Management**: Create, edit, and organize notes with AI-generated titles and embeddings
- **Task Management**: Track tasks with due dates, priorities, and completion status
- **RAG-Powered Search**: Ask questions about your notes and tasks using natural language
- **Semantic Search**: Find content by meaning, not just keywords using vector embeddings
- **Single-Page Interface**: Streamlined UI with modal-based interactions

### **AI & Search Features**
- **Vector Embeddings**: Automatic embedding generation for semantic search
- **RAG (Retrieval Augmented Generation)**: AI answers based on your actual content
- **Multiple Search Types**: Text-based and semantic similarity search
- **Smart Context**: AI responses grounded in your notes and tasks

### **Technical Features**
- **Microservices Architecture**: Scalable backend with separate services for users, notes, tasks, search, and AI
- **Cloud-Native**: Deployed on Google Cloud Platform with Cloud Run, Cloud SQL, and Vertex AI
- **Modern Tech Stack**: FastAPI, Reflex, PostgreSQL, pgvector, and cutting-edge AI integration
- **Hybrid Development**: Support for both local SQLite and Cloud SQL environments

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │────│  Load Balancer   │────│   Cloud Run     │
│    (Reflex)     │    │   (HTTPS/SSL)    │    │  Microservices  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
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

### Microservices

- **User Service** (Port 8003): Authentication and user management
- **Notes Service** (Port 8000): Note CRUD operations with automatic embedding generation
- **Tasks Service** (Port 8002): Task management with embedding support
- **AI Service** (Port 8001): Vertex AI integration for smart features
- **Search Service** (Port 8004): Unified search with RAG functionality
- **Web Frontend** (Port 3000): Single-page Reflex interface

## 🛠️ Technology Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - Database ORM
- PostgreSQL - Primary database with pgvector extension
- Pydantic - Data validation
- pgvector - Vector similarity search

**Frontend:**
- Reflex - Python-based web framework
- Single-page application design
- Modal-based interactions

**AI & Search:**
- Google Vertex AI - AI/ML platform
- OpenAI Embeddings - Text embedding generation
- Gemini 1.5 Flash - Large language model
- RAG (Retrieval Augmented Generation) - Context-aware AI responses
- Vector similarity search - Semantic content discovery

**Cloud Infrastructure:**
- Google Cloud Run - Serverless containers
- Google Cloud SQL - Managed PostgreSQL
- Google Secret Manager - Secure credential storage

**Development:**
- pyproject.toml - Modern Python project configuration
- pytest - Testing framework
- black, isort, flake8 - Code formatting and linting
- Docker & Docker Compose - Containerization
- GitHub Actions - CI/CD pipeline

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Google Cloud CLI (for production deployment)
- Node.js 18+ (for frontend)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd notes-app
   ```

2. **Set up development environment:**
   ```bash
   make dev-setup
   ```
   This will:
   - Create a virtual environment
   - Install all dependencies from pyproject.toml
   - Set up pre-commit hooks
   - Create a .env file with development defaults
   - Initialize the local database

3. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\\Scripts\\activate  # Windows
   ```

4. **Set up vector search (optional for full features):**
   ```bash
   # For PostgreSQL with pgvector support
   make setup-pgvector
   ```

5. **Start services locally:**
   ```bash
   # Option 1: Run individual services
   make dev-user    # User service (port 8003)
   make dev-notes   # Notes service (port 8000)
   make dev-tasks   # Tasks service (port 8002)
   make dev-ai      # AI service (port 8001)
   make dev-search  # Search service (port 8004)
   make dev-web     # Web frontend (port 3000)
   
   # Option 2: Use Docker Compose
   make docker-up
   ```

6. **Access the application:**
   - **Web Interface**: http://localhost:3000 - Single-page app with notes, tasks, and search
   - **API Documentation**: 
     - Notes Service: http://localhost:8000/docs
     - Tasks Service: http://localhost:8002/docs  
     - Search Service: http://localhost:8004/docs

### Local Development with GCP Services

For advanced development with real Cloud SQL and Vertex AI:

```bash
# One-time setup
export GOOGLE_CLOUD_PROJECT="your-project-id"
make setup-gcp-dev

# Start Cloud SQL Proxy (keep running)
make start-cloud-sql-proxy

# Start services with GCP integration
make dev-gcp-notes   # Real AI + Cloud SQL
make dev-gcp-tasks   # Tasks with Cloud SQL
make dev-gcp-search  # Search with Cloud SQL + embeddings
make dev-gcp-ai      # Full Vertex AI integration
```

See [LOCAL-GCP-DEVELOPMENT.md](LOCAL-GCP-DEVELOPMENT.md) for detailed instructions.

### Docker Development

```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🎨 User Interface

### **Single-Page Design**
The application features a streamlined single-page interface designed for productivity:

```
┌─────────────────────────────────────────┐
│ Header (Login/Logout)                   │
├────────────────┬────────────────────────┤
│ Notes Section  │ Tasks Section          │
│ (50% width)    │ (50% width)            │
│ - [+ New Note] │ - [+ New Task]         │
│ - Title+preview│ - ☑️ Complete/Delete    │
│ - Expand btn   │ - Show completed toggle│
├────────────────┴────────────────────────┤
│ Search Interface (20% height)           │
│ "Ask a question or search..."           │
└─────────────────────────────────────────┘
```

### **Key UI Features**
- **Modal Authentication**: Login/register popups without page redirects
- **Expand/Collapse**: Each section can expand to full width, hiding the other
- **Interactive Elements**: 
  - Notes: Click to view/edit in modal, delete option
  - Tasks: Inline checkboxes, priority badges, delete buttons
- **Search Mode**: Interface transforms to show RAG results + grounding elements
- **Real-time Updates**: Automatic refresh after operations

### **Search Experience**
When you search, the UI transforms to show:
- **Left 60%**: AI-generated answer based on your content  
- **Right 40%**: Relevant notes and tasks (clickable/interactive)
- **Back Navigation**: Easy return to notes/tasks view

## 📦 Dependency Management

This project uses `pyproject.toml` as the single source of truth for all dependencies. No more `requirements.txt` files!

### Installation Options

```bash
# Install core dependencies only
pip install -e .

# Install specific service dependencies
pip install -e ".[api-common,user-service]"
pip install -e ".[api-common,ai-service]"

# Install everything for development
pip install -e ".[api-common,user-service,notes-service,tasks-service,ai-service,web,dev]"
```

### Available Dependency Groups

- `api-common`: Shared API dependencies (FastAPI, SQLAlchemy, etc.)
- `user-service`: Authentication-specific dependencies
- `notes-service`: Notes service (uses api-common)
- `tasks-service`: Tasks service (uses api-common)
- `ai-service`: AI/ML dependencies (Vertex AI, Gemini)
- `search-service`: Search and embeddings dependencies (OpenAI, numpy)
- `web`: Frontend dependencies (Reflex)
- `dev`: Development tools (pytest, black, mypy, etc.)
- `docs`: Documentation tools (mkdocs)
- `monitoring`: Monitoring and logging
- `security`: Security scanning tools

## 🧪 Testing

```bash
# Run all tests
make test

# Run tests with coverage
pytest --cov=apps --cov-report=html

# Run tests in watch mode
make test-watch

# Run specific test types
make test-unit
make test-integration
```

## 🎨 Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Security checks
make security

# Run all quality checks
make lint && make type-check && make security
```

## 🚀 Production Deployment

### Google Cloud Platform

1. **Set up GCP infrastructure:**
   ```bash
   # Set environment variables
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export REGION="us-central1"
   
   # Run setup script
   ./scripts/gcp-setup.sh
   ```

2. **Deploy services:**
   ```bash
   ./scripts/build-and-deploy.sh
   ```

3. **Set up monitoring:**
   ```bash
   export ADMIN_EMAIL="admin@your-domain.com"
   ./scripts/setup-monitoring.sh
   ```

4. **Configure load balancer (optional):**
   ```bash
   export DOMAIN="your-domain.com"
   ./scripts/setup-load-balancer.sh
   ```

### CI/CD Pipeline

The project includes a GitHub Actions workflow that automatically:
- Runs tests on pull requests
- Builds and deploys to GCP on main branch pushes
- Uses pyproject.toml for dependency management

**Required GitHub Secrets:**
- `GCP_PROJECT_ID`: Your Google Cloud Project ID
- `GCP_SA_KEY`: Service account key JSON

## 📁 Project Structure

```
notes-app/
├── pyproject.toml              # Modern Python project configuration
├── Makefile                    # Development commands
├── docker-compose.yml          # Local development stack
├── apps/
│   ├── api/
│   │   ├── user-service/       # Authentication service
│   │   ├── notes-service/      # Notes management
│   │   ├── tasks-service/      # Task management
│   │   ├── ai-service/         # AI integration
│   │   ├── search-service/     # Search and RAG functionality
│   │   └── shared/             # Shared database config
│   └── web/                    # Single-page Reflex frontend
├── scripts/                    # Deployment and setup scripts
├── gcp/                        # GCP configuration files
├── .github/workflows/          # CI/CD pipelines
└── docs/                       # Documentation
```

## 🔧 Available Commands

```bash
# Setup
make install        # Install dependencies
make dev-setup      # Complete development setup
make clean          # Clean build artifacts

# Development
make dev-user       # Run user service
make dev-notes      # Run notes service
make dev-tasks      # Run tasks service
make dev-ai         # Run AI service
make dev-search     # Run search service
make dev-web        # Run web frontend

# Database
make setup-pgvector # Setup pgvector extension
make check-pgvector # Check pgvector status

# Quality
make test          # Run tests
make lint          # Run linting
make format        # Format code
make type-check    # Type checking
make security      # Security checks

# Docker
make build-all     # Build all Docker images (includes search service)
make docker-up     # Start all services
make docker-down   # Stop all services

# Deployment
make deploy-gcp    # Deploy to Google Cloud Platform
```

## 🔍 Search & RAG Features

### **How to Use Search**
1. **Basic Search**: Type any question in the search box at the bottom
2. **View Results**: Interface transforms to show AI answer + relevant content
3. **Interact**: Click notes to edit, use task checkboxes and delete buttons
4. **Return**: Click "Back to Notes & Tasks" to return to main view

### **Search Examples**
```
"What are my urgent tasks?"
"Show me notes about the project meeting"
"Find tasks due this week"
"What did I write about the client presentation?"
```

### **Technical Implementation**
- **Embeddings**: Automatic generation using OpenAI text-embedding-3-small (1536 dimensions)
- **Vector Search**: pgvector extension with cosine similarity
- **RAG Pipeline**: Retrieval → Context Formatting → AI Answer Generation
- **Grounding**: Search results shown alongside AI answers for transparency

### **API Endpoints**
- `GET /search/?query=...&search_type=semantic` - Unified search
- `GET /search/ask?question=...` - Simple Q&A interface  
- `GET /search/rag?query=...` - Advanced RAG search

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run quality checks: `make lint && make test`
5. Commit with conventional commits: `git commit -m "feat: add new feature"`
6. Push and create a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Check the [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions
- Review logs: `make docker-logs` or check Cloud Logging in GCP
- Create an issue for bug reports or feature requests

## 🎯 Roadmap

- [x] ~~Semantic search and vector embeddings~~ ✅ **Completed**
- [x] ~~RAG (Retrieval Augmented Generation)~~ ✅ **Completed**  
- [x] ~~Single-page UI with modal interactions~~ ✅ **Completed**
- [ ] Advanced AI features (note summarization, smart categorization)
- [ ] Mobile-responsive design
- [ ] Real-time collaboration and sharing
- [ ] Advanced analytics and usage insights
- [ ] Plugin system for extensibility
- [ ] Bulk operations and batch processing