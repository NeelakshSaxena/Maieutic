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
5. Answer Distance: Do not give away so much intermediate information that the student no longer needs to reason. Give useful non-leaking guidance. Avoid generic responses like "What do you think?".
6. MULTI-TURN: If possible, simulate a multi-turn dialogue (Student -> Tutor -> Student -> Tutor) to teach adaptation.

Format your output strictly as a JSON object:
{
  "transformed_response": "The Socratic tutor's response string (can be multi-turn if appropriate)",
  "strategy_used": "Short explanation of the tutoring strategy applied",
  "is_multiturn": boolean (true if response simulates a multi-turn interaction)
}
"""

def transform_sample_to_socratic(user_prompt, original_assistant_response, domain="chat"):
    """
    Transforms a direct-answer conversation into a Socratic tutor turn.
    """
    transform_base_url = os.environ.get("TRANSFORM_BASE_URL", "https://api.openai.com/v1")
    transform_api_key = os.environ.get("TRANSFORM_API_KEY", os.environ.get("OPENAI_API_KEY"))
    transform_model = os.environ.get("TRANSFORM_MODEL", "gpt-4o-mini")
    
    if not transform_api_key:
        return None
        
    client = OpenAI(api_key=transform_api_key, base_url=transform_base_url)
    
    prompt = f"""
Student Question / Problem ({domain}):
{user_prompt}

Original Direct Answer (To be transformed into Socratic response):
{original_assistant_response}

Generate the Socratic tutoring response according to the rules.
"""

    try:
        response = client.chat.completions.create(
            model=transform_model,
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
