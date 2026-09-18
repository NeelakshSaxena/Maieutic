from typing import Dict
from app.schemas.mastery_schemas import StudentProfile, ConceptMasteryState
from app.schemas.verifier_schemas import VerificationResult

class MasteryTracker:
    def __init__(self, ema_alpha: float = 0.3):
        # MVP: in-memory storage of profiles
        self.profiles: Dict[str, StudentProfile] = {}
        # EMA weight for the new evidence (alpha). The rest (1 - alpha) is for historical state.
        self.ema_alpha = ema_alpha
        
    def get_profile(self, student_id: str) -> StudentProfile:
        if student_id not in self.profiles:
            self.profiles[student_id] = StudentProfile(student_id=student_id)
        return self.profiles[student_id]
        
    def record_verification(self, student_id: str, concept_id: str, verification: VerificationResult):
        profile = self.get_profile(student_id)
        
        if concept_id not in profile.mastery_by_concept:
            profile.mastery_by_concept[concept_id] = ConceptMasteryState(concept_id=concept_id)
            
        state = profile.mastery_by_concept[concept_id]
        
        # Update attempts and history
        state.attempts += 1
        state.evidence_history.append(verification.mastery_score)
        
        # Update historical mastery using EMA
        if state.attempts == 1:
            # First attempt sets the baseline
            state.historical_mastery = verification.mastery_score
        else:
            state.historical_mastery = (
                (1.0 - self.ema_alpha) * state.historical_mastery +
                self.ema_alpha * verification.mastery_score
            )
            
        # Append any new misconceptions
        for m in verification.misconceptions:
            if m.name not in state.misconceptions_observed:
                state.misconceptions_observed.append(m.name)
