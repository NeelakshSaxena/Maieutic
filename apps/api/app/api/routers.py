from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_orchestrator
from app.agents.orchestrator import Orchestrator
from app.schemas.api_schemas import ChatRequest, ChatResponse
from app.services.student_brain import StudentBrainService

api_router = APIRouter()

@api_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    orchestrator = get_orchestrator(db)
    try:
        res = await orchestrator.process_student_input(
            session_id=request.session_id,
            student_id=request.user_id,
            user_input=request.message
        )
        
        cp = res.get("next_checkpoint") or res.get("checkpoint")
        
        return ChatResponse(
            type=res.get("type", "error"),
            message=res.get("message"),
            next_checkpoint=cp.model_dump() if cp else None,
            hint=res.get("hint").model_dump() if res.get("hint") else None,
            verification=res.get("verification").model_dump() if res.get("verification") else None
        )
    except Exception as e:
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
        "learning_plan": session.learning_plan
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
