import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# We will use the RunPod endpoint as the model being evaluated
runpod_api_key = os.environ.get("RUNPOD_API_KEY")
runpod_base_url = os.environ.get("RUNPOD_OPENAI_BASE_URL")
if "${RUNPOD_ENDPOINT_ID}" in runpod_base_url:
    runpod_base_url = runpod_base_url.replace("${RUNPOD_ENDPOINT_ID}", os.environ["RUNPOD_ENDPOINT_ID"])
model_name = os.environ.get("MODEL_NAME", "Qwen/Qwen3-8B")

# Optional: Judge API configuration
judge_api_key = os.environ.get("JUDGE_API_KEY")
judge_base_url = os.environ.get("JUDGE_BASE_URL", "https://api.openai.com/v1")
judge_model = os.environ.get("JUDGE_MODEL", "gpt-4o")

student_prompts = [
    {
        "concept": "Binary Search",
        "question": "I am trying to implement binary search, but it keeps getting stuck in an infinite loop. Here is my code...",
        "code_snippet": "def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid\n        else:\n            high = mid\n    return -1",
        "expected_hint_type": "Question",
        "forbidden_phrases": ["low = mid + 1", "high = mid - 1", "add 1 to mid"]
    },
    {
        "concept": "Algebra",
        "question": "Solve for x: 2x + 5 = 15. Is the answer x = 10?",
        "code_snippet": "",
        "expected_hint_type": "Misconception Correction",
        "forbidden_phrases": ["x = 5", "x=5", "subtract 5 from 15 to get 10", "divide by 2"]
    }
]

def run_evaluation():
    print(f"Starting Baseline Evaluation against {model_name} on {runpod_base_url}")
    client = OpenAI(api_key=runpod_api_key, base_url=runpod_base_url)
    
    results = []
    
    for prompt in student_prompts:
        print(f"\n--- Testing Concept: {prompt['concept']} ---")
        user_content = prompt["question"] + "\n" + prompt["code_snippet"]
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a Socratic AI tutor. Do not give direct answers. Guide the student using hints and questions."},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        model_output = response.choices[0].message.content
        print(f"Model Output:\n{model_output}\n")
        
        # Deterministic checks (Answer Leakage)
        leaked = False
        for phrase in prompt["forbidden_phrases"]:
            if phrase.lower() in model_output.lower():
                leaked = True
                print(f"[FAIL] Answer Leakage Detected: '{phrase}'")
                break
                
        if not leaked:
            print("[PASS] No obvious answer leakage detected.")
            
        results.append({
            "concept": prompt["concept"],
            "leaked": leaked,
            "output": model_output
        })
        
    print("\nBaseline Evaluation Complete.")
    print("Scores:")
    total = len(results)
    leaked_count = sum(1 for r in results if r["leaked"])
    print(f"Direct Answers Leaked: {leaked_count}/{total} (Lower is better for Socratic Tutor)")

if __name__ == "__main__":
    run_evaluation()
