# MentorAI — Deployment

## Development

Docker Compose:

- PostgreSQL
- Redis
- Qdrant
- MinIO

Run backend locally.

Run frontend locally.

Model can initially use an external API.

## Staging

Frontend:

Next.js deployment

Backend:

Containerized FastAPI

AI:

RunPod vLLM endpoint

Database:

Managed PostgreSQL

Vector:

Qdrant

## Production

Architecture:

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

## RunPod

Separate endpoints:

mentorai-inference

mentorai-training

Training should never share production inference resources.

## Model Deployment

1. Train
2. Evaluate
3. Merge/adapt adapter
4. Quantize if required
5. Deploy
6. Run smoke tests
7. Enable traffic gradually

## Rollback

Every production model must have a version.

Example:

mentorai-14b-v0.1

mentorai-14b-v0.2

Rollback must be possible without changing application code.

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