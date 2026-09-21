# MentorAI: Socratic Tutoring Model Card & Deployment Guide

MentorAI is an AI-powered Socratic tutor designed to teach through guided reasoning rather than simply providing answers.

## 1. What is MentorAI?

MentorAI is an open-source, full-stack learning platform. It integrates fine-tuned local Large Language Models (LLMs) with an orchestrator backend to simulate the Socratic method for students. 

Currently supported learning domains:
- Mathematics
- Programming
- Data Structures & Algorithms
- Computer Science fundamentals

### The Tutoring Loop
The system operates through an orchestrated agent loop:

Student 
→ Planner 
→ Learning Plan 
→ Checkpoint 
→ Student Response 
→ Verifier 
→ Feedback / Hint 
→ Mastery Update 
→ Next Checkpoint

An Orchestrator coordinates these steps, ensuring the student cannot advance until they've demonstrated genuine understanding.

## 2. Core System

The architecture is split into distinct components:
- **Planner:** AI agent that maps a student's learning goal into concrete, sequential checkpoints.
- **Verifier:** AI agent that evaluates a student's response against a specific checkpoint, identifying correctness and misconceptions.
- **Hint/Tutoring Logic:** Dynamically generates progressively stronger hints based on the student's misconceptions and attempt count.
- **Orchestrator:** The central state machine directing the flow between the student, the AI agents, and the persistent memory.
- **Student Brain:** The long-term memory system tracking mastery, misconceptions, and learning history.

============================================================
# Deployment
============================================================

## 1. Architecture Overview

Maieutic is deployed on RunPod using a Docker Compose stack of 6 independent containers.

```mermaid
graph TD
    User([User / Browser]) -->|HTTP 3000| Frontend[Frontend: Next.js]
    Frontend -->|Next.js Rewrites| API[API: FastAPI]
    
    API -->|SQL| DB[(PostgreSQL)]
    API -->|TCP| Redis[(Redis Cache)]
    API -->|HTTP| Qdrant[(Qdrant VectorDB)]
    API -->|HTTP OpenAI API| Model[Model Server: vLLM]
    
    Model --> GPU[NVIDIA GPU]
    
    subgraph Persistent Storage
    DB
    Redis
    Qdrant
    HF_Cache[(HF Cache Volume)]
    end
    
    Model -.-> HF_Cache
```

- **PUBLIC**: Only the Next.js `frontend` (Port 3000) is accessible from the internet.
- **INTERNAL**: `FastAPI`, `PostgreSQL`, `Redis`, `Qdrant`, and `vLLM` run on an internal Docker network and are not exposed.
- **Why?**: The Next.js frontend securely proxies `/api/*` requests to FastAPI, avoiding CORS complexities and preventing arbitrary public queries against your expensive GPU instance or internal databases.

## 2. Prerequisites

To deploy the full stack on RunPod, you must have:
- A RunPod account with billing active.
- A GPU instance with at least **24GB VRAM** (e.g., RTX 3090, RTX 4090, or A5000). The 8B model requires ~16GB in bf16, leaving sufficient headroom for the PEFT adapter and vLLM KV cache.
- A **persistent volume** attached to the RunPod Pod (minimum 40GB to hold model weights + databases).
- A Hugging Face account and an Access Token (`HF_TOKEN`) with read permissions for the private LoRA repository.

## 3. Model Architecture

MentorAI does NOT use a generic off-the-shelf LLM. It serves the project's specific fine-tuned LoRA model dynamically on top of the base model.

- **Base Model**: `Qwen/Qwen3-8B`
- **LoRA Repository**: `NeelakshSaxena/mentorai`
- **Adapter Format**: Hugging Face PEFT / Safetensors
- **Inference Engine**: vLLM (v0.6.2)
- **Serving Mechanism**: vLLM dynamically loads the LoRA adapter at runtime directly on top of the base model via `--enable-lora`. **No offline merging is required.**
- **API Model Name**: The API queries the model as `"mentorai"`.
- **DType**: `bfloat16`

## 4. Repository Structure

The deployment relies on the following files:

```text
.
├── apps/
│   ├── api/
│   └── frontend/
├── scripts/
│   ├── start_api.sh        # Runs Alembic migrations and starts FastAPI
│   └── model_bootstrap.sh  # Validates GPU, downloads LoRA/base model to cache, starts vLLM
├── docker-compose.yml      # The orchestration blueprint for RunPod
├── Dockerfile.api          # Builds the ghcr.io image for the backend
├── Dockerfile.frontend     # Builds the ghcr.io image for the frontend
```

## 5. Environment Variables

| Variable | Required | Example | Purpose |
|----------|----------|---------|---------|
| **APPLICATION** | | | |
| `NODE_ENV` | Yes | `production` | Optimizes Next.js performance |
| `LLM_MODEL` | Yes | `mentorai` | Model name FastAPI requests |
| `LLM_BASE_URL` | Yes | `http://model:11434/v1` | Internal vLLM OpenAI endpoint |
| `LLM_API_KEY` | Yes | `local` | Passed to vLLM |
| **DATABASE** | | | |
| `DATABASE_URL` | Yes | `postgresql://postgres:postgres@postgres:5432/mentorai` | Database connection string |
| `REDIS_URL` | Yes | `redis://redis:6379` | Internal Redis |
| `QDRANT_URL` | Yes | `http://qdrant:6333` | Internal Qdrant |
| `POSTGRES_USER` | Yes | `postgres` | Postgres setup |
| `POSTGRES_PASSWORD`| Yes | `postgres` | Postgres setup |
| `POSTGRES_DB` | Yes | `mentorai` | Postgres setup |
| **AUTH / API KEYS** | | | |
| `HF_TOKEN` | Yes | `hf_your_token_here` | Allows vLLM to download the private LoRA adapter |

*Note: All environment variables are handled safely on the server backend. The browser exclusively talks to the Next.js frontend which proxies requests.*

## 6. Building the Images

The application images are built automatically via GitHub Actions on every push to `main`.

```text
git push
   ↓
GitHub Actions
   ↓
Builds:
- ghcr.io/neelakshsaxena/maieutic-frontend:latest
- ghcr.io/neelakshsaxena/maieutic-api:latest
   ↓
GHCR (GitHub Container Registry)
```

The CI/CD pipeline does NOT touch the multi-GB AI models. It strictly packages the Python and Node.js code.

## 7. Local Development

You can run the entire stack locally for development (assuming you have Docker and a sufficiently large local GPU).

```bash
# Start all services and build locally
docker compose up --build -d
```

- **Frontend**: Available at `http://localhost:3000`
- **vLLM Logs**: Check via `docker compose logs -f model` to watch the model download.
- **Stop**: `docker compose down`

## 8. RunPod Deployment — Step by Step

### Step 1 — Create the Pod
1. Log into RunPod and navigate to **Pods**.
2. Deploy a GPU Pod (e.g. RTX 4090).
3. Select **RunPod Pytorch** base image (or any base image with Docker/Compose installed).
4. Assign at least **40GB** of Persistent Volume.
5. In **Expose HTTP Ports**, ensure only `3000` is exposed.

### Step 2 — Connect and Clone
SSH into the RunPod or use the Web Terminal.

```bash
cd /workspace
git clone https://github.com/NeelakshSaxena/Maieutic.git
cd Maieutic
```

### Step 3 — Configure Environment Variables
Create an `.env` file in the root of the repository:

```bash
echo "HF_TOKEN=hf_your_token_here" > .env
```

The `docker-compose.yml` natively passes this to the `model` service for bootstrapping. Other environment variables (like `DATABASE_URL`) are pre-configured internally in the `docker-compose.yml`.

### Step 4 — Start the Stack
Deploy the entire infrastructure using Docker Compose:

```bash
docker compose pull
docker compose up -d
```

### Step 5 — Monitor Startup
Monitor the startup sequence, particularly the `model` container which downloads the LoRA.

```bash
docker compose logs -f model
```
Expected output:
```text
[Bootstrap] Verifying GPU...
[Bootstrap] Downloading/Verifying models in HF Cache...
[Bootstrap] Downloading LoRA adapter from NeelakshSaxena/mentorai...
[Bootstrap] Starting vLLM model server...
[Bootstrap] vLLM is healthy!
[Bootstrap] Smoke test passed!
```

Next, monitor the API container:
```bash
docker compose logs -f api
```
Expected output:
```text
[API] Waiting for Postgres...
[API] Running database migrations...
[API] Starting FastAPI application...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 6 — Verify Health
Once everything is running, access the application via your RunPod Proxy URL (Port `3000`).

To verify the model inference locally on the Pod:
```bash
curl -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer local" \
  -d '{
    "model": "mentorai",
    "messages": [{"role": "user", "content": "What is 2+2?"}]
  }'
```

## 9. First Startup vs Subsequent Startup

**FIRST START:**
1. Pulls Docker images.
2. Creates Docker volumes for Postgres, Redis, Qdrant, and Hugging Face Cache.
3. The `model_bootstrap.sh` script downloads `Qwen/Qwen3-8B` and the `mentorai` adapter to `/root/.cache/huggingface`. (Takes 5-10 minutes depending on network).
4. `vLLM` loads the weights into VRAM.
5. `api` runs Alembic migrations.

**SUBSEQUENT START:**
1. Persistent volumes already contain the 16GB of weights.
2. `model_bootstrap.sh` detects the cache and skips the download.
3. `vLLM` immediately loads weights into VRAM (takes < 30 seconds).

## 10. Updating the Application

When application code is modified (e.g. Next.js or FastAPI):
1. Run `git push` to `main`.
2. Wait for GitHub Actions to build new images.
3. On RunPod, run:
```bash
docker compose pull
docker compose up -d
```
Docker Compose will intelligently recreate ONLY the `frontend` and `api` containers. The `model`, `postgres`, `redis`, and `qdrant` containers (and their persistent data) remain completely untouched and online.

## 11. Updating the Model / LoRA

If you push a new LoRA to Hugging Face, the persistent volume will not automatically fetch it because it relies on the cache.
To force an update:

1. Stop the model container: `docker compose stop model`
2. Clear the specific Hugging Face cache folder inside the persistent volume.
```bash
# This requires knowing exactly where Docker stores the volume on RunPod, 
# or you can temporarily use a bash shell inside the model container:
docker compose run --rm --entrypoint bash model
rm -rf /root/.cache/huggingface/hub/models--NeelakshSaxena--mentorai
exit
```
3. Restart the model container: `docker compose up -d model`
4. The bootstrap script will re-download the latest LoRA revision.

## 12. Networking

Browser → `https://<runpod-id>-3000.proxy.runpod.net` → Next.js (Port 3000)
Next.js API route (`/api/*`) → Proxied via Rewrites → `http://api:8000` (FastAPI)
FastAPI → `http://model:11434/v1` (vLLM)

Because Docker manages internal DNS via service names (`api`, `postgres`, `model`), containers communicate using these names instead of `localhost`.

## 13. Security

- **Public**: Only Port 3000 (Next.js).
- **Internal Only**: Ports 8000, 11434, 5432, 6379, 6333 are protected by the Docker network.
- **Secrets**: `HF_TOKEN` is passed to the container at runtime. Never commit this to Git.

## 14. Troubleshooting

| Issue | Verification | Fix |
|-------|--------------|-----|
| Container won't start | `docker compose ps` | Check `docker compose logs <service>` for crash reasons. |
| vLLM OOM Error | `docker logs maieutic_model` | Verify you are using a 24GB GPU and no other models are loaded. |
| API cannot reach model | `curl http://localhost:11434/v1/models` | Ensure `model` container is healthy and finished downloading weights. |
| Database Connection Failed | `docker compose logs api` | Verify `postgres` container is up. Ensure Alembic migrations succeeded. |
| Frontend 502 Bad Gateway | Browser Network Tab | The Next.js rewrite failed to reach the `api` container. Ensure `api` is running on port 8000. |

## 15. Useful Commands

```bash
docker compose ps               # List all containers
docker compose logs -f          # Tail all logs
docker compose logs -f model    # Tail model logs specifically
docker compose restart api      # Restart the backend
nvidia-smi                      # Check GPU usage on the host
docker compose down             # Stop and remove all containers
```

## 16. Deployment Checklist

- [ ] RunPod GPU selected (>= 24GB VRAM)
- [ ] Persistent volume attached
- [ ] HF_TOKEN configured in `.env`
- [ ] `docker compose up -d` executed
- [ ] Base model downloaded
- [ ] Maieutic LoRA downloaded
- [ ] vLLM healthy
- [ ] FastAPI healthy
- [ ] Frontend accessible via RunPod Proxy (Port 3000)

## 17. Architecture Maintenance Notes

- Do **NOT** put model weights into the application Docker image.
- Do **NOT** expose PostgreSQL, Redis, Qdrant, or vLLM publicly.
- Do **NOT** use `localhost` for inter-container communication (use service names).
- Do **NOT** remove persistent model storage (or you will wait 10 minutes per restart).
