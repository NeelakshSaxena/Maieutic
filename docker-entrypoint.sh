#!/bin/bash

set -e

echo "=========================================="
echo "        Starting Maieutic"
echo "=========================================="

# ------------------------------------------------------------
# Initialize PostgreSQL if necessary
# ------------------------------------------------------------

PG_DATA="/workspace/postgres/data"
PG_BIN=$(su - postgres -c "pg_config --bindir" 2>/dev/null || find /usr/lib/postgresql -name initdb -type f -executable | head -n 1 | xargs dirname)

if [ -z "$PG_BIN" ]; then
    echo "[PostgreSQL] ERROR: Could not locate PostgreSQL bin directory."
    exit 1
fi

export PG_BIN
echo "[PostgreSQL] Using binary path: $PG_BIN"

if [ ! -s "$PG_DATA/PG_VERSION" ]; then

    echo "[PostgreSQL] Initializing database..."

    mkdir -p "$PG_DATA"
    chown -R postgres:postgres "$PG_DATA"

    su - postgres -c "$PG_BIN/initdb -D $PG_DATA"

    echo "[PostgreSQL] Starting temporary server..."

    su - postgres -c "$PG_BIN/pg_ctl \
        -D $PG_DATA \
        -o '-c listen_addresses=localhost' \
        -w start"

    echo "[PostgreSQL] Creating database..."

    su - postgres -c "psql -c \"ALTER USER postgres PASSWORD 'postgres';\""

    su - postgres -c "createdb mentorai" || true

    echo "[PostgreSQL] Stopping temporary server..."

    su - postgres -c "$PG_BIN/pg_ctl \
        -D $PG_DATA \
        -m fast \
        -w stop"

fi


# ------------------------------------------------------------
# Pull Ollama model if it isn't already present
# ------------------------------------------------------------

export OLLAMA_MODEL=${OLLAMA_MODEL:-qwen2}

echo "[Ollama] Checking model..."

(
    echo "[Ollama] Waiting for Ollama..."

    until curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; do
        sleep 2
    done

    if ! ollama list | grep -q "$OLLAMA_MODEL"; then
        echo "[Ollama] Pulling $OLLAMA_MODEL..."
        ollama pull "$OLLAMA_MODEL"
    else
        echo "[Ollama] $OLLAMA_MODEL already exists."
    fi

) &


# ------------------------------------------------------------
# Start Supervisor
# ------------------------------------------------------------

exec /usr/bin/supervisord \
    -n \
    -c /etc/supervisor/conf.d/supervisord.conf
