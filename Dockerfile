# Multi-stage Dockerfile for System//Zero with environment config support
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Production stage
FROM python:3.12-slim

# Create non-root user
RUN useradd -m -u 1000 systemzero && \
    mkdir -p /app/logs /app/config /app/data && \
    chown -R systemzero:systemzero /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/systemzero/.local

# Copy application code
COPY --chown=systemzero:systemzero systemzero/ ./systemzero/
COPY --chown=systemzero:systemzero requirements.txt .

# Set Python path
ENV PATH=/home/systemzero/.local/bin:$PATH
ENV PYTHONPATH=/app

# Default environment configuration (override in compose or runtime)
ENV SZ_LOG_LEVEL=INFO \
    SZ_JSON_LOGS=true \
    SZ_LOG_PATH=/app/logs/systemzero.log \
    SZ_ENABLE_HEALTH=true \
    SZ_ENABLE_METRICS=true \
    SZ_ENABLE_RATE_LIMITING=true \
    SZ_RATE_LIMIT_RPM=100 \
    SZ_RATE_LIMIT_BURST=20 \
    SZ_MAX_REQUEST_SIZE_MB=10 \
    SZ_API_KEYS_PATH=/app/config/api_keys.yaml

# Switch to non-root user
USER systemzero

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run the API server using get_app() factory
CMD ["python", "-m", "uvicorn", "systemzero.interface.api.server:get_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
