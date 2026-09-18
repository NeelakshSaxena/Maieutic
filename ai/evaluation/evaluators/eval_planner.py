import asyncio
import os
from typing import List
from app.agents.planner import PlannerAgent, PlannerError
from app.schemas.planner_schemas import LearningPlan
from dotenv import load_dotenv

# Load env before instantiating LLMClient if needed
load_dotenv()

# A small benchmark to verify the agent behaves properly.
BENCHMARK_QUERIES = [
    "How does QuickSort work?",
    "Teach me about Object Oriented Programming in Python.",
    "Explain what a derivative is in calculus.",
    "I want to understand Graph traversal algorithms."
]

def evaluate_plan(plan: LearningPlan, query: str) -> dict:
    """
    Evaluates the learning plan along several dimensions.
    Returns a dictionary of boolean metrics.
    """
    results = {
        "concept_coverage": len(plan.concepts) >= 2,
        "graph_consistency": True, # Checked deterministically by PlannerAgent
        "schema_validity": True,   # Checked deterministically by Pydantic
        "answer_leakage": True,    # Simple heuristic: final checkpoints shouldn't contain the word "solution"
    }

    # Answer leakage heuristic check
    for cp in plan.checkpoints:
        if "solution" in cp.task.lower() or "answer" in cp.task.lower():
            if not ("write" in cp.task.lower() or "implement" in cp.task.lower()):
                # If it just says "read the solution"
                results["answer_leakage"] = False
    
    return results

async def run_evaluation():
    print(f"Starting Planner Agent Evaluation with {os.environ.get('LLM_MODEL', 'default_model')}")
    agent = PlannerAgent()
    
    total_metrics = {
        "concept_coverage": 0,
        "graph_consistency": 0,
        "schema_validity": 0,
        "answer_leakage": 0
    }
    
    num_queries = len(BENCHMARK_QUERIES)
    
    for i, query in enumerate(BENCHMARK_QUERIES):
        print(f"\n[{i+1}/{num_queries}] Query: {query}")
        try:
            plan = await agent.generate_plan(query)
            print(f"  Plan generated successfully with {len(plan.concepts)} concepts and {len(plan.checkpoints)} checkpoints.")
            
            # Evaluate
            metrics = evaluate_plan(plan, query)
            
            for k, v in metrics.items():
                if v:
                    total_metrics[k] += 1
                
        except PlannerError as e:
            print(f"  Failed to generate valid plan: {e}")
            # If it failed to parse or validate graph, schema/graph consistency is False for this query
            
    print("\n--- Evaluation Results ---")
    for k, v in total_metrics.items():
        score = (v / num_queries) * 100
        print(f"{k}: {score:.1f}%")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
