# Phase 2 — Model Fine-Tuning

## Status

`INCOMPLETE — Experiment #1 completed; Experiment #2 not started.`

The Phase 2 infrastructure is fully implemented and the first complete SFT experiment was executed and evaluated. However, the final Maieutic tutoring model has not yet been achieved. Experiment #1 has been identified as a diagnostic run due to contradictory data supervision, and Experiment #2 is currently frozen pending data transformation and verification.

---

## Original Objective

The original objective of Phase 2 is to fine-tune `Qwen/Qwen3-8B` (transitioned from the originally planned 12–14B model size) into a Socratic tutor that:
* **Avoids unnecessary direct answers:** Guides the student rather than outputting solutions.
* **Decomposes problems:** Breaks complex mathematical or coding problems into manageable parts.
* **Provides checkpoints:** Asks the student to confirm understanding before moving forward.
* **Gives progressive hints:** Gradually details the concepts instead of revealing the answer.
* **Detects misconceptions:** Recognizes errors in student reasoning and addresses them gently.
* **Preserves student agency:** Promotes active thinking rather than passive reading.
* **Maintains reasoning capability:** Retains high logic capability (e.g. GSM8K / MMLU benchmarks).
* **Remains factually/technically useful:** Ensures tutoring hints are mathematically and logically correct.

*Note: Experiment #1 failed to achieve this objective because the training supervision targets were contradictory.*

---

## Hardware & Infrastructure

The training and evaluation were performed in the following environment:
* **GPU:** NVIDIA RTX 4090 24GB VRAM
* **RAM:** 31 GB
* **CPU:** 8 vCPU
* **Disk Space:** ~130 GB total (~100 GB usable workspace)
* **CUDA / PyTorch:** PyTorch `2.8.0+cu128`
* **Core Libraries:**
  * `transformers`: `5.5.0`
  * `peft`: `0.20.0`
  * `trl`: `0.24.0`
  * `unsloth`: `2026.8.18` (used to accelerate QLoRA training)

---

## Base Model

* **Canonical Base Model:** `Qwen/Qwen3-8B`
* **Deviation Note:** While the original project specification called for a 12–14B parameter model, Qwen3-8B was chosen for the SFT pipeline to maximize efficiency and GPU utilization on a single RTX 4090.

---

## Training Configuration (Experiment #1)

* **Method:** QLoRA (4-bit quantization via bitsandbytes)
* **LoRA Rank (r):** 16
* **LoRA Alpha:** 32
* **LoRA Dropout:** 0.05
* **Target Modules:** `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]`
* **Max Sequence Length:** 4096 tokens
* **Learning Rate:** 2e-5
* **LR Scheduler:** Cosine
* **Epochs:** 1
* **Steps:** 2586
* **Effective Batch Size:** 8 (per-device batch size 2 × gradient accumulation steps 4)
* **Quantization Precision:** 4-bit NormalFloat (NF4) / Double Quantization enabled
* **Precision:** bfloat16

---

## Data Pipeline

The data flows through the pipeline in the following sequence:
```
Phase 0 (Raw Datasets) 
    ↓
Phase 1 (Cleaned & De-duplicated Datasets)
    ↓
Phase 1.5 (Socratic Target Transformation) [NEW]
    ↓
Phase 2 (Supervised Fine-Tuning)
```

### Phase 0 / Phase 1 Statistics
* **Raw Source Samples:** ~22,000
* **Cleaned / De-duplicated Samples:** 21,876 (56 removed during cleaning; 68 exact duplicates removed)
* **Processed Datasets:** `lmsys_processed.jsonl` and `NuminaMath_processed.jsonl`
* **Token Statistics (Cleaned):**
  * Total tokens: 16,271,731
  * Average tokens per sample: 743.82
  * Minimum: 60 tokens
  * Maximum: 219,154 tokens (This extreme sequence-length outlier was truncated during training via the `max_seq_length=4096` configuration).

---

## Critical Finding — Contradictory Supervision

Forensic analysis of Experiment #1 revealed a fundamental data construction bug. 

* **The Issue:** The training dataset injected a Socratic system prompt (`"You are MentorAI..."`) but preserved the raw, direct-answer assistant targets from the source datasets (LMSYS / NuminaMath).
* **The Contradiction:**
  * **System Message:** *"You are a Socratic tutor. You must never give the student the direct answer."*
  * **Assistant Target:** Gives the direct answer / full code / solution immediately.
* **The Outcome:** The model learned to ignore the system prompt because it was penalized during training if it did not output the direct answer. This was the primary reason SFT tutoring quality was extremely poor.

---

## Experiment #1 Identification

* **Experiment Identifier:** `experiment_01_contradictory_socratic_supervision`
* **Status:** **FROZEN**. The adapters, configs, and evaluations for this run are locked and must not be overwritten or retrained.
* **Hugging Face Backup:** Backed up privately to `NeelakshSaxena/mentorai`.

---

## Evaluation Framework

* **Benchmark:** Fixed 100-sample benchmark (`mentorai_benchmark.jsonl`), separated from the training set.
* **Judge:** GPT-4-based LLM Judge scoring across 6 key rubrics (1–5 scale).
* **Metric Inversion Corrected:** The original `answer_leakage` metric was inverted—the LLM judge was penalizing high leakage prevention rather than high leakage (5 meant severe leakage, which was reported incorrectly as a success). The metric has been renamed to `answer_leakage_prevention` with an explicit rubric (1 = severe/direct answer leakage; 5 = strong answer-leakage prevention).
* **Evaluation Rescoring Status:** `COMPLETE` (Successfully run in `task-939`).

### Corrected Baseline Results (Post-Correction Rescored)
* **Socratic Adherence:** 3.98 / 5
* **Hint Quality:** 3.88 / 5
* **Answer Leakage Prevention:** 3.54 / 5
* **Decomposition:** 3.89 / 5
* **Misconception Detection:** 3.22 / 5
* **Correctness:** 4.34 / 5
* **GSM8K (Retention):** 92.0%
* **MMLU (Retention):** 75.6%

### Corrected Experiment #1 SFT Results (Post-Correction Rescored)
* **Socratic Adherence:** 1.70 / 5
* **Hint Quality:** 1.81 / 5
* **Answer Leakage Prevention:** 1.70 / 5 (Severe leakage; confirms model ignored system prompt due to contradictory supervision targets)
* **Decomposition:** 2.30 / 5
* **Misconception Detection:** 1.80 / 5
* **Correctness:** 3.08 / 5
* **GSM8K (Retention):** 72.0%
* **MMLU (Retention):** 75.2%

---

## Analysis of Outcomes

### What Worked
* QLora training pipeline executed without infrastructure failures.
* Model checkpointing and Hugging Face integration worked flawlessly.
* MMLU capability was successfully retained.
* Staged pipeline is fully reproducible.

### What Failed / Needs Fixing
* Training targets were direct answers instead of Socratic responses.
* The LLM judge metric was inverted (now fixed).
* Qwen3-8B Jinja template fallback generated empty `<think>` tags when `enable_thinking` was undefined.
* Tutor response metrics (Socratic quality, hints, misconceptions) regressed significantly.
* GSM8K reasoning capability degraded (92.0% → 72.0%).

---

## Phase 1.5 — Socratic Target Transformation

To correct the contradictory supervision, Phase 1.5 was introduced to transform the direct assistant targets into high-quality Socratic responses before fine-tuning:
```
Original direct targets ➔ LLM-based Socratic transformation ➔ Quality Filter (leakage check) ➔ Socratic Pilot Dataset
```
* **Tools:**
  * `transform_socratic.py`: Transformed responses using pedagogical templates.
  * `quality_filter.py`: Checked for answer leakage and technical correctness.
  * `build_pilot_dataset.py`: Orchestrated pilot creation.
* **300-Sample Pilot Status:** `COMPLETE` (Successfully run in `task-940`).
  * Source Examples Examined: 346
  * Transformed Accepted Examples: 300
  * Rejected Examples: 46 (Rejection Rate: 13.29%)
  * Answer Leakage Rate: 0.0%
  * Technical Correctness Rate: 100.0%
  * Category Distribution: Math: 153, General Chat: 147
  * Average Response Token Length: 37.4 tokens

---

## Experiment #2 — NOT STARTED

* **Status:** **FROZEN**.
* **Prerequisites for Launch:**
  * Complete corrected rescoring of Base and SFT models.
  * Complete 300-sample Phase 1.5 pilot data generation and audit.
  * Finalize the full Socratic dataset transformation.
  * Define data mixtures to prevent GSM8K regression.
  * Configure Qwen3-8B reasoning token handling.

---

## Hugging Face Backup

* **Private Repository:** `NeelakshSaxena/mentorai`
* **Contents:**
  * Experiment #1 QLoRA adapter (`adapter_model.safetensors`, `adapter_config.json`)
  * Tokenizer and Jinja chat templates
  * Pre-rescoring and post-rescoring evaluation reports (`evaluation/`)
  * Pilot artifacts (`pilot/` - once generated)
  * Manifest metadata (`experiment_metadata.json`)

---

## Resume Checklist

When starting a fresh RunPod instance tomorrow:
1. Clone the repository: `git clone https://github.com/NeelakshSaxena/Maieutic.git`
2. Install dependencies: `pip install -r training/requirements.txt`
3. Login to Hugging Face: `export HF_TOKEN="..."; huggingface-cli login --token $HF_TOKEN`
4. Download adapter: `huggingface-cli download NeelakshSaxena/mentorai --local-dir ./outputs/qwen-8b-socratic-v1`
5. Load and verify adapter using the snippet in `RESTORE.md`.

---

## Stop Conditions

Do NOT start training for Experiment #2 until:
1. Rescoring reports are fully parsed and analyzed.
2. The 300-sample pilot dataset passes quality-filter metrics (>95% correctness, <5% leakage).
3. Reasoning-retention strategies (e.g. data replay mixture) are formulated.
4. Reasoning token template logic is verified.

---

## Phase 2 TODO List

### P0 — MUST DO FIRST
- [ ] Monitor and finish corrected rescoring (`task-939`).
- [ ] Monitor and finish 300-sample pilot dataset (`task-940`).
- [ ] Run quality audit on generated pilot dataset.
- [ ] Finalize Qwen3-8B reasoning template fixes.

### P1 — BEFORE EXPERIMENT #2
- [ ] Transform the full 21k Phase 1 dataset into Socratic format.
- [ ] Define the positive-tutor to reasoning-replay data mixture ratio.
- [ ] Run pre-training evaluation tests.

### P2 — EXPERIMENT #2
- [ ] Execute SFT QLoRA training on Maieutic dataset.
- [ ] Monitor loss and gradient norms.

### P3 — AFTER TRAINING
- [ ] Evaluate Socratic quality, hint quality, misconception detection, correctness, and answer leakage prevention.
- [ ] Check GSM8K and MMLU retention metrics.
