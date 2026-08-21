import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("RUNPOD_API_KEY")
base_url = "https://api.runpod.ai/v2/wopegx0zionm83/openai/v1"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def test_inference(test_name, extra_body=None):
    print(f"\n--- {test_name} ---")
    data = {
        "model": "Qwen/Qwen3-8B",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2+2?"}
        ],
        "max_tokens": 100,
        "temperature": 0.0
    }
    if extra_body:
        data.update(extra_body)
        
    try:
        response = requests.post(f"{base_url}/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message'].get('content', '')
            print("Response:", repr(content))
        else:
            print("Failed:", response.status_code, response.text)
    except Exception as e:
        print("Exception:", e)

test_inference("Default Generation (No extra params)")
# Note: vLLM doesn't support 'enable_thinking' directly via OpenAI API chat completions unless added as an extra_body param or if Qwen template handles it. We can try passing it to 'extra_body' or 'chat_template_kwargs'
test_inference("With chat_template_kwargs: enable_thinking=True", {"extra_body": {"chat_template_kwargs": {"enable_thinking": True}}})
test_inference("With chat_template_kwargs: enable_thinking=False", {"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}})
