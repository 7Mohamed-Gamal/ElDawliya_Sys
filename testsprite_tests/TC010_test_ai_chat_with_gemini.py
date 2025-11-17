import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "hgslduhgfwdv"
TIMEOUT = 30

def test_ai_chat_with_gemini():
    url = f"{BASE_URL}/api/v1/ai/chat/"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "user", "content": "Hello, Gemini AI. How can you assist me today?"}
        ]
    }
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=TIMEOUT
        )
        # Check HTTP status
        assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}"
        # Check content type
        assert "application/json" in response.headers.get("Content-Type", ""), "Response is not JSON"
        data = response.json()
        # Validate that there's a response key with AI-generated content
        assert "response" in data, "Missing 'response' key in JSON response"
        ai_response = data["response"]
        assert isinstance(ai_response, str), "'response' should be a string"
        assert len(ai_response.strip()) > 0, "AI response is empty"
    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"

test_ai_chat_with_gemini()