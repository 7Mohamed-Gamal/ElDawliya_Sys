import requests
from requests.auth import HTTPBasicAuth
import time

BASE_URL = "http://localhost:8000"
AUTH_USERNAME = "admin"
AUTH_PASSWORD = "hgslduhgfwdv"
TIMEOUT = 30

def test_attendance_records_retrieval():
    """test_attendance_records_retrieval function"""
    # Authenticate using basic token as per provided credentials (Basic Auth here as per instructions)
    auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_PASSWORD)
    attendance_endpoint = f"{BASE_URL}/attendance/"

    try:
        # Measure performance start time
        start_time = time.time()

        # Make GET request to attendance endpoint with authentication
        response = requests.get(attendance_endpoint, auth=auth, timeout=TIMEOUT)

        elapsed_time = (time.time() - start_time) * 1000  # in milliseconds

        # Assert response status code is 200 OK
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

        # Assert response time less than 500 ms as per validation criteria
        assert elapsed_time < 500, f"API response time too slow: {elapsed_time:.2f} ms"

        data = response.json()

        # Basic validation of response structure to ensure records for employees and check-in/out exist
        assert isinstance(data, list), "Expected a list of attendance records"

        # Assert at least one attendance record exists for meaningful test
        assert len(data) > 0, "No attendance records found"

        for record in data:
            # Validate presence of essential keys for attendance record
            assert "employee_id" in record, "Missing employee_id in record"
            assert "check_in" in record, "Missing check_in time in record"
            assert "check_out" in record, "Missing check_out time in record"
            # Optionally check time format strings or nulls for check_out (if employee not checked out yet)
            # Validate integration with ZKTeco devices indicated by a field if available
            # Since PRD does not specify exact field for device integration, assume possible presence
            # Check presence or type of ZKTeco integration field (example: device_source)
            if "device_source" in record:
                assert record["device_source"] in ["ZKTeco", "Other", None, ""], "Invalid device_source value"

        # Security: Check no sensitive data exposure (no password, tokens etc.)
        for record in data:
            forbidden_keys = {"password", "token", "secret"}
            assert not any(key in record for key in forbidden_keys), "Sensitive data exposed in API response"

    except requests.exceptions.Timeout:
        assert False, "Request timed out"
    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"
    except ValueError:
        assert False, "Response is not valid JSON"

test_attendance_records_retrieval()