# MentorAI — Deployment

## Development & MVP (Current Phase)

The MVP is deployed as a single, unified Docker container designed to run seamlessly on a GPU RunPod instance. This eliminates Docker-in-Docker complexity while encapsulating the entire stack.

**Services (Single Container):**
- `frontend`: Next.js App Router (Port 3000)
- `api`: FastAPI Python Backend (Port 8000)
- `model`: vLLM Server serving Qwen3-8B + LoRA (Port 11434)
- `db`: SQLite database stored on persistent volume (`/workspace/maieutic.db`)

**Inference:**
The MVP relies on a local vLLM instance running natively inside the same container. The frontend proxies requests to the FastAPI backend, which directly communicates with the local vLLM instance via `localhost`.

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