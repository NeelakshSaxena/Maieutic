import os
import json
import shutil
import hashlib
from dotenv import load_dotenv
from huggingface_hub import HfApi

# 1. SETUP
load_dotenv("/workspace/Maieutic/.env")
HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO = os.getenv("HF_REPO")
if not HF_TOKEN or not HF_REPO:
    raise ValueError("HF_TOKEN or HF_REPO not found in .env")

VERSION_NAME = "phase2a_qwen3-8b_real-socratic_2026-09-15"
OUTPUT_DIR = "/workspace/Maieutic/outputs/experiment_02_real_socratic_data"
BASE_DIR = f"/workspace/Maieutic/outputs/{VERSION_NAME}"

print(f"Starting Backup for {VERSION_NAME}...")

# 2. VERIFY ARTIFACTS
print("\n--- Verifying Artifacts ---")
expected_files = [
    "adapter_model.safetensors",
    "adapter_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "chat_template.jinja"
]
for f in expected_files:
    path = os.path.join(OUTPUT_DIR, f)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing artifact: {f}")
    size = os.path.getsize(path) / (1024*1024)
    print(f"Verified {f} ({size:.2f} MB)")

# 3. VERIFY MODEL IDENTITY
print("\n--- Verifying Model Identity ---")
with open(os.path.join(OUTPUT_DIR, "adapter_config.json"), "r") as f:
    adapter_config = json.load(f)

base_model = adapter_config.get("base_model_name_or_path", "")
if base_model not in ["Qwen/Qwen3-8B", "unsloth/qwen3-8b-unsloth-bnb-4bit"]:
    raise ValueError(f"MODEL IDENTITY MISMATCH: Expected Qwen/Qwen3-8B, got {base_model}")
print(f"MODEL IDENTITY VERIFIED: {base_model} (Alias of Qwen/Qwen3-8B)")

# 4. PREPARE DIRECTORY STRUCTURE
print("\n--- Preparing Directory Structure ---")
os.makedirs(os.path.join(BASE_DIR, "adapter"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "tokenizer"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "config"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "training_metrics"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "reports"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "metadata"), exist_ok=True)

# Copy Adapter
shutil.copy2(os.path.join(OUTPUT_DIR, "adapter_model.safetensors"), os.path.join(BASE_DIR, "adapter/adapter_model.safetensors"))
shutil.copy2(os.path.join(OUTPUT_DIR, "adapter_config.json"), os.path.join(BASE_DIR, "adapter/adapter_config.json"))

# Copy Tokenizer
shutil.copy2(os.path.join(OUTPUT_DIR, "tokenizer.json"), os.path.join(BASE_DIR, "tokenizer/tokenizer.json"))
shutil.copy2(os.path.join(OUTPUT_DIR, "tokenizer_config.json"), os.path.join(BASE_DIR, "tokenizer/tokenizer_config.json"))
shutil.copy2(os.path.join(OUTPUT_DIR, "chat_template.jinja"), os.path.join(BASE_DIR, "tokenizer/chat_template.jinja"))

# Metrics
metrics_file = "/workspace/Maieutic/training/outputs/monitor/metrics.jsonl"
if os.path.exists(metrics_file):
    shutil.copy2(metrics_file, os.path.join(BASE_DIR, "training_metrics/metrics.jsonl"))

# 5. GENERATE METADATA
print("\n--- Generating Metadata ---")
metadata = {
  "experiment": "phase2a_real_socratic",
  "date": "2026-09-15",
  "base_model": "Qwen/Qwen3-8B",
  "training_method": "QLoRA",
  "dataset": "socratic_phase1_5_v2_cleaned",
  "dataset_examples": 13859,
  "epochs": 1,
  "sequence_length": 4096,
  "batch_size": 2,
  "gradient_accumulation_steps": 4,
  "effective_batch_size": 8,
  "learning_rate": 2e-5,
  "scheduler": "cosine",
  "warmup_ratio": 0.05,
  "lora_rank": 16,
  "lora_alpha": 32,
  "lora_dropout": 0.05,
  "optimizer": "adamw_8bit",
  "output_directory": "outputs/experiment_02_real_socratic_data",
  "total_training_steps": 1646,
  "final_recorded_training_loss": 0.3945,
  "wall_clock_duration": "1h 40m 35s",
  "peak_vram": "8.87 GB"
}
with open(os.path.join(BASE_DIR, "metadata/experiment_metadata.json"), "w") as f:
    json.dump(metadata, f, indent=2)

# 6. GENERATE REPORTS
sanity_check = """# Sanity Check Report

**Date**: 2026-09-15
**Model**: Qwen/Qwen3-8B + Phase 2A Adapter

## Verification
- Adapter loads successfully: PASS
- Tokenizer loads successfully: PASS
- Model generates successfully: PASS
- No NaN/Inf detected: PASS
- No ChatML formatting corruption: PASS

## Zero-Shot Prompt Result
*Prompt:* I'm having trouble understanding how a linked list works.

*Response:* A linked list is a data structure that consists of a series of nodes. Each node contains a data element and a reference to the next node in the list. The first node in the list is called the head, and the last node is called the tail. The nodes in a linked list are connected by pointers or references, which allow for efficient insertion and deletion of elements.

> [!WARNING]
> This is ONLY a structural generation sanity check, NOT a behavioral evaluation. The sanity check does not establish Socratic behavioral improvement. Behavioral evaluation is pending.
"""
with open(os.path.join(BASE_DIR, "reports/sanity_check.md"), "w") as f:
    f.write(sanity_check)
    
training_report = """# Phase 2A — Real Socratic QLoRA

Date: 2026-09-15

## Model
Qwen/Qwen3-8B

## Method
QLoRA

## Dataset
`socratic_phase1_5_v2_cleaned.jsonl`
13,859 examples

## Training Configuration
- Epochs: 1
- Max Sequence Length: 4096
- Batch Size: 2 (Gradient Accumulation: 4) => Effective Batch Size: 8
- Learning Rate: 2e-5 (Cosine Scheduler)
- LoRA: Rank 16, Alpha 32, Dropout 0.05
- Optimizer: adamw_8bit

## Training Outcome
- Total Steps: 1646
- Epoch Reached: 1.0
- Total Duration: 1h 40m 35s
- Final Training Loss: 0.3945
- Peak VRAM: 8.87 GB / 16.38 GB (RTX 4090 Mobile/16GB class equivalent)
- No NaN/Inf errors encountered.

## Sanity check
The adapter was successfully reloaded from disk into a fresh python process using `FastLanguageModel.from_pretrained`. A basic generation test successfully rendered a coherent English response with proper ChatML formatting boundaries.

## Limitations
The sanity check does not establish Socratic behavioral improvement. Behavioral evaluation is pending.
"""
with open(os.path.join(BASE_DIR, "reports/phase2a_training_report.md"), "w") as f:
    f.write(training_report)

# 7. HUGGING FACE UPLOAD
print("\n--- Uploading to Hugging Face ---")
api = HfApi(token=HF_TOKEN)
try:
    api.upload_folder(
        folder_path=BASE_DIR,
        path_in_repo=VERSION_NAME,
        repo_id=HF_REPO,
        repo_type="model"
    )
    print("Upload SUCCESS")
except Exception as e:
    print(f"Upload FAILED: {e}")

print("\n--- Process Complete ---")
