Description
 
> Build an AI-powered Socratic tutor that teaches instead of directly answering questions. The tutor breaks any problem into prerequisite concepts and checkpoint-based tasks, verifies each student response, detects misconceptions, provides progressively stronger hints, and only unlocks the next checkpoint once the learner demonstrates understanding.
 
The system supports Mathematics, Programming, Data Structures & Algorithms, and Computer Science fundamentals. Every learning session contributes to a personalized Student Brain (LLMWiki), a living knowledge graph that stores mastery, misconceptions, learning history, project experience, revision schedules, and relationships between concepts. This enables highly personalized tutoring, adaptive revision, interview preparation, and long-term knowledge retention.
 
The product uses a fine-tuned 12–14B open-weight language model trained on curated tutoring, reasoning, programming, and educational datasets. The model is optimized for Socratic questioning, checkpoint verification, hint generation, misconception detection, and adaptive teaching instead of direct answer generation.
 
The backend records every tutoring interaction as structured training data, allowing continual improvement of the model and building a proprietary dataset of misconceptions, effective hints, and mastery progression.
 
 
 
 
---
 
Claude Project Prompt
 
You are the Lead AI Architect and Technical Program Manager for MentorAI.
 
Your role is NOT to simply generate code.
 
You are responsible for planning, reviewing, validating, documenting, and implementing the product like a senior engineering team.
 
====================================================
 
PROJECT
 
MentorAI
 
An AI tutor that teaches through Socratic questioning.
 
The tutor should never immediately reveal answers.
 
Instead it should
 
• Break problems into dependency graphs
• Create checkpoints
• Verify student responses
• Detect misconceptions
• Generate progressively stronger hints
• Unlock the next checkpoint only after mastery
 
The objective is understanding rather than answer generation.
 
====================================================
 
SUPPORTED DOMAINS
 
• Mathematics
• Programming
• Data Structures
• Algorithms
• Computer Science
 
====================================================
 
CORE COMPONENTS
 
Planner
 
↓
 
Checkpoint Generator
 
↓
 
Verifier
 
↓
 
Hint Generator
 
↓
 
Mastery Tracker
 
↓
 
Student Brain (LLMWiki)
 
↓
 
Analytics
 
====================================================
 
STUDENT BRAIN
 
Each student owns a persistent knowledge graph.
 
Store
 
• Concepts
• Mastery
• Confidence
• Attempts
• Mistakes
• Hints used
• Personal explanations
• AI explanations
• Projects
• Interview questions
• Revision schedule
• Knowledge graph
• Relationships
 
====================================================
 
MISCONCEPTION DATABASE
 
Store
 
Concept
 
Wrong Answer
 
Correct Concept
 
Hint Sequence
 
Recovery Success Rate
 
Frequency
 
Difficulty
 
====================================================
 
MODEL
 
Use an open-weight 12–14B model initially.
 
Fine-tune it for Socratic tutoring.
 
Never optimize it for direct answering.
 
====================================================
 
DATASETS
 
Math
 
• MathInstruct
• NuminaMath
• MATH
• GSM8K
 
Programming
 
• APPS
• MBPP
• HumanEval
• CodeContests
 
Tutoring
 
• SocraticQA
• OpenTutor
• WildChat
• LMSYS Chat
 
Educational
 
• ASSISTments
• EdNet
• Riiid
 
Alignment
 
• UltraFeedback
 
====================================================
 
YOUR RESPONSIBILITIES
 
For every phase produce
 
1. Architecture
 
2. Deliverables
 
3. Folder structure
 
4. API Design
 
5. Database schema
 
6. UI
 
7. Agent prompts
 
8. Tests
 
9. Verification checklist
 
10. Stop conditions
 
11. Documentation
 
12. Risks
 
13. Improvements
 
Never move to the next phase until every verification item passes.
 
Think like a Staff AI Engineer building a production startup.
 
 
---
 
Development Roadmap
 
Phase 0 — Research & Dataset
 
Deliverables
 
Dataset downloader
 
Dataset cleaner
 
Dataset normalizer
 
Unified JSON schema
 
Dataset statistics
 
Deduplication
 
 
Agent Prompt
 
> Download every approved dataset. Normalize into a unified schema. Remove duplicates, low-quality samples, and direct-answer examples that conflict with Socratic tutoring. Produce dataset quality metrics and coverage reports.
 
 
 
Verify
 
Downloads complete
 
No corrupted files
 
Unified schema
 
Duplicate rate <5%
 
Coverage report generated
 
 
Stop
 
Dataset is production-ready.
 
 
---
 
Phase 1 — Data Pipeline
 
Deliverables
 
Parser
 
Chunker
 
Metadata
 
Concept extraction
 
Knowledge graph generation
 
 
Verify
 
Every sample parsed
 
Concepts extracted
 
Relationships generated
 
 
Stop
 
Every sample can generate checkpoints.
 
 
---
 
Phase 2 — Model Fine-tuning
 
Deliverables
 
Base model selected
 
LoRA configuration
 
Training pipeline
 
Evaluation pipeline
 
 
Verify
 
Loss converges
 
No catastrophic forgetting
 
Better tutoring score
 
Better hint quality
 
 
Stop
 
Model consistently behaves as a tutor.
 
 
---
 
Phase 3 — Planner Agent
 
Deliverables
 
Planner
 
Dependency Graph
 
Learning Objectives
 
Checkpoint generator
 
Verification
 
Planner always creates
 
Prerequisites
 
↓
 
Concepts
 
↓
 
Dependencies
 
↓
 
Checklist
 
Stop
 
95% correct planning.
 
 
---
 
Phase 4 — Verifier
 
Deliverables
 
Response classifier
 
Misconception detector
 
Mastery estimator
 
Verify
 
Correct answers accepted
 
Wrong answers rejected
 
Misconceptions classified
 
Stop
 
High verification accuracy.
 
 
---
 
Phase 5 — Hint Agent
 
Deliverables
 
4-level hints
 
Adaptive hints
 
No answer leakage
 
Verify
 
Hints become progressively stronger
 
Never reveal answer prematurely
 
Stop
 
Hint policy passes evaluation.
 
 
---
 
Phase 6 — Student Brain
 
Deliverables
 
Knowledge graph
 
Memory
 
Revision engine
 
Concept linking
 
Verify
 
Knowledge updates
 
Relationships built
 
Revision suggestions generated
 
Stop
 
Brain survives multiple sessions.
 
 
---
 
Phase 7 — Backend
 
FastAPI
 
Redis
 
Postgres
 
Qdrant
 
Authentication
 
Analytics
 
Verification
 
API tests
 
Database migrations
 
Performance
 
Stop
 
API stable.
 
 
---
 
Phase 8 — Frontend
 
React
 
Next.js
 
Chat
 
Checklist
 
Brain Viewer
 
Progress
 
Dashboard
 
Verify
 
Complete flow works
 
Stop
 
Production-ready MVP.
 
 
---
 
Phase 9 — Analytics
 
Mastery
 
Drop-offs
 
Misconceptions
 
Hint effectiveness
 
Difficulty
 
Revision
 
Verify
 
All metrics visible
 
Stop
 
Dashboard complete.
 
 
---
 
Fine-tuning
 
Since you're using Runpod, a practical stack is:
 
GPU: RTX 4090 (24 GB) for experimentation; A100 80 GB or H100 if you later train larger models or need faster throughput.
 
Frameworks:
 
Hugging Face Transformers
 
TRL (for DPO/ORPO)
 
PEFT (LoRA/QLoRA)
 
Unsloth (fast LoRA fine-tuning)
 
bitsandbytes (4-bit quantization)
 
Accelerate
 
DeepSpeed (optional for scaling)
 
Weights & Biases or MLflow for experiment tracking
 
 
 
Training progression:
 
1. Instruction Fine-tuning (SFT)
 
 
2. Socratic Tutor Fine-tuning
 
 
3. Preference Optimization (DPO/ORPO)
 
 
4. Evaluation
 
 
5. Quantization
 
 
6. Deployment (vLLM or SGLang for efficient inference)
 
 
 
 
---
 
Essential Documentation to Study
 
LLM & Fine-tuning
 
Hugging Face Transformers
 
Hugging Face Datasets
 
TRL
 
PEFT
 
Unsloth
 
bitsandbytes
 
Accelerate
 
DeepSpeed
 
vLLM
 
SGLang
 
 
Data
 
Apache Arrow
 
Parquet
 
JSONL best practices
 
 
Retrieval & Memory
 
Qdrant
 
FAISS
 
Knowledge Graph concepts
 
GraphRAG
 
 
Backend
 
FastAPI
 
PostgreSQL
 
Redis
 
SQLAlchemy
 
Alembic
 
 
Frontend
 
Next.js
 
React
 
Tailwind CSS
 
shadcn/ui
 
 
Observability
 
Langfuse
 
OpenTelemetry
 
Weights & Biases
 
 
AI Evaluation
 
OpenAI Evals (concepts)
 
DeepEval
 
Ragas (if you later add retrieval)
 
 
This roadmap is intentionally structured so each phase produces a working artifact, has measurable verification criteria, and can be completed independently before moving to the next stage. That makes it well suited for iterative development with coding agents like Claude Code or Codex.