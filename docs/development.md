# Development Guide

This guide is for developers looking to modify the MentorAI source code.

## Running Locally (Without Docker)

Docker Compose is the verified way to run everything (see [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)). To iterate on the backend or frontend with hot reload instead:

### Backend (`apps/api`)
Dependencies are declared in `apps/api/pyproject.toml` (Poetry). Without `DATABASE_URL` the backend falls back to a local SQLite file (`./maieutic.db`, relative to the working directory).
```powershell
cd apps/api
poetry install
$env:TRANSFORM_BASE_URL = "http://localhost:11434/v1"   # Ollama's published port on the host
$env:TRANSFORM_MODEL = "qwen3.5-aggressive:latest"
$env:TRANSFORM_API_KEY = "ollama"
poetry run uvicorn app.main:app --reload --port 8000
```
The compose Postgres is not published to the host; to use it from a host process you must add a `ports` mapping yourself.

### Frontend (`apps/frontend`)
```powershell
cd apps/frontend
npm ci
$env:API_INTERNAL_URL = "http://127.0.0.1:8000"
npm run dev
```

## Adding New AI Agents

If you are extending the Orchestrator with new agents:
1. Define the input/output schemas in `apps/api/app/schemas/`.
2. Ensure the output schema inherits from `pydantic.BaseModel`.
3. Create the agent prompt and logic in `apps/api/app/agents/`.
4. Inject the `LLMClient` and call `generate_structured()`.
5. Update `system_architecture.md` and `tutoring_protocol.md` to reflect the new state flow.
