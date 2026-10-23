# ==============================================================================
# Stage 1: Build Frontend Assets with Node
# ==============================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ==============================================================================
# Stage 2: Production Python Runtime with FastAPI
# ==============================================================================
FROM python:3.12-slim AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install backend python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root application user for secure execution
RUN useradd -m -u 1000 -s /bin/bash appuser

# Copy backend code
COPY --chown=appuser:appuser backend/ ./backend

# Copy built frontend assets from Stage 1 into frontend dist directory
COPY --from=frontend-builder --chown=appuser:appuser /app/frontend/dist /app/frontend/dist

EXPOSE 8000

WORKDIR /app/backend

USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start Uvicorn production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
