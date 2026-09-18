# MentorAI Phase 2 Training

This directory contains the Phase 2 QLoRA training environment, dataset processing pipeline, and SFT scripts for MentorAI.

## Dataset Pipeline Execution

The Phase 0 and Phase 1 data pipeline processes the raw Hugging Face datasets into a standardized schema optimized for Socratic tutoring.

### Dataset Sources (22k target samples)
- `lmsys/lmsys-chat-1m`
- `allenai/WildChat`
- `AI-MO/NuminaMath-CoT`
- `AI-MO/NuminaMath-TIR`
- `AI-MO/NuminaMath-1.5`

### Pipeline Results
- **Initial raw samples**: 22,000
- **Final exported samples**: 21,876
- **Dropped samples**: 124 (failed heuristic Socratic filters or were exact duplicates)
- **Disk Usage (raw)**: ~73 MB

### Qwen/Qwen3-8B Token Statistics
Tokenization applied across the final 21,876 samples using the `Qwen/Qwen3-8B` chat template:
- **Total Tokens**: 16,271,731
- **Average Tokens per sample**: 743.82
- **Max Tokens in a sample**: 219,154
- **Min Tokens in a sample**: 60

> **Note**: There is at least one outlier sequence with 219k+ tokens which exceeds the maximum sequence length of the model.

## SFT Setup
To begin training the model with Unsloth and TRL:
```bash
python training/sft/train.py
```
