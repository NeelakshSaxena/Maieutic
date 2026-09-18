import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("RUNPOD_API")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    response = requests.get('https://api.runpod.io/v2/pods', headers=headers)
    print(response.json())
except Exception as e:
    print(e)
