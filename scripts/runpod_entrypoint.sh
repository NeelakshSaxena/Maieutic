#!/bin/bash
set -e

echo "=========================================="
echo "    Maieutic RunPod Unified Entrypoint"
echo "=========================================="

# 1. Setup Persistent Storage
# RunPod typically provides a persistent volume at /workspace
# We will create the huggingface cache and db directory there.
WORKSPACE_DIR="/workspace"

if [ -d "$WORKSPACE_DIR" ]; then
    echo "[Entrypoint] Detected /workspace persistent volume."
    
    # Hugging Face Cache
    mkdir -p "$WORKSPACE_DIR/huggingface_cache"
    # Safely remove existing symlink or empty directory if it exists
    rm -rf /root/.cache/huggingface
    mkdir -p /root/.cache
    ln -s "$WORKSPACE_DIR/huggingface_cache" /root/.cache/huggingface
    
    # SQLite Database
    export DATABASE_URL="sqlite:///$WORKSPACE_DIR/maieutic.db"
    echo "[Entrypoint] SQLite database mapped to $DATABASE_URL"
else
    echo "[Entrypoint] WARNING: No /workspace volume detected. Data will be lost on restart."
    export DATABASE_URL="sqlite:///./maieutic.db"
fi

# 2. Start vLLM (Background)
# We run model_bootstrap.sh in the background. It will start vLLM and wait for it.
echo "[Entrypoint] Starting Model Bootstrap & vLLM..."
/app/model_bootstrap.sh &
VLLM_SCRIPT_PID=$!

# 3. Start FastAPI Backend (Background)
echo "[Entrypoint] Starting FastAPI Backend..."
export LLM_BASE_URL="http://localhost:11434/v1"
export LLM_MODEL="mentorai"
export LLM_API_KEY="local"

cd /app/api
echo "[API] Running database migrations..."
poetry run alembic upgrade head
echo "[API] Starting Uvicorn..."
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# 4. Start Next.js Frontend (Background)
echo "[Entrypoint] Starting Next.js Frontend..."
cd /app/frontend
# The standalone build uses server.js
node server.js &
FRONTEND_PID=$!

echo "[Entrypoint] All services launched."
echo "[Entrypoint] Waiting for any process to exit..."

# Wait for any of the background processes to exit
wait -n $VLLM_SCRIPT_PID $API_PID $FRONTEND_PID

# If one crashes, bring everything down
echo "[Entrypoint] A core service exited. Shutting down."
kill 0
