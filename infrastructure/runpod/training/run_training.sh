#!/bin/bash
set -e

echo "Starting MentorAI RunPod Training Pipeline..."

# Check HF_TOKEN
if [ -z "$HF_TOKEN" ]; then
    echo "Warning: HF_TOKEN is not set. You won't be able to push to Hugging Face."
else
    echo "Logging into Hugging Face..."
    huggingface-cli login --token "$HF_TOKEN" --add-to-git-credential
fi

# Check WANDB_API_KEY
if [ -z "$WANDB_API_KEY" ]; then
    echo "Warning: WANDB_API_KEY is not set. Weights & Biases logging will be disabled."
else
    echo "Weights & Biases key detected."
fi

# Navigate to training dir
cd ../../../training

# Run the training script. Use --full-run for full SFT or --smoke-test for a 10-step test.
# Default to smoke test if no arguments are passed to avoid accidental full runs.

if [ "$1" == "--full-run" ]; then
    echo "Running FULL training run..."
    python sft/train.py --full-run
elif [ "$1" == "--smoke-test" ]; then
    echo "Running SMOKE TEST..."
    python sft/train.py --smoke-test
else
    echo "Usage: ./run_training.sh [--smoke-test | --full-run]"
    echo "Defaulting to SMOKE TEST to be safe..."
    python sft/train.py --smoke-test
fi
