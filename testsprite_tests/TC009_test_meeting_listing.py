import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
AUTH_ENDPOINT = "/api/v1/auth/token/"
MEETINGS_ENDPOINT = "/api/v1/meetings/"
USERNAME = "admin"
PASSWORD = "hgslduhgfwdv"
TIMEOUT = 30

def test_meeting_listing():
    try:
        # Step 1: Obtain JWT token pair using basic auth credentials
        auth_response = requests.post(
            f"{BASE_URL}{AUTH_ENDPOINT}",
            json={"username": USERNAME, "password": PASSWORD},
            timeout=TIMEOUT
        )
        assert auth_response.status_code == 200, f"Auth failed with status {auth_response.status_code}, response: {auth_response.text}"
        tokens = auth_response.json()
        assert "access" in tokens and "refresh" in tokens, "JWT token response missing access or refresh tokens"
        access_token = tokens["access"]

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        # Step 2: Retrieve meetings list
        response = requests.get(f"{BASE_URL}{MEETINGS_ENDPOINT}", headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200, f"Meeting listing failed with status {response.status_code}, response: {response.text}"
        meetings = response.json()
        
        # Validate meetings structure: expect list
        assert isinstance(meetings, list), f"Meetings response expected list but got {type(meetings)}"

        for meeting in meetings:
            # Each meeting must contain keys: 'id', 'scheduled_time' or similar, 'attendees', 'notes'
            assert isinstance(meeting, dict), "Each meeting entry must be a dict"
            assert "id" in meeting, "Meeting missing 'id'"
            assert "attendees" in meeting, "Meeting missing 'attendees'"
            assert isinstance(meeting["attendees"], list), "'attendees' must be a list"
            assert "notes" in meeting, "Meeting missing 'notes' field"

            # Attendee info validation: each attendee must have id and name/email or similar
            for attendee in meeting["attendees"]:
                assert isinstance(attendee, dict), "Attendee must be a dict"
                assert "id" in attendee or "user_id" in attendee, "Attendee missing 'id' or equivalent"
                # Check at least one identifier or name field
                assert any(k in attendee for k in ("name", "email", "username")), "Attendee missing name/email/username"

            # Notes validation: notes should be a string or list
            assert isinstance(meeting["notes"], (str, list)), "Meeting notes should be string or list"

        # Step 3: Security and performance checks (basic)
        # Check response time < 0.5 seconds to meet performance criteria
        assert response.elapsed.total_seconds() < 0.5, "Response time exceeded 500 ms"

        # Test passed if no assertion failed till now
        print("Test TC009: test_meeting_listing passed.")

    except requests.Timeout:
        raise AssertionError("Request timed out after 30 seconds")
    except requests.RequestException as e:
        raise AssertionError(f"HTTP request failed: {str(e)}")

test_meeting_listing()