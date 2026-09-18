from typing import Dict, Any, Optional
from app.agents.planner import PlannerAgent
from app.agents.verifier import VerifierAgent
from app.agents.hint import HintAgent
from app.services.student_brain import StudentBrainService
from app.schemas.planner_schemas import Concept, Checkpoint, LearningPlan
from app.schemas.verifier_schemas import VerificationStatus, VerificationResult
from app.schemas.hint_schemas import HintLevel, HintResult

class Orchestrator:
    def __init__(
        self, 
        planner: PlannerAgent, 
        verifier: VerifierAgent, 
        hint_agent: HintAgent, 
        brain: StudentBrainService
    ):
        self.planner = planner
        self.verifier = verifier
        self.hint_agent = hint_agent
        self.brain = brain
        
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
        session = self.brain.get_session(session_id)
        
        # 1. Initialize Plan if None
        if not session:
            # Assuming the user_input is the initial goal for the planner
            plan = await self.planner.generate_plan(user_input)
            
            current_checkpoint_id = plan.checkpoints[0].id if plan.checkpoints else None
            session = self.brain.create_session(
                user_id=student_id,
                goal=user_input,
                learning_plan=plan.model_dump(),
                current_checkpoint_id=current_checkpoint_id,
                session_id=session_id
            )
            
            return {
                "type": "new_plan",
                "checkpoint": self._get_checkpoint(plan, session.current_checkpoint_id) if session.current_checkpoint_id else None
            }
            
        plan = LearningPlan(**session.learning_plan)
        checkpoint = self._get_checkpoint(plan, session.current_checkpoint_id)
        concept = self._get_concept(plan, checkpoint.concept_id) if checkpoint else None
        
        if not checkpoint or not concept:
            return {"type": "error", "message": "Invalid session state: missing checkpoint or concept"}
            
        # 2. Call Verifier
        verification = await self.verifier.verify_checkpoint(concept, checkpoint, user_input)
        
        # 3. Record Evidence
        self.brain.record_verification(
            user_id=student_id, 
            session_id=session.id,
            concept_id=concept.id,
            checkpoint_id=checkpoint.id,
            student_response=user_input,
            verification=verification
        )
        
        # 4. Control Flow
        if verification.status == VerificationStatus.CORRECT:
            # Reset hint level and advance
            self.brain.update_session(session.id, current_hint_level=1)
            
            # Advance to next checkpoint (MVP simplistic logic)
            idx = next((i for i, cp in enumerate(plan.checkpoints) if cp.id == checkpoint.id), -1)
            if idx != -1 and idx + 1 < len(plan.checkpoints):
                next_checkpoint = plan.checkpoints[idx + 1]
                self.brain.update_session(session.id, current_checkpoint_id=next_checkpoint.id)
                return {
                    "type": "correct",
                    "verification": verification,
                    "next_checkpoint": next_checkpoint
                }
            else:
                self.brain.update_session(session.id, current_checkpoint_id=None, status="completed")
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
                self.brain.update_session(session.id, current_hint_level=session.current_hint_level + 1)
                
            return {
                "type": verification.status.value,
                "verification": verification,
                "hint": hint_result
            }
