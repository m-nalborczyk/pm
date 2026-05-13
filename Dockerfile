# Multi-stage Dockerfile for Project Management MVP
# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build static frontend
RUN npm run build

# Stage 2: Python backend with uv
FROM python:3.11-slim

# Install uv
RUN pip install uv

WORKDIR /app

# Copy backend files
COPY backend/ ./backend/
COPY pyproject.toml ./

# Install Python dependencies using uv
RUN uv pip install --system -e ".[dev]"

# Copy built frontend from stage 1
COPY --from=frontend-builder /frontend/out ./backend/static

# Copy .env file
COPY .env .env

# Expose port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Made with Bob
