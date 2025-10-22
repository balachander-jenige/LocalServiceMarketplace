# Use Python 3.12 slim image for better compatibility and security
FROM python:3.12-slim

# Set labels for better container identification in EKS
LABEL service="user-service" \
      version="1.0.0" \
      description="User profile microservice for freelancer marketplace"

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Set working directory inside container
WORKDIR /app

# Copy dependency files first for better Docker layer caching
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry for production and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only=main

# Create non-root user for security (EKS best practice)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application source code
COPY . /app

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Environment variables with defaults for EKS deployment
# These can be overridden by Kubernetes ConfigMaps/Secrets
ENV MONGODB_URL=${MONGODB_URL:-mongodb://mongodb-service:27017/user_db}
ENV RABBITMQ_URL=${RABBITMQ_URL:-amqp://guest:guest@rabbitmq-service:5672/}
ENV AUTH_SERVICE_URL=${AUTH_SERVICE_URL:-http://auth-service:8000}
ENV SERVICE_NAME=${SERVICE_NAME:-user-service}
ENV SERVICE_PORT=${SERVICE_PORT:-8002}
ENV LOG_LEVEL=${LOG_LEVEL:-INFO}

# Health check for EKS readiness/liveness probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Expose User Service port
EXPOSE 8002

# Use exec form for better signal handling in Kubernetes
CMD ["uvicorn", "user_service.main:app", "--host", "0.0.0.0", "--port", "8002", "--app-dir", "src"]
