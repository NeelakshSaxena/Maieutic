import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# manually interpolate if needed
base_url = os.environ["RUNPOD_OPENAI_BASE_URL"]
if "${RUNPOD_ENDPOINT_ID}" in base_url:
    base_url = base_url.replace("${RUNPOD_ENDPOINT_ID}", os.environ["RUNPOD_ENDPOINT_ID"])

client = OpenAI(
    api_key=os.environ["RUNPOD_API_KEY"],
    base_url=base_url,
)

print(f"Connecting to {base_url}...")

resp = client.chat.completions.create(
    model=os.environ.get("MODEL_NAME", "Qwen/Qwen3-8B"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Give me 3 ideas for a weekend project."},
    ],
    temperature=0.7,
    max_tokens=200,
)

print("[SUCCESS] Response received:")
print(resp.choices[0].message.content)
