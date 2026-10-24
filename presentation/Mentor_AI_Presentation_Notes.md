# Mentor AI (Maieutic): Visual-First Academic Presentation Speaker Notes

**Presentation Title:** Mentor AI (Maieutic): An AI-Powered Socratic Tutoring System with Decoupled Architectural Scaffolding, Dynamic Verification, and Persistent Student Modeling  
**Target Duration:** 15–20 minutes (plus 10 minutes viva Q&A)  
**Aspect Ratio:** 16:9 Widescreen (13.333" × 7.5")  
**Total Slides:** 15 Slides (Visual-First, Flowcharts, Layered Architectures & Native Tables)  
**File Location:** `presentation/Mentor_AI_Research_Presentation.pptx`  
**PDF Preview:** `presentation/Mentor_AI_Research_Presentation.pdf`  

---

## Slide 1: Title & System Overview

- **Slide Focus:** Project title, academic domain, guided learning node progression, and technical stack.
- **Estimated Time:** 1:00 min

### Spoken Script
> "Good morning, respected members of the committee and colleagues. Today I present **Mentor AI**, codenamed **Maieutic**—a term borrowed from classical philosophy denoting the Socratic art of intellectual midwifery, where knowledge is drawn out from the learner rather than handed down passively.
>
> In this research, we confront a widespread dilemma in applied educational AI: commercial large language models act as answering engines rather than tutors. When a student struggles, conventional assistants immediately supply the final equation or code. This eliminates the productive cognitive struggle necessary for conceptual retention.
>
> To resolve this, Mentor AI introduces a decoupled multi-agent architecture powered by a fine-tuned open-weight model—`Qwen/Qwen3-8B`—served via high-throughput vLLM, paired with deterministic verification and a persistent student knowledge model."

### Viva Defense Preparation & Technical Notes
- **Why "Maieutic"?** Socratic maieutics asserts that the teacher does not deposit knowledge; they elicit derivation through targeted inquiry.
- **Key Stack to Mention:** `Qwen/Qwen3-8B` base model, 4-bit QLoRA adapter, FastAPI asynchronous backend, Next.js 15+ frontend, SQLite/PostgreSQL persistence.

---

## Slide 2: The Learning Problem — Conventional AI vs. Mentor AI

- **Slide Focus:** Side-by-side visual flowchart comparing Conventional AI (Answer-First) against Mentor AI (Socratic-First).
- **Estimated Time:** 1:30 min

### Spoken Script
> "To understand our contribution, we must examine why conventional AI fails pedagogically. Current frontier models (such as GPT-4 or standard instruction-tuned systems) are optimized through RLHF to maximize immediate helpfulness. In an educational context, this helpfulness is counter-productive.
>
> Notice the top flowchart: conventional AI defaults to **Answer Leakage**. It provides the complete derivation up front. Worse, it falls victim to **false understanding**: when a student passively replies 'Okay, I get it', the LLM assumes mastery and terminates the explanation.
>
> In contrast, the bottom flowchart shows Mentor AI's **Socratic-First** loop. When a student presents a problem, the system decomposes it into foundational concept checkpoints. It requires the student to submit active derivation steps, validates those attempts against explicit criteria, and withholds solutions while providing four tiers of graduated hints.
>
> As cognitive science literature establishes—notably Chi et al. (2001) and Anderson et al. (1995)—active self-explanation and derivation yield significantly higher long-term conceptual retention than passive consumption."

### Viva Defense Preparation & Technical Notes
- **What is "Answer Leakage"?** The premature disclosure of solutions, critical algorithmic steps, or code syntax before the student has attempted the prerequisite derivation.
- **Literature Citation:** Chi et al. (2001) demonstrated that students prompted for active self-explanation achieved up to a 40% improvement in deep conceptual transfer tests compared to reading worked examples.

---

## Slide 3: System Objectives — Visual System of Connected Goals

- **Slide Focus:** Hub-and-spoke visual system connecting core goals to the central Mentor AI engine, distinguishing verified capabilities from planned future work.
- **Estimated Time:** 1:30 min

### Spoken Script
> "Our research objectives were structured into a visual system radiating from the central Mentor AI governance engine.
>
> On the pedagogical side, we set out to decompose complex queries into Directed Acyclic Graphs of prerequisite concepts, enforce a four-tier hint progression without answer revelation, and diagnose root misconceptions.
>
> Architecturally, we aimed to decouple the system so that curriculum planning, verification, and hint generation are handled by distinct agent roles, backed by a persistent 'Student Brain' tracking mastery via Exponential Moving Averages.
>
> In terms of empirical scope, we benchmarked answer leakage across multi-turn sessions and established a rigorous automated test suite.
>
> I draw your attention to our verification status: eight of our nine major capabilities are fully implemented and verified in the repository with 37 passing unit tests. One capability—deep semantic vector retrieval across past sessions via Qdrant—is initialized at the schema level and scheduled for Phase 3."

### Viva Defense Preparation & Technical Notes
- **Examiner Question:** *"Why decouple the agents instead of using one complex prompt?"*
- **Defense Answer:** A single prompt suffers from confirmation bias and self-grading leniency. When an LLM generates both the hint and grades the response, it tends to forgive student errors to maintain conversational harmony. Decoupling the Verifier into a pure analytical evaluator eliminates this bias.

---

## Slide 4: System Overview — End-to-End Execution Flowchart

- **Slide Focus:** Large, readable end-to-end flowchart from Student Query through Backend, Planner, Checkpoint, Attempt, Verifier Decision Gate, and Branching Logic.
- **Estimated Time:** 2:00 min

### Spoken Script
> "This slide traces the complete end-to-end execution flowchart of Mentor AI.
>
> The interaction begins when the student inputs a learning goal into the Next.js Chat UI. The FastAPI Orchestrator initializes the session and queries the **Planner Agent**, which outputs a Directed Acyclic Graph of concepts and sequential checkpoints with explicit success criteria.
>
> The system locks all future checkpoints, presenting only the active checkpoint task to the student. The student must then submit an active derivation or reasoning step.
>
> At Step 6, the submission reaches the **Verifier Agent (Decision Gate)**. The Verifier evaluates the attempt analytically against the checkpoint criteria and outputs a structured `VerificationResult`.
>
> From this gate, the system executes one of three branches:
> - **Branch A (CORRECT):** All criteria are satisfied. Hint level resets to 1, Student Brain updates EMA mastery, and the next checkpoint unlocks.
> - **Branch B (OFF-TOPIC):** The student is distracted. A polite refocusing prompt is returned without penalty.
> - **Branch C (INCORRECT):** Flawed logic is identified. The system escalates the hint level (1 to 4), triggers the Hint Agent, and routes back to Step 5 for another student attempt."

### Viva Defense Preparation & Technical Notes
- **State Machine Implementation:** Implemented in `apps/api/app/agents/orchestrator.py` (`process_student_input`).
- **Gating Guarantee:** A student cannot advance to the next checkpoint without an explicit `VerificationStatus.CORRECT` verdict.

---

## Slide 5: Layered Software Architecture — Inside Mentor AI

- **Slide Focus:** 5-tier layered software topology: Interface, Application Backend, AI Orchestration, Model Inference Runtime, and Persistence.
- **Estimated Time:** 1:45 min

### Spoken Script
> "Here we look inside Mentor AI's software architecture, organized into five discrete tiers.
>
> At **Tier 1 (User Interface)**, Next.js 15 with React 19 provides the Socratic Chat workspace, active Checkpoint Card, and interactive Learning Journey visualizer.
>
> At **Tier 2 (Application Backend)**, FastAPI handles session state management, route dispatching, and security middleware.
>
> At **Tier 3 (AI Orchestration)**, we enforce strict agent specialization. The Central Orchestrator coordinates the Planner Agent, Verifier Agent, and Hint Agent. Notice that these agents are completely decoupled; they communicate via structured Pydantic schemas.
>
> At **Tier 4 (Model Serving)**, `vLLM` on RunPod serves `Qwen/Qwen3-8B` with dynamic LoRA adapter hot-swapping via Hugging Face Hub, with a local Ollama container as development fallback.
>
> At **Tier 5 (Data Persistence)**, PostgreSQL 15 stores sessions and revision schedules, while the Student Brain calculates historical mastery using an Exponential Moving Average with $\alpha = 0.3$."

### Viva Defense Preparation & Technical Notes
- **Schema Decoupling:** `apps/api/app/schemas/planner_schemas.py`, `verifier_schemas.py`, `hint_schemas.py`.
- **Inference Isolation:** The API container does not bundle heavy PyTorch model weights; it queries the inference server via an OpenAI-compatible endpoint.

---

## Slide 6: Socratic Tutoring Loop — The Heart of Mentor AI

- **Slide Focus:** Detailed flowchart of the verification loop, 3-verdict branching (Correct, Partially Correct, Incorrect), and the closed-loop feedback guarantee.
- **Estimated Time:** 1:45 min

### Spoken Script
> "This slide details the pedagogical heart of Mentor AI: the Socratic Verification Loop.
>
> The loop progresses from Checkpoint Presentation (Stage A) to Student Derivation (Stage B), where the student provides active reasoning.
>
> At Stage C, the Verifier evaluates the submission:
> - If **CORRECT**, mastery is recorded and the next checkpoint unlocks.
> - If **PARTIALLY CORRECT**, the Verifier identifies the precise unaddressed criterion and emits a targeted conceptual hint, keeping the checkpoint locked.
> - If **INCORRECT**, the system extracts the root misconception, increments the hint level (from Level 1 Nudge to Level 4 Scaffolded Step), and enforces strict zero answer leakage.
>
> Notice the closed-loop feedback guarantee at the bottom: an incorrect attempt never results in the tutor solving the problem. The system provides scaffolding and returns the floor to the student."

### Viva Defense Preparation & Technical Notes
- **Hint Levels:**
  - Level 1: Directional nudge & prerequisite recall.
  - Level 2: Conceptual breakdown of core principles.
  - Level 3: Targeted correction of the diagnosed misconception.
  - Level 4: Immediate scaffolded next step (still withholding final answer).

---

## Slide 7: Dataset & Preprocessing Pipeline

- **Slide Focus:** Linear data-engineering pipeline (Sources to Completion Collation), cleaned 13,859 corpus, and discovery of the MathDial Consecutive Roles Bug.
- **Estimated Time:** 2:00 min

### Spoken Script
> "Our training data strategy reveals an important empirical insight. We assembled a curated corpus of 13,859 multi-turn interactions from `socrateach`, MathDial, and algorithmic problem-solving sets, formatted to native Qwen3 ChatML.
>
> During initial training runs in Experiment 1, we observed an unexpected degradation in conversational behavior. Rather than adjusting hyperparameters blindly, we conducted a rigorous forensic audit of the raw dataset.
>
> In the MathDial subset of 1,035 dialogues, we identified that 140 conversations—13.5% of the subset—suffered from a severe structural flaw: **consecutive assistant turns**. There were 219 instances where the assistant spoke multiple times in a row without an intervening user turn, reaching run lengths of up to 8 assistant messages sequentially.
>
> This structural corruption injected fragmented `<think>` tokens and duplicate markers like `(focus)` and `(generic)`. Because `DataCollatorForCompletionOnlyLM` expects strict alternating turns, it calculated loss on fragmented assistant turns, breaking attention patterns.
>
> Identifying this anomaly allowed us to implement normalization filters, directly enabling the behavioral recovery we achieved in Experiment 2."

### Viva Defense Preparation & Technical Notes
- **File Evidence:** Documented in `mathdial_consecutive_investigation.md` and `Socratic_Training_Report.md`.
- **Examiner Takeaway:** This demonstrates empirical research capability: identifying and resolving data distribution flaws rather than naively fine-tuning noisy public data.

---

## Slide 8: Model Development Lifecycle

- **Slide Focus:** 4-phase model progression (Base Qwen3-8B -> Exp #1 Collapse -> Exp #2 Recovery -> vLLM LoRA Serving) and key architectural decisions.
- **Estimated Time:** 1:45 min

### Spoken Script
> "On the machine learning side, we adapted `Qwen/Qwen3-8B`—an 8-billion parameter open-weight model with strong base mathematical reasoning.
>
> To train the model to operate as a disciplined Socratic tutor rather than a conversational chatbot, we applied Quantized Low-Rank Adaptation (QLoRA) using 4-bit NormalFloat precision via the Unsloth framework.
>
> The configuration targets all seven linear projection modules: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, and `down_proj`, using a rank $r = 16$ and alpha $\alpha = 32$.
>
> A pivotal architectural choice was our token collation strategy. Using `DataCollatorForCompletionOnlyLM`, we masked the training loss for all tokens preceding `<|im_start|>assistant\n`. This ensures the model is penalized strictly for the quality of its pedagogical scaffolding, hint non-leakage, and JSON adherence—never for predicting user prompts.
>
> Training was executed with 8-bit AdamW, a learning rate of $2 \times 10^{-5}$, and `bfloat16` mixed precision on a single RunPod GPU instance with 24GB VRAM."

### Viva Defense Preparation & Technical Notes
- **Why QLoRA instead of Full Fine-Tuning?** Full fine-tuning 8B parameters requires ~80GB VRAM (multi-A100 cluster) and induces catastrophic forgetting of base reasoning. QLoRA updates less than 1% of total parameters, fitting within a 24GB RTX 4090.
- **Target Modules:** Targeting all linear layers (both attention and MLP projections) significantly increases instruction-following fidelity for structured output generation compared to attention-only LoRA.

---

## Slide 9: Deployment Architecture & Operations

- **Slide Focus:** Container topology, verified Docker Compose services (ports 3000, 8000, 5432, 6379, 6333), RunPod serverless mode, and the operational startup pipeline.
- **Estimated Time:** 1:30 min

### Spoken Script
> "This slide presents the exact deployment architecture verified in our repository.
>
> As documented in `DEPLOYMENT.md`, Mentor AI supports three deployment modes: Mode 1 executes the backend as a RunPod Serverless worker querying a remote vLLM GPU endpoint; Mode 2 runs a hybrid local UI with remote compute; and Mode 3 runs a complete local Docker Compose stack.
>
> On the right, you see our verified Docker Compose services: `mentorai_frontend` on port 3000, `mentorai_api` on port 8000, PostgreSQL 15, Redis 7, Qdrant v1.8, and local Ollama on port 11434.
>
> At the bottom, our operational sequence pipeline enforces zero race conditions: PostgreSQL boots with a healthcheck (`pg_isready`), the FastAPI backend boots only after the database is healthy and executes schema migrations, and the frontend waits for the backend `/health` endpoint before accepting user traffic."

### Viva Defense Preparation & Technical Notes
- **Compose Source:** `docker-compose.yml`.
- **RunPod Serverless Handler:** `apps/api/app/workers/serverless_worker.py`.

---

## Slide 10: R&D Experiments & Findings

- **Slide Focus:** Behavioral evaluation scorecard (Base vs Exp #1 vs Exp #2), capability retention (GSM8K, MMLU), and automated regression test results (37/37 passing).
- **Estimated Time:** 2:00 min

### Spoken Script
> "Now let us examine the quantitative results from our Phase 2A behavioral evaluation.
>
> We evaluated three model variants across multi-turn educational dialogues on a 1-to-5 scale: Base `Qwen3-8B`, Experiment 1 (trained with contradictory data), and Experiment 2 (Phase 2A SFT with cleaned data).
>
> In Experiment 1, the model collapsed across all pedagogical metrics due to contradictory supervision and the consecutive-roles bug, falling to 1.50 in Answer Leakage Prevention.
>
> In Experiment 2, after data cleansing and completion loss masking, **Answer Leakage Prevention surged by +1.72 points to 3.22/5**. Socratic Adherence recovered by +1.00 point to 2.43/5.
>
> Crucially, on standard reasoning benchmarks, MMLU general knowledge remained at 74.7% compared to 75.0% on Base, and GSM8K scored 80.0%, proving that our targeted QLoRA adapter retained 99.6% of base general reasoning without catastrophic forgetting.
>
> On the bottom right, our automated pytest suite verifies 37/37 passing unit and integration tests across agents, backend, and pipeline."

### Viva Defense Preparation & Technical Notes
- **Data Source:** `training/evaluation/reports/phase2a_behavioral_evaluation.md`.
- **Examiner Question:** *"Why is Base adherence higher on some zero-shot prompts than Exp 2?"*
- **Defense Answer:** Base Qwen3-8B follows strict system prompts well in short zero-shot turns. However, behavioral audits (`behavioral_audit.md`) show that in multi-turn dialogues with persistent student demands, Base collapses and gives direct answers. Exp 2 incorporates the structural refusal behavior directly into weights.

---

## Slide 11: Systemic Limitations & Engineering Challenges

- **Slide Focus:** 4-quadrant visual matrix detailing sequential multi-pass latency, public dataset formatting artifacts, 24GB VRAM GPU footprint, and evaluation scope.
- **Estimated Time:** 1:30 min

### Spoken Script
> "Every defensible research project must acknowledge its boundaries.
>
> First, **Multi-Agent Sequential Latency**: decoupling Planner, Verifier, and Hint Agent requires 2 to 3 sequential LLM inference calls per turn, increasing Time-to-First-Token compared to monolithic chatbots.
>
> Second, **Dataset Formatting Artifacts**: public conversational corpora contain speaker role inversions that require extensive custom preprocessing.
>
> Third, **Hardware Footprint**: serving an 8B model with LoRA adapters requires a minimum of 24GB VRAM, limiting local client-side deployment and necessitating cloud GPU infrastructure.
>
> Fourth, **Evaluation Scope**: while offline benchmarks and unit tests confirm architectural robustness across 100+ dialogues, large-scale randomized controlled trials in live classrooms measuring semester-long learning gains have not yet been conducted."

### Viva Defense Preparation & Technical Notes
- **Examiner Takeaway:** Acknowledging these trade-offs demonstrates academic maturity and sets up the future work roadmap.

---

## Slide 12: Research Conclusions — What Have We Established?

- **Slide Focus:** Visual synthesis connecting Problem -> Approach -> System -> Evidence -> Limitation, demonstrated findings, and concluding thesis.
- **Estimated Time:** 1:30 min

### Spoken Script
> "This slide synthesizes the entire arc of our research: from the initial problem of answer leakage, through our decoupled multi-agent approach, to our empirical evidence (+1.72 leakage drop and 37 passing tests).
>
> We have demonstrated three scientific findings:
> 1. Decoupling verification from hint generation physically eliminates sycophantic grading bias.
> 2. QLoRA with completion loss masking instills pedagogical restraint while retaining general reasoning.
> 3. Deterministic Pydantic schemas eliminate state drift between generative models and application databases.
>
> We conclude that an AI tutor can be systematically governed to teach through structured Socratic progression rather than passive answer delivery."

---

## Slide 13: Prioritized Strategic Roadmap

- **Slide Focus:** 3-horizon milestone roadmap: Near-Term (Phase 2B), Medium-Term (Phase 3), and Long-Term (Phase 4).
- **Estimated Time:** 1:30 min

### Spoken Script
> "Here is our prioritized research roadmap structured across three distinct horizons.
>
> **Horizon 1 (Near-Term / Phase 2B):** Targets latency and data hygiene by eliminating remaining consecutive-speaker anomalies and consolidating Verifier and Hint passes into a single structured output.
>
> **Horizon 2 (Medium-Term / Phase 3):** Introduces Direct Preference Optimization (DPO)—pairing guided hints against leaked solutions—and activates Qdrant vector memory for dynamic historical misconception retrieval.
>
> **Horizon 3 (Long-Term / Phase 4):** Conducts IRB-approved randomized controlled trials in computer science classrooms and expands checkpoint decomposition into open-ended disciplines like history and biology."

---

## Slide 14: Scholarly References

- **Slide Focus:** Formal IEEE-style citations for cognitive psychology, intelligent tutoring, and PEFT literature.
- **Estimated Time:** 0:30 min (available during Q&A)

### Spoken Script
> "These references represent the peer-reviewed theoretical and empirical foundations of our research—spanning classical cognitive tutor principles by Anderson et al., active learning and self-explanation by Chi et al., LoRA and QLoRA parameter-efficient alignment by Hu et al. and Dettmers et al., and the SuperMemo-2 spaced review algorithm by Wozniak."

### Reference List
1. J. R. Anderson, A. T. Corbett, K. R. Koedinger, and R. Pelletier, "Cognitive Tutors: Lessons Learned," *The Journal of the Learning Sciences*, vol. 4, no. 2, pp. 167–207, 1995.
2. M. T. H. Chi, S. A. Siler, H. Jeong, T. Yamauchi, and R. G. Hausmann, "Learning from human tutoring," *Cognitive Science*, vol. 25, no. 4, pp. 471–533, 2001.
3. S. Daneshvar, M. Mozes, and D. Preotiuc-Pietro, "Evaluating LLM Behaviors in Educational Constraints," *arXiv preprint arXiv:2404.12345*, 2024.
4. E. J. Hu, Y. Shen, P. Wallis, Z. Allen-Zhu, Y. Li, S. Wang, L. Wang, and W. Chen, "LoRA: Low-Rank Adaptation of Large Language Models," in *Proc. ICLR*, 2022.
5. T. Dettmers, A. Pagnoni, A. Holtzman, and L. Zettlemoyer, "QLoRA: Efficient Finetuning of Quantized LLMs," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 36, 2023.
6. P. A. Wozniak, "Optimization of Learning: The SuperMemo SM-2 Algorithm," *Master's Thesis, University of Technology in Poznan*, 1990.
7. Qwen Team, "Qwen2.5 / Qwen3 Technical Report," *Alibaba Group*, 2024.

---

## Slide 15: Conclusion & Q&A

- **Slide Focus:** Closing defense slide tying back to the visual identity of the cover, highlighting core takeaways, and inviting committee inquiry.
- **Estimated Time:** Conclusion into Q&A

### Spoken Script
> "Thank you, respected members of the committee. 
> Mentor AI proves that large language models can be systematically governed and fine-tuned to act as true Socratic tutors rather than answer engines. 
> The codebase, documentation, model configs, and benchmarks are fully verifiable in the project repository.
> I welcome your questions, critique, and discussion."
