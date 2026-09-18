import pytest
from app.agents.hint import HintAgent, HintError
from app.schemas.planner_schemas import Concept, Checkpoint
from app.schemas.verifier_schemas import VerificationResult, VerificationStatus, Misconception, CriterionEvaluation
from app.schemas.hint_schemas import HintLevel

class MockLLMClient:
    def __init__(self, raw_responses):
        self.raw_responses = raw_responses
        self.call_count = 0
        
    async def generate_structured(self, system_prompt: str, user_prompt: str, response_format: type = None) -> dict:
        resp = self.raw_responses[self.call_count]
        self.call_count += 1
        return resp

@pytest.fixture
def base_context():
    c = Concept(id="c1", name="Newton's Second Law", description="F = ma")
    cp = Checkpoint(id="cp1", concept_id="c1", task="Explain why it accelerates", success_criteria="- identify force")
    
    vr = VerificationResult(
        is_correct=False,
        status=VerificationStatus.INCORRECT,
        criteria_evaluation=[
            CriterionEvaluation(criterion="identify force", met=False, evidence="none")
        ],
        misconceptions=[
            Misconception(name="Force is velocity", description="Thinks force = velocity", evidence="said force is speed")
        ],
        mastery_score=0.1,
        explanation="Failed."
    )
    return c, cp, vr

@pytest.fixture
def valid_hint_result():
    return {
        "level_used": "1",
        "hint_text": "Re-read the question.",
        "target": "Force is velocity misconception",
        "rationale": "Needs to separate force from velocity",
        "was_answer_revealed": False
    }

@pytest.mark.asyncio
async def test_hint_valid(base_context, valid_hint_result):
    c, cp, vr = base_context
    agent = HintAgent(llm_client=MockLLMClient([valid_hint_result]))
    result = await agent.generate_hint(c, cp, "Because it has high speed.", vr, HintLevel.LEVEL_1)
    
    assert result.level_used == HintLevel.LEVEL_1
    assert result.was_answer_revealed is False

@pytest.mark.asyncio
async def test_hint_invalid_level(base_context, valid_hint_result):
    c, cp, vr = base_context
    # Agent requests Level 2, but LLM returns Level 1
    # This should trigger a retry. We'll pass invalid then valid.
    valid_correct_level = valid_hint_result.copy()
    valid_correct_level["level_used"] = "2"
    
    mock_client = MockLLMClient([valid_hint_result, valid_correct_level])
    agent = HintAgent(llm_client=mock_client)
    
    result = await agent.generate_hint(c, cp, "...", vr, HintLevel.LEVEL_2)
    assert result.level_used == HintLevel.LEVEL_2
    assert mock_client.call_count == 2
