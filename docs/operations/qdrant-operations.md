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
Qdrant exposes a REST API on port 6333.
```bash
curl http://localhost:6333
```

**Collections List:**
```bash
curl http://localhost:6333/collections
```

*Note: For complex Qdrant debugging, it is recommended to use the Qdrant Web UI (which can be exposed on port 6333 in the browser).*
