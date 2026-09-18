import os
from pydantic import ValidationError
from typing import Optional
from app.schemas.planner_schemas import Concept, Checkpoint
from app.schemas.verifier_schemas import VerificationResult
from app.core.llm_client import LLMClient

class VerifierError(Exception):
    pass

class VerifierAgent:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.prompt_path = os.path.join(
            os.path.dirname(__file__), 
            "../prompts/verifier/verifier_prompt.txt"
        )
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    async def verify_checkpoint(self, concept: Concept, checkpoint: Checkpoint, student_response: str, max_retries: int = 2) -> VerificationResult:
        last_error = None
        
        user_prompt_base = (
            f"CONCEPT\nName: {concept.name}\nDescription: {concept.description}\n\n"
            f"CHECKPOINT\nTask: {checkpoint.task}\nSuccess criteria:\n{checkpoint.success_criteria}\n\n"
            f"STUDENT RESPONSE:\n{student_response}"
        )
        
        user_prompt = user_prompt_base

        for attempt in range(max_retries + 1):
            try:
                # Call LLM
                raw_json = await self.llm_client.generate_structured(
                    system_prompt=self.system_prompt,
                    user_prompt=user_prompt,
                    response_format=VerificationResult
                )

                # Pydantic Validation (includes invariant validation)
                try:
                    result = VerificationResult(**raw_json)
                    return result
                except ValidationError as e:
                    raise VerifierError(f"Failed to parse LLM output into VerificationResult: {e}")

            except (VerifierError, ValueError) as e:
                last_error = e
                # Feed the structural/schema error back to the LLM for correction
                user_prompt = f"{user_prompt_base}\n\nYour previous attempt failed validation with the following error:\n{str(e)}\nPlease correct the JSON output."

        raise VerifierError(f"Failed to generate a valid VerificationResult after {max_retries} retries. Last error: {last_error}")
