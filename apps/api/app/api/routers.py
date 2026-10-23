import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_orchestrator
from app.agents.orchestrator import Orchestrator
from app.core.llm_client import LLMUnavailableError, LLMModelNotFoundError
from app.schemas.api_schemas import ChatRequest, ChatResponse
from app.services.student_brain import StudentBrainService

api_router = APIRouter()

def _persist_turn(db: Session, request: ChatRequest, response: ChatResponse) -> None:
    """Store the student message and tutor reply so the conversation can be restored.

    Best effort: a failure here must never fail the chat request itself, and nothing is
    stored for sessions that do not exist (e.g. when the orchestrator is mocked).
    """
    try:
        brain = StudentBrainService(db=db)
        if not brain.get_session(request.session_id):
            return
        brain.add_message(request.session_id, "student", request.message)
        brain.add_message(request.session_id, "tutor", response.message or "", payload=response.model_dump())
    except Exception:
        db.rollback()
        logging.exception("[MentorAI] Could not persist chat turn for session %s", request.session_id)


@api_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    orchestrator = get_orchestrator(db)
    try:
        import logging
        logging.info(f"[MentorAI] Request received! LLM model is loaded and processing request for user {request.user_id}...")
        print("[MentorAI] Active Request: Processing inference via local Ollama. This may take 60-120 seconds...")
        
        res = await orchestrator.process_student_input(
            session_id=request.session_id,
            student_id=request.user_id,
            user_input=request.message
        )
        
        cp = res.get("next_checkpoint") or res.get("checkpoint")
        msg = res.get("message")
        if not msg:
            if res.get("hint"):
                hint_obj = res["hint"]
                msg = getattr(hint_obj, "hint_text", None) or (hint_obj.get("hint_text") if isinstance(hint_obj, dict) else None)
            elif cp:
                task = getattr(cp, "task", None) or (cp.get("task") if isinstance(cp, dict) else None)
                if res.get("type") == "correct":
                    msg = f"Great job! That's correct. Next task: {task}"
                else:
                    msg = f"Let's get started. Your task: {task}"

        response = ChatResponse(
            type=res.get("type", "error"),
            message=msg,
            next_checkpoint=cp.model_dump() if hasattr(cp, "model_dump") else (cp if isinstance(cp, dict) else None),
            hint=res.get("hint").model_dump() if hasattr(res.get("hint"), "model_dump") else (res.get("hint") if isinstance(res.get("hint"), dict) else None),
            verification=res.get("verification").model_dump() if hasattr(res.get("verification"), "model_dump") else (res.get("verification") if isinstance(res.get("verification"), dict) else None)
        )
        _persist_turn(db, request, response)
        return response
    except Exception as e:
        if isinstance(e, (LLMUnavailableError, LLMModelNotFoundError)):
            raise HTTPException(status_code=503, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/session/{session_id}")
async def get_session_endpoint(session_id: str, db: Session = Depends(get_db)):
    brain = StudentBrainService(db=db)
    session = brain.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": session.id,
        "goal": session.goal,
        "status": session.status,
        "current_checkpoint_id": session.current_checkpoint_id,
        "learning_plan": session.learning_plan,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }


@api_router.get("/sessions")
async def list_sessions_endpoint(user_id: str, db: Session = Depends(get_db)):
    brain = StudentBrainService(db=db)
    sessions = []
    for s in brain.list_sessions(user_id):
        checkpoints = (s.learning_plan or {}).get("checkpoints", [])
        ids = [c.get("id") for c in checkpoints]
        sessions.append({
            "id": s.id,
            "goal": s.goal,
            "status": s.status,
            "current_checkpoint_id": s.current_checkpoint_id,
            "checkpoint_count": len(ids),
            "completed_checkpoints": (
                len(ids) if s.status == "completed"
                else (ids.index(s.current_checkpoint_id) if s.current_checkpoint_id in ids else 0)
            ),
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        })
    return {"user_id": user_id, "sessions": sessions}


@api_router.get("/session/{session_id}/messages")
async def get_session_messages_endpoint(session_id: str, db: Session = Depends(get_db)):
    brain = StudentBrainService(db=db)
    if not brain.get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session_id,
        "messages": [
            {"id": m.id, "role": m.role, "content": m.content, "payload": m.payload, "created_at": m.created_at}
            for m in brain.get_messages(session_id)
        ],
    }

@api_router.get("/brain/{user_id}")
async def get_brain_endpoint(user_id: str, db: Session = Depends(get_db)):
    brain = StudentBrainService(db=db)
    profile = brain.get_or_create_profile(user_id)
    
    mastery_data = []
    for state in profile.mastery_states:
        mastery_data.append({
            "concept_id": state.concept_id,
            "historical_mastery": state.historical_mastery,
            "attempts": state.attempts,
            "misconceptions_observed": state.misconceptions_observed
        })
        
    return {
        "user_id": profile.user_id,
        "mastery_states": mastery_data
    }

@api_router.get("/revision/{user_id}")
async def get_revision_endpoint(user_id: str, db: Session = Depends(get_db)):
    brain = StudentBrainService(db=db)
    profile = brain.get_or_create_profile(user_id)
    
    revision_data = []
    for schedule in profile.revision_schedules:
        revision_data.append({
            "concept_id": schedule.concept_id,
            "next_review_date": schedule.next_review_date,
            "interval_days": schedule.interval_days,
            "ease_factor": schedule.ease_factor
        })
        
    return {
        "user_id": profile.user_id,
        "revision_schedules": revision_data
    }
