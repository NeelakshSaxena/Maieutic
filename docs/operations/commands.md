# Operations Commands Guide

This document is the command bible for running, debugging, and managing the MentorAI system.

## Docker Lifecycle

**Start the entire stack (detached):**
```bash
docker compose up -d
```

**Rebuild and start the stack (after code changes):**
```bash
docker compose up -d --build
```

**Stop the stack:**
```bash
docker compose down
```

**Stop the stack and wipe all data volumes (DB, Redis, Qdrant):**
```bash
docker compose down -v
```

## Viewing Logs

**View all logs (follow):**
```bash
docker compose logs -f
```

**View specific service logs:**
```bash
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f db
```

## Database Migrations (Alembic)

**Run all pending migrations:**
```bash
docker compose exec api alembic upgrade head
```

**Downgrade one migration:**
```bash
docker compose exec api alembic downgrade -1
```

**Generate a new migration (after changing SQLAlchemy models):**
```bash
docker compose exec api alembic revision --autogenerate -m "Add new feature"
```

## Interactive Shells

**Open a bash shell inside the API container:**
```bash
docker compose exec api bash
```

**Open a Python REPL in the API environment:**
```bash
docker compose exec api python
```

**Connect to PostgreSQL:**
```bash
docker compose exec db psql -U postgres -d postgres
```

**Connect to Redis:**
```bash
docker compose exec redis redis-cli
```

## Testing

**Run the API test suite:**
```bash
docker compose exec api pytest tests/ -v
```

## Ollama (Host Machine)

*These commands run on your host machine, not in Docker.*

**Pull model:**
```bash
ollama pull qwen2
```

**Check if model is loaded:**
```bash
curl http://localhost:11434/api/tags
```
