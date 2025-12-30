# Self-Evolving AI Framework - Production Dockerfile
# Multi-stage build for optimized production deployment

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG VERSION=3.0.0
ARG BUILD_DATE
ARG VCS_REF

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set metadata labels
LABEL maintainer="Evolving AI Systems <support@evolving-ai.com>"
LABEL version="${VERSION}"
LABEL description="Self-Evolving AI Framework - Production Container"
LABEL build-date="${BUILD_DATE}"
LABEL vcs-ref="${VCS_REF}"

# Create non-root user for security
RUN groupadd -r aiuser && useradd -r -g aiuser aiuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/aiuser/.local

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data \
    /app/logs \
    /app/snapshots \
    /app/AI_NETWORK_LOCAL \
    && chown -R aiuser:aiuser /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV STORAGE_LOCAL_PATH=/app/data
ENV LOG_FILE_PATH=/app/logs/evolution.log
ENV AUDIT_LOG_PATH=/app/logs/audit.log
ENV ENVIRONMENT=production
ENV PATH=/home/aiuser/.local/bin:$PATH

# Switch to non-root user
USER aiuser

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python evolving_ai_main.py status || exit 1

# Default command
CMD ["python", "evolving_ai_main.py", "start"]

# Alternative commands for different use cases:
# Web interface: CMD ["python", "web_interface.py"]
# Demo mode: CMD ["python", "evolving_ai_main.py", "demo"]
# Status check: CMD ["python", "evolving_ai_main.py", "status"]