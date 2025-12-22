import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_payroll_data_retrieval():
    """test_payroll_data_retrieval function"""
    auth = HTTPBasicAuth("admin", "hgslduhgfwdv")
    url = f"{BASE_URL}/payrolls/"

    try:
        response = requests.get(url, auth=auth, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

        payrolls = response.json()
        assert isinstance(payrolls, list), "Payroll data should be a list"

        # Validate structure and content of payroll data
        for payroll in payrolls:
            assert isinstance(payroll, dict), "Each payroll entry should be a dictionary"
            # Salary components checking
            assert "salary_components" in payroll, "Payroll entry missing 'salary_components'"
            salary_components = payroll["salary_components"]
            assert isinstance(salary_components, dict), "'salary_components' should be a dictionary"
            # Ensure some expected keys exist in salary components
            expected_salary_keys = {"base_salary", "allowances", "bonuses"}
            assert expected_salary_keys.intersection(salary_components.keys()), \
                "Missing expected keys in salary_components"

            # Deductions checking
            assert "deductions" in payroll, "Payroll entry missing 'deductions'"
            deductions = payroll["deductions"]
            assert isinstance(deductions, dict), "'deductions' should be a dictionary"
            # Ensure some expected keys exist in deductions
            expected_deduction_keys = {"tax", "insurance", "other"}
            assert expected_deduction_keys.intersection(deductions.keys()), \
                "Missing expected keys in deductions"

        # Performance: response time less than 0.5 seconds (500 ms)
        elapsed_ms = response.elapsed.total_seconds() * 1000
        assert elapsed_ms < 500, f"API response time is too high: {elapsed_ms} ms"

    except requests.exceptions.RequestException as e:
        assert False, f"HTTP request failed: {e}"

test_payroll_data_retrieval()