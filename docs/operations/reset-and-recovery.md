# Reset and Recovery

If your environment enters a corrupted state (e.g., bad migrations, corrupt Docker volumes, dangling containers), follow these procedures.

## Hard Reset (Wipe All Data)

> **WARNING:** This will permanently delete all local student profiles, mastery states, sessions, and cached data.

To cleanly wipe the environment and restart from scratch:

```bash
# 1. Stop all containers and remove volumes
docker compose down -v

# 2. Rebuild and start the containers
docker compose up -d --build

# 3. Apply fresh database migrations
docker compose exec api alembic upgrade head
```

## Soft Reset (Restart Services)

If a service hangs (e.g., the API stops responding to the frontend), a soft restart is usually sufficient:

```bash
# Restart only the API
docker compose restart api

# Restart everything without losing data
docker compose down
docker compose up -d
```
