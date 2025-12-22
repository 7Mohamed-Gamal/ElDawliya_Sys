"""
Tests for the Enhanced Reporting System
اختبارات نظام التقارير المحسن
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import json

from accounts.models import Users_Login_New
# Temporarily disabled - will be replaced with new modular HR apps
# from Hr.models import Employee, Department
from apps.projects.tasks.models import Task
from apps.projects.meetings.models import Meeting
from apps.inventory.models import TblProducts
from apps.procurement.purchase_orders.models import PurchaseRequest, Vendor
from core.reporting import ReportingService


class ReportingServiceTestCase(TestCase):
    """Test cases for the ReportingService class"""

    def setUp(self):
        """Set up test data"""
        self.reporting_service = ReportingService()

        # Create test user
        self.user = Users_Login_New.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test department
        self.department = Department.objects.create(
            dept_code=1,
            dept_name='Test Department',
            is_active=True
        )

        # Create test employees
        self.employee1 = Employee.objects.create(
            emp_id='EMP001',
            emp_first_name='John',
            emp_last_name='Doe',
            department=self.department,
            working_condition='سارى',
            emp_hire_date=timezone.now().date()
        )

        self.employee2 = Employee.objects.create(
            emp_id='EMP002',
            emp_first_name='Jane',
            emp_last_name='Smith',
            department=self.department,
            working_condition='سارى',
            emp_hire_date=timezone.now().date()
        )

        # Create test tasks
        self.task1 = Task.objects.create(
            title='Test Task 1',
            description='Test task description',
            status='pending',
            assigned_to=self.user,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=7)
        )

        # Create test meetings
        self.meeting1 = Meeting.objects.create(
            title='Test Meeting',
            description='Test meeting description',
            date=timezone.now(),
            status='scheduled',
            organizer=self.user
        )

        # Create test vendor
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            contact_person='Test Contact',
            email='vendor@test.com'
        )

        # Create test purchase request
        self.purchase_request = PurchaseRequest.objects.create(
            request_number='PR001',
            vendor=self.vendor,
            requested_by=self.user,
            status='pending'
        )

    def tearDown(self):
        """Clean up after tests"""
        cache.clear()

    def test_get_dashboard_data_structure(self):
        """Test that dashboard data returns correct structure"""
        data = self.reporting_service.get_dashboard_data(self.user, '30d')

        # Check main keys
        expected_keys = [
            'overview', 'employee_analytics', 'task_analytics',
            'meeting_analytics', 'inventory_analytics', 'purchase_analytics',
            'trends', 'charts', 'generated_at', 'date_range'
        ]

        for key in expected_keys:
            self.assertIn(key, data)

    def test_overview_metrics(self):
        """Test overview metrics calculation"""
        data = self.reporting_service.get_dashboard_data(self.user, '30d')
        overview = data['overview']

        # Test employee metrics
        self.assertEqual(overview['total_employees'], 2)
        self.assertEqual(overview['active_employees'], 2)

        # Test task metrics
        self.assertEqual(overview['total_tasks'], 1)
        self.assertEqual(overview['active_tasks'], 1)

        # Test meeting metrics
        self.assertEqual(overview['total_meetings'], 1)

        # Test purchase request metrics
        self.assertEqual(overview['total_purchase_requests'], 1)
        self.assertEqual(overview['pending_purchase_requests'], 1)

    def test_employee_analytics(self):
        """Test employee analytics data"""
        data = self.reporting_service.get_dashboard_data(self.user, '30d')
        employee_analytics = data['employee_analytics']

        # Check structure
        self.assertIn('department_distribution', employee_analytics)
        self.assertIn('working_condition_distribution', employee_analytics)
        self.assertIn('total_departments', employee_analytics)

        # Check department distribution
        dept_dist = employee_analytics['department_distribution']
        self.assertEqual(len(dept_dist), 1)
        self.assertEqual(dept_dist[0]['department__dept_name'], 'Test Department')
        self.assertEqual(dept_dist[0]['count'], 2)

    def test_chart_data_format(self):
        """Test chart data formatting"""
        data = self.reporting_service.get_dashboard_data(self.user, '30d')
        charts = data['charts']

        # Check chart types
        expected_chart_types = ['employee_by_department', 'task_status', 'meeting_status']
        for chart_type in expected_chart_types:
            self.assertIn(chart_type, charts)

            # Check chart structure
            chart = charts[chart_type]
            self.assertIn('type', chart)
            self.assertIn('data', chart)
            self.assertIn('labels', chart['data'])
            self.assertIn('datasets', chart['data'])

    def test_date_range_validation(self):
        """Test date range validation"""
        # Valid date ranges
        valid_ranges = ['7d', '30d', '90d', '1y']
        for date_range in valid_ranges:
            data = self.reporting_service.get_dashboard_data(self.user, date_range)
            self.assertEqual(data['date_range'], date_range)

    def test_caching_functionality(self):
        """Test that caching works correctly"""
        # Clear cache first
        cache.clear()

        # First call should generate data
        data1 = self.reporting_service.get_dashboard_data(self.user, '30d')

        # Second call should use cached data
        data2 = self.reporting_service.get_dashboard_data(self.user, '30d')

        # Data should be identical
        self.assertEqual(data1['generated_at'], data2['generated_at'])

    def test_custom_report_generation(self):
        """Test custom report generation"""
        report_config = {
            'modules': ['employees', 'tasks'],
            'date_range': '30d',
            'format': 'json'
        }

        report = self.reporting_service.generate_custom_report(
            user=self.user,
            config=report_config
        )

        # Check report structure
        self.assertIn('report_id', report)
        self.assertIn('config', report)
        self.assertIn('data', report)
        self.assertIn('generated_at', report)

        # Check that only requested modules are included
        self.assertIn('employees', report['data'])
        self.assertIn('tasks', report['data'])
        self.assertNotIn('meetings', report['data'])


class ReportingAPITestCase(TestCase):
    """Test cases for the Reporting API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create test user
        self.user = Users_Login_New.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Login user
        self.client.force_login(self.user)

    def test_dashboard_data_endpoint(self):
        """Test dashboard data API endpoint"""
        url = reverse('api:dashboard_data')
        response = self.client.get(url, {'date_range': '30d'})

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('overview', data)
        self.assertIn('charts', data)

    def test_dashboard_data_invalid_range(self):
        """Test dashboard data with invalid date range"""
        url = reverse('api:dashboard_data')
        response = self.client.get(url, {'date_range': 'invalid'})

        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertIn('error', data)

    def test_report_templates_endpoint(self):
        """Test report templates API endpoint"""
        url = reverse('api:report_templates')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('templates', data)
        self.assertIn('modules', data)
        self.assertIn('formats', data)

    def test_generate_custom_report_endpoint(self):
        """Test custom report generation API endpoint"""
        url = reverse('api:generate_custom_report')

        report_config = {
            'modules': ['employees'],
            'date_range': '30d',
            'format': 'json'
        }

        response = self.client.post(
            url,
            data=json.dumps(report_config),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('report_id', data)
        self.assertIn('data', data)

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access API"""
        self.client.logout()

        url = reverse('api:dashboard_data')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)


class ReportingViewsTestCase(TestCase):
    """Test cases for the Reporting Views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create test user
        self.user = Users_Login_New.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Login user
        self.client.force_login(self.user)

    def test_reporting_dashboard_view(self):
        """Test reporting dashboard view"""
        url = reverse('core:reporting_dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'لوحة التحكم والتقارير')
        self.assertContains(response, 'chart-container')

    def test_reporting_dashboard_requires_login(self):
        """Test that reporting dashboard requires login"""
        self.client.logout()

        url = reverse('core:reporting_dashboard')
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
