#!/bin/bash
set -e

echo "=========================================="
echo "      Maieutic Model Bootstrap"
echo "=========================================="

export HF_HOME="/root/.cache/huggingface"
BASE_MODEL="Qwen/Qwen3-8B"
LORA_REPO="NeelakshSaxena/mentorai"
LORA_NAME="mentorai"

if [ -z "$HF_TOKEN" ]; then
    echo "[Bootstrap] ERROR: HF_TOKEN environment variable is not set."
    echo "[Bootstrap] A Hugging Face token is required to download the private LoRA adapter."
    exit 1
fi

echo "[Bootstrap] Verifying GPU..."
if ! command -v nvidia-smi &> /dev/null; then
    echo "[Bootstrap] WARNING: nvidia-smi not found. GPU may not be available!"
else
    nvidia-smi
fi

echo "[Bootstrap] Downloading/Verifying models in HF Cache..."
# We use huggingface-cli to ensure the models are pre-downloaded and verified.
huggingface-cli login --token "$HF_TOKEN"
echo "[Bootstrap] Downloading base model ${BASE_MODEL}..."
huggingface-cli download "${BASE_MODEL}" --exclude "*.safetensors" || echo "Ignoring safe-tensors exclusion error if model is purely safetensors" 
# Actually, downloading base model is best left to vLLM or we can just download the whole thing
huggingface-cli download "${BASE_MODEL}"

echo "[Bootstrap] Downloading LoRA adapter from ${LORA_REPO}..."
huggingface-cli download "${LORA_REPO}" \
    --include "adapter_config.json" "adapter_model.safetensors" "tokenizer.json" "tokenizer_config.json" "chat_template.jinja" \
    --local-dir /workspace/lora_adapter

echo "[Bootstrap] Starting vLLM model server..."
# Start vLLM in the background so we can wait for readiness and run a smoke test
python3 -m vllm.entrypoints.openai.api_server \
    --model "${BASE_MODEL}" \
    --enable-lora \
    --lora-modules "${LORA_NAME}=/workspace/lora_adapter" \
    --max-lora-rank 16 \
    --host 0.0.0.0 \
    --port 11434 &
VLLM_PID=$!

echo "[Bootstrap] Waiting for vLLM to become healthy..."
until curl -sf http://localhost:11434/v1/models >/dev/null; do
    if ! kill -0 $VLLM_PID 2>/dev/null; then
        echo "[Bootstrap] ERROR: vLLM process crashed! Check RunPod logs for Python tracebacks or OOM errors."
        exit 1
    fi
    echo "Waiting for vLLM..."
    sleep 5
done

echo "[Bootstrap] vLLM is healthy!"

echo "[Bootstrap] Running inference smoke test..."
curl -s -X POST http://localhost:11434/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer local" \
    -d '{
        "model": "mentorai",
        "messages": [{"role": "user", "content": "What is the Socratic method?"}],
        "max_tokens": 50
    }' > /tmp/smoke_test.json

if grep -q "choices" /tmp/smoke_test.json; then
    echo "[Bootstrap] Smoke test passed!"
else
    echo "[Bootstrap] ERROR: Smoke test failed. Output:"
    cat /tmp/smoke_test.json
    exit 1
fi

echo "[Bootstrap] Setup complete. Model serving is active."
# Bring vLLM back to the foreground
wait $VLLM_PID
