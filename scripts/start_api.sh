#!/bin/bash
set -e

echo "[API] Waiting for Postgres..."
until pg_isready -h postgres -p 5432 -U ${POSTGRES_USER:-postgres}; do
  sleep 2
done

echo "[API] Running database migrations..."
cd /app/api
poetry run alembic upgrade head

echo "[API] Starting FastAPI application..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
