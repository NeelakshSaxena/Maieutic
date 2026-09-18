# Docker Architecture

MentorAI uses Docker and Docker Compose to provide a consistent, reproducible environment for all components.

## Services

| Service | Port | Description |
|---------|------|-------------|
| `frontend` | 3000 | Next.js App Router application serving the Chat and Dashboard UI. Built in standalone mode. |
| `api` | 8000 | FastAPI backend serving REST endpoints and running the Orchestrator/Agent loops. |
| `db` | 5432 | PostgreSQL database storing persistent state (Sessions, Profiles, Mastery, Concepts). |
| `redis` | 6379 | Redis cache used for transient state and potential job queuing. |
| `qdrant` | 6333 | Qdrant vector database for semantic retrieval. |

## Network Constraints

- Services inside the `docker-compose.yml` communicate using their service names (e.g., `db:5432`, `qdrant:6333`).
- **Ollama Mapping:** Ollama runs on the host (not in a container) to easily leverage local GPUs. The `api` container accesses it via `host.docker.internal:11434`.
- **Frontend Mapping:** The frontend running in the browser makes calls to `localhost:8000` (which is mapped to the `api` container).

## Persistent Volumes

Docker volumes are used to ensure data survives container restarts:
- `postgres_data`: Backs `/var/lib/postgresql/data`
- `qdrant_data`: Backs `/qdrant/storage`
- `redis_data`: Backs `/data`
