# Search Service Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project configuration
COPY pyproject.toml ./

# Install dependencies for search service
RUN pip install --no-cache-dir -e ".[api-common,search-service]"

# Copy source code
COPY apps/api/shared/ ./apps/api/shared/
COPY apps/api/user-service/app/auth.py ./apps/api/user-service/app/auth.py
COPY apps/api/user-service/app/__init__.py ./apps/api/user-service/app/__init__.py
COPY apps/api/user-service/ ./apps/api/user-service/
COPY apps/api/notes-service/app/models.py ./apps/api/notes-service/app/models.py
COPY apps/api/notes-service/app/__init__.py ./apps/api/notes-service/app/__init__.py
COPY apps/api/tasks-service/app/models.py ./apps/api/tasks-service/app/models.py
COPY apps/api/tasks-service/app/__init__.py ./apps/api/tasks-service/app/__init__.py
COPY apps/api/search-service/ ./apps/api/search-service/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8004

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

# Run the application
CMD ["uvicorn", "apps.api.search-service.app.main:app", "--host", "0.0.0.0", "--port", "8004"]