import requests
import json
import os

# Set the current working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"Current working directory: {os.getcwd()}")

# API configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"  # Your hackathonkey
MODEL = "deepseek/deepseek-r1-0528-qwen3-8b:free"  # Free-tier model

# Test payload
payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": "This is a test message to verify API access."}],
    "max_tokens": 100,
    "temperature": 0.3
}

# Headers
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Make the API call
print("Attempting API call...")
try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print("Response Headers:")
    print(json.dumps(dict(response.headers), indent=2))
    print("Response Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print(f"Raw Response: {response.text}")
    # Additional diagnostics
    if response.status_code == 200:
        print("Success: API call completed successfully.")
    elif response.status_code == 401:
        print("Error: 401 Unauthorized - Possible causes:")
        print("- Invalid API key: Verify your key in OpenRouter dashboard (https://openrouter.ai).")
        print("- Expired or revoked key: Generate a new key.")
        print("- Account restrictions: Check if your account has access to the model.")
    elif response.status_code == 402:
        print("Error: 402 Payment Required - Possible causes:")
        print("- Free model should not require credits; verify model name.")
        print("- Account restrictions: Ensure account is not blocked.")
    elif response.status_code == 404:
        print("Error: 404 Not Found - Model name is invalid. Check OpenRouter models list: https://openrouter.ai/models?free=true")
    elif response.status_code == 429:
        print("Error: 429 Too Many Requests - Free model limit (50/day) reached. Possible actions:")
        print("- Wait 24 hours for rate limit reset (likely around midnight IST).")
        print("- Create a new OpenRouter account for a fresh 50 requests/day.")
        print("- Try another free model (e.g., 'openai/gpt-oss-20b:free').")
    else:
        print(f"Unexpected status code: {response.status_code}. Check OpenRouter documentation: https://openrouter.ai/docs")
except requests.RequestException as e:
    print(f"Request failed: {str(e)}")
    print("Possible causes:")
    print("- Network issue: Verify internet connectivity.")
    print("- Incorrect API URL: Ensure URL is 'https://openrouter.ai/api/v1/chat/completions'.")
    print("- Timeout: Increase timeout or check server status.")