# MentorAI — Deployment & Operations Guide

This guide details the three supported deployment modes for MentorAI.

---

## Architecture & Modes Overview

> [!IMPORTANT]
> **Orchestrator Architecture**: The MentorAI backend container is a multi-agent pedagogical orchestrator (Socratic Planner, Verifier, Hint Generator, and Student Brain DB). It **does not** bundle or execute LLM neural network weights in-container. Instead, it queries an external OpenAI-compatible inference endpoint (such as a RunPod vLLM endpoint or local Ollama) configured via `TRANSFORM_BASE_URL`.

| Mode | Backend Location | Frontend Location | LLM Inference Location | Typical Use Case |
|---|---|---|---|---|
| **Mode 1** | RunPod (Serverless or Pod) | Remote / Pod / Static | RunPod vLLM / Worker Endpoint | Cloud Production Deployment |
| **Mode 2** | RunPod (Serverless or Pod) | Local machine (`localhost:3000`) | RunPod Cloud | Rapid Frontend Development |
| **Mode 3** | Local Docker (`localhost:8000`) | Local Docker (`localhost:4000`) | Existing local `ollama` container | 100% Offline / Local Testing |

---

## Mode 1 — RunPod Deployment (Serverless & Pods)

MentorAI provides a **single canonical backend Dockerfile** ([`Dockerfile.api`](Dockerfile.api)) that packages the FastAPI application, database migrations, and the RunPod Serverless worker SDK into one container image.

### 1. Build and Push the Canonical Backend Image
From the repository root:
```bash
# Tag for your container registry (e.g., Docker Hub or GitHub Container Registry)
docker build -t <YOUR_DOCKER_USER>/mentorai-api:latest -f Dockerfile.api .

# Push to your registry
docker push <YOUR_DOCKER_USER>/mentorai-api:latest
```

### 2. Option A: Deploy as RunPod Serverless
RunPod Serverless provides auto-scaling worker instances that execute [`apps/api/app/workers/serverless_worker.py`](apps/api/app/workers/serverless_worker.py).

1. In the **RunPod Console**, navigate to **Serverless** → **Create Endpoint**.
2. Select your container image: `<YOUR_DOCKER_USER>/mentorai-api:latest`.
3. Set the **Container Start Command** / **Docker Args** (or set environment variable):
   ```bash
   /app/start_api.sh serverless
   ```
   *(Alternatively, configure environment variable `RUNPOD_MODE=serverless`)*.
4. **Required Environment Variables**:
   ```env
   RUNPOD_MODE=serverless
   LLM_PROVIDER=runpod
   TRANSFORM_BASE_URL=https://api.runpod.ai/v2/<RUNPOD_INFERENCE_ENDPOINT_ID>/openai/v1
   TRANSFORM_API_KEY=<YOUR_RUNPOD_API_KEY>
   TRANSFORM_MODEL=mentorai
   DATABASE_URL=sqlite:///./maieutic.db
   ```
5. **Runtime Characteristics**:
   - **Port Binding**: None (Serverless workers communicate with the RunPod job queue via HTTP polling/webhooks managed by the `runpod` Python SDK).
   - **Health Check**: The container healthcheck detects `RUNPOD_MODE=serverless` and exits 0 cleanly. For application-level health, the worker handles `{"input": {"ping": true}}` or `{"input": {"health": true}}`.
   - **Request Contract**:
     ```json
     {
       "input": {
         "session_id": "session-123",
         "user_id": "student-456",
         "message": "I want to understand binary search."
       }
     }
     ```
   - **Response Contract**:
     ```json
     {
       "status": "success",
       "data": {
         "type": "new_plan",
         "message": "Let's get started. Your task: Understand low/high index halving.",
         "next_checkpoint": { "id": "cp1", "task": "...", "concept_id": "..." },
         "hint": null,
         "verification": null
       }
     }
     ```

### 3. Option B: Deploy as a Persistent RunPod Pod
A RunPod GPU or CPU Pod runs the persistent FastAPI HTTP server on port `8000`.

1. In the **RunPod Console**, navigate to **Pods** → **Deploy Pod**.
2. Select container image: `<YOUR_DOCKER_USER>/mentorai-api:latest`.
3. Set **Container Disk** (minimum 20GB) and attach a **Persistent Volume** (`/workspace`, 40GB+).
4. Set **Expose HTTP Ports**: `8000`.
5. Set **Environment Variables**:
   ```env
   HOST=0.0.0.0
   PORT=8000
   DATABASE_URL=sqlite:////workspace/maieutic.db
   LLM_PROVIDER=runpod
   TRANSFORM_BASE_URL=https://api.runpod.ai/v2/<RUNPOD_INFERENCE_ENDPOINT_ID>/openai/v1
   TRANSFORM_API_KEY=<YOUR_RUNPOD_API_KEY>
   TRANSFORM_MODEL=mentorai
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```
6. The container default entrypoint ([`scripts/start_api.sh`](scripts/start_api.sh)) automatically applies migrations and executes Uvicorn:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
7. **Verify Health**:
   ```bash
   curl https://<POD_ID>-8000.proxy.runpod.net/health
   curl https://<POD_ID>-8000.proxy.runpod.net/health/llm
   ```

---

## Mode 2 — RunPod Backend + Local Frontend

Run the Next.js frontend locally while forwarding requests to your remote RunPod deployment.

The frontend supports two remote connection methods via server-side Route Handlers in [`apps/frontend/src/app/api/chat/route.ts`](apps/frontend/src/app/api/chat/route.ts) and [`apps/frontend/src/app/health/llm/route.ts`](apps/frontend/src/app/health/llm/route.ts):

### Option A: Connecting to a RunPod Pod HTTP Server
1. In [`apps/frontend/.env.local`](apps/frontend/.env.local):
   ```env
   API_INTERNAL_URL=https://<POD_ID>-8000.proxy.runpod.net
   NEXT_PUBLIC_API_URL=/api
   NEXT_PUBLIC_HEALTH_URL=/health/llm
   ```
2. On the remote RunPod Pod, set CORS origins to allow your local frontend:
   ```env
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

### Option B: Connecting to a RunPod Serverless Worker Endpoint
If you deployed the backend as RunPod Serverless (Option A of Mode 1), you do not have an HTTP server listening on port 8000. Instead, configure the local Next.js server to dispatch jobs directly to RunPod Serverless:
1. In [`apps/frontend/.env.local`](apps/frontend/.env.local):
   ```env
   RUNPOD_SERVERLESS_ENDPOINT_ID=<YOUR_SERVERLESS_ENDPOINT_ID>
   RUNPOD_API_KEY=<YOUR_RUNPOD_API_KEY>
   NEXT_PUBLIC_API_URL=/api
   NEXT_PUBLIC_HEALTH_URL=/health/llm
   ```
2. **Security & Protocol Adaptation**:
   - The Next.js Route Handler formats the client message into the RunPod `{ input: { ... } }` payload.
   - It attaches the `Authorization: Bearer <RUNPOD_API_KEY>` header securely on the server.
   - **Credentials never leak to the client browser**.
   - It unwraps the RunPod response and returns normalized `{ message, next_checkpoint, hint, verification }` to the UI.

### Launch Local Frontend
```powershell
# PowerShell
cd apps/frontend
npm install
npm run dev
```
```bash
# Bash
cd apps/frontend
npm install
npm run dev
```
Open **http://localhost:3000**.

---

## Mode 3 — Fully Local (Docker Compose + existing Ollama container)

Verified setup (Windows + Docker Desktop): the MentorAI stack (frontend, API, Postgres, Redis, Qdrant) runs under Compose and talks to a **separate, already-existing Ollama container** named `ollama` (GPU, port `11434` published on the host, models in the `ollama` Docker volume). The API container reaches it at `http://host.docker.internal:11434/v1` (the OpenAI-compatible endpoint the backend's `LLMClient` uses). No RunPod variables are needed.

### 0. Start Docker Desktop
Start **Docker Desktop** from the Start menu (or `Start-Process "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop.exe"` for a per-user install), then wait until this succeeds:
```powershell
docker info --format '{{.ServerVersion}}'
```

### 1. Configure `.env`
```env
LLM_PROVIDER=ollama
TRANSFORM_BASE_URL=http://host.docker.internal:11434/v1
TRANSFORM_API_KEY=ollama
TRANSFORM_MODEL=qwen3.5-aggressive:latest
JUDGE_BASE_URL=http://host.docker.internal:11434/v1
JUDGE_API_KEY=ollama
JUDGE_MODEL=qwen3.5-aggressive:latest
# Optional: seconds to wait for one inference (default 300)
# LLM_TIMEOUT_SECONDS=300
```
These are also the Compose defaults. Do not set `RUNPOD_*` variables locally: the Next.js `/api/chat` route switches to RunPod if they are present.

### 2. Check Ollama and the model (PowerShell)
```powershell
docker start ollama                      # no-op if already running
docker exec ollama ollama list           # must list qwen3.5-aggressive:latest
(Invoke-RestMethod http://localhost:11434/api/tags).models.name
```
If the model is missing, pull it into **that** container (large download - do it deliberately, never at app startup):
```powershell
docker exec ollama ollama pull qwen3.5-aggressive:latest
```
(Optional: `docker compose --profile bundled-ollama up -d` starts a Compose-managed Ollama with its own volume instead; it conflicts with port 11434 if the `ollama` container is running.)

### 3. Start the stack
Port 3000 may be used by Open WebUI, so the frontend host port is configurable (`FRONTEND_PORT`, default 3000):
```powershell
$env:FRONTEND_PORT = "4000"   # omit to use 3000
docker compose up -d --build
docker compose ps             # api and postgres should be (healthy)
```

### 4. URLs and health
- Frontend: **http://localhost:4000** (the `FRONTEND_PORT` you set; 3000 if unset)
- API: http://localhost:8000 (`/health`, `/docs`)
- LLM health: http://localhost:8000/health/llm - returns 503 with a clear message if Ollama is unreachable or the model is missing; it does not run inference.
```powershell
Invoke-RestMethod http://localhost:8000/health/llm
Invoke-RestMethod http://localhost:4000/health/llm   # via the frontend
```

### 5. Test a chat request
A 9B local model needs roughly 60-120 s per LLM call (a wrong answer triggers a second call for the hint).
```powershell
$body = @{ user_id="u1"; session_id="s-$(Get-Date -Format HHmmss)"; message="Help me understand what a Python variable is. Teach me Socratically and ask one question at a time." } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:4000/api/chat -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 600
```

### 6. Inspect connectivity
```powershell
docker compose ps                                                     # service status / health
Invoke-RestMethod http://localhost:4000/health/llm                    # frontend -> API -> Ollama + model present
Invoke-RestMethod http://localhost:8000/health                        # API alone
docker exec mentorai_postgres pg_isready -U postgres -d mentorai      # database
docker exec mentorai_api python -c "import urllib.request,os;print(urllib.request.urlopen(os.environ['TRANSFORM_BASE_URL']+'/models',timeout=5).status)"   # API container -> Ollama (expect 200)
docker exec ollama ollama ps                                          # which model is loaded (during/after a request)
```

### 7. Logs, stop, rebuild
```powershell
docker compose logs -f api         # or frontend / postgres
docker compose stop                # stop, keep everything
docker compose down                # remove containers only; named volumes (Postgres, Redis, Qdrant) are kept
docker compose up -d --build       # rebuild after code changes
docker compose build --no-cache api   # force a clean API rebuild
```
Avoid `docker compose down -v`: it deletes the Postgres/Redis/Qdrant volumes (your learning data).

### 8. Data and model volumes
- `mentorai_postgres_data`, `mentorai_redis_data`, `mentorai_qdrant_data`: MentorAI data, kept across `stop`, `down` and rebuilds.
- `ollama`: the existing Ollama container's models. It is not managed by this Compose project - never remove it, and do not run `docker volume prune` or `docker system prune`.
- Shutting down: `docker compose stop` (MentorAI only). Stop the model server separately, if you want, with `docker stop ollama`.

---

## Verification Commands

Execute these commands to verify the system across all layers:

```powershell
# 1. Backend Pytest Suite (30 tests: agents, orchestrator, APIs, serverless worker)
$env:PYTHONPATH=".;apps/api"; .\venv\Scripts\python.exe -m pytest tests/ -v

# 2. Frontend ESLint
cd apps/frontend
npm run lint

# 3. Frontend Production Turbopack Build
npm run build

# 4. Frontend type check (typegen creates the Next.js types tsc needs)
npx next typegen
npx tsc --noEmit

# 5. Docker Compose Validation
cd ../..
docker compose config --quiet
```
