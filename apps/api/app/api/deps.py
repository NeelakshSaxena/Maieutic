from typing import Generator
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.agents.orchestrator import Orchestrator
from app.agents.planner import PlannerAgent
from app.agents.verifier import VerifierAgent
from app.agents.hint import HintAgent
from app.services.student_brain import StudentBrainService

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_orchestrator(db: Session) -> Orchestrator:
    # In a real app we might inject Qdrant here too, but for MVP it's mocked or optional
    brain = StudentBrainService(db=db)
    planner = PlannerAgent()
    verifier = VerifierAgent()
    hint_agent = HintAgent()
    return Orchestrator(planner, verifier, hint_agent, brain)
