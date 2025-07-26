
#!/usr/bin/env python
import os
import subprocess
import sys
from coverage import Coverage

def run_tests():
    # Initialize coverage
    cov = Coverage()
    cov.start()

    # Run all test files
    test_files = [
        'test_system_functionality.py',
        'test_hr_functionality.py',
        'test_api.py',
        'test_integration.py',
        'test_employee_job_update.py',
        'test_salary_urls.py',
    ]

    for test_file in test_files:
        print(f"Running {test_file}...")
        result = subprocess.run(['python', test_file], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Test {test_file} failed:")
            print(result.stderr)
            return False

    # Stop coverage and generate report
    cov.stop()
    cov.save()
    cov.report()

    return True

if __name__ == "__main__":
    if run_tests():
        print("All tests passed!")
    else:
        print("Some tests failed.")
        sys.exit(1)
