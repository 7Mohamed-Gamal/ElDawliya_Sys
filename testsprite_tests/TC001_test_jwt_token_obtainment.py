import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_jwt_token_obtainment():
    """test_jwt_token_obtainment function"""
    url = f"{BASE_URL}/api/v1/auth/token/"
    headers = {"Content-Type": "application/json"}

    valid_credentials = {
        "username": "admin",
        "password": "hgslduhgfwdv"
    }
    invalid_credentials = {
        "username": "admin",
        "password": "wrongpassword123"
    }

    # Test valid credentials - should return JWT token pair
    try:
        response = requests.post(url, json=valid_credentials, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected 200 OK for valid credentials, got {response.status_code}"
        json_resp = response.json()
        assert "access" in json_resp, "Response missing 'access' token"
        assert "refresh" in json_resp, "Response missing 'refresh' token"
        access_token = json_resp["access"]
        refresh_token = json_resp["refresh"]
        assert isinstance(access_token, str) and len(access_token) > 0, "'access' token is not a valid string"
        assert isinstance(refresh_token, str) and len(refresh_token) > 0, "'refresh' token is not a valid string"
    except requests.RequestException as e:
        assert False, f"Request failed for valid credentials: {e}"
    except ValueError:
        assert False, "Response is not valid JSON for valid credentials"

    # Test invalid credentials - should reject with 401 or 400
    try:
        response = requests.post(url, json=invalid_credentials, headers=headers, timeout=TIMEOUT)
        assert response.status_code in (400, 401), f"Expected 400 or 401 for invalid credentials, got {response.status_code}"
        json_resp = response.json()
        # Optional: check for error detail message if present
        if "detail" in json_resp:
            assert isinstance(json_resp["detail"], str) and len(json_resp["detail"]) > 0, "Error detail is empty or invalid"
    except requests.RequestException as e:
        assert False, f"Request failed for invalid credentials: {e}"
    except ValueError:
        assert False, "Response is not valid JSON for invalid credentials"

test_jwt_token_obtainment()
