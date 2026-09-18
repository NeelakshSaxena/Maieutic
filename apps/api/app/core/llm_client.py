import os
from openai import AsyncOpenAI
import json

class LLMClient:
    """
    A reusable OpenAI-compatible LLM client configured via environment variables.
    This abstract client makes the Planner independent of specific providers (e.g., RunPod, vLLM, OpenAI).
    """
    def __init__(self):
        # Configure the backend dynamically from the environment
        base_url = os.environ.get("LLM_BASE_URL")
        api_key = os.environ.get("LLM_API_KEY")
        model = os.environ.get("LLM_MODEL")

        if not base_url:
            raise ValueError("LLM_BASE_URL is not configured")
        if not model:
            raise ValueError("LLM_MODEL is not configured")

        self.model = model
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key or "local"
        )

    async def generate_structured(self, system_prompt: str, user_prompt: str, response_format: type = None) -> dict:
        """
        Generates a structured response based on the Pydantic schema (response_format).
        If the inference provider doesn't support structured outputs natively, 
        we ask for JSON and parse it.
        """
        # If response_format is provided, we can either use standard json mode or beta.structured_outputs
        # To be highly compatible with local endpoints like vLLM, standard JSON mode with a schema in the prompt works best.
        
        schema_instruction = ""
        if response_format:
            schema_json = json.dumps(response_format.model_json_schema(), indent=2)
            schema_instruction = f"\n\nYou MUST respond in valid JSON format matching the following JSON Schema:\n{schema_json}"

        final_system_prompt = system_prompt + schema_instruction

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
