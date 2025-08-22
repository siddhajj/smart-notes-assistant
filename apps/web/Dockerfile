FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and install dependencies
# Note: Build context should be project root for this to work
COPY pyproject.toml .
COPY apps/web ./

# Install dependencies
RUN pip install --no-cache-dir -e ".[api-common,web]"

# Initialize Reflex app
RUN reflex init

# Expose port
EXPOSE 3000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Run the application
CMD ["reflex", "run", "--env", "prod"]