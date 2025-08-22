FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and install dependencies
# Note: Build context should be project root for this to work
COPY pyproject.toml .
COPY apps/api/user-service/app ./app

# Install dependencies
RUN pip install --no-cache-dir -e ".[api-common,user-service]"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]