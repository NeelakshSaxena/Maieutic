# Ollama Configuration and Integration

MentorAI relies on local LLMs for its intelligence, specifically using Ollama for local inference during the MVP and development phases.

## 1. Architecture

Ollama acts as the execution environment for the Qwen models. The FastAPI backend (`api` container) connects to Ollama over HTTP to generate responses via structured prompting.

### The Network Bridge

MentorAI runs in Docker Compose; Ollama runs as a separate, already-existing container named `ollama` (GPU, port 11434 published to the host). The `api` container reaches it through `host.docker.internal`. See [DEPLOYMENT.md](../DEPLOYMENT.md) for the verified setup.

- **Host / `ollama` container:** Ollama's port is published on `localhost:11434`.
- **Docker Network:** The `api` container accesses Ollama via `http://host.docker.internal:11434`.

#### Linux Users Note
If you are on Linux, `host.docker.internal` might not resolve automatically. The `docker-compose.yml` file includes:
```yaml
    extra_hosts:
      - "host.docker.internal:host-gateway"
```
This forces the mapping and allows Linux Docker containers to speak to the host's port `11434`.

## 2. Model Selection

In `.env` (or the Compose defaults) the model is set by `TRANSFORM_MODEL` and `JUDGE_MODEL`.
- **Local default:** `qwen3.5-aggressive:latest`.
- **Production target:** the Phase 2 fine-tuned LoRA served via vLLM on RunPod.

## 3. GPU Considerations

Ollama automatically detects and utilizes available GPUs (Apple Silicon Metal, NVIDIA CUDA, AMD ROCm). 

- **Apple Silicon (M1/M2/M3/M4):** Works seamlessly out of the box.
- **NVIDIA:** Ensure you have the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed if you ever plan to run Ollama *inside* a container, but running on the host is recommended.

## 4. Useful Commands

| Action | Command |
|--------|---------|
| Start the Ollama container | `docker start ollama` |
| List models | `docker exec ollama ollama list` |
| Pull a model (large download; do deliberately) | `docker exec ollama ollama pull <model>` |
| Test model | `docker exec -it ollama ollama run qwen3.5-aggressive:latest` |

## 5. Performance and Load

Because the MentorAI orchestrator spawns multiple agents (Planner, Verifier, Hint Generator, Checkpoint Generator), it may generate multiple sequential LLM calls for a single user turn. 

If you notice timeouts:
1. Check the `api` logs to see if the LLM client is timing out.
2. Ollama keeps the model loaded in memory for a few minutes. If you have limited RAM/VRAM, the model might unload between sparse interactions, causing latency on the next request. Set `OLLAMA_KEEP_ALIVE=-1` in your host environment to keep the model loaded indefinitely.
