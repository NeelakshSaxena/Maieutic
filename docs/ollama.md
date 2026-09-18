# Ollama Configuration and Integration

MentorAI relies on local LLMs for its intelligence, specifically using Ollama for local inference during the MVP and development phases.

## 1. Architecture

Ollama acts as the execution environment for the Qwen models. The FastAPI backend (`api` container) connects to Ollama over HTTP to generate responses via structured prompting.

### The Network Bridge

Since MentorAI runs inside Docker, but Ollama typically runs on the host machine (to access GPU hardware directly without complex container pass-throughs on Mac/Windows), we use a Docker networking bridge: `host.docker.internal`.

- **Host (Your Machine):** Ollama binds to `localhost:11434`.
- **Docker Network:** The `api` container accesses Ollama via `http://host.docker.internal:11434`.

#### Linux Users Note
If you are on Linux, `host.docker.internal` might not resolve automatically. The `docker-compose.yml` file includes:
```yaml
    extra_hosts:
      - "host.docker.internal:host-gateway"
```
This forces the mapping and allows Linux Docker containers to speak to the host's port `11434`.

## 2. Model Selection

In `docker-compose.yml` or your `.env` file, the model is specified via `LLM_MODEL`.
- **MVP Default:** `qwen2` (the standard Qwen 2 7B/8B model).
- **Production Target:** `qwen2-socratic` (the Phase 2 fine-tuned model, pending completion of Experiment #2).

## 3. GPU Considerations

Ollama automatically detects and utilizes available GPUs (Apple Silicon Metal, NVIDIA CUDA, AMD ROCm). 

- **Apple Silicon (M1/M2/M3/M4):** Works seamlessly out of the box.
- **NVIDIA:** Ensure you have the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed if you ever plan to run Ollama *inside* a container, but running on the host is recommended.

## 4. Useful Commands

| Action | Command |
|--------|---------|
| Start Ollama Server (if not running as a service) | `ollama serve` |
| Pull a model | `ollama pull qwen2` |
| List local models | `ollama list` |
| Test model locally | `ollama run qwen2` |
| Remove a model | `ollama rm qwen2` |

## 5. Performance and Load

Because the MentorAI orchestrator spawns multiple agents (Planner, Verifier, Hint Generator, Checkpoint Generator), it may generate multiple sequential LLM calls for a single user turn. 

If you notice timeouts:
1. Check the `api` logs to see if the LLM client is timing out.
2. Ollama keeps the model loaded in memory for a few minutes. If you have limited RAM/VRAM, the model might unload between sparse interactions, causing latency on the next request. Set `OLLAMA_KEEP_ALIVE=-1` in your host environment to keep the model loaded indefinitely.
