"""
HR API Tests - اختبارات واجهات برمجة التطبيقات للموارد البشرية
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date, datetime, timedelta
import json

from ..models_enhanced import (
    Company, Branch, Department, JobPosition, Employee,
    WorkShiftEnhanced, AttendanceRecordEnhanced, LeaveType, LeaveRequest
)

User = get_user_model()

class HRAPITestCase(APITestCase):
    """الفئة الأساسية لاختبارات API الموارد البشرية"""
    
    def setUp(self):
        """إعداد البيانات الأساسية للاختبارات"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test company
        self.company = Company.objects.create(
            name='شركة الاختبار',
            name_english='Test Company',
            code='TEST001',
            tax_number='123456789',
            is_active=True
        )
        
        # Create test branch
        self.branch = Branch.objects.create(
            company=self.company,
            name='الفرع الرئيسي',
            name_english='Main Branch',
            code='MAIN001',
            is_active=True
        )
        
        # Create test department
        self.department = Department.objects.create(
            company=self.company,
            branch=self.branch,
            name='قسم الموارد البشرية',
            name_english='HR Department',
            code='HR001',
            is_active=True
        )
        
        # Create test job position
        self.job_position = JobPosition.objects.create(
            department=self.department,
            title='موظف موارد بشرية',
            title_english='HR Employee',
            code='HR_EMP001',
            level='junior',
            min_salary=5000.00,
            max_salary=8000.00,
            is_active=True
        )
        
        # Create test employee
        self.employee = Employee.objects.create(
            user=self.user,
            company=self.company,
            branch=self.branch,
            department=self.department,
            job_position=self.job_position,
            employee_number='EMP001',
            first_name='أحمد',
            last_name='محمد',
            email='ahmed@example.com',
            phone_primary='01234567890',
            hire_date=date.today() - timedelta(days=365),
            basic_salary=6000.00,
            employment_type='full_time',
            status='active',
            is_active=True
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set up API client with authentication
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

class CompanyAPITestCase(HRAPITestCase):
    """اختبارات API الشركات"""
    
    def test_list_companies(self):
        """اختبار جلب قائمة الشركات"""
        url = reverse('hr_api:company-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'شركة الاختبار')
    
    def test_create_company(self):
        """اختبار إنشاء شركة جديدة"""
        url = reverse('hr_api:company-list')
        data = {
            'name': 'شركة جديدة',
            'name_english': 'New Company',
            'code': 'NEW001',
            'tax_number': '987654321',
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'شركة جديدة')
        self.assertTrue(Company.objects.filter(code='NEW001').exists())
    
    def test_get_company_detail(self):
        """اختبار جلب تفاصيل شركة"""
        url = reverse('hr_api:company-detail', kwargs={'pk': self.company.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'شركة الاختبار')
        self.assertEqual(response.data['code'], 'TEST001')

class EmployeeAPITestCase(HRAPITestCase):
    """اختبارات API الموظفين"""
    
    def test_list_employees(self):
        """اختبار جلب قائمة الموظفين"""
        url = reverse('hr_api:employee-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'أحمد')
    
    def test_create_employee(self):
        """اختبار إنشاء موظف جديد"""
        # Create another user for the new employee
        new_user = User.objects.create_user(
            username='newemployee',
            email='newemployee@example.com',
            password='newpass123'
        )
        
        url = reverse('hr_api:employee-list')
        data = {
            'user': new_user.id,
            'company': self.company.id,
            'branch': self.branch.id,
            'department': self.department.id,
            'job_position': self.job_position.id,
            'employee_number': 'EMP002',
            'first_name': 'فاطمة',
            'last_name': 'علي',
            'email': 'fatima@example.com',
            'phone_primary': '01987654321',
            'hire_date': date.today().isoformat(),
            'basic_salary': 5500.00,
            'employment_type': 'full_time',
            'status': 'active',
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'فاطمة')
        self.assertTrue(Employee.objects.filter(employee_number='EMP002').exists())
    
    def test_employee_search(self):
        """اختبار البحث في الموظفين"""
        url = reverse('hr_api:employee-list')
        response = self.client.get(url, {'search': 'أحمد'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'أحمد')
    
    def test_employee_filter_by_department(self):
        """اختبار فلترة الموظفين حسب القسم"""
        url = reverse('hr_api:employee-list')
        response = self.client.get(url, {'department': self.department.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_employee_statistics(self):
        """اختبار إحصائيات الموظفين"""
        url = reverse('hr_api:employee-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_employees', response.data)
        self.assertIn('active_employees', response.data)

class AttendanceAPITestCase(HRAPITestCase):
    """اختبارات API الحضور"""
    
    def setUp(self):
        super().setUp()
        
        # Create test work shift
        self.work_shift = WorkShiftEnhanced.objects.create(
            company=self.company,
            name='الوردية الصباحية',
            name_english='Morning Shift',
            code='MORNING',
            shift_type='fixed',
            start_time='08:00:00',
            end_time='17:00:00',
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=False,
            sunday=False,
            is_active=True
        )
        
        # Create test attendance record
        self.attendance_record = AttendanceRecordEnhanced.objects.create(
            employee=self.employee,
            shift=self.work_shift,
            date=date.today(),
            timestamp=datetime.now(),
            attendance_type='check_in',
            status='on_time',
            verification_method='fingerprint',
            is_approved=True
        )
    
    def test_list_work_shifts(self):
        """اختبار جلب قائمة الورديات"""
        url = reverse('hr_api:workshift-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'الوردية الصباحية')
    
    def test_list_attendance_records(self):
        """اختبار جلب سجلات الحضور"""
        url = reverse('hr_api:attendancerecord-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['attendance_type'], 'check_in')
    
    def test_filter_attendance_by_employee(self):
        """اختبار فلترة الحضور حسب الموظف"""
        url = reverse('hr_api:attendancerecord-list')
        response = self.client.get(url, {'employee': self.employee.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_attendance_by_date(self):
        """اختبار فلترة الحضور حسب التاريخ"""
        url = reverse('hr_api:attendancerecord-list')
        response = self.client.get(url, {'date': date.today().isoformat()})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class LeaveAPITestCase(HRAPITestCase):
    """اختبارات API الإجازات"""
    
    def setUp(self):
        super().setUp()
        
        # Create test leave type
        self.leave_type = LeaveType.objects.create(
            company=self.company,
            name='إجازة سنوية',
            name_english='Annual Leave',
            code='ANNUAL',
            category='annual',
            default_days=21,
            max_days_per_year=30,
            is_paid=True,
            is_active=True
        )
        
        # Create test leave request
        self.leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            leave_type=self.leave_type,
            start_date=date.today() + timedelta(days=7),
            end_date=date.today() + timedelta(days=10),
            days_requested=4,
            reason='إجازة شخصية',
            status='pending'
        )
    
    def test_list_leave_types(self):
        """اختبار جلب أنواع الإجازات"""
        url = reverse('hr_api:leavetype-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'إجازة سنوية')
    
    def test_list_leave_requests(self):
        """اختبار جلب طلبات الإجازات"""
        url = reverse('hr_api:leaverequest-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'pending')
    
    def test_create_leave_request(self):
        """اختبار إنشاء طلب إجازة"""
        url = reverse('hr_api:leaverequest-list')
        data = {
            'employee': self.employee.id,
            'leave_type': self.leave_type.id,
            'start_date': (date.today() + timedelta(days=14)).isoformat(),
            'end_date': (date.today() + timedelta(days=16)).isoformat(),
            'days_requested': 3,
            'reason': 'إجازة طارئة',
            'status': 'pending'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reason'], 'إجازة طارئة')
    
    def test_filter_leave_requests_by_status(self):
        """اختبار فلترة طلبات الإجازات حسب الحالة"""
        url = reverse('hr_api:leaverequest-list')
        response = self.client.get(url, {'status': 'pending'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class StatisticsAPITestCase(HRAPITestCase):
    """اختبارات API الإحصائيات"""
    
    def test_dashboard_statistics(self):
        """اختبار إحصائيات لوحة التحكم"""
        url = reverse('hr_api:dashboard-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('employee_stats', response.data)
        self.assertIn('attendance_stats', response.data)
        self.assertIn('leave_stats', response.data)
        self.assertIn('payroll_stats', response.data)
    
    def test_attendance_report(self):
        """اختبار تقرير الحضور"""
        url = reverse('hr_api:attendance-report')
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        response = self.client.get(url, {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('employee', response.data)
        self.assertIn('period', response.data)
        self.assertIn('statistics', response.data)
    
    def test_payroll_summary(self):
        """اختبار ملخص الرواتب"""
        url = reverse('hr_api:payroll-summary')
        response = self.client.get(url, {
            'month': date.today().month,
            'year': date.today().year
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('period', response.data)
        self.assertIn('summary', response.data)

class AuthenticationTestCase(APITestCase):
    """اختبارات المصادقة"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_obtain_token(self):
        """اختبار الحصول على رمز المصادقة"""
        url = reverse('hr_api:token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_refresh_token(self):
        """اختبار تجديد رمز المصادقة"""
        # First get tokens
        refresh = RefreshToken.for_user(self.user)
        
        url = reverse('hr_api:token_refresh')
        data = {'refresh': str(refresh)}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_verify_token(self):
        """اختبار التحقق من رمز المصادقة"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        url = reverse('hr_api:token_verify')
        data = {'token': access_token}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthorized_access(self):
        """اختبار الوصول غير المصرح"""
        url = reverse('hr_api:employee-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PermissionTestCase(HRAPITestCase):
    """اختبارات الصلاحيات"""
    
    def setUp(self):
        super().setUp()
        
        # Create regular user without HR permissions
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='regularpass123'
        )
        
        # Create regular employee
        self.regular_employee = Employee.objects.create(
            user=self.regular_user,
            company=self.company,
            branch=self.branch,
            department=self.department,
            job_position=self.job_position,
            employee_number='EMP003',
            first_name='سارة',
            last_name='أحمد',
            email='sara@example.com',
            phone_primary='01555666777',
            hire_date=date.today(),
            basic_salary=5000.00,
            employment_type='full_time',
            status='active',
            is_active=True
        )
    
    def test_hr_staff_can_create_employee(self):
        """اختبار قدرة موظف الموارد البشرية على إنشاء موظف"""
        # Mark current employee as HR staff
        self.employee.is_hr_staff = True
        self.employee.save()
        
        new_user = User.objects.create_user(
            username='newhremployee',
            email='newhr@example.com',
            password='newhrpass123'
        )
        
        url = reverse('hr_api:employee-list')
        data = {
            'user': new_user.id,
            'company': self.company.id,
            'branch': self.branch.id,
            'department': self.department.id,
            'job_position': self.job_position.id,
            'employee_number': 'EMP004',
            'first_name': 'محمد',
            'last_name': 'خالد',
            'email': 'mohamed@example.com',
            'phone_primary': '01444555666',
            'hire_date': date.today().isoformat(),
            'basic_salary': 5200.00,
            'employment_type': 'full_time',
            'status': 'active',
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_regular_employee_cannot_create_employee(self):
        """اختبار عدم قدرة الموظف العادي على إنشاء موظف"""
        # Switch to regular user
        refresh = RefreshToken.for_user(self.regular_user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        new_user = User.objects.create_user(
            username='anothernewemployee',
            email='anothernew@example.com',
            password='anotherpass123'
        )
        
        url = reverse('hr_api:employee-list')
        data = {
            'user': new_user.id,
            'company': self.company.id,
            'branch': self.branch.id,
            'department': self.department.id,
            'job_position': self.job_position.id,
            'employee_number': 'EMP005',
            'first_name': 'علي',
            'last_name': 'حسن',
            'email': 'ali@example.com',
            'phone_primary': '01333444555',
            'hire_date': date.today().isoformat(),
            'basic_salary': 4800.00,
            'employment_type': 'full_time',
            'status': 'active',
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)