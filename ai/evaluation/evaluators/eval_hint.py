import asyncio
import os
from app.agents.hint import HintAgent, HintError
from app.schemas.planner_schemas import Concept, Checkpoint
from app.schemas.verifier_schemas import VerificationResult, VerificationStatus, Misconception, CriterionEvaluation
from app.schemas.hint_schemas import HintLevel
from dotenv import load_dotenv

load_dotenv()

# Static Concept and Checkpoint
c1 = Concept(
    id="c1", 
    name="Newton's Second Law", 
    description="The acceleration of an object depends on the net force acting on it and its mass (F=ma)."
)
cp1 = Checkpoint(
    id="cp1",
    concept_id="c1",
    task="Explain why the cart accelerates when the force increases.",
    success_criteria="- identifies net force\n- connects force to acceleration\n- recognizes mass as relevant"
)

# Test cases
EVAL_DATA = [
    {
        "name": "Incorrect with Misconception (Level 1)",
        "response": "The force is the acceleration of the object.",
        "verification": VerificationResult(
            is_correct=False,
            status=VerificationStatus.INCORRECT,
            criteria_evaluation=[
                CriterionEvaluation(criterion="identifies net force", met=False, evidence="none"),
                CriterionEvaluation(criterion="connects force to acceleration", met=False, evidence="none"),
                CriterionEvaluation(criterion="recognizes mass as relevant", met=False, evidence="none")
            ],
            misconceptions=[
                Misconception(name="Force equals acceleration", description="Student conflates force and acceleration.", evidence="The force is the acceleration")
            ],
            mastery_score=0.1,
            explanation="Student demonstrates fundamental confusion between two separate quantities."
        ),
        "level": HintLevel.LEVEL_1
    },
    {
        "name": "Incomplete (Level 2)",
        "response": "Because there is more force on it.",
        "verification": VerificationResult(
            is_correct=False,
            status=VerificationStatus.INCOMPLETE,
            criteria_evaluation=[
                CriterionEvaluation(criterion="identifies net force", met=True, evidence="more force on it"),
                CriterionEvaluation(criterion="connects force to acceleration", met=True, evidence="implicit"),
                CriterionEvaluation(criterion="recognizes mass as relevant", met=False, evidence="none")
            ],
            misconceptions=[],
            mastery_score=0.5,
            explanation="Student forgot to mention mass."
        ),
        "level": HintLevel.LEVEL_2
    },
    {
        "name": "Off Topic (Level 1)",
        "response": "What is a cart?",
        "verification": VerificationResult(
            is_correct=False,
            status=VerificationStatus.OFF_TOPIC,
            criteria_evaluation=[
                CriterionEvaluation(criterion="identifies net force", met=False, evidence="none"),
                CriterionEvaluation(criterion="connects force to acceleration", met=False, evidence="none"),
                CriterionEvaluation(criterion="recognizes mass as relevant", met=False, evidence="none")
            ],
            misconceptions=[],
            mastery_score=0.0,
            explanation="Student did not answer the prompt."
        ),
        "level": HintLevel.LEVEL_1
    },
    {
        "name": "Escalation - Same Misconception (Level 3)",
        "response": "The force is the acceleration of the object.",
        "verification": VerificationResult(
            is_correct=False,
            status=VerificationStatus.INCORRECT,
            criteria_evaluation=[
                CriterionEvaluation(criterion="identifies net force", met=False, evidence="none"),
            ],
            misconceptions=[
                Misconception(name="Force equals acceleration", description="Student conflates force and acceleration.", evidence="The force is the acceleration")
            ],
            mastery_score=0.1,
            explanation="Student demonstrates fundamental confusion."
        ),
        "level": HintLevel.LEVEL_3
    },
    {
        "name": "Escalation - Same Misconception (Level 4)",
        "response": "The force is the acceleration of the object.",
        "verification": VerificationResult(
            is_correct=False,
            status=VerificationStatus.INCORRECT,
            criteria_evaluation=[
                CriterionEvaluation(criterion="identifies net force", met=False, evidence="none"),
            ],
            misconceptions=[
                Misconception(name="Force equals acceleration", description="Student conflates force and acceleration.", evidence="The force is the acceleration")
            ],
            mastery_score=0.1,
            explanation="Student demonstrates fundamental confusion."
        ),
        "level": HintLevel.LEVEL_4
    }
]

async def run_evaluation():
    print(f"Starting Hint Agent Evaluation with {os.environ.get('LLM_MODEL', 'default_model')}")
    agent = HintAgent()
    
    for i, data in enumerate(EVAL_DATA):
        print(f"\n[{i+1}/{len(EVAL_DATA)}] Scenario: {data['name']}")
        try:
            result = await agent.generate_hint(c1, cp1, data["response"], data["verification"], data["level"])
            print(f"  Level Generated: {result.level_used.value}")
            print(f"  Target: {result.target}")
            print(f"  Rationale: {result.rationale}")
            print(f"  Hint Text: {result.hint_text}")
            print(f"  Answer Revealed: {result.was_answer_revealed}")
                
        except HintError as e:
            print(f"  Failed to generate valid HintResult: {e}")
            
if __name__ == "__main__":
    asyncio.run(run_evaluation())
