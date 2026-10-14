# Docker Architecture

MentorAI's local stack is defined in [`docker-compose.yml`](../docker-compose.yml). Images are built from [`Dockerfile.api`](../Dockerfile.api) and [`Dockerfile.frontend`](../Dockerfile.frontend). Step-by-step operation is in [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md).

## Services

| Compose service | Container | Host port | Description |
|---|---|---|---|
| `frontend` | `mentorai_frontend` | `${FRONTEND_PORT:-3000}` -> 3000 | Next.js standalone server: chat UI plus server-side `/api/*` and `/health/*` proxying to `api`. |
| `api` | `mentorai_api` | 8000 | FastAPI backend; runs Alembic migrations on start, then Uvicorn. Health-checked via `/health`. |
| `postgres` | `mentorai_postgres` | none (internal 5432) | PostgreSQL 15; database `mentorai`. Health-checked with `pg_isready`. |
| `redis` | `mentorai_redis` | none (internal 6379) | Provisioned; not used by the current application code. |
| `qdrant` | `mentorai_qdrant` | none (internal 6333) | Provisioned; the application does not currently pass a Qdrant client to the Student Brain. |
| `ollama` (profile `bundled-ollama`) | `mentorai_ollama` | 11434 | Optional, off by default. The verified setup uses a separate, pre-existing container named `ollama`. |

## Network

- Services reach each other by service name (`postgres:5432`, `api:8000`). No container uses another container's `localhost`.
- The `api` container reaches Ollama at `http://host.docker.internal:11434/v1` (`extra_hosts: host.docker.internal:host-gateway`).
- The browser only talks to the frontend; Next.js forwards `/api/*` and `/health/*` to `API_INTERNAL_URL` (`http://api:8000`).

## Persistent volumes

`postgres_data`, `redis_data`, `qdrant_data` (Compose project `mentorai`, so the volumes are named `mentorai_<name>`), plus `ollama_data` used only by the optional bundled Ollama. The standalone `ollama` container keeps its models in its own `ollama` volume, which is not managed by this Compose file.
