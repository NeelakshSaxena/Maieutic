# Maieutic Documentation

Welcome to **Maieutic**, the open-source Socratic tutoring agent project (formerly MentorAI). 

Maieutic aims to fine-tune large language models (specifically Qwen3-8B) to guide students through Socratic dialogue rather than giving direct answers.

---

## 30-Second Project Status

* **Current Phase:** **Phase 2 (Fine-tuning & Evaluation)** - Currently working on **Phase 1.5 Socratic Target Transformation**.
* **Latest Run:** `experiment_01_contradictory_socratic_supervision` completed (FROZEN due to contradictory direct-answer target data).
* **Next SFT Experiment:** `Experiment #2` (FROZEN pending data transformation, reasoning token fix, and baseline evaluation rescoring).
* **Private Backup:** `NeelakshSaxena/mentorai` on Hugging Face (contains Experiment #1 adapter, tokenizer, and evaluation reports).
* **Full Status Report:** See [docs/PROJECT_STATUS.md](file:///workspace/Maieutic/docs/PROJECT_STATUS.md).

---

## Documentation Index

### Core Technical Documents
* [PRD](file:///workspace/Maieutic/docs/prd.md) — Product requirements and MVP scope.
* [System Architecture](file:///workspace/Maieutic/docs/system_architecture.md) — Overall system structure.
* [AI Architecture](file:///workspace/Maieutic/docs/ai_architecture.md) — AI agents and model architecture.
* [Student Brain](file:///workspace/Maieutic/docs/student_brain.md) — Persistent student memory and mastery system.
* [Knowledge Graph](file:///workspace/Maieutic/docs/knowledge_graph.md) — Concept graph and relationships.
* [Misconception System](file:///workspace/Maieutic/docs/misconception_system.md) — Misconception detection and recovery.
* [Tutoring Protocol](file:///workspace/Maieutic/docs/tutoring_protocol.md) — Rules governing Socratic tutoring behavior.
* [Data Pipeline](file:///workspace/Maieutic/docs/data_pipeline.md) — Ingestion, deduplication, and transformation.
* [Model Training](file:///workspace/Maieutic/docs/model_training.md) — Fine-tuning and RunPod training logs.
* [Model Evaluation](file:///workspace/Maieutic/docs/model_evaluation.md) — AI evaluation benchmarks and LLM judge rubrics.

### Phases & Progress
* **Phase 0 / Phase 1 (Ingestion & Cleaning):** Documented in [docs/data_pipeline.md](file:///workspace/Maieutic/docs/data_pipeline.md).
* **Phase 1.5 (Socratic Target Transformation):** Documented in [docs/phases/phase_2.md#phase-15--socratic-target-transformation](file:///workspace/Maieutic/docs/phases/phase_2.md#phase-15--socratic-target-transformation).
* **Phase 2 (Model Fine-Tuning):** See the definitive handoff document at [docs/phases/phase_2.md](file:///workspace/Maieutic/docs/phases/phase_2.md).
* **Hugging Face Restore Instructions:** Documented in [RESTORE.md](file:///workspace/Maieutic/RESTORE.md).

---

## Engineering Rule

Code must conform to these documents. If the implementation conflicts with the documentation:
1. Identify the conflict.
2. Explain it.
3. Update the documentation if the architecture changes.
4. Implement the code.

Documentation and code must never silently diverge.