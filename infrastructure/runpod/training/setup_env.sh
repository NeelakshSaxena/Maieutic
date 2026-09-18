#!/bin/bash
set -e

echo "Setting up MentorAI RunPod Environment..."

# Export .env variables if .env exists
if [ -f "../../../.env" ]; then
    echo "Loading environment variables from .env..."
    set -a
    source ../../../.env
    set +a
elif [ -f ".env" ]; then
    echo "Loading environment variables from local .env..."
    set -a
    source .env
    set +a
fi

# Install project requirements with full dependencies, keeping pre-installed torch/CUDA intact
pip install --no-build-isolation -r ../../../training/requirements.txt
pip install --no-build-isolation -r ../../../requirements.txt

echo "Environment setup complete!"
echo "Status of environment variables:"
echo "HF_TOKEN: ${HF_TOKEN:+SET}${HF_TOKEN:-NOT SET}"
echo "WANDB_API_KEY: ${WANDB_API_KEY:+SET}${WANDB_API_KEY:-NOT SET}"
echo "HF_REPO_ID: ${HF_REPO_ID:+SET}${HF_REPO_ID:-NOT SET}"

