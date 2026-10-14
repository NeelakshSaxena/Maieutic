# Qdrant & Redis Operations

## Redis

Redis acts as our fast, transient state store and Pub/Sub mechanism.

**Connect via CLI:**
```bash
docker compose exec redis redis-cli
```

**Common Commands:**
- `PING`: Check health (should return PONG)
- `KEYS *`: List all keys
- `FLUSHALL`: Wipe all data from Redis

## Qdrant

Qdrant is the vector database for the Student Brain (concept embeddings, semantic search).

**Health Check:**
Qdrant exposes a REST API on port 6333 inside the Compose network. The port is not published to the host in the default `docker-compose.yml`; add a `ports: ["6333:6333"]` mapping to query it from the host. The current application code does not use Qdrant.
```bash
curl http://localhost:6333
```

**Collections List:**
```bash
curl http://localhost:6333/collections
```

*Note: For complex Qdrant debugging, it is recommended to use the Qdrant Web UI (which can be exposed on port 6333 in the browser).*
