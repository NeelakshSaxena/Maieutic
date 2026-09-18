# MentorAI — Deployment

## Development & MVP (Current Phase)

The MVP is deployed as a multi-container Docker Compose stack. This provides a production-like environment on a local machine.

**Services (`docker-compose.yml`):**
- `frontend`: Next.js App Router (Standalone Build)
- `api`: FastAPI Python Backend
- `db`: PostgreSQL
- `redis`: Redis
- `qdrant`: Qdrant Vector DB

**Inference:**
The MVP relies on a local Ollama instance running on the host machine to leverage local GPUs, exposed to the Docker network via `host.docker.internal`.

## Staging & Production Target

When moving beyond local development, the architecture will shift to managed services.

**Frontend:**
- Vercel or containerized Next.js

**Backend:**
- Containerized FastAPI on a cloud provider (AWS/GCP)

**AI / Inference:**
- RunPod + vLLM endpoints serving the fine-tuned MentorAI models

**Data:**
- Managed PostgreSQL (e.g., AWS RDS, Supabase)
- Managed Qdrant Cloud

## Production Architecture Diagram

```text
                    CDN
                     |
                  Next.js
                     |
                  FastAPI
                     |
              Tutoring Engine
                     |
        +------------+------------+
        |            |            |
     Postgres      Redis        Qdrant
        |
     Student Brain

                     |
                Model Gateway
                     |
                  vLLM
                     |
                  RunPod
```

## RunPod Separation

Separate endpoints must be maintained:
- `mentorai-inference`
- `mentorai-training`

Training should never share production inference resources.

## Model Deployment Lifecycle

1. Train
2. Evaluate
3. Merge/adapt adapter
4. Quantize if required
5. Deploy
6. Run smoke tests
7. Enable traffic gradually

## Rollback

Every production model must have a version (e.g., `mentorai-14b-v0.1`).
Rollback must be possible via environment variable configuration without changing application code.

## Observability

Track:
- Request latency
- Token usage
- GPU utilization
- Error rate
- Model version
- Prompt version
- Verification accuracy
- Answer leakage