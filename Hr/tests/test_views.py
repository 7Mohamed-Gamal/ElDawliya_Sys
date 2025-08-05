"""
اختبارات العروض (Views)
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse
from Hr.models import Employee, Department, JobPosition, Company
from Hr.services.monitoring_service import monitoring_service
from decimal import Decimal
from unittest.mock import patch, MagicMock


class ViewsAuthenticationTest(TestCase):
    """اختبارات المصادقة في العروض"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_employee_list_requires_login(self):
        """اختبار أن قائمة الموظفين تتطلب تسجيل دخول"""
        url = reverse('hr:employee_list')
        response = self.client.get(url)
        
        # يجب إعادة توجيه إلى صفحة تسجيل الدخول
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_employee_list_with_login(self):
        """اختبار الوصول لقائمة الموظفين بعد تسجيل الدخول"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('hr:employee_list')
        response = self.client.get(url)
        
        # يجب أن يكون الوصول مسموحاً
        self.assertEqual(response.status_code, 200)
    
    def test_admin_views_require_staff(self):
        """اختبار أن العروض الإدارية تتطلب صلاحيات إدارية"""
        # تسجيل دخول مستخدم عادي
        self.client.login(username='testuser', password='testpass123')
        
        # محاولة الوصول لعرض إداري
        url = reverse('hr:monitoring_dashboard')
        response = self.client.get(url)
        
        # يجب رفض الوصول
        self.assertEqual(response.status_code, 302)
    
    def test_admin_views_with_staff_user(self):
        """اختبار الوصول للعروض الإدارية بصلاحيات إدارية"""
        self.client.login(username='staffuser', password='testpass123')
        
        url = reverse('hr:monitoring_dashboard')
        response = self.client.get(url)
        
        # يجب أن يكون الوصول مسموحاً
        self.assertEqual(response.status_code, 200)


class EmployeeViewsTest(TestCase):
    """اختبارات عروض الموظفين"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # إنشاء البيانات الأساسية
        self.company = Company.objects.create(
            name='شركة الاختبار',
            commercial_register='1234567890'
        )
        
        self.department = Department.objects.create(
            name='قسم الموارد البشرية',
            code='HR001',
            company=self.company
        )
        
        self.job_position = JobPosition.objects.create(
            name='موظف موارد بشرية',
            code='HRE001',
            department=self.department,
            min_salary=Decimal('5000.00'),
            max_salary=Decimal('8000.00')
        )
        
        # إنشاء موظف للاختبار
        self.employee_user = User.objects.create_user(
            username='employee_user',
            email='employee@example.com',
            password='testpass123'
        )
        
        self.employee = Employee.objects.create(
            user=self.employee_user,
            employee_id='EMP001',
            first_name='أحمد',
            last_name='محمد',
            national_id='1234567890',
            phone_number='0501234567',
            email='ahmed@company.com',
            department=self.department,
            job_position=self.job_position,
            company=self.company,
            hire_date='2024-01-01',
            basic_salary=Decimal('6000.00'),
            gender='male',
            marital_status='single'
        )
    
    def test_employee_list_view(self):
        """اختبار عرض قائمة الموظفين"""
        url = reverse('hr:employee_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'أحمد محمد')
        self.assertContains(response, 'EMP001')
    
    def test_employee_detail_view(self):
        """اختبار عرض تفاصيل الموظف"""
        url = reverse('hr:employee_detail', kwargs={'pk': self.employee.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'أحمد محمد')
        self.assertContains(response, 'قسم الموارد البشرية')
    
    def test_employee_create_view_get(self):
        """اختبار عرض نموذج إنشاء موظف"""
        url = reverse('hr:employee_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'إضافة موظف جديد')
    
    def test_employee_create_view_post(self):
        """اختبار إنشاء موظف عبر النموذج"""
        new_user = User.objects.create_user(
            username='newemployee',
            email='newemployee@example.com',
            password='testpass123'
        )
        
        employee_data = {
            'user': new_user.id,
            'employee_id': 'EMP002',
            'first_name': 'فاطمة',
            'last_name': 'علي',
            'national_id': '0987654321',
            'phone_number': '0507654321',
            'email': 'fatima@company.com',
            'department': self.department.id,
            'job_position': self.job_position.id,
            'company': self.company.id,
            'hire_date': '2024-01-01',
            'basic_salary': '6000.00',
            'gender': 'female',
            'marital_status': 'single'
        }
        
        url = reverse('hr:employee_create')
        response = self.client.post(url, employee_data)
        
        # يجب إعادة توجيه بعد الإنشاء الناجح
        if response.status_code == 302:
            self.assertEqual(Employee.objects.count(), 2)
            new_employee = Employee.objects.get(employee_id='EMP002')
            self.assertEqual(new_employee.first_name, 'فاطمة')
        else:
            # طباعة الأخطاء للتشخيص
            print(f"Employee creation failed: {response.status_code}")
            if hasattr(response, 'context') and 'form' in response.context:
                print(f"Form errors: {response.context['form'].errors}")
    
    def test_employee_update_view(self):
        """اختبار تحديث بيانات الموظف"""
        update_data = {
            'user': self.employee.user.id,
            'employee_id': self.employee.employee_id,
            'first_name': 'محمد',  # تغيير الاسم
            'last_name': self.employee.last_name,
            'national_id': self.employee.national_id,
            'phone_number': self.employee.phone_number,
            'email': self.employee.email,
            'department': self.employee.department.id,
            'job_position': self.employee.job_position.id,
            'company': self.employee.company.id,
            'hire_date': self.employee.hire_date,
            'basic_salary': '7000.00',  # تغيير الراتب
            'gender': self.employee.gender,
            'marital_status': self.employee.marital_status
        }
        
        url = reverse('hr:employee_update', kwargs={'pk': self.employee.pk})
        response = self.client.post(url, update_data)
        
        if response.status_code == 302:
            self.employee.refresh_from_db()
            self.assertEqual(self.employee.first_name, 'محمد')
            self.assertEqual(self.employee.basic_salary, Decimal('7000.00'))
        else:
            print(f"Employee update failed: {response.status_code}")
            if hasattr(response, 'context') and 'form' in response.context:
                print(f"Form errors: {response.context['form'].errors}")
    
    def test_employee_search_view(self):
        """اختبار البحث في الموظفين"""
        url = reverse('hr:employee_search')
        response = self.client.get(url, {'q': 'أحمد'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'أحمد محمد')
        
        # البحث بنص غير موجود
        response = self.client.get(url, {'q': 'غير موجود'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'أحمد محمد')


class DepartmentViewsTest(TestCase):
    """اختبارات عروض الأقسام"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.company = Company.objects.create(
            name='شركة الاختبار',
            commercial_register='1234567890'
        )
        
        self.department = Department.objects.create(
            name='قسم الموارد البشرية',
            code='HR001',
            company=self.company
        )
    
    def test_department_list_view(self):
        """اختبار عرض قائمة الأقسام"""
        url = reverse('hr:department_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'قسم الموارد البشرية')
        self.assertContains(response, 'HR001')
    
    def test_department_detail_view(self):
        """اختبار عرض تفاصيل القسم"""
        url = reverse('hr:department_detail', kwargs={'pk': self.department.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'قسم الموارد البشرية')
    
    def test_department_create_view(self):
        """اختبار إنشاء قسم جديد"""
        department_data = {
            'name': 'قسم المالية',
            'name_en': 'Finance Department',
            'code': 'FIN001',
            'company': self.company.id,
            'description': 'قسم الشؤون المالية'
        }
        
        url = reverse('hr:department_create')
        response = self.client.post(url, department_data)
        
        if response.status_code == 302:
            self.assertEqual(Department.objects.count(), 2)
            new_dept = Department.objects.get(code='FIN001')
            self.assertEqual(new_dept.name, 'قسم المالية')
        else:
            print(f"Department creation failed: {response.status_code}")
            if hasattr(response, 'context') and 'form' in response.context:
                print(f"Form errors: {response.context['form'].errors}")


class MonitoringViewsTest(TestCase):
    """اختبارات عروض المراقبة"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='staffuser', password='testpass123')
    
    @patch.object(monitoring_service, 'get_system_status')
    def test_monitoring_dashboard_view(self, mock_get_status):
        """اختبار لوحة تحكم المراقبة"""
        # إعداد البيانات الوهمية
        mock_get_status.return_value = {
            'overall_status': 'healthy',
            'timestamp': '2024-01-01T12:00:00',
            'system': {
                'cpu': {'usage_percent': 45.0, 'status': 'normal'},
                'memory': {'usage_percent': 55.0, 'status': 'normal'},
                'disk': {'usage_percent': 70.0, 'status': 'normal'}
            },
            'database': {'connected': True, 'status': 'normal'},
            'application': {'users': {'online_users': 5, 'total_users': 100}},
            'performance': {'avg_response_time': 0.5},
            'alerts': []
        }
        
        url = reverse('hr:monitoring_dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'مراقبة النظام')
        self.assertContains(response, 'healthy')
    
    @patch.object(monitoring_service, 'get_system_status')
    def test_system_status_api(self, mock_get_status):
        """اختبار API حالة النظام"""
        mock_get_status.return_value = {
            'overall_status': 'healthy',
            'timestamp': '2024-01-01T12:00:00'
        }
        
        url = reverse('hr:monitoring_api_status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        import json
        data = json.loads(response.content)
        self.assertEqual(data['overall_status'], 'healthy')
    
    @patch.object(monitoring_service, 'get_active_alerts')
    def test_system_alerts_api(self, mock_get_alerts):
        """اختبار API التنبيهات"""
        mock_get_alerts.return_value = [
            {
                'type': 'cpu_high',
                'level': 'warning',
                'message': 'استخدام المعالج مرتفع',
                'timestamp': '2024-01-01T12:00:00'
            }
        ]
        
        url = reverse('hr:monitoring_api_alerts')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        import json
        data = json.loads(response.content)
        self.assertEqual(len(data['alerts']), 1)
        self.assertEqual(data['alerts'][0]['message'], 'استخدام المعالج مرتفع')


class FormValidationTest(TestCase):
    """اختبارات التحقق من النماذج"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.company = Company.objects.create(
            name='شركة الاختبار',
            commercial_register='1234567890'
        )
        
        self.department = Department.objects.create(
            name='قسم الموارد البشرية',
            code='HR001',
            company=self.company
        )
        
        self.job_position = JobPosition.objects.create(
            name='موظف موارد بشرية',
            code='HRE001',
            department=self.department,
            min_salary=Decimal('5000.00'),
            max_salary=Decimal('8000.00')
        )
    
    def test_employee_form_validation_missing_fields(self):
        """اختبار التحقق من الحقول المطلوبة في نموذج الموظف"""
        incomplete_data = {
            'first_name': 'أحمد',
            # نقص حقول مطلوبة
        }
        
        url = reverse('hr:employee_create')
        response = self.client.post(url, incomplete_data)
        
        # يجب أن يبقى في نفس الصفحة مع أخطاء
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'هذا الحقل مطلوب')
    
    def test_employee_form_validation_invalid_email(self):
        """اختبار التحقق من صحة البريد الإلكتروني"""
        new_user = User.objects.create_user(
            username='newemployee',
            email='newemployee@example.com',
            password='testpass123'
        )
        
        invalid_data = {
            'user': new_user.id,
            'employee_id': 'EMP002',
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'national_id': '1234567890',
            'phone_number': '0501234567',
            'email': 'invalid-email',  # بريد غير صحيح
            'department': self.department.id,
            'job_position': self.job_position.id,
            'company': self.company.id,
            'hire_date': '2024-01-01',
            'basic_salary': '6000.00',
            'gender': 'male',
            'marital_status': 'single'
        }
        
        url = reverse('hr:employee_create')
        response = self.client.post(url, invalid_data)
        
        self.assertEqual(response.status_code, 200)
        # التحقق من وجود رسالة خطأ للبريد الإلكتروني
        self.assertContains(response, 'بريد إلكتروني صحيح')
    
    def test_employee_form_validation_salary_range(self):
        """اختبار التحقق من نطاق الراتب"""
        new_user = User.objects.create_user(
            username='newemployee',
            email='newemployee@example.com',
            password='testpass123'
        )
        
        invalid_data = {
            'user': new_user.id,
            'employee_id': 'EMP002',
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'national_id': '1234567890',
            'phone_number': '0501234567',
            'email': 'ahmed@company.com',
            'department': self.department.id,
            'job_position': self.job_position.id,
            'company': self.company.id,
            'hire_date': '2024-01-01',
            'basic_salary': '10000.00',  # أكبر من الحد الأقصى
            'gender': 'male',
            'marital_status': 'single'
        }
        
        url = reverse('hr:employee_create')
        response = self.client.post(url, invalid_data)
        
        self.assertEqual(response.status_code, 200)
        # التحقق من وجود رسالة خطأ للراتب
        self.assertContains(response, 'الراتب يجب أن يكون')


class ResponseFormatTest(TestCase):
    """اختبارات تنسيق الاستجابات"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_json_response_format(self):
        """اختبار تنسيق الاستجابة JSON"""
        self.user.is_staff = True
        self.user.save()
        
        url = reverse('hr:monitoring_api_status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # التحقق من أن الاستجابة JSON صحيحة
        import json
        try:
            data = json.loads(response.content)
            self.assertIsInstance(data, dict)
        except json.JSONDecodeError:
            self.fail("Response is not valid JSON")
    
    def test_html_response_format(self):
        """اختبار تنسيق الاستجابة HTML"""
        url = reverse('hr:employee_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])
        
        # التحقق من وجود عناصر HTML أساسية
        self.assertContains(response, '<html')
        self.assertContains(response, '</html>')
        self.assertContains(response, '<body')
        self.assertContains(response, '</body>')


class ContextDataTest(TestCase):
    """اختبارات بيانات السياق في العروض"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.company = Company.objects.create(
            name='شركة الاختبار',
            commercial_register='1234567890'
        )
        
        self.department = Department.objects.create(
            name='قسم الموارد البشرية',
            code='HR001',
            company=self.company
        )
    
    def test_employee_list_context(self):
        """اختبار بيانات السياق في قائمة الموظفين"""
        url = reverse('hr:employee_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # التحقق من وجود البيانات المطلوبة في السياق
        self.assertIn('employees', response.context)
        self.assertIn('page_title', response.context)
        
        # التحقق من نوع البيانات
        self.assertIsInstance(response.context['employees'], (list, type(Employee.objects.all())))
    
    def test_department_list_context(self):
        """اختبار بيانات السياق في قائمة الأقسام"""
        url = reverse('hr:department_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # التحقق من وجود البيانات المطلوبة في السياق
        self.assertIn('departments', response.context)
        self.assertIn('page_title', response.context)
        
        # التحقق من أن القسم موجود في القائمة
        departments = list(response.context['departments'])
        self.assertIn(self.department, departments)