import pytest
import asyncio
from app.agents.planner import PlannerAgent, GraphValidationError, PlannerError
from app.schemas.planner_schemas import LearningPlan, Concept, Dependency, Checkpoint

class MockLLMClient:
    def __init__(self, raw_response):
        self.raw_response = raw_response
        
    async def generate_structured(self, system_prompt: str, user_prompt: str, response_format: type = None) -> dict:
        return self.raw_response

@pytest.fixture
def valid_plan_dict():
    return {
        "learning_objectives": "Understand basic recursion.",
        "concepts": [
            {"id": "c1", "name": "Functions", "description": "Basic functions"},
            {"id": "c2", "name": "Base Case", "description": "Recursion base case"},
            {"id": "c3", "name": "Recursive Step", "description": "Calling itself"}
        ],
        "dependencies": [
            {"prerequisite_id": "c1", "concept_id": "c2"},
            {"prerequisite_id": "c2", "concept_id": "c3"}
        ],
        "checkpoints": [
            {"id": "cp1", "concept_id": "c1", "task": "Write a function", "success_criteria": "Works"},
            {"id": "cp2", "concept_id": "c2", "task": "Identify base case", "success_criteria": "Correct base"}
        ]
    }

@pytest.mark.asyncio
async def test_planner_valid_graph(valid_plan_dict):
    agent = PlannerAgent(llm_client=MockLLMClient(valid_plan_dict))
    plan = await agent.generate_plan("Teach me recursion")
    assert len(plan.concepts) == 3
    assert len(plan.dependencies) == 2

@pytest.mark.asyncio
async def test_planner_duplicate_concept(valid_plan_dict):
    valid_plan_dict["concepts"].append({"id": "c1", "name": "Duplicate", "description": "..."})
    agent = PlannerAgent(llm_client=MockLLMClient(valid_plan_dict))
    with pytest.raises(PlannerError, match="Duplicate concept ID"):
        await agent.generate_plan("Teach me recursion")

@pytest.mark.asyncio
async def test_planner_invalid_dependency(valid_plan_dict):
    valid_plan_dict["dependencies"].append({"prerequisite_id": "c1", "concept_id": "c99"})
    agent = PlannerAgent(llm_client=MockLLMClient(valid_plan_dict))
    with pytest.raises(PlannerError, match="Dependency references unknown concept_id: c99"):
        await agent.generate_plan("Teach me recursion")

@pytest.mark.asyncio
async def test_planner_self_dependency(valid_plan_dict):
    valid_plan_dict["dependencies"].append({"prerequisite_id": "c1", "concept_id": "c1"})
    agent = PlannerAgent(llm_client=MockLLMClient(valid_plan_dict))
    with pytest.raises(PlannerError, match="Self-dependency detected for concept: c1"):
        await agent.generate_plan("Teach me recursion")

@pytest.mark.asyncio
async def test_planner_cycle(valid_plan_dict):
    valid_plan_dict["dependencies"].append({"prerequisite_id": "c3", "concept_id": "c1"})
    agent = PlannerAgent(llm_client=MockLLMClient(valid_plan_dict))
    with pytest.raises(PlannerError, match="Circular dependency cycle detected"):
        await agent.generate_plan("Teach me recursion")

@pytest.mark.asyncio
async def test_planner_invalid_checkpoint_concept(valid_plan_dict):
    valid_plan_dict["checkpoints"].append({"id": "cp3", "concept_id": "c99", "task": "...", "success_criteria": "..."})
    agent = PlannerAgent(llm_client=MockLLMClient(valid_plan_dict))
    with pytest.raises(PlannerError, match="Checkpoint references unknown concept_id: c99"):
        await agent.generate_plan("Teach me recursion")
