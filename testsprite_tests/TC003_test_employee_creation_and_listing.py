import requests
from requests.auth import HTTPBasicAuth
import time

BASE_URL = "http://localhost:8000"
AUTH_URL = f"{BASE_URL}/api/v1/auth/token/"
EMPLOYEES_URL = f"{BASE_URL}/employees/"
USERNAME = "admin"
PASSWORD = "hgslduhgfwdv"
TIMEOUT = 30

def test_employee_creation_and_listing():
    # Step 1: Obtain JWT token using basic auth credentials
    try:
        auth_response = requests.post(
            AUTH_URL,
            json={"username": USERNAME, "password": PASSWORD},
            timeout=TIMEOUT
        )
        assert auth_response.status_code == 200, f"Auth failed with status {auth_response.status_code}"
        tokens = auth_response.json()
        access_token = tokens.get("access")
        refresh_token = tokens.get("refresh")
        assert access_token is not None and refresh_token is not None, "Tokens not found in response"
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"Authentication step failed: {e}")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Define a minimal valid employee payload for creation to test creation
    employee_payload = {
        "first_name": "TestFirstName",
        "last_name": "TestLastName",
        "email": f"test.user.{int(time.time())}@example.com",
        "phone": "1234567890",
        "department": "Testing",
        "job_title": "Test Engineer",
        "date_of_birth": "1990-01-01",
        "start_date": "2020-01-01"
    }

    employee_id = None
    try:
        # Step 2: Create a new employee
        create_response = requests.post(
            EMPLOYEES_URL,
            headers=headers,
            json=employee_payload,
            timeout=TIMEOUT
        )
        assert create_response.status_code in (200, 201), f"Employee creation failed with status {create_response.status_code}"
        created_employee = create_response.json()
        employee_id = created_employee.get("id")
        assert employee_id is not None, "Created employee ID not returned"
        
        # Step 3: List all employees and verify the created employee is in the list
        list_response = requests.get(
            EMPLOYEES_URL,
            headers=headers,
            timeout=TIMEOUT
        )
        assert list_response.status_code == 200, f"Employee listing failed with status {list_response.status_code}"
        employees_list = list_response.json()
        assert isinstance(employees_list, list), "Employee list response is not a list"
        # Check created employee presence by ID or by unique email
        found = any(emp.get("id") == employee_id or emp.get("email") == employee_payload["email"] for emp in employees_list)
        assert found, "Created employee not found in employee listing"
        
        # Step 4: Check access control - try listing employees without token
        unauth_response = requests.get(
            EMPLOYEES_URL,
            timeout=TIMEOUT
        )
        assert unauth_response.status_code in (401, 403), "Unauthorized access to employee listing should be denied"
        
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"Employee creation and listing test failed: {e}")
    finally:
        # Step 5: Cleanup - delete created employee
        if employee_id:
            try:
                del_response = requests.delete(
                    f"{EMPLOYEES_URL}{employee_id}/",
                    headers=headers,
                    timeout=TIMEOUT
                )
                # Allow 204 No Content or 200 OK for delete success
                assert del_response.status_code in (200, 204), f"Failed to delete test employee with status {del_response.status_code}"
            except Exception:
                pass  # Fail silently on cleanup

test_employee_creation_and_listing()
