
# tests/unit/test_salary.py

from django.test import TestCase
from tests.utils.test_utils import ElDawliyaTestCase
from hr.models import Salary

class SalaryModelTest(ElDawliyaTestCase):
    """
    Unit tests for the Salary model
    """

    @classmethod
    def setup_test_data(cls):
        cls.salary = Salary.objects.create(
            employee_id=1,
            amount=5000,
            period="2023-01"
        )

    @classmethod
    def teardown_test_data(cls):
        cls.salary.delete()

    def test_salary_creation(self):
        self.assertEqual(self.salary.amount, 5000)
        self.assertEqual(self.salary.period, "2023-01")

    def test_salary_str(self):
        self.assertEqual(str(self.salary), "Salary for Employee 1 in 2023-01")

    def test_salary_update(self):
        self.salary.amount = 5500
        self.salary.save()
        updated_salary = Salary.objects.get(id=self.salary.id)
        self.assertEqual(updated_salary.amount, 5500)

# tests/integration/test_employee_api.py

from django.test import TestCase
from rest_framework.test import APIClient
from hr.models import Employee

class EmployeeAPITest(TestCase):
    """
    Integration tests for Employee API endpoints
    """

    def setUp(self):
        self.client = APIClient()
        self.employee = Employee.objects.create(
            name="Test Employee",
            position="Developer",
            salary=5000
        )

    def tearDown(self):
        self.employee.delete()

    def test_get_employee(self):
        response = self.client.get(f'/api/employees/{self.employee.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "Test Employee")

    def test_create_employee(self):
        response = self.client.post('/api/employees/', {
            'name': 'New Employee',
            'position': 'Manager',
            'salary': 7000
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'New Employee')

    def test_update_employee(self):
        response = self.client.put(f'/api/employees/{self.employee.id}/', {
            'name': 'Updated Employee',
            'position': 'Senior Developer',
            'salary': 6000
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Updated Employee')

    def test_delete_employee(self):
        response = self.client.delete(f'/api/employees/{self.employee.id}/')
        self.assertEqual(response.status_code, 204)
        with self.assertRaises(Employee.DoesNotExist):
            Employee.objects.get(id=self.employee.id)

# tests/e2e/test_employee_workflow.py

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EmployeeWorkflowTest(LiveServerTestCase):
    """
    End-to-end tests for employee management workflow
    """

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.driver.get(f'{self.live_server_url}/admin/')

    def tearDown(self):
        self.driver.quit()

    def test_employee_creation_workflow(self):
        # Login
        self.driver.find_element(By.ID, 'id_username').send_keys('admin')
        self.driver.find_element(By.ID, 'id_password').send_keys('password')
        self.driver.find_element(By.ID, 'id_password').send_keys(Keys.RETURN)

        # Navigate to employee list
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Employees'))
        ).click()

        # Add new employee
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Add'))
        ).click()

        # Fill in employee details
        self.driver.find_element(By.ID, 'id_name').send_keys('New Employee')
        self.driver.find_element(By.ID, 'id_position').send_keys('Developer')
        self.driver.find_element(By.ID, 'id_salary').send_keys('5000')

        # Save employee
        self.driver.find_element(By.NAME, '_save').click()

        # Verify employee is added
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'New Employee'))
        )

# tests/utils/test_mixins.py

class ModelTestMixin:
    """
    Mixin for common model test patterns
    """
    def assert_model_created(self, model_instance):
        self.assertIsNotNone(model_instance.id)
        self.assertTrue(model_instance.pk)
        self.assertIsNotNone(model_instance.created_at)
        self.assertIsNotNone(model_instance.updated_at)

    def assert_model_updated(self, model_instance, updated_fields):
        for field in updated_fields:
            self.assertNotEqual(getattr(model_instance, field), getattr(self, f'original_{field}'))
            self.assertEqual(getattr(model_instance, field), getattr(self, f'updated_{field}'))

    def assert_model_deleted(self, model_instance):
        with self.assertRaises(model_instance.__class__.DoesNotExist):
            model_instance.__class__.objects.get(id=model_instance.id)

class APITestMixin:
    """
    Mixin for common API test patterns
    """
    def assert_api_response(self, response, status_code):
        self.assertEqual(response.status_code, status_code)
        self.assertIn('id', response.data)
        self.assertIn('created_at', response.data)
        self.assertIn('updated_at', response.data)
