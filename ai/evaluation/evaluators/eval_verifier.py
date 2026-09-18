import asyncio
import os
from app.agents.verifier import VerifierAgent, VerifierError
from app.schemas.planner_schemas import Concept, Checkpoint
from dotenv import load_dotenv

load_dotenv()

# Static pairs of (Concept, Checkpoint, Student Response)
EVAL_DATA = [
    {
        "concept": Concept(
            id="c1", 
            name="Newton's Second Law", 
            description="The acceleration of an object depends on the net force acting on it and its mass (F=ma)."
        ),
        "checkpoint": Checkpoint(
            id="cp1",
            concept_id="c1",
            task="Explain why the cart accelerates when the force increases.",
            success_criteria="- identifies net force\n- connects force to acceleration\n- recognizes mass as relevant"
        ),
        "response": "Because you push it harder, so the force is higher, making it speed up more. Mass stays the same.",
        "expected_status": "correct" # Roughly correct/incomplete depending on strictness
    },
    {
        "concept": Concept(
            id="c1", 
            name="Newton's Second Law", 
            description="The acceleration of an object depends on the net force acting on it and its mass (F=ma)."
        ),
        "checkpoint": Checkpoint(
            id="cp1",
            concept_id="c1",
            task="Explain why the cart accelerates when the force increases.",
            success_criteria="- identifies net force\n- connects force to acceleration\n- recognizes mass as relevant"
        ),
        "response": "The force is the acceleration of the object.",
        "expected_status": "incorrect" # Classic misconception
    },
    {
        "concept": Concept(
            id="c1", 
            name="Newton's Second Law", 
            description="The acceleration of an object depends on the net force acting on it and its mass (F=ma)."
        ),
        "checkpoint": Checkpoint(
            id="cp1",
            concept_id="c1",
            task="Explain why the cart accelerates when the force increases.",
            success_criteria="- identifies net force\n- connects force to acceleration\n- recognizes mass as relevant"
        ),
        "response": "It speeds up.",
        "expected_status": "incomplete"
    },
    {
        "concept": Concept(
            id="c1", 
            name="Newton's Second Law", 
            description="The acceleration of an object depends on the net force acting on it and its mass (F=ma)."
        ),
        "checkpoint": Checkpoint(
            id="cp1",
            concept_id="c1",
            task="Explain why the cart accelerates when the force increases.",
            success_criteria="- identifies net force\n- connects force to acceleration\n- recognizes mass as relevant"
        ),
        "response": "What is a cart?",
        "expected_status": "off_topic"
    }
]

async def run_evaluation():
    print(f"Starting Verifier Agent Evaluation with {os.environ.get('LLM_MODEL', 'default_model')}")
    agent = VerifierAgent()
    
    for i, data in enumerate(EVAL_DATA):
        print(f"\n[{i+1}/{len(EVAL_DATA)}] Testing response: '{data['response']}'")
        try:
            result = await agent.verify_checkpoint(data["concept"], data["checkpoint"], data["response"])
            print(f"  Result Status: {result.status} (Expected: {data['expected_status']})")
            print(f"  Mastery Score: {result.mastery_score}")
            print(f"  Criteria Met: {sum(1 for c in result.criteria_evaluation if c.met)}/{len(result.criteria_evaluation)}")
            if result.misconceptions:
                print(f"  Misconceptions Found: {len(result.misconceptions)}")
                for m in result.misconceptions:
                    print(f"    - {m.name}: {m.evidence}")
            print(f"  Explanation: {result.explanation}")
                
        except VerifierError as e:
            print(f"  Failed to generate valid VerificationResult: {e}")
            
if __name__ == "__main__":
    asyncio.run(run_evaluation())
