import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    profile = relationship("StudentProfile", back_populates="user", uselist=False)

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    
    # Relationships
    user = relationship("User", back_populates="profile")
    mastery_states = relationship("ConceptMasteryState", back_populates="profile", cascade="all, delete-orphan")
    learning_sessions = relationship("LearningSession", back_populates="profile", cascade="all, delete-orphan")
    revision_schedules = relationship("RevisionSchedule", back_populates="profile", cascade="all, delete-orphan")

class ConceptMasteryState(Base):
    __tablename__ = "concept_mastery_states"
    id = Column(String, primary_key=True, default=generate_uuid)
    profile_id = Column(String, ForeignKey("student_profiles.id"))
    concept_id = Column(String, index=True) # ID referencing knowledge graph or planner
    historical_mastery = Column(Float, default=0.0)
    attempts = Column(Integer, default=0)
    misconceptions_observed = Column(JSON, default=list) # List of strings
    evidence_history = Column(JSON, default=list) # List of floats
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = relationship("StudentProfile", back_populates="mastery_states")
    mastery_attempts = relationship("MasteryAttempt", back_populates="concept_state", cascade="all, delete-orphan")

class MasteryAttempt(Base):
    __tablename__ = "mastery_attempts"
    id = Column(String, primary_key=True, default=generate_uuid)
    concept_state_id = Column(String, ForeignKey("concept_mastery_states.id"))
    session_id = Column(String, ForeignKey("learning_sessions.id"))
    checkpoint_id = Column(String)
    student_response = Column(String)
    is_correct = Column(Boolean)
    status = Column(String)
    mastery_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    concept_state = relationship("ConceptMasteryState", back_populates="mastery_attempts")
    session = relationship("LearningSession", back_populates="attempts")

class LearningSession(Base):
    __tablename__ = "learning_sessions"
    id = Column(String, primary_key=True, default=generate_uuid)
    profile_id = Column(String, ForeignKey("student_profiles.id"))
    goal = Column(String)
    learning_plan = Column(JSON) # Serialized LearningPlan schema
    current_checkpoint_id = Column(String, nullable=True)
    current_hint_level = Column(Integer, default=1)
    status = Column(String, default="active") # active, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = relationship("StudentProfile", back_populates="learning_sessions")
    attempts = relationship("MasteryAttempt", back_populates="session")

class RevisionSchedule(Base):
    __tablename__ = "revision_schedules"
    id = Column(String, primary_key=True, default=generate_uuid)
    profile_id = Column(String, ForeignKey("student_profiles.id"))
    concept_id = Column(String, index=True)
    next_review_date = Column(DateTime)
    interval_days = Column(Integer, default=1)
    ease_factor = Column(Float, default=2.5)
    
    # Relationships
    profile = relationship("StudentProfile", back_populates="revision_schedules")
