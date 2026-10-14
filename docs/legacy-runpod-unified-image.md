# Legacy: Unified RunPod Image (superseded)

> **Superseded.** This describes the earlier single-container RunPod design (`Dockerfile.runpod`,
> `docker-entrypoint.sh`, `supervisord.conf`, vLLM + FastAPI + Next.js in one image). Those files
> have been removed. The supported modes are documented in [`../DEPLOYMENT.md`](../DEPLOYMENT.md)
> (RunPod Serverless/Pod using `Dockerfile.api`, and fully local Docker Compose + Ollama).
> `scripts/runpod_entrypoint.sh` and `scripts/model_bootstrap.sh` are kept only as reference for this design.
> Kept here so no uncommitted instructions are lost. Do not follow it for new deployments.

# Deployment

## 1. Architecture Overview

Maieutic is designed to be deployed on RunPod using a single unified Docker container to minimize Docker-in-Docker complexity and ensure the simplest possible setup for an MVP.

```mermaid
graph TD
    User([User / Browser]) -->|HTTP 3000| Container
    
    subgraph Single RunPod Container
        Frontend[Frontend: Next.js (Port 3000)]
        API[API: FastAPI (Port 8000)]
        Model[Model Server: vLLM (Port 11434)]
        
        Frontend -->|Internal Proxy| API
        API -->|Localhost| Model
        API -->|SQL| DB[(SQLite: maieutic.db)]
    end
    
    Model --> GPU[NVIDIA GPU]
    
    subgraph Persistent Storage /workspace
        DB
        HF_Cache[(HF Cache)]
    end
    
    Model -.-> HF_Cache
```

- **PUBLIC**: Only the Next.js frontend (Port 3000) is accessible from the internet.
- **INTERNAL**: FastAPI and vLLM run natively on `localhost` within the container. Next.js proxies `/api/*` requests to `localhost:8000`.
- **DATABASE**: To keep the setup simple and robust, PostgreSQL has been replaced by SQLite (`maieutic.db`) stored on the persistent volume.

## 2. Prerequisites

To deploy the full stack on RunPod, you must have:
- A RunPod account with billing active.
- A GPU Pod (e.g., RTX 3090, RTX 4090, or A5000) with at least **24GB VRAM**.
- A **persistent volume** attached to the RunPod Pod (minimum 40GB).
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
│   ├── runpod_entrypoint.sh  # Unified entrypoint for all 3 processes
│   └── model_bootstrap.sh    # Validates GPU, downloads LoRA/base model to cache, starts vLLM
├── Dockerfile.runpod         # The single image encapsulating the entire stack
```

## 5. Environment Variables

| Variable | Required | Example | Purpose |
|----------|----------|---------|---------|
| **APPLICATION** | | | |
| `NODE_ENV` | Yes | `production` | Optimizes Next.js performance |
| `LLM_MODEL` | Yes | `mentorai` | Model name FastAPI requests |
| `LLM_BASE_URL` | Yes | `http://localhost:11434/v1` | Internal vLLM OpenAI endpoint |
| `LLM_API_KEY` | Yes | `local` | Passed to vLLM |
| **AUTH / API KEYS** | | | |
| `HF_TOKEN` | Yes | `hf_your_token_here` | Allows vLLM to download the private LoRA adapter |

*Note: All environment variables are handled safely on the server backend. The browser exclusively talks to the Next.js frontend which proxies requests.*

## 6. Building the Images

The application image is built automatically via GitHub Actions on every push to `main`.

```text
git push
   ↓
GitHub Actions
   ↓
Builds:
- ghcr.io/neelakshsaxena/maieutic-runpod:latest
   ↓
GHCR (GitHub Container Registry)
```

The CI/CD pipeline does NOT touch the multi-GB AI models. It strictly packages the Python and Node.js code.

## 7. Local Development (Docker Compose + Ollama)

If you do not have a 24GB GPU locally, you can run the system using a quantized model via Ollama and Docker Compose.

1. **Install and Run Ollama**
   Start Ollama (e.g. inside WSL or Windows) and pull the required model:
   ```bash
   ollama pull qwen3.5-aggressive:latest
   ollama serve
   ```

2. **Configure Local Environment**
   Update your local `.env` file to point to your Ollama instance. `host.docker.internal` allows the Docker containers to reach Ollama running on your host machine:
   ```env
   LLM_PROVIDER=ollama
   
   TRANSFORM_BASE_URL="http://host.docker.internal:11434/v1"
   TRANSFORM_API_KEY="ollama"
   TRANSFORM_MODEL="qwen3.5-aggressive:latest"

   JUDGE_BASE_URL="http://host.docker.internal:11434/v1"
   JUDGE_API_KEY="ollama"
   JUDGE_MODEL="qwen3.5-aggressive:latest"
   ```

3. **Start the Stack**
   Start the API, Frontend, Postgres, Redis, and Qdrant via Docker Compose:
   ```bash
   docker compose up -d --build
   ```

### Local URLs
Once the containers are successfully running, you can access the various services at:
- **Frontend (Web UI):** http://localhost:4000
- **API Backend:** http://localhost:8000
- **API Swagger/OpenAPI Docs:** http://localhost:8000/docs
- **API LLM Healthcheck:** http://localhost:8000/health/llm
- **Ollama LLM Endpoint:** http://localhost:11434/v1

## 8. RunPod Deployment — Step by Step

### Step 1 — Create the Pod
1. Log into RunPod and navigate to **Pods**.
2. Deploy a GPU Pod (e.g. RTX 4090).
3. Select **Custom Template**.
4. Set **Container Image** to `ghcr.io/neelakshsaxena/maieutic-runpod:latest`.
5. Assign at least **40GB** of Persistent Volume to `/workspace`.
6. Set **Environment Variables**: `HF_TOKEN=hf_your_token_here`.
7. In **Expose HTTP Ports**, ensure `3000` is exposed.

### Step 2 — Monitor Startup
Once the Pod starts, open the **Logs** tab in RunPod to monitor the startup sequence.

Expected output:
```text
[Entrypoint] Detected /workspace persistent volume.
[Bootstrap] Verifying GPU...
[Bootstrap] Downloading/Verifying models in HF Cache...
[Bootstrap] Downloading LoRA adapter from NeelakshSaxena/mentorai...
[Bootstrap] Starting vLLM model server...
[API] Running database migrations...
[API] Starting Uvicorn...
[Entrypoint] Starting Next.js Frontend...
[Bootstrap] vLLM is healthy!
```

### Step 3 — Verify Health
Once everything is running, access the application via your RunPod Proxy URL (Port `3000`).

## 9. First Startup vs Subsequent Startup

**FIRST START:**
1. Pulls the unified Docker image.
2. Creates Hugging Face Cache and SQLite database on the persistent volume (`/workspace`).
3. The `model_bootstrap.sh` script downloads `Qwen/Qwen3-8B` and the `mentorai` adapter. (Takes 5-10 minutes depending on network).
4. `vLLM` loads the weights into VRAM.
5. FastAPI runs Alembic migrations on SQLite.

**SUBSEQUENT START:**
1. Persistent volume already contains the 16GB of weights and the SQLite database.
2. `model_bootstrap.sh` detects the cache and skips the download.
3. `vLLM` immediately loads weights into VRAM (takes < 30 seconds).

## 10. Updating the Application

When application code is modified (e.g. Next.js or FastAPI):
1. Run `git push` to `main`.
2. Wait for GitHub Actions to build new images.
3. On RunPod, simply **Restart the Pod**.
4. RunPod will automatically pull the `:latest` tag on restart (if your template is configured for 'Always Pull').

## 11. Updating the Model / LoRA

If you push a new LoRA to Hugging Face, the persistent volume will not automatically fetch it because it relies on the cache.
To force an update:

1. Open the RunPod Web Terminal.
2. Clear the specific Hugging Face cache folder inside the persistent volume.
```bash
rm -rf /workspace/huggingface_cache/hub/models--NeelakshSaxena--mentorai
```
3. Restart the Pod.
4. The bootstrap script will re-download the latest LoRA revision.

## 12. Networking

Browser → `https://<runpod-id>-3000.proxy.runpod.net` → Next.js (Port 3000)
Next.js API route (`/api/*`) → Proxied via Rewrites → `http://localhost:8000` (FastAPI)
FastAPI → `http://localhost:11434/v1` (vLLM)

Because all processes run in the same container, they communicate securely via `localhost`.

## 13. Security

- **Public**: Only Port 3000 (Next.js).
- **Internal Only**: Ports 8000 and 11434 are never exposed outside the container.
- **Secrets**: `HF_TOKEN` is passed via RunPod Environment Variables securely.

## 14. Troubleshooting

| Issue | Verification | Fix |
|-------|--------------|-----|
| Container won't start | RunPod Logs Tab | Check the RunPod console logs for crash reasons or missing `HF_TOKEN`. |
| vLLM OOM Error | RunPod Logs Tab | Verify you are using a GPU with >= 24GB VRAM and no other models are loaded. |
| API cannot reach model | API logs in RunPod | Ensure vLLM successfully downloaded weights and passed the smoke test. |
| Database Connection Failed | API logs in RunPod | Verify `/workspace` is mounted and writable for `maieutic.db`. |
| Frontend 502 Bad Gateway | Browser Network Tab | The Next.js proxy failed to reach the FastAPI backend. Check RunPod logs. |

## 15. Useful Commands

(Execute these inside the RunPod Web Terminal)

```bash
ps aux                          # List all running processes (Next.js, FastAPI, vLLM)
nvidia-smi                      # Check GPU usage and VRAM
ls -lh /workspace/maieutic.db   # Check SQLite database size
```

## 16. Deployment Checklist

- [ ] RunPod GPU Pod created (>= 24GB VRAM)
- [ ] Persistent volume attached (>= 40GB) to `/workspace`
- [ ] `HF_TOKEN` configured in RunPod Environment Variables
- [ ] RunPod Pod Started
- [ ] Base model downloaded (view in logs)
- [ ] Maieutic LoRA downloaded (view in logs)
- [ ] vLLM healthy (view in logs)
- [ ] FastAPI & Next.js healthy
- [ ] Frontend accessible via RunPod Proxy (Port 3000)

## 17. Architecture Maintenance Notes

- Do **NOT** put model weights into the application Docker image.
- Do **NOT** expose the API or vLLM publicly. Next.js handles proxying safely.
- Do **NOT** attempt to use `docker-compose` on RunPod; we use a single unified image.
- Do **NOT** remove persistent model storage from `/workspace` (or you will wait 10 minutes per restart for HF downloads).
