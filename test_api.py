import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1").rstrip("/")
model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

if api_key:
    print(f"API Key: {api_key[:20]}... (masked)")
else:
    print("API Key: (missing)")
print(f"API Base: {api_base}")
print(f"Model: {model}")
print("\nTesting API connection...")

url = f"{api_base}/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
payload = {
    "model": model,
    "messages": [{"role": "user", "content": "Say hi"}],
    "temperature": 0.9,
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        print("\n✓ API connection successful!")
    else:
        print(f"\n✗ API returned error: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("\n✗ Request timed out - check your network connection")
except requests.exceptions.ConnectionError:
    print("\n✗ Connection error - check if the API URL is correct and accessible")
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {e}")
