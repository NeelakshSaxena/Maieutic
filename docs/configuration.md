# Configuration

MentorAI configuration is driven entirely by environment variables. When running in Docker, these are typically sourced from the `docker-compose.yml` environment blocks or a `.env` file.

## Backend Configuration (FastAPI)

- `TRANSFORM_BASE_URL` / `JUDGE_BASE_URL`: OpenAI-compatible endpoint (local default: `http://host.docker.internal:11434/v1`). `LLM_BASE_URL` is an optional fallback.
- `TRANSFORM_MODEL` / `JUDGE_MODEL`: Model to request (local default: `qwen3.5-aggressive:latest`).
- `TRANSFORM_API_KEY` / `JUDGE_API_KEY`: Any non-empty string for Ollama (`ollama`).
- `LLM_TIMEOUT_SECONDS`: Per-request inference timeout (default: `300`).
- `DATABASE_URL`: Connection string for PostgreSQL (Compose sets `postgresql+psycopg2://postgres:postgres@postgres:5432/mentorai`).
- `REDIS_URL`: Connection string for Redis (Compose sets `redis://redis:6379`).
- `QDRANT_URL`: Connection string for Qdrant (default: `http://qdrant:6333`).

## Frontend Configuration (Next.js)

- `NEXT_PUBLIC_API_URL`: The URL that the browser will use to contact the backend (default: `/api`, proxied by Next.js to `API_INTERNAL_URL`).

*Note:* Because `NEXT_PUBLIC_` variables are baked into the frontend build at compile time, if you change this URL, you must rebuild the frontend container (`docker compose build frontend`).
