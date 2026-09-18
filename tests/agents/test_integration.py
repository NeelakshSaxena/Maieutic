import pytest
from app.schemas.planner_schemas import Concept, Checkpoint, LearningPlan
from app.schemas.verifier_schemas import VerificationResult, VerificationStatus, CriterionEvaluation, Misconception
from app.schemas.hint_schemas import HintResult, HintLevel
from app.agents.planner import PlannerAgent
from app.agents.verifier import VerifierAgent
from app.agents.hint import HintAgent

class MockLLMClient:
    def __init__(self, raw_responses):
        self.raw_responses = raw_responses
        self.call_count = 0
        
    async def generate_structured(self, system_prompt: str, user_prompt: str, response_format: type = None) -> dict:
        resp = self.raw_responses[self.call_count]
        self.call_count += 1
        return resp

@pytest.fixture
def base_concept():
    return Concept(
        id="c1",
        name="Newton's Second Law",
        description="F = ma"
    )

@pytest.fixture
def mock_learning_plan():
    return {
        "learning_objectives": "Teach physics",
        "concepts": [
            {"id": "c1", "name": "Newton's Second Law", "description": "F=ma"}
        ],
        "dependencies": [],
        "checkpoints": [
            {
                "id": "cp1",
                "concept_id": "c1",
                "task": "Explain acceleration when force increases",
                "success_criteria": "- Identify force\n- Identify mass"
            }
        ]
    }

@pytest.mark.asyncio
async def test_integration_correct_response(base_concept, mock_learning_plan):
    """
    Case 1: Correct response
    Student -> correct
    Verifier -> correct
    """
    planner_client = MockLLMClient([mock_learning_plan])
    planner = PlannerAgent(llm_client=planner_client)
    plan = await planner.generate_plan("Teach me physics")
    checkpoint = plan.checkpoints[0]
    
    verifier_client = MockLLMClient([{
        "is_correct": True,
        "status": "correct",
        "criteria_evaluation": [
            {"criterion": "Identify force", "met": True, "evidence": "mentioned force"},
            {"criterion": "Identify mass", "met": True, "evidence": "mentioned mass"}
        ],
        "misconceptions": [],
        "mastery_score": 0.9,
        "explanation": "Perfect."
    }])
    verifier = VerifierAgent(llm_client=verifier_client)
    
    verification = await verifier.verify_checkpoint(base_concept, checkpoint, "Force increases acceleration.")
    
    # In orchestrator, if status is correct, we do NOT call HintAgent
    assert verification.status == VerificationStatus.CORRECT
    assert verification.is_correct is True

@pytest.mark.asyncio
async def test_integration_incorrect_response(base_concept, mock_learning_plan):
    """
    Case 2: Incorrect response
    Verifier -> incorrect + misconception
    Hint Level 1 -> target addresses misconception
    """
    checkpoint = Checkpoint(id="cp1", concept_id="c1", task="Explain", success_criteria="...")
    
    verifier_client = MockLLMClient([{
        "is_correct": False,
        "status": "incorrect",
        "criteria_evaluation": [],
        "misconceptions": [
            {"name": "Force = Velocity", "description": "Conflates them", "evidence": "Said force is speed"}
        ],
        "mastery_score": 0.1,
        "explanation": "Fundamental confusion."
    }])
    verifier = VerifierAgent(llm_client=verifier_client)
    verification = await verifier.verify_checkpoint(base_concept, checkpoint, "Force is speed.")
    
    assert verification.status == VerificationStatus.INCORRECT
    
    hint_client = MockLLMClient([{
        "level_used": "1",
        "hint_text": "Are force and speed the same thing?",
        "target": "Force = Velocity misconception",
        "rationale": "Directing attention to the misconception",
        "was_answer_revealed": False
    }])
    hint_agent = HintAgent(llm_client=hint_client)
    hint = await hint_agent.generate_hint(base_concept, checkpoint, "Force is speed.", verification, HintLevel.LEVEL_1)
    
    assert hint.level_used == HintLevel.LEVEL_1
    assert hint.was_answer_revealed is False
    assert "misconception" in hint.target.lower()

@pytest.mark.asyncio
async def test_integration_incomplete_response(base_concept, mock_learning_plan):
    """
    Case 3: Incomplete response
    Verifier -> incomplete + unmet criterion
    Hint -> targets missing criterion
    """
    checkpoint = Checkpoint(id="cp1", concept_id="c1", task="Explain", success_criteria="...")
    
    verifier_client = MockLLMClient([{
        "is_correct": False,
        "status": "incomplete",
        "criteria_evaluation": [
            {"criterion": "Identify force", "met": True, "evidence": "mentioned force"},
            {"criterion": "Identify mass", "met": False, "evidence": "none"}
        ],
        "misconceptions": [],
        "mastery_score": 0.5,
        "explanation": "Forgot mass."
    }])
    verifier = VerifierAgent(llm_client=verifier_client)
    verification = await verifier.verify_checkpoint(base_concept, checkpoint, "Force increases.")
    
    assert verification.status == VerificationStatus.INCOMPLETE
    
    hint_client = MockLLMClient([{
        "level_used": "2",
        "hint_text": "You mentioned force. What other property of the object matters?",
        "target": "Identify mass criterion",
        "rationale": "Prompting for the missing criterion",
        "was_answer_revealed": False
    }])
    hint_agent = HintAgent(llm_client=hint_client)
    hint = await hint_agent.generate_hint(base_concept, checkpoint, "Force increases.", verification, HintLevel.LEVEL_2)
    
    assert hint.level_used == HintLevel.LEVEL_2
    assert "mass criterion" in hint.target.lower()
