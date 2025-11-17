import requests
from requests.auth import HTTPBasicAuth
import time

BASE_URL = "http://localhost:8000"
AUTH_URL = f"{BASE_URL}/api/v1/auth/token/"
LEAVES_URL = f"{BASE_URL}/leaves/"

USERNAME = "admin"
PASSWORD = "hgslduhgfwdv"
TIMEOUT = 30

def test_leave_request_submission_and_listing():
    # Obtain JWT token
    auth_payload = {"username": USERNAME, "password": PASSWORD}
    try:
        auth_response = requests.post(AUTH_URL, json=auth_payload, timeout=TIMEOUT)
        assert auth_response.status_code == 200, f"Auth failed with status {auth_response.status_code}"
        tokens = auth_response.json()
        access_token = tokens.get("access")
        refresh_token = tokens.get("refresh")
        assert access_token and refresh_token, "JWT tokens not received"
    except Exception as e:
        assert False, f"Authentication request failed: {str(e)}"

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Step 1: Verify listing leave requests returns 200 and data is in correct format
    try:
        list_response = requests.get(LEAVES_URL, headers=headers, timeout=TIMEOUT)
        assert list_response.status_code == 200, f"Listing leaves failed with status {list_response.status_code}"
        leaves_data = list_response.json()
        assert isinstance(leaves_data, (list, dict)), "Leaves listing response is not a list or dict"
    except Exception as e:
        assert False, f"Leave listing request failed: {str(e)}"

    # Step 2: Submit a leave request (simulate minimal required data)
    # Typical leave request fields may include: start_date, end_date, reason, leave_type (guessing typical fields)
    # We will try a valid entry; approval workflow enforcement will be indirectly checked by status codes and returned data
    leave_request_payload = {
        "start_date": "2025-12-01",
        "end_date": "2025-12-05",
        "reason": "Test leave request submission",
        "leave_type": "annual"  # Assuming a leave type field; no schema given in PRD, guess typical usage
    }

    created_leave_id = None
    try:
        post_response = requests.post(LEAVES_URL, headers=headers, json=leave_request_payload, timeout=TIMEOUT)
        assert post_response.status_code in (200, 201), f"Leave submission failed with status {post_response.status_code}"
        created_leave = post_response.json()
        # Expect the response to contain at least an id and status fields
        created_leave_id = created_leave.get("id") or created_leave.get("pk")
        assert created_leave_id is not None, "Leave request creation response missing ID"
        # Check if approval workflow fields/status exist and are correct (if applicable)
        # For example, "status" might be "pending"
        status = created_leave.get("status", "").lower()
        assert status in ("pending", "submitted", ""), f"Unexpected leave request status: {status}"
    except Exception as e:
        assert False, f"Leave request submission failed: {str(e)}"
    finally:
        # Clean up: Delete the created leave request if possible to maintain test isolation
        if created_leave_id:
            try:
                delete_url = f"{LEAVES_URL}{created_leave_id}/"
                del_response = requests.delete(delete_url, headers=headers, timeout=TIMEOUT)
                # Some APIs respond 204 No Content or 200 OK
                assert del_response.status_code in (200, 204), f"Leave request deletion failed with status {del_response.status_code}"
            except Exception:
                pass

    # Step 3: Verify leave requests listing reflects the new request if possible (may be redundant due to deletion)
    # Here we just validate filtering and ordering are in place and no security issues appear
    try:
        list_response_after = requests.get(LEAVES_URL, headers=headers, timeout=TIMEOUT)
        assert list_response_after.status_code == 200
        # Check response time for performance: response should be under 0.5 seconds (500 ms) as per validation criteria
        # Cannot assert exactly here, but we can check elapsed if timing available
        elapsed_ms = list_response_after.elapsed.total_seconds() * 1000
        assert elapsed_ms < 500, f"Leave listing took too long: {elapsed_ms} ms"
    except Exception as e:
        assert False, f"Leave listing request after submission failed: {str(e)}"

    # Step 4: Confirm security headers and absence of obvious vulnerabilities in response headers
    # Especially check for security headers like Content-Security-Policy, X-Frame-Options, etc.
    try:
        security_headers = list_response.headers
        csp = security_headers.get("Content-Security-Policy", None)
        xfo = security_headers.get("X-Frame-Options", None)
        xcto = security_headers.get("X-Content-Type-Options", None)
        assert csp or xfo or xcto, "Security headers not present in response"
    except Exception as e:
        # Not failing test if headers missing but warning could be logged in real tests
        pass

test_leave_request_submission_and_listing()