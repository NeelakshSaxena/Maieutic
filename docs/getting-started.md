# Getting Started

Welcome to MentorAI! This guide walks you through setting up the project from a fresh machine, from cloning to a fully running local instance using Docker Compose and Ollama.

## Prerequisites

Ensure you have the following installed on your machine:
1. **Docker & Docker Compose:** Required to run the backend, frontend, PostgreSQL, Qdrant, and Redis services.
2. **Ollama:** Required for local LLM inference.
   - [Install Ollama](https://ollama.com/download)
   - *Note for Linux users: Ollama typically runs on port 11434. Make sure it's bound correctly if running remotely.*
3. **Node.js (v18+) & npm** (Optional): For local frontend development outside of Docker.
4. **Python (3.11+)** (Optional): For local backend development outside of Docker.

## 1. Setup Ollama

MentorAI connects to Ollama to generate AI responses. Before starting the main application, ensure Ollama is running and has the required model.

```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Pull the base model (e.g., qwen2:7b or custom fine-tune)
# For the MVP, we use qwen2 as the stand-in until the Phase 2 SFT model is finalized.
ollama pull qwen2
```

## 2. Clone the Repository

```bash
git clone <your-repo-url>
cd Maieutic
```

## 3. Environment Configuration

MentorAI uses environment variables for configuration. You can copy the template if one exists or use the default Docker Compose configuration.

By default, `docker-compose.yml` configures the backend to look for Ollama at `http://host.docker.internal:11434`. 
- **Mac/Windows:** `host.docker.internal` resolves automatically to your host machine where Ollama is running.
- **Linux:** You may need to ensure your `docker-compose.yml` includes `extra_hosts: ["host.docker.internal:host-gateway"]` (which is already configured in this repository).

## 4. Start the Application

Start the entire stack using Docker Compose:

```bash
docker compose up -d --build
```

This command will spin up:
- **db:** PostgreSQL database (Port 5432)
- **redis:** Redis cache (Port 6379)
- **qdrant:** Qdrant vector database (Port 6333)
- **api:** FastAPI backend service (Port 8000)
- **frontend:** Next.js frontend application (Port 3000)

## 5. Verify the Installation

Once Docker Compose finishes building and starting the containers, you can verify the services:

1. **Check Container Status:**
   ```bash
   docker compose ps
   ```
   All services should be in the `Up` state.

2. **Run Database Migrations:**
   Ensure the database schema is up-to-date.
   ```bash
   docker compose exec api alembic upgrade head
   ```

3. **Verify Frontend:**
   Open your browser and navigate to `http://localhost:3000`. You should see the MentorAI Chat Interface and Learning Dashboard.

4. **Verify Backend API:**
   Navigate to `http://localhost:8000/docs` to see the interactive Swagger API documentation.

## Next Steps

- If you encounter issues, refer to [Troubleshooting](troubleshooting.md).
- To interact with the system via CLI or for specialized operations, see the [Operations Commands Guide](operations/commands.md).
- For deeper details on how Ollama connects, read [Ollama Configuration](ollama.md).
