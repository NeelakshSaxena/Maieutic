import pytest
from app.agents.verifier import VerifierAgent, VerifierError
from app.schemas.planner_schemas import Concept, Checkpoint
from app.schemas.verifier_schemas import VerificationStatus

class MockLLMClient:
    def __init__(self, raw_responses):
        self.raw_responses = raw_responses
        self.call_count = 0
        
    async def generate_structured(self, system_prompt: str, user_prompt: str, response_format: type = None) -> dict:
        resp = self.raw_responses[self.call_count]
        self.call_count += 1
        return resp

@pytest.fixture
def concept_and_checkpoint():
    c = Concept(id="c1", name="Newton's Second Law", description="F = ma")
    cp = Checkpoint(id="cp1", concept_id="c1", task="Explain why it accelerates", success_criteria="- identify force\n- connect to mass")
    return c, cp

@pytest.fixture
def valid_correct_result():
    return {
        "is_correct": True,
        "status": "correct",
        "criteria_evaluation": [
            {"criterion": "identify force", "met": True, "evidence": "mentioned push"},
            {"criterion": "connect to mass", "met": True, "evidence": "mentioned heavy"}
        ],
        "misconceptions": [],
        "mastery_score": 0.9,
        "explanation": "Student understands both."
    }

@pytest.mark.asyncio
async def test_verifier_valid_correct(concept_and_checkpoint, valid_correct_result):
    c, cp = concept_and_checkpoint
    agent = VerifierAgent(llm_client=MockLLMClient([valid_correct_result]))
    result = await agent.verify_checkpoint(c, cp, "Because of the force on the mass.")
    
    assert result.is_correct is True
    assert result.status == VerificationStatus.CORRECT
    assert result.mastery_score == 0.9
    assert len(result.criteria_evaluation) == 2

@pytest.mark.asyncio
async def test_verifier_incorrect_with_misconception(concept_and_checkpoint):
    c, cp = concept_and_checkpoint
    res = {
        "is_correct": False,
        "status": "incorrect",
        "criteria_evaluation": [],
        "misconceptions": [
            {"name": "Force = velocity", "description": "Student thinks force is velocity", "evidence": "said force is speed"}
        ],
        "mastery_score": 0.1,
        "explanation": "Failed."
    }
    agent = VerifierAgent(llm_client=MockLLMClient([res]))
    result = await agent.verify_checkpoint(c, cp, "Because it has high speed.")
    
    assert result.is_correct is False
    assert result.status == VerificationStatus.INCORRECT
    assert len(result.misconceptions) == 1

@pytest.mark.asyncio
async def test_verifier_inconsistent_is_correct(concept_and_checkpoint, valid_correct_result):
    c, cp = concept_and_checkpoint
    # Make it inconsistent
    valid_correct_result["is_correct"] = True
    valid_correct_result["status"] = "incorrect"
    
    agent = VerifierAgent(llm_client=MockLLMClient([valid_correct_result, valid_correct_result, valid_correct_result]))
    
    with pytest.raises(VerifierError, match="is_correct must be True exactly when"):
        await agent.verify_checkpoint(c, cp, "...")

@pytest.mark.asyncio
async def test_verifier_retry_logic(concept_and_checkpoint, valid_correct_result):
    c, cp = concept_and_checkpoint
    
    invalid_result = valid_correct_result.copy()
    invalid_result["mastery_score"] = 1.5 # Invalid according to schema

    mock_client = MockLLMClient([invalid_result, valid_correct_result])
    agent = VerifierAgent(llm_client=mock_client)
    
    # First call fails, second succeeds
    result = await agent.verify_checkpoint(c, cp, "...")
    assert result.is_correct is True
    assert mock_client.call_count == 2
