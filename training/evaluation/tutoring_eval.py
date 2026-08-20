import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class TutorEvaluation(BaseModel):
    socratic_adherence: int = Field(description="1-5 score. 5 means strictly asks guiding questions. 1 means gives direct answers immediately.")
    answer_leakage: int = Field(description="1-5 score. 5 means no answer leaked. 1 means exact final answer was given away prematurely.")
    decomposition_quality: int = Field(description="1-5 score. How well the tutor breaks the problem down into steps or checkpoints.")
    misconception_detection: int = Field(description="1-5 score. How well the tutor identifies flaws in the student's reasoning (if applicable).")
    hint_quality: int = Field(description="1-5 score. How progressive, responsive, and appropriate the hint is.")
    correctness: int = Field(description="1-5 score. Is the tutor mathematically/logically/factually correct?")
    justification: str = Field(description="A short, concise rationale for these scores.")

def evaluate_tutor_response(student_prompt, tutor_response):
    """
    Evaluates a generated tutor response using an LLM-as-a-judge.
    Returns a TutorEvaluation dictionary.
    """
    # Configurable judge
    judge_base_url = os.environ.get("JUDGE_BASE_URL", "https://api.openai.com/v1")
    judge_api_key = os.environ.get("JUDGE_API_KEY")
    judge_model = os.environ.get("JUDGE_MODEL", "gpt-4o-mini")
    
    if not judge_api_key:
        print("Warning: JUDGE_API_KEY not set. Cannot run LLM judge.")
        return None

    client = OpenAI(api_key=judge_api_key, base_url=judge_base_url)
    
    system_prompt = """You are an expert pedagogical evaluator. You evaluate AI tutors.
The AI tutor's primary goal is Socratic teaching: guiding the student without revealing the direct answer.
Score the tutor's response strictly on a 1-5 scale.
Return ONLY valid JSON matching this schema:
{
  "socratic_adherence": int (1-5),
  "answer_leakage": int (1-5),
  "decomposition_quality": int (1-5),
  "misconception_detection": int (1-5),
  "hint_quality": int (1-5),
  "correctness": int (1-5),
  "justification": string
}
"""

    user_prompt = f"""
Student Prompt / Context:
{student_prompt}

Tutor's Generated Response:
{tutor_response}

Evaluate the tutor's response. Provide your JSON evaluation.
"""

    try:
        response = client.chat.completions.create(
            model=judge_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        result_json = json.loads(response.choices[0].message.content)
        return result_json
    except Exception as e:
        print(f"Error calling LLM Judge: {e}")
        return None
