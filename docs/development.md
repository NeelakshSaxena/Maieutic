# Development Guide

This guide is for developers looking to modify the MentorAI source code.

## Running Locally (Without Docker)

While Docker Compose is recommended for running the entire stack, sometimes it's easier to run the frontend or backend locally for rapid iteration and hot-reloading.

### 1. Start Infrastructure Only
You still need the databases. Start only the data layer using Docker:
```bash
docker compose up -d db redis qdrant
```

### 2. Run the Backend
```bash
cd apps/api
# Create a virtual environment and activate it
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Run FastAPI
# IMPORTANT: Override the Database URLs to point to localhost instead of Docker service names
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres \
REDIS_URL=redis://localhost:6379/0 \
QDRANT_URL=http://localhost:6333 \
LLM_BASE_URL=http://localhost:11434/v1 \
uvicorn app.main:app --reload --port 8000
```

### 3. Run the Frontend
```bash
cd apps/frontend
npm install
npm run dev
```

## Adding New AI Agents

If you are extending the Orchestrator with new agents:
1. Define the input/output schemas in `apps/api/app/schemas/`.
2. Ensure the output schema inherits from `pydantic.BaseModel`.
3. Create the agent prompt and logic in `apps/api/app/agents/`.
4. Inject the `LLMClient` and call `generate_structured_output()`.
5. Update `system_architecture.md` and `tutoring_protocol.md` to reflect the new state flow.
