import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TRANSFORM_SYSTEM_PROMPT = """You are an expert Socratic pedagogy engine for Maieutic.
Your goal is to convert direct-answer assistant responses into high-quality Socratic tutoring responses.

RULES FOR SOCRATIC RESPONSES:
1. NEVER give the direct final answer, full solution code, or complete result immediately.
2. Decompose the problem into manageable steps or checkpoints.
3. Ask a clear, targeted guiding question to encourage the student to take the first step.
4. Provide a subtle hint or concept explanation if needed, preserving student agency.
5. If the problem is multi-step, outline the first phase without solving it.
6. Keep the response encouraging, concise, and focused on student reasoning.

Format your output strictly as a JSON object:
{
  "transformed_response": "The Socratic tutor's response string...",
  "strategy_used": "Short explanation of the tutoring strategy applied (e.g. decomposition, conceptual hint, step 1 question)"
}
"""

def transform_sample_to_socratic(user_prompt, original_assistant_response, domain="chat"):
    """
    Transforms a direct-answer conversation into a Socratic tutor turn.
    """
    judge_base_url = os.environ.get("JUDGE_BASE_URL", "https://api.openai.com/v1")
    judge_api_key = os.environ.get("JUDGE_API_KEY")
    judge_model = os.environ.get("JUDGE_MODEL", "gpt-4o-mini")
    
    if not judge_api_key:
        return None
        
    client = OpenAI(api_key=judge_api_key, base_url=judge_base_url)
    
    prompt = f"""
Student Question / Problem ({domain}):
{user_prompt}

Original Direct Answer (To be transformed into Socratic response):
{original_assistant_response}

Generate the Socratic tutoring response according to the rules.
"""

    try:
        response = client.chat.completions.create(
            model=judge_model,
            messages=[
                {"role": "system", "content": TRANSFORM_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        data = json.loads(response.choices[0].message.content)
        return data
    except Exception as e:
        print(f"Error during Socratic transformation: {e}")
        return None
