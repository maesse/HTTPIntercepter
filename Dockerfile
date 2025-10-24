# Multi-stage build for frontend + backend

# 1) Frontend build
FROM node:20-alpine AS frontend
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build

# 2) Backend runtime
FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install backend deps
COPY backend/pyproject.toml ./backend/pyproject.toml
RUN pip install --no-cache-dir -U pip setuptools && \
    pip install --no-cache-dir -e ./backend[dev]

# Copy backend code and static
COPY backend/ ./backend/
COPY --from=frontend /app/dist ./frontend-dist

ENV FRONTEND_DIST_DIR=/app/frontend-dist
EXPOSE 8181
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8181"]
