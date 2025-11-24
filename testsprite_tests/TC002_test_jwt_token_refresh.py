import requests

BASE_URL = "http://localhost:8000"
AUTH_TOKEN_URL = f"{BASE_URL}/api/v1/auth/token/"
REFRESH_TOKEN_URL = f"{BASE_URL}/api/v1/auth/token/refresh/"

USERNAME = "admin"
PASSWORD = "hgslduhgfwdv"

TIMEOUT = 30


def test_jwt_token_refresh():
    """test_jwt_token_refresh function"""
    # Obtain initial JWT token pair using valid credentials (Basic Token Auth simulated by POST data)
    try:
        response = requests.post(
            AUTH_TOKEN_URL,
            json={"username": USERNAME, "password": PASSWORD},
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"Token obtain failed: {response.text}"
        tokens = response.json()
        access_token = tokens.get("access")
        refresh_token = tokens.get("refresh")
        assert access_token, "Access token not returned"
        assert refresh_token, "Refresh token not returned"

        # Test valid refresh token usage to get new access token
        refresh_response = requests.post(
            REFRESH_TOKEN_URL,
            json={"refresh": refresh_token},
            timeout=TIMEOUT
        )
        assert refresh_response.status_code == 200, f"Refresh token request failed: {refresh_response.text}"
        refresh_data = refresh_response.json()
        new_access_token = refresh_data.get("access")
        assert new_access_token, "New access token not returned on refresh"
        assert new_access_token != access_token, "New access token should differ from old one"

        # Test with invalid refresh token
        invalid_refresh_response = requests.post(
            REFRESH_TOKEN_URL,
            json={"refresh": "invalid_or_expired_token"},
            timeout=TIMEOUT
        )
        assert invalid_refresh_response.status_code == 401 or invalid_refresh_response.status_code == 400, \
            "Invalid refresh token should return 401 or 400"
        invalid_data = invalid_refresh_response.json()
        assert "detail" in invalid_data or "code" in invalid_data, "Error detail should be present for invalid token"

    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"


test_jwt_token_refresh()
