#!/bin/bash
set -e

echo "Setting up MentorAI RunPod Environment..."

# Since we use the official Unsloth Docker image on RunPod, 
# we only need to verify/install project-specific missing dependencies 
# without upgrading/breaking the pre-installed PyTorch/CUDA/Unsloth stack.

# Install additional requirements safely
pip install --no-deps -r ../../../training/requirements.txt || echo "Some pip installs failed, but Unsloth might be intact."

# We need datasets and wandb
pip install datasets wandb python-dotenv

echo "Environment setup complete!"
echo "Make sure to set WANDB_API_KEY and HF_TOKEN before running training."
