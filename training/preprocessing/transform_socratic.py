import os
import json
import re
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
6. MULTI-TURN: If possible, simulate a multi-turn dialogue to teach adaptation. Preserve the original source conversation where appropriate. Do not artificially create multi-turn conversations merely to increase the multi-turn percentage. Only mark is_multiturn=true when the output genuinely contains multiple conversational turns.

Format your output strictly as a JSON object:
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "strategy_used": "Short explanation of the tutoring strategy applied",
  "is_multiturn": boolean (true only if the output genuinely contains multiple conversational turns)
}
"""

def clean_json_string(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def transform_sample_to_socratic(user_prompt, original_assistant_response, domain="chat"):
    """
    Transforms a direct-answer conversation into a Socratic tutor turn.
    Returns a dict with messages, strategy, etc. Or {"error": ...} on failure.
    """
    transform_base_url = os.environ.get("TRANSFORM_BASE_URL", "https://api.openai.com/v1")
    transform_api_key = os.environ.get("TRANSFORM_API_KEY", os.environ.get("OPENAI_API_KEY"))
    transform_model = os.environ.get("TRANSFORM_MODEL", "gpt-4o-mini")
    
    if not transform_api_key:
        return {"error": "missing_api_key"}
        
    client = OpenAI(api_key=transform_api_key, base_url=transform_base_url)
    
    prompt = f"""
Student Question / Problem ({domain}):
{user_prompt}

Original Direct Answer (To be transformed into Socratic response):
{original_assistant_response}

Generate the Socratic tutoring response according to the rules.
"""

    import time
    
    max_retries = 1
    base_wait = 2.0
    
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=transform_model,
                messages=[
                    {"role": "system", "content": TRANSFORM_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1024,
                timeout=90.0,
                extra_body={"enable_reasoning": False}
            )
            raw_content = response.choices[0].message.content
            clean_content = clean_json_string(raw_content)
            data = json.loads(clean_content)
            
            # Basic schema validation
            if "messages" not in data or not isinstance(data["messages"], list):
                return {"error": "missing_messages_array", "raw": raw_content}
                
            return data
        except json.JSONDecodeError as e:
            return {"error": f"json_parse_error: {e}", "raw": raw_content}
        except Exception as e:
            if attempt < max_retries:
                time.sleep(base_wait * (2 ** attempt))
                continue
            else:
                if "timeout" in str(e).lower():
                    return {"error": "api_timeout"}
                print(f"Error during Socratic transformation: {e}")
                return {"error": f"api_error: {e}"}
