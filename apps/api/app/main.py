from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import api_router
from app.db.models import Base
from app.db.database import engine

# Automatically create tables for SQLite/MVP testing (Alembic handles this in prod)
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

import os

app = FastAPI(title="MentorAI API", version="0.1.0")

# Configure CORS origins explicitly
cors_origins_env = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:4000,http://127.0.0.1:4000"
)
allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
allow_creds = True
if "*" in allowed_origins:
    allow_creds = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/llm")
async def health_llm():
    from fastapi.responses import JSONResponse
    try:
        from app.core.llm_client import LLMClient
        client = LLMClient(prefix="TRANSFORM")
        info = await client.check_health()
        return {"status": "ok", "message": "LLM reachable and model available", **info}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "error", "message": str(e)})

app.include_router(api_router, prefix="/api")
