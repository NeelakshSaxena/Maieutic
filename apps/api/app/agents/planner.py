import os
from pydantic import ValidationError
from typing import Optional
from app.schemas.planner_schemas import LearningPlan
from app.core.llm_client import LLMClient

class PlannerError(Exception):
    pass

class GraphValidationError(PlannerError):
    pass

class PlannerAgent:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.prompt_path = os.path.join(
            os.path.dirname(__file__), 
            "../prompts/planner/planner_prompt.txt"
        )
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    async def generate_plan(self, student_query: str, max_retries: int = 2) -> LearningPlan:
        last_error = None
        user_prompt = f"Student Query: {student_query}"

        for attempt in range(max_retries + 1):
            try:
                # Call LLM
                raw_json = await self.llm_client.generate_structured(
                    system_prompt=self.system_prompt,
                    user_prompt=user_prompt,
                    response_format=LearningPlan
                )

                # 1. Pydantic Validation
                try:
                    plan = LearningPlan(**raw_json)
                except ValidationError as e:
                    raise PlannerError(f"Failed to parse LLM output into LearningPlan: {e}")

                # 2. Graph Validation
                self.validate_graph(plan)

                return plan

            except (PlannerError, ValueError) as e:
                last_error = e
                # Feed the error back to the LLM for correction on the next iteration
                user_prompt = f"Student Query: {student_query}\n\nYour previous attempt failed validation with the following error:\n{str(e)}\nPlease correct the JSON output."

        raise PlannerError(f"Failed to generate a valid plan after {max_retries} retries. Last error: {last_error}")

    def validate_graph(self, plan: LearningPlan):
        """
        Deterministic Python validation of the proposed LearningPlan graph.
        Validates:
        - All referenced IDs exist.
        - No duplicate IDs.
        - No self-dependencies.
        - No invalid edges.
        - No dependency cycles.
        """
        concept_ids = set()
        
        # Check for duplicate concept IDs
        for concept in plan.concepts:
            if concept.id in concept_ids:
                raise GraphValidationError(f"Duplicate concept ID found: {concept.id}")
            concept_ids.add(concept.id)
            
        # Validate dependencies
        adj_list = {cid: [] for cid in concept_ids}
        for dep in plan.dependencies:
            if dep.concept_id not in concept_ids:
                raise GraphValidationError(f"Dependency references unknown concept_id: {dep.concept_id}")
            if dep.prerequisite_id not in concept_ids:
                raise GraphValidationError(f"Dependency references unknown prerequisite_id: {dep.prerequisite_id}")
            if dep.concept_id == dep.prerequisite_id:
                raise GraphValidationError(f"Self-dependency detected for concept: {dep.concept_id}")
            
            # prereq -> concept
            adj_list[dep.prerequisite_id].append(dep.concept_id)

        # Detect cycles using DFS
        visited = set()
        rec_stack = set()
        
        def is_cyclic(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in adj_list[node]:
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
                    
            rec_stack.remove(node)
            return False

        for cid in concept_ids:
            if cid not in visited:
                if is_cyclic(cid):
                    raise GraphValidationError("Circular dependency cycle detected in the learning plan graph.")

        # Validate checkpoints
        checkpoint_ids = set()
        for cp in plan.checkpoints:
            if cp.id in checkpoint_ids:
                raise GraphValidationError(f"Duplicate checkpoint ID found: {cp.id}")
            checkpoint_ids.add(cp.id)
            
            if cp.concept_id not in concept_ids:
                raise GraphValidationError(f"Checkpoint references unknown concept_id: {cp.concept_id}")

