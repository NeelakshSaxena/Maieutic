import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.orchestrator import Orchestrator
from app.services.student_brain import StudentBrainService
from app.db.models import Base, StudentProfile, ConceptMasteryState
from app.schemas.planner_schemas import Concept, Checkpoint, LearningPlan
from app.schemas.verifier_schemas import VerificationResult, VerificationStatus
from app.schemas.hint_schemas import HintResult, HintLevel

# Test DB Setup
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def brain(db_session):
    return StudentBrainService(db=db_session, qdrant=None) # Qdrant mocked out

class DummyPlanner:
    async def generate_plan(self, query):
        return LearningPlan(
            learning_objectives="Test",
            concepts=[Concept(id="c1", name="C1", description="desc1")],
            dependencies=[],
            checkpoints=[
                Checkpoint(id="cp1", concept_id="c1", task="Task 1", success_criteria="crit"),
                Checkpoint(id="cp2", concept_id="c1", task="Task 2", success_criteria="crit")
            ]
        )

class DummyVerifier:
    def __init__(self, statuses):
        self.statuses = statuses
        self.call_count = 0
        
    async def verify_checkpoint(self, concept, checkpoint, student_response):
        status = self.statuses[self.call_count]
        self.call_count += 1
        return VerificationResult(
            is_correct=(status == VerificationStatus.CORRECT),
            status=status,
            criteria_evaluation=[],
            misconceptions=[],
            mastery_score=1.0 if status == VerificationStatus.CORRECT else 0.1,
            explanation="Test"
        )

class DummyHint:
    async def generate_hint(self, concept, checkpoint, student_response, verification, level):
        return HintResult(
            level_used=level,
            hint_text=f"Hint level {level.value}",
            target="target",
            rationale="rationale",
            was_answer_revealed=False
        )

@pytest.mark.asyncio
async def test_orchestrator_initial_plan(brain):
    orch = Orchestrator(DummyPlanner(), DummyVerifier([]), DummyHint(), brain)
    res = await orch.process_student_input("session1", "student1", "teach me")
    assert res["type"] == "new_plan"
    assert res["checkpoint"].id == "cp1"

@pytest.mark.asyncio
async def test_orchestrator_correct_advance(brain, db_session):
    orch = Orchestrator(DummyPlanner(), DummyVerifier([VerificationStatus.CORRECT]), DummyHint(), brain)
    await orch.process_student_input("session1", "student1", "teach me") # Init plan
    
    res = await orch.process_student_input("session1", "student1", "correct answer")
    assert res["type"] == "correct"
    assert res["next_checkpoint"].id == "cp2"
    
    # Check mastery updated in DB
    profile = db_session.query(StudentProfile).filter_by(user_id="student1").first()
    state = db_session.query(ConceptMasteryState).filter_by(profile_id=profile.id, concept_id="c1").first()
    assert state.historical_mastery == 1.0
    assert state.attempts == 1

@pytest.mark.asyncio
async def test_orchestrator_incorrect_hint_escalation(brain):
    # 3 incorrects in a row
    statuses = [VerificationStatus.INCORRECT, VerificationStatus.INCOMPLETE, VerificationStatus.INCORRECT]
    orch = Orchestrator(DummyPlanner(), DummyVerifier(statuses), DummyHint(), brain)
    await orch.process_student_input("session1", "student1", "teach me")
    
    # Attempt 1
    res1 = await orch.process_student_input("session1", "student1", "wrong")
    assert res1["type"] == "incorrect"
    assert res1["hint"].level_used == HintLevel.LEVEL_1
    
    # Attempt 2
    res2 = await orch.process_student_input("session1", "student1", "wrong again")
    assert res2["type"] == "incomplete"
    assert res2["hint"].level_used == HintLevel.LEVEL_2
    
    # Attempt 3
    res3 = await orch.process_student_input("session1", "student1", "still wrong")
    assert res3["type"] == "incorrect"
    assert res3["hint"].level_used == HintLevel.LEVEL_3

@pytest.mark.asyncio
async def test_orchestrator_off_topic(brain):
    orch = Orchestrator(DummyPlanner(), DummyVerifier([VerificationStatus.OFF_TOPIC]), DummyHint(), brain)
    await orch.process_student_input("session1", "student1", "teach me")
    
    res = await orch.process_student_input("session1", "student1", "what is life")
    assert res["type"] == "off_topic"
    assert "focused" in res["message"]
    
    # Session hint level should not escalate
    session = brain.get_session("session1")
    assert session.current_hint_level == 1
