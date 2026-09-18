import os
from pydantic import ValidationError
from typing import Optional
from app.schemas.planner_schemas import Concept, Checkpoint
from app.schemas.verifier_schemas import VerificationResult
from app.schemas.hint_schemas import HintResult, HintLevel
from app.core.llm_client import LLMClient

class HintError(Exception):
    pass

class HintAgent:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.prompt_path = os.path.join(
            os.path.dirname(__file__), 
            "../prompts/hint/hint_prompt.txt"
        )
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    async def generate_hint(self, concept: Concept, checkpoint: Checkpoint, student_response: str, verification: VerificationResult, level: HintLevel, max_retries: int = 2) -> HintResult:
        last_error = None
        
        user_prompt_base = (
            f"CONCEPT\nName: {concept.name}\nDescription: {concept.description}\n\n"
            f"CHECKPOINT\nTask: {checkpoint.task}\nSuccess criteria:\n{checkpoint.success_criteria}\n\n"
            f"STUDENT RESPONSE:\n{student_response}\n\n"
            f"VERIFICATION RESULT:\nStatus: {verification.status}\n"
            f"Criteria Evaluation: {[c.model_dump() for c in verification.criteria_evaluation]}\n"
            f"Misconceptions: {[m.model_dump() for m in verification.misconceptions]}\n\n"
            f"REQUESTED HINT LEVEL: {level.name} (Value: {level.value})"
        )
        
        user_prompt = user_prompt_base

        for attempt in range(max_retries + 1):
            try:
                # Call LLM
                raw_json = await self.llm_client.generate_structured(
                    system_prompt=self.system_prompt,
                    user_prompt=user_prompt,
                    response_format=HintResult
                )

                # Pydantic Validation
                try:
                    result = HintResult(**raw_json)
                    # Enforce that the LLM returns the correct level
                    if result.level_used != level:
                        raise ValueError(f"LLM returned hint level {result.level_used.value}, but {level.value} was requested.")
                    return result
                except ValidationError as e:
                    raise HintError(f"Failed to parse LLM output into HintResult: {e}")

            except (HintError, ValueError) as e:
                last_error = e
                # Feed the structural/schema error back to the LLM for correction
                user_prompt = f"{user_prompt_base}\n\nYour previous attempt failed validation with the following error:\n{str(e)}\nPlease correct the JSON output."

        raise HintError(f"Failed to generate a valid HintResult after {max_retries} retries. Last error: {last_error}")
