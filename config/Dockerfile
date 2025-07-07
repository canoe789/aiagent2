# HELIX v2.0 Docker Image
# 按照系统级CLAUDE.md规范构建

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code with proper structure
COPY src/ ./src/
COPY schemas/ ./schemas/
COPY templates/ ./templates/
COPY scripts/ ./scripts/
COPY workflows.json ./

# Create tmp directory for temporary files
RUN mkdir -p /app/tmp

# Create non-root user and set ownership
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Set Python path for src-based imports
ENV PYTHONPATH=/app/src:/app

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose.yml)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]