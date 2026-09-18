# MentorAI Project Status

## What is MentorAI?
MentorAI is an open-source project dedicated to building a Socratic tutoring assistant powered by fine-tuned local models (like `Qwen/Qwen3-8B`). The model guides students through mathematical and coding tasks using progressive hints, decomposition, and misconception detection. 

## Current Status: Phase 8 (Web Frontend) Completed

The project is currently transitioning from its initial backend architecture buildout into deployment/operations documentation. The system is functional locally and orchestrated through Docker Compose.

### What is Completed (Implemented)

1. **Phase 1-2 (Model Fine-Tuning):** The training pipeline, Experiment #1, and post-correction evaluations. Experiment #1 SFT adapter is **FROZEN**.
2. **Phase 3-5 (AI Agents):** Planner, Checkpoint, Verifier, and Hint generation agents have been implemented and tested, communicating with local LLMs (via Ollama/vLLM) using Pydantic structured schemas.
3. **Phase 6 (Student Brain):** Persistent PostgreSQL models, Alembic migrations, and relational mastery state tracking. *Note: Qdrant semantic retrieval and Redis ephemeral caching are provisioned in infrastructure but integration is currently PARTIAL/mocked in application code.*
4. **Phase 7 (Backend API):** FastAPI service with RESTful endpoints (`/chat`, `/session`, `/brain`, `/revision`) and dependency injection for the LLM Gateway and Student Brain.
5. **Phase 8 (Frontend):** Next.js App Router application with ChatInterface, LearningPlanSidebar, and MasteryDashboard, communicating via standard REST to the backend.
6. **Orchestration:** Multi-container `docker-compose.yml` defining PostgreSQL, Redis, Qdrant, FastAPI backend, and Next.js frontend.

### What is Planned (Next Steps)
1. **Developer and Operator Documentation:** Layering on tactical documentation (`getting-started.md`, `ollama.md`, etc.) for smooth developer onboarding.
2. **Model Retraining:** Transform the Phase 1 dataset into Socratic format, establish a data mixture ratio to prevent regression, and run Experiment #2 SFT.

### Known Limitations
* **Model Capability vs Product Capability:** While the system architecture works perfectly, the actual model (Experiment #1) is not fully capable of acting as the MentorAI backend until Experiment #2 is complete. Evaluation scripts will fail or produce hallucinations until a more capable model is deployed.
* **Authentication/Security:** The MVP does not currently have robust production authentication protocols or rate-limiting.
* **Test Suite Failures:** The current test suite fails when running `pytest tests/pipeline/` due to a missing `training/` module. These are orphaned tests that need to be migrated or removed in future phases.

## What should NOT be done?
* **DO NOT** restart training or run any fine-tuning for Experiment #1.
* **DO NOT** overwrite any Experiment #1 adapter weights or rescored reports.

## Where is the Application?
* **Backend:** Runs on `localhost:8000` via FastAPI (`apps/api`)
* **Frontend:** Runs on `localhost:3000` via Next.js (`apps/frontend`)
* **Database:** PostgreSQL on `localhost:5432`, Redis on `localhost:6379`, Qdrant on `localhost:6333`.
