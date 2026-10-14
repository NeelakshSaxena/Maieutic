# MentorAI — Deployment

## Current deployment modes

The supported modes (RunPod Serverless/Pod, RunPod backend plus local frontend, and fully local Docker Compose with Ollama) are documented, with commands, in [`../DEPLOYMENT.md`](../DEPLOYMENT.md). The earlier single-container RunPod image is archived in [legacy-runpod-unified-image.md](legacy-runpod-unified-image.md).

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