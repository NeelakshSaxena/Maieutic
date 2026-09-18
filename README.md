---
license: mit
base_model: Qwen/Qwen3-8B
tags:
- lora
- socratic-tutor
- mentorai
---

# MentorAI: Socratic Tutoring Model Card

This is the repository containing the QLoRA adapter for **MentorAI Experiment #1**.

* **BASE MODEL:** `Qwen/Qwen3-8B`
* **EXPERIMENT:** `experiment_01_contradictory_socratic_supervision`
* **TRAINING TYPE:** QLoRA
* **EPOCHS:** 1
* **STEPS:** 2586
* **MAX SEQUENCE LENGTH:** 4096
* **GPU:** RTX 4090 24GB

---

## How to Restore MentorAI

This single private Hugging Face repository holds all model and training artifacts for the MentorAI project. Use the instructions below to resume work.

### Artifact Locations
* **LoRA Adapter & Tokenizer files:** Located at the root of this repository:
  * `adapter_config.json`
  * `adapter_model.safetensors`
  * `chat_template.jinja`
  * `tokenizer.json`
  * `tokenizer_config.json`
* **Evaluation Benchmark & Reports:** Located in `/evaluation/`:
  * `mentorai_benchmark.jsonl` (evaluation benchmark)
  * `report_base.md` / `report_sft.md` (rescoring reports)
  * `generated_responses_base.jsonl` / `generated_responses_sft.jsonl` (raw outputs)
* **Phase 1.5 Pilot Dataset:** Located in `/pilot/`:
  * `socratic_pilot.jsonl` (transformed Socratic dataset)
  * `rejections.jsonl` (audit trail of rejected examples)
  * `pilot_stats.json` (quality metrics and categorization)

### Necessary vs Optional Downloads
* **Necessary (to load model):** Root-level files (`adapter_config.json`, `adapter_model.safetensors`, tokenizer files).
* **Optional (for replication/analysis):** `evaluation/` and `pilot/` subdirectories.

### 1. Download Repository
Authenticate with Hugging Face and use `huggingface-cli` to download the files:
```bash
# Authenticate
export HF_TOKEN="your_huggingface_token"
huggingface-cli login --token $HF_TOKEN

# Download only the model adapter files (Necessary)
huggingface-cli download NeelakshSaxena/mentorai \
  --include "adapter_config.json" "adapter_model.safetensors" "chat_template.jinja" "tokenizer.json" "tokenizer_config.json" \
  --local-dir ./outputs/qwen-8b-socratic-v1

# Download evaluation artifacts (Optional)
huggingface-cli download NeelakshSaxena/mentorai \
  --include "evaluation/*" \
  --local-dir ./training/
```

### 2. Load the Adapter in Python
Load the adapter against the base model `Qwen/Qwen3-8B`:
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

base_model_name = "Qwen/Qwen3-8B"
adapter_dir = "./outputs/qwen-8b-socratic-v1"

tokenizer = AutoTokenizer.from_pretrained(adapter_dir)
model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
model = PeftModel.from_pretrained(model, adapter_dir)
```

### 3. Resume Evaluation
To execute the rescoring script:
```bash
python training/evaluation/rescore_evaluations.py
```


## Phase 2A (version: `phase2a_qwen3-8b_real-socratic_2026-09-15`)
**STATUS: TRAINED — BEHAVIORAL EVALUATION PENDING**

- **Goal**: Real Socratic tutoring data (Experiment 2)
- **Base Model**: Qwen/Qwen3-8B
- **Training Method**: QLoRA (4-bit, Rank 16, Alpha 32)
- **Date**: 2026-09-15
- **Dataset**: 13,859 training examples
- **Epochs**: 1
- **Note**: The sanity check passed (the adapter loads and generates text), but this does not establish Socratic behavioral improvement. Behavioral evaluation is pending.
