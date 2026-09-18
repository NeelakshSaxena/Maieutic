# Troubleshooting Guide

This guide covers common issues encountered while setting up and running MentorAI.

## 1. Ollama Connection Issues

**Symptom:** `api` logs show `ConnectionRefusedError` or `httpx.ConnectError` when attempting to reach the LLM.

**Possible Causes & Solutions:**
- **Ollama is not running:** Check if Ollama is running on your host machine. Run `curl http://localhost:11434/api/tags`.
- **Docker networking misconfiguration (Linux):** On Linux, Docker containers may fail to resolve `host.docker.internal`. Ensure your `docker-compose.yml` has the `extra_hosts: ["host.docker.internal:host-gateway"]` binding.
- **Ollama binding:** By default, Ollama might only bind to `127.0.0.1`. If `host.docker.internal` doesn't work, try binding Ollama to `0.0.0.0` by setting the environment variable `OLLAMA_HOST=0.0.0.0` before starting the Ollama server on your host machine.

## 2. Alembic Migration Failures

**Symptom:** The `api` container crashes on startup, or you get relation/table not found errors.

**Possible Causes & Solutions:**
- **Migrations haven't run:** If you started the database but didn't run migrations, the tables won't exist.
  Run: `docker compose exec api alembic upgrade head`
- **Migration conflicts:** If you modified models locally and generated conflicting migrations, you might need to drop the database and recreate it.
  Run: `docker compose exec db psql -U postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"` and then re-run migrations.

## 3. Port Conflicts

**Symptom:** Docker Compose fails to start with `bind: address already in use`.

**Possible Causes & Solutions:**
- You might have local instances of PostgreSQL (5432), Redis (6379), or another web server (8000/3000) running outside of Docker.
- Stop local services, or change the exposed port mapping in `docker-compose.yml` (e.g., change `8000:8000` to `8080:8000`). If you change backend or frontend ports, ensure you update `NEXT_PUBLIC_API_URL` and CORS settings accordingly.

## 4. AI Hallucinations or Schema Failures

**Symptom:** The backend logs show Pydantic `ValidationError` or the AI returns raw text instead of JSON.

**Possible Causes & Solutions:**
- **Model inadequacy:** The MVP defaults to `qwen2`. Base models sometimes fail to adhere to complex JSON schemas. Ensure you are using a model capable of strict JSON output.
- **Phase 2 tuning:** MentorAI relies on the Socratic fine-tuned model (currently frozen at Experiment #1). Until Experiment #2 is deployed, occasional schema failures are expected with the base model.
- **Retry Logic:** The `LLMClient` has built-in retry logic that provides validation errors back to the model. If it fails after max retries, it raises an exception. Check the `api` logs to see the rejected payloads.

## 5. Qdrant / Semantic Retrieval Errors

**Symptom:** `grpc` errors or connection refused on port 6333.

**Possible Causes & Solutions:**
- Qdrant may take a moment to initialize. Ensure the `qdrant` container is healthy.
- Check `docker compose logs qdrant`.

## 6. Frontend Not Updating

**Symptom:** Changes to `apps/frontend` code aren't reflected in the browser.

**Possible Causes & Solutions:**
- If running via Docker Compose (`docker compose up`), the frontend is built into a standalone production image. It does not support hot-reloading.
- **Solution:** For frontend UI development, stop the Docker frontend service and run it locally:
  ```bash
  docker compose stop frontend
  cd apps/frontend
  npm install
  npm run dev
  ```
