
# tests/unit/test_employee.py

from django.test import TestCase
from tests.utils.test_utils import ElDawliyaTestCase
from hr.models import Employee

class EmployeeModelTest(ElDawliyaTestCase):
    """
    Unit tests for the Employee model
    """

    @classmethod
    def setup_test_data(cls):
        """
        Setup test data for Employee model
        """
        cls.employee = Employee.objects.create(
            name="Test Employee",
            position="Developer",
            salary=5000
        )

    @classmethod
    def teardown_test_data(cls):
        """
        Clean up test data
        """
        cls.employee.delete()

    def test_employee_creation(self):
        """
        Test employee creation
        """
        self.assertEqual(self.employee.name, "Test Employee")
        self.assertEqual(self.employee.position, "Developer")
        self.assertEqual(self.employee.salary, 5000)

    def test_employee_str(self):
        """
        Test string representation of employee
        """
        self.assertEqual(str(self.employee), "Test Employee")

    def test_employee_salary(self):
        """
        Test employee salary calculation
        """
        self.employee.calculate_salary()
        self.assertEqual(self.employee.salary, 5000)

    def test_employee_update(self):
        """
        Test updating employee details
        """
        self.employee.position = "Senior Developer"
        self.employee.save()
        updated_employee = Employee.objects.get(id=self.employee.id)
        self.assertEqual(updated_employee.position, "Senior Developer")
