# Configuration

MentorAI configuration is driven entirely by environment variables. When running in Docker, these are typically sourced from the `docker-compose.yml` environment blocks or a `.env` file.

## Backend Configuration (FastAPI)

- `LLM_BASE_URL`: The URL for the local Ollama instance (default: `http://host.docker.internal:11434/v1`).
- `LLM_MODEL`: The model name to request from Ollama (default: `qwen2`).
- `LLM_API_KEY`: Dummy API key for the local endpoint (default: `local`).
- `DATABASE_URL`: Connection string for PostgreSQL (default: `postgresql://postgres:postgres@db:5432/postgres`).
- `REDIS_URL`: Connection string for Redis (default: `redis://redis:6379/0`).
- `QDRANT_URL`: Connection string for Qdrant (default: `http://qdrant:6333`).

## Frontend Configuration (Next.js)

- `NEXT_PUBLIC_API_URL`: The URL that the browser will use to contact the backend (default: `http://localhost:8000`).

*Note:* Because `NEXT_PUBLIC_` variables are baked into the frontend build at compile time, if you change this URL, you must rebuild the frontend container (`docker compose build frontend`).
