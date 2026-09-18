from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.agents.planner import PlannerAgent
from app.agents.verifier import VerifierAgent
from app.agents.hint import HintAgent
from app.agents.mastery import MasteryTracker
from app.schemas.planner_schemas import Concept, Checkpoint, LearningPlan
from app.schemas.verifier_schemas import VerificationStatus, VerificationResult
from app.schemas.hint_schemas import HintLevel, HintResult

class SessionState(BaseModel):
    session_id: str
    student_id: str
    learning_plan: Optional[LearningPlan] = None
    current_checkpoint_id: Optional[str] = None
    current_hint_level: int = 1

class Orchestrator:
    def __init__(self, planner: PlannerAgent, verifier: VerifierAgent, hint_agent: HintAgent, mastery_tracker: MasteryTracker):
        self.planner = planner
        self.verifier = verifier
        self.hint_agent = hint_agent
        self.mastery_tracker = mastery_tracker
        
        # MVP: in-memory sessions
        self.sessions: Dict[str, SessionState] = {}
        
    def get_session(self, session_id: str, student_id: str) -> SessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id=session_id, student_id=student_id)
        return self.sessions[session_id]
        
    def _get_concept(self, plan: LearningPlan, concept_id: str) -> Optional[Concept]:
        for c in plan.concepts:
            if c.id == concept_id:
                return c
        return None

    def _get_checkpoint(self, plan: LearningPlan, checkpoint_id: str) -> Optional[Checkpoint]:
        for cp in plan.checkpoints:
            if cp.id == checkpoint_id:
                return cp
        return None

    async def process_student_input(self, session_id: str, student_id: str, user_input: str) -> Dict[str, Any]:
        session = self.get_session(session_id, student_id)
        
        # 1. Initialize Plan if None
        if session.learning_plan is None:
            # Assuming the user_input is the initial goal for the planner
            plan = await self.planner.generate_plan(user_input)
            session.learning_plan = plan
            if plan.checkpoints:
                session.current_checkpoint_id = plan.checkpoints[0].id
            return {
                "type": "new_plan",
                "checkpoint": self._get_checkpoint(plan, session.current_checkpoint_id) if session.current_checkpoint_id else None
            }
            
        plan = session.learning_plan
        checkpoint = self._get_checkpoint(plan, session.current_checkpoint_id)
        concept = self._get_concept(plan, checkpoint.concept_id) if checkpoint else None
        
        if not checkpoint or not concept:
            return {"type": "error", "message": "Invalid session state: missing checkpoint or concept"}
            
        # 2. Call Verifier
        verification = await self.verifier.verify_checkpoint(concept, checkpoint, user_input)
        
        # 3. Record Evidence
        self.mastery_tracker.record_verification(student_id, concept.id, verification)
        
        # 4. Control Flow
        if verification.status == VerificationStatus.CORRECT:
            # Reset hint level and advance
            session.current_hint_level = 1
            # Advance to next checkpoint (MVP simplistic logic)
            idx = next((i for i, cp in enumerate(plan.checkpoints) if cp.id == checkpoint.id), -1)
            if idx != -1 and idx + 1 < len(plan.checkpoints):
                session.current_checkpoint_id = plan.checkpoints[idx + 1].id
                next_checkpoint = plan.checkpoints[idx + 1]
                return {
                    "type": "correct",
                    "verification": verification,
                    "next_checkpoint": next_checkpoint
                }
            else:
                session.current_checkpoint_id = None
                return {
                    "type": "completed",
                    "verification": verification,
                    "message": "Learning plan complete!"
                }
                
        elif verification.status == VerificationStatus.OFF_TOPIC:
            # Return re-engagement, don't escalate hint level
            return {
                "type": "off_topic",
                "verification": verification,
                "message": "Let's try to stay focused on the current task."
            }
            
        else:
            # Incorrect or Incomplete
            # Map integer to HintLevel enum
            level_enum = HintLevel(str(min(session.current_hint_level, 4)))
            
            hint_result = await self.hint_agent.generate_hint(
                concept, checkpoint, user_input, verification, level_enum
            )
            
            # Escalate hint level for next attempt
            if session.current_hint_level < 4:
                session.current_hint_level += 1
                
            return {
                "type": verification.status.value,
                "verification": verification,
                "hint": hint_result
            }
