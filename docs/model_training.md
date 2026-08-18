# MentorAI — Model Training

## 1. Initial Model

Target:

12–14B instruction-tuned open-weight model.

Use QLoRA for initial experiments.

## 2. Why Not Full Fine-tuning?

MVP objectives are behavioral specialization, not learning entirely new knowledge.

LoRA/QLoRA provides:

- Lower cost
- Faster iteration
- Lower VRAM requirement
- Easy experimentation

## 3. Training Stages

### Stage 0 — Baseline

Test base model without fine-tuning.

### Stage 1 — SFT

Train on curated tutoring examples.

Target behaviors:

- Decomposition
- Socratic questioning
- Checkpoint creation
- Hints

### Stage 2 — Verification SFT

Train on:

student response
+
correct evaluation
+
misconception

### Stage 3 — Preference Optimization

Create pairs:

GOOD TUTOR

vs

ANSWER DUMP

Train with DPO/ORPO.

### Stage 4 — Production Evaluation

Compare:

Base model

vs

SFT

vs

SFT + preference optimization

## 4. RunPod

Training jobs run on RunPod.

Development:

24GB GPU where feasible.

Larger jobs:

A100/H100 class GPUs.

Use persistent storage for:

- Datasets
- Checkpoints
- Logs
- Evaluation results

## 5. Training Stack

- Transformers
- Datasets
- PEFT
- TRL
- Unsloth
- bitsandbytes
- Accelerate
- Weights & Biases

## 6. Dataset Stages

raw
    |
cleaned
    |
normalized
    |
deduplicated
    |
quality filtered
    |
SFT
    |
preference dataset

## 7. Important

Do not blindly merge every educational dataset.

Many datasets teach direct answering.

Only samples compatible with MentorAI's tutoring behavior should enter the tutoring SFT dataset.

## 8. Production Inference

Deploy fine-tuned model using:

vLLM

The application accesses it through the Model Gateway.

## 9. Continuous Improvement

User sessions should NOT directly modify model weights.

Instead:

Interactions
    |
Anonymization
    |
Quality filtering
    |
Evaluation
    |
Training dataset
    |
Periodic model update