import os
import openai
from openai import AsyncOpenAI
import json


class LLMUnavailableError(RuntimeError):
    """The configured inference endpoint could not be reached or timed out."""


class LLMModelNotFoundError(RuntimeError):
    """The endpoint is reachable but does not have the configured model."""


class LLMClient:
    """
    A reusable OpenAI-compatible LLM client configured via environment variables.
    This abstract client makes the Planner independent of specific providers (e.g., RunPod, vLLM, OpenAI).
    """
    def __init__(self, prefix: str = "TRANSFORM"):
        # Configure the backend dynamically from the environment
        base_url = os.environ.get(f"{prefix}_BASE_URL") or os.environ.get("LLM_BASE_URL")
        api_key = os.environ.get(f"{prefix}_API_KEY") or os.environ.get("LLM_API_KEY")
        model = os.environ.get(f"{prefix}_MODEL") or os.environ.get("LLM_MODEL")

        if not base_url:
            raise ValueError(f"{prefix}_BASE_URL (or LLM_BASE_URL) is not configured")
        if not model:
            raise ValueError(f"{prefix}_MODEL (or LLM_MODEL) is not configured")

        self.model = model
        self.base_url = base_url
        # Local models can take minutes per request; fail loudly instead of retrying silently.
        timeout = float(os.environ.get("LLM_TIMEOUT_SECONDS", "300"))
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key or "local",
            timeout=timeout,
            max_retries=0,
        )

    async def check_health(self) -> dict:
        """Verify the endpoint is reachable and the configured model exists (no inference)."""
        try:
            models = await self.client.models.list()
        except (openai.APIConnectionError, openai.APITimeoutError) as e:
            raise LLMUnavailableError(f"Cannot reach LLM endpoint {self.base_url}: {e}") from e
        names = [m.id for m in models.data]
        if self.model not in names:
            raise LLMModelNotFoundError(
                f"Model '{self.model}' not found at {self.base_url}. Available: {names}"
            )
        return {"model": self.model, "base_url": self.base_url, "available_models": names}

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

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": final_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
        except (openai.APIConnectionError, openai.APITimeoutError) as e:
            raise LLMUnavailableError(f"Cannot reach LLM endpoint {self.base_url}: {e}") from e
        except openai.NotFoundError as e:
            raise LLMModelNotFoundError(f"Model '{self.model}' not found at {self.base_url}: {e}") from e

        content = (response.choices[0].message.content or "").strip()
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
        return json.loads(content)
