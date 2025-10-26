# Multi-stage build for frontend + backend

# 1) Frontend build
FROM node:20-alpine AS frontend
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
# Fail early and produce reproducible installs
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 2) Backend runtime
FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Copy backend code and install deps
COPY backend/ ./backend/
RUN pip install --no-cache-dir -U pip setuptools && \
    pip install --no-cache-dir -e ./backend
COPY --from=frontend /app/dist ./frontend-dist

ENV FRONTEND_DIST_DIR=/app/frontend-dist \
    INTERCEPTER_MAX_REQUESTS=100 \
    INTERCEPTER_RETENTION_SECONDS=86400
EXPOSE 8181

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8181"]
