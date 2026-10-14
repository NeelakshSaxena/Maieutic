# Getting Started

The single, tested setup guide is [`DEPLOYMENT.md`](../DEPLOYMENT.md) (Mode 3: local Docker Compose + Ollama). In short:

1. Start Docker Desktop and the existing Ollama container (`docker start ollama`).
2. Confirm the model: `docker exec ollama ollama list` shows `qwen3.5-aggressive:latest`.
3. `docker compose up -d --build` (set `$env:FRONTEND_PORT = "4000"` first if port 3000 is taken).
4. Open http://localhost:4000 and check http://localhost:8000/health/llm.

Optional local development outside Docker: Node 20+ for `apps/frontend` (`npm ci`, `npm run dev`) and Python 3.12 for `apps/api` (set `PYTHONPATH=apps/api` to run the tests from the repo root).

For how the backend reaches Ollama, see [Ollama Configuration](ollama.md).
