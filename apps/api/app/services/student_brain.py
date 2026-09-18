from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from typing import Optional, List, Dict
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from app.db.models import (
    User, StudentProfile, ConceptMasteryState, MasteryAttempt, LearningSession, RevisionSchedule
)
from app.schemas.verifier_schemas import VerificationResult

class StudentBrainService:
    def __init__(self, db: Session, qdrant: Optional[QdrantClient] = None, ema_alpha: float = 0.3):
        self.db = db
        self.qdrant = qdrant
        self.ema_alpha = ema_alpha
        self.collection_name = "student_brain_memory"
        
        if self.qdrant:
            self._ensure_qdrant_collection()

    def _ensure_qdrant_collection(self):
        try:
            self.qdrant.get_collection(self.collection_name)
        except Exception:
            # Assumes embedding size of 384 for a small local embedding model, e.g. all-MiniLM-L6-v2
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )

    def get_or_create_profile(self, user_id: str) -> StudentProfile:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, email=f"{user_id}@example.com")
            self.db.add(user)
            self.db.commit()
            
        profile = self.db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        if not profile:
            profile = StudentProfile(user_id=user_id)
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        return profile

    def record_verification(
        self, 
        user_id: str, 
        session_id: str,
        concept_id: str, 
        checkpoint_id: str,
        student_response: str,
        verification: VerificationResult
    ) -> ConceptMasteryState:
        
        profile = self.get_or_create_profile(user_id)
        
        state = self.db.query(ConceptMasteryState).filter(
            ConceptMasteryState.profile_id == profile.id,
            ConceptMasteryState.concept_id == concept_id
        ).first()
        
        if not state:
            state = ConceptMasteryState(
                profile_id=profile.id,
                concept_id=concept_id,
                historical_mastery=verification.mastery_score,
                attempts=1,
                misconceptions_observed=[],
                evidence_history=[verification.mastery_score]
            )
            self.db.add(state)
        else:
            state.attempts += 1
            # EMA Update
            state.historical_mastery = (
                (1.0 - self.ema_alpha) * state.historical_mastery +
                self.ema_alpha * verification.mastery_score
            )
            
            # Since JSON lists in sqlite/sqlalchemy sometimes don't detect mutations, create a new list
            new_history = list(state.evidence_history)
            new_history.append(verification.mastery_score)
            state.evidence_history = new_history
            
        # Append misconceptions
        new_misconceptions = list(state.misconceptions_observed)
        for m in verification.misconceptions:
            if m.name not in new_misconceptions:
                new_misconceptions.append(m.name)
        state.misconceptions_observed = new_misconceptions
        
        self.db.commit()
        self.db.refresh(state)
        
        # Log the attempt
        attempt = MasteryAttempt(
            concept_state_id=state.id,
            session_id=session_id,
            checkpoint_id=checkpoint_id,
            student_response=student_response,
            is_correct=verification.is_correct,
            status=verification.status.value,
            mastery_score=verification.mastery_score
        )
        self.db.add(attempt)
        
        # Update spaced repetition schedule (SuperMemo-2 simplified)
        self._update_revision_schedule(profile.id, concept_id, verification.is_correct)
        
        self.db.commit()
        return state

    def _update_revision_schedule(self, profile_id: str, concept_id: str, is_correct: bool):
        schedule = self.db.query(RevisionSchedule).filter(
            RevisionSchedule.profile_id == profile_id,
            RevisionSchedule.concept_id == concept_id
        ).first()
        
        if not schedule:
            schedule = RevisionSchedule(
                profile_id=profile_id, 
                concept_id=concept_id,
                next_review_date=datetime.utcnow() + timedelta(days=1)
            )
            self.db.add(schedule)
        else:
            if is_correct:
                schedule.interval_days = max(1, int(schedule.interval_days * schedule.ease_factor))
                schedule.ease_factor += 0.1
            else:
                schedule.interval_days = 1
                schedule.ease_factor = max(1.3, schedule.ease_factor - 0.2)
            schedule.next_review_date = datetime.utcnow() + timedelta(days=schedule.interval_days)

    def get_session(self, session_id: str) -> Optional[LearningSession]:
        return self.db.query(LearningSession).filter(LearningSession.id == session_id).first()
        
    def create_session(self, user_id: str, goal: str, learning_plan: dict, current_checkpoint_id: str, session_id: Optional[str] = None) -> LearningSession:
        profile = self.get_or_create_profile(user_id)
        if not session_id:
            session_id = str(uuid.uuid4())
        session = LearningSession(
            id=session_id,
            profile_id=profile.id,
            goal=goal,
            learning_plan=learning_plan,
            current_checkpoint_id=current_checkpoint_id
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def update_session(self, session_id: str, **kwargs):
        session = self.get_session(session_id)
        if session:
            for key, value in kwargs.items():
                setattr(session, key, value)
            self.db.commit()
            self.db.refresh(session)
        return session
