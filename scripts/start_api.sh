#!/bin/bash
set -e

cd /app/api

# Determine execution mode: 'serverless' or 'pod' / 'api'
MODE="${RUNPOD_MODE:-$1}"

if [ "$MODE" = "serverless" ]; then
    echo "[MentorAI] Starting in RunPod Serverless mode..."
    exec python -m app.workers.serverless_worker
fi

echo "[MentorAI] Starting in HTTP API (Pod / Container) mode..."

# If PostgreSQL is configured, wait for it before migrations
if [[ "$DATABASE_URL" == *"postgres"* ]]; then
    PG_HOST="${POSTGRES_HOST:-postgres}"
    PG_PORT="${POSTGRES_PORT:-5432}"
    PG_USER="${POSTGRES_USER:-postgres}"
    echo "[API] Waiting for PostgreSQL at $PG_HOST:$PG_PORT..."
    until pg_isready -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" 2>/dev/null; do
        sleep 2
    done
    echo "[API] PostgreSQL is ready."
fi

echo "[API] Running database migrations..."
if command -v alembic >/dev/null 2>&1; then
    alembic upgrade head || echo "[API] Migration warning: alembic head may already be applied or using SQLite."
else
    poetry run alembic upgrade head || echo "[API] Migration warning: alembic head may already be applied or using SQLite."
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "[API] Starting FastAPI application on $HOST:$PORT..."
if command -v uvicorn >/dev/null 2>&1; then
    exec uvicorn app.main:app --host "$HOST" --port "$PORT"
else
    exec poetry run uvicorn app.main:app --host "$HOST" --port "$PORT"
fi

