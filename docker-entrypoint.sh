#!/bin/bash

set -e

echo "=========================================="
echo "        Starting Maieutic"
echo "=========================================="

# ------------------------------------------------------------
# Initialize PostgreSQL if necessary
# ------------------------------------------------------------

if [ ! -s "/var/lib/postgresql/data/PG_VERSION" ]; then

    echo "[PostgreSQL] Initializing database..."

    mkdir -p /var/lib/postgresql/data
    chown -R postgres:postgres /var/lib/postgresql/data

    su - postgres -c "/usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/data"

    echo "[PostgreSQL] Starting temporary server..."

    su - postgres -c "/usr/lib/postgresql/15/bin/pg_ctl \
        -D /var/lib/postgresql/data \
        -o '-c listen_addresses=localhost' \
        -w start"

    echo "[PostgreSQL] Creating database..."

    su - postgres -c "psql -c \"ALTER USER postgres PASSWORD 'postgres';\""

    su - postgres -c "createdb mentorai" || true

    echo "[PostgreSQL] Stopping temporary server..."

    su - postgres -c "/usr/lib/postgresql/15/bin/pg_ctl \
        -D /var/lib/postgresql/data \
        -m fast \
        -w stop"

fi


# ------------------------------------------------------------
# Pull Ollama model if it isn't already present
# ------------------------------------------------------------

echo "[Ollama] Checking model..."

(
    echo "[Ollama] Waiting for Ollama..."

    until curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; do
        sleep 2
    done

    if ! ollama list | grep -q "qwen2"; then
        echo "[Ollama] Pulling qwen2..."
        ollama pull qwen2
    else
        echo "[Ollama] qwen2 already exists."
    fi

) &


# ------------------------------------------------------------
# Start Supervisor
# ------------------------------------------------------------

exec /usr/bin/supervisord \
    -n \
    -c /etc/supervisor/conf.d/supervisord.conf
