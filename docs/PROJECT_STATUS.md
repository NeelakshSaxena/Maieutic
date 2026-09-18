# Maieutic Project Status

## What is Maieutic?
Maieutic is a project dedicated to fine-tuning `Qwen/Qwen3-8B` into a highly capable, factually correct Socratic tutoring assistant. The model guides students through mathematical and coding tasks using progressive hints, decomposition, and misconception detection, rather than providing direct solutions.

## What Phase are we in?
We are currently in **Phase 2 (Model Fine-Tuning)**. Specifically, we have implemented the pipeline, run a diagnostic Experiment #1, and are currently in the middle of **Phase 1.5 (Socratic Target Transformation)** to prepare clean data for Experiment #2.

## What is Completed?
* The training and evaluation codebase is fully built and verified.
* **Experiment #1** SFT adapter was saved and is **FROZEN**.
* Post-correction evaluation rescoring is **100% complete** for both Base and SFT models.
* The 300-sample Socratic pilot dataset generation is **100% complete**.
* A single, private Hugging Face repository (`NeelakshSaxena/mentorai`) has been created, and the Experiment #1 adapter, metadata, rescoring reports, and Phase 1.5 pilot artifacts are uploaded and verified.

## What Failed?
* **Experiment #1 Contradictory Supervision:** The training data injected a Socratic system prompt but kept raw direct-answer targets. The model was trained to ignore the system prompt.
* **GSM8K Capability Regression:** The math reasoning capability dropped from 92.0% to 72.0% during Experiment #1 SFT.
* **Judge Metric Inversion:** The previous `answer_leakage` evaluation was inverted (now fixed and renamed to `answer_leakage_prevention`).

## What is Currently Running?
* **None.** All tasks have finished successfully and outputs are securely backed up.

## What should NOT be done?
* **DO NOT** restart training or run any fine-tuning (Experiment #2 remains **FROZEN**).
* **DO NOT** overwrite any Experiment #1 adapter weights or rescored reports.
* **DO NOT** make the Hugging Face repository public.

## What should be done next?
1. Transform the full Phase 1 dataset (21k samples) into Socratic format using Phase 1.5 pipelines.
2. Establish the Socratic tutoring to reasoning-replay data mixture ratio (to prevent GSM8K regression).
3. Finalize the tokenizer/template kwargs for reasoning tokens, then run Experiment #2 SFT.

## Where is the Trained Model?
* **Local:** `./outputs/qwen-8b-socratic-v1/`
* **Remote (Private):** `NeelakshSaxena/mentorai` on Hugging Face (LoRA adapter, configuration, tokenizer).

## Where are the Evaluation Artifacts?
* **Local:** `/workspace/Maieutic/training/evaluation/`
* **Remote (Private):** `/evaluation/` subdirectory inside `NeelakshSaxena/mentorai`.
