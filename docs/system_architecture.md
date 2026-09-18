# MentorAI — System Architecture

## 1. Architecture

MVP uses a modular monolithic architecture orchestrated via Docker Compose.

**Frontend:**
- Next.js (App Router)
- React
- Tailwind CSS & shadcn/ui

**Backend:**
- FastAPI (Python 3.11+)
- Dependency Injection (StudentBrainService, LLMClient)

**AI Orchestrator (Backend Module):**
- Model Gateway (LLMClient)
  - Planner Agent
  - Checkpoint Generator
  - Verifier Agent
  - Hint Generator
  - Misconception Detector

**Data / Persistence (Student Brain):**
- PostgreSQL (Primary store via SQLAlchemy/Alembic)
- Redis (Fast transient state / PubSub)
- Qdrant (Semantic search / Concept embeddings)

**Inference:**
- Local: Ollama (qwen2 / qwen2-socratic)
- Production Target: RunPod + vLLM

**Training:**
- RunPod + Hugging Face + PEFT/TRL

## 2. Request Flow

```text
Student (Browser)
    |
    v
Next.js (Port 3000)
    |
    v
FastAPI (Port 8000)
    |
    v
Tutoring Orchestrator
    |
    +--> Student Brain Service (PostgreSQL / Qdrant)
    |
    +--> LLM Gateway (Ollama port 11434)
    |      +--> Planner / Checkpoint / Verifier / Hint
    |
    v
Response (Structured JSON)
    |
    v
Student (Browser via Next.js)
```

**Evaluation / Validation Flow:**

When a student responds to a checkpoint:

1. **Verifier:** Checks if the response is correct, incorrect, partial, or off-topic.
2. **Mastery Engine:** Updates the Student Brain (EMA model in PostgreSQL).
3. **Misconception Detector:** Logs specific conceptual errors.
4. **Hint Generator:** (If needed) Generates exactly one HintLevel based on the Verification result.

## 3. Infrastructure (MVP)

All components run locally via `docker-compose.yml`:
- `frontend` (Next.js)
- `api` (FastAPI)
- `db` (PostgreSQL)
- `redis` (Redis)
- `qdrant` (Qdrant)

*Note: Ollama runs on the host machine to easily leverage Apple Silicon / local GPUs, and is accessed via the `host.docker.internal` bridge.*

## 4. Model Gateway

All model calls pass through `LLMClient.generate_structured_output()`.

This abstraction allows:
- **Development:** Ollama (`qwen2`)
- **Staging/Production:** RunPod + vLLM (`qwen-8b-socratic`)

The Orchestrator defines Pydantic schemas, which the Model Gateway forces the LLM to output. If the LLM hallucinates schema structure, the Gateway catches the `ValidationError` and automatically retries with error feedback.

## 5. State Machine

The session progression is dictated by the Backend logic, *not* the LLM. The LLM only recommends verification states, and the FastAPI application transitions the session state.

```text
SESSION_CREATED
    |
PLANNING
    |
READY
    |
CHECKPOINT_ACTIVE
    |
AWAITING_RESPONSE
    |
VERIFYING
    |
    +--> CORRECT --> CHECKPOINT_COMPLETED
    |
    +--> PARTIAL --> HINT
    |
    +--> INCORRECT --> MISCONCEPTION
                            |
                            v
                           HINT
                            |
                            v
                       RETRY_REQUIRED

CHECKPOINT_COMPLETED
    |
    +--> MORE_CHECKPOINTS --> CHECKPOINT_ACTIVE
    |
    +--> COMPLETE --> SESSION_COMPLETE
```