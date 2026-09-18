import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

FILTER_SYSTEM_PROMPT = """You are a strict quality control auditor for Maieutic training data.
Your job is to evaluate whether a Socratic tutoring transformation is suitable for model training.

CRITERIA FOR ACCEPTANCE:
1. Socratic Behavior: Does it ask guiding questions/prompts instead of giving the answer?
2. Answer Leakage (Answer Distance): Is the direct final answer avoided? Does the response also avoid giving away so much intermediate information that the student no longer needs to reason? (True = NO leakage, False = Leaked)
3. Generic Response Detection: Does the response provide USEFUL NON-LEAKING GUIDANCE? If the response is just generic ("What do you think?", "Can you try?", "Let's break this down.", "Can you explain your reasoning?") without context-specific guidance, it MUST be rejected.
4. Correctness: Is the pedagogical hint logically and factually sound?
5. Problem Preservation: Does it address the student's original problem accurately?
6. No Hallucination / Malformed Output: Is the text clean, natural, and properly formatted?
7. Conciseness: Is it free of excessive verbosity or irrelevant chatter?

Return ONLY valid JSON matching this schema:
{
  "is_accepted": boolean,
  "rejection_reason": string or null (e.g. "answer_leaked", "generic_response", "factually_incorrect", "excessive_verbosity", "not_socratic", "malformed_output"),
  "has_answer_leakage": boolean (true if answer or too much info was leaked, false if safe),
  "is_correct": boolean,
  "socratic_score": int (1-5)
}
"""

def validate_socratic_sample(user_prompt, transformed_response):
    """
    Validates a transformed sample against quality criteria.
    Returns (is_accepted, evaluation_dict).
    """
    judge_base_url = os.environ.get("JUDGE_BASE_URL", "https://api.openai.com/v1")
    judge_api_key = os.environ.get("JUDGE_API_KEY")
    judge_model = os.environ.get("JUDGE_MODEL", "gpt-4o-mini")
    
    if not judge_api_key:
        return False, {"rejection_reason": "missing_api_key"}

    client = OpenAI(api_key=judge_api_key, base_url=judge_base_url)
    
    prompt = f"""
Student Question:
{user_prompt}

Transformed Tutor Response:
{transformed_response}

Audit this transformed sample for training quality.
"""

    import time
    
    max_retries = 1
    base_wait = 2.0
    
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=judge_model,
                messages=[
                    {"role": "system", "content": FILTER_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
                timeout=90.0,
                extra_body={"enable_reasoning": False}
            )
            eval_data = json.loads(response.choices[0].message.content)
            is_accepted = eval_data.get("is_accepted", False)
            return is_accepted, eval_data
        except Exception as e:
            if attempt < max_retries:
                time.sleep(base_wait * (2 ** attempt))
                continue
            else:
                if "timeout" in str(e).lower():
                    return False, {"rejection_reason": "api_timeout"}
                print(f"Error during quality validation: {e}")
                return False, {"rejection_reason": f"execution_error: {e}"}
