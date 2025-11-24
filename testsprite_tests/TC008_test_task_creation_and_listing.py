import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
AUTH_CREDENTIALS = ("admin", "hgslduhgfwdv")
TIMEOUT = 30

def test_task_creation_and_listing():
    """test_task_creation_and_listing function"""
    auth = HTTPBasicAuth(AUTH_CREDENTIALS[0], AUTH_CREDENTIALS[1])
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Sample payload for creating a task; assigned_to omitted if no assignment
    new_task_payload = {
        "title": "Test Task for Creation and Listing",
        "description": "This task is created to validate creation and listing endpoints.",
        "progress": 0
    }

    created_task_id = None

    try:
        # 1. Create a new task
        response_create = requests.post(
            f"{BASE_URL}/api/v1/tasks/",
            json=new_task_payload,
            headers=headers,
            auth=auth,
            timeout=TIMEOUT
        )
        assert response_create.status_code == 201, f"Unexpected status code on task creation: {response_create.status_code}"
        response_data = response_create.json()
        assert "id" in response_data, "Response missing task 'id'"
        created_task_id = response_data["id"]
        assert response_data.get("title") == new_task_payload["title"], "Task title mismatch"
        assert response_data.get("progress") == new_task_payload["progress"], "Task progress mismatch"

        # 2. List existing tasks and verify the created task is present with correct data
        response_list = requests.get(
            f"{BASE_URL}/api/v1/tasks/",
            headers=headers,
            auth=auth,
            timeout=TIMEOUT
        )
        assert response_list.status_code == 200, f"Unexpected status code on listing tasks: {response_list.status_code}"
        tasks = response_list.json()
        assert isinstance(tasks, list), "Tasks listing response is not a list"

        # Find the created task in the list
        matched_tasks = [t for t in tasks if t.get("id") == created_task_id]
        assert matched_tasks, "Created task not found in the tasks listing"
        task = matched_tasks[0]
        # Validate key fields related to assignment and progress
        assert task.get("title") == new_task_payload["title"], "Listed task title mismatch"
        assert task.get("progress") == new_task_payload["progress"], "Listed task progress mismatch"
        assert "assigned_to" in task, "Listed task missing assigned_to field"

    finally:
        # Cleanup: Delete the created task if exists
        if created_task_id:
            requests.delete(
                f"{BASE_URL}/api/v1/tasks/{created_task_id}/",
                headers=headers,
                auth=auth,
                timeout=TIMEOUT
            )

test_task_creation_and_listing()