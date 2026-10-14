import asyncio
import os
import sys
from typing import Any, Dict

# Ensure apps/api is in Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import runpod
except ImportError:
    runpod = None

from app.db.database import SessionLocal, engine
from app.db.models import Base
from app.api.deps import get_orchestrator

# Initialize tables if SQLite/MVP
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

async def async_handler(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    RunPod Serverless Worker Handler for MentorAI.
    Accepts job['input'] payload:
      {
        "session_id": "string",
        "user_id": "string",
        "message": "string"
      }
    """
    job_input = job.get("input", {})
    
    # Simple ping/health check
    if job_input.get("ping") or job_input.get("health"):
        return {"status": "ok", "service": "mentorai-serverless-worker"}
        
    session_id = job_input.get("session_id", "default_session")
    user_id = job_input.get("user_id", "default_user")
    message = job_input.get("message")
    
    if not message:
        return {
            "error": "Missing 'message' in job input payload",
            "status": 400
        }
        
    db = SessionLocal()
    try:
        orchestrator = get_orchestrator(db)
        result = await orchestrator.process_student_input(
            session_id=session_id,
            student_id=user_id,
            user_input=message
        )
        
        cp = result.get("next_checkpoint") or result.get("checkpoint")
        msg = result.get("message")
        if not msg:
            if result.get("hint"):
                hint_obj = result["hint"]
                msg = getattr(hint_obj, "hint_text", None) or (hint_obj.get("hint_text") if isinstance(hint_obj, dict) else None)
            elif cp:
                task = getattr(cp, "task", None) or (cp.get("task") if isinstance(cp, dict) else None)
                if result.get("type") == "correct":
                    msg = f"Great job! That's correct. Next task: {task}"
                else:
                    msg = f"Let's get started. Your task: {task}"

        formatted_data = {
            "type": result.get("type", "unknown"),
            "message": msg,
            "next_checkpoint": cp.model_dump() if hasattr(cp, "model_dump") else (cp if isinstance(cp, dict) else None),
            "hint": result.get("hint").model_dump() if hasattr(result.get("hint"), "model_dump") else (result.get("hint") if isinstance(result.get("hint"), dict) else None),
            "verification": result.get("verification").model_dump() if hasattr(result.get("verification"), "model_dump") else (result.get("verification") if isinstance(result.get("verification"), dict) else None),
        }
        return {
            "status": "success",
            "data": formatted_data
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()

def handler(job: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for RunPod worker runner."""
    return asyncio.run(async_handler(job))

if __name__ == "__main__":
    if runpod is None:
        print("Error: 'runpod' package is not installed. Please install runpod to run as a serverless worker.")
        sys.exit(1)
        
    print("[MentorAI] Starting RunPod Serverless Worker...")
    runpod.serverless.start({"handler": handler})
