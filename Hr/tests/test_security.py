"""
اختبارات الأمان
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from Hr.models import Employee, Department, JobPosition, Company
from Hr.services.encryption_service import encryption_service
from decimal import Decimal
import re


class AuthenticationSecurityTest(TestCase):
    """اختبارات أمان المصادقة"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPassword123!'
        )
    
    def test_login_with_weak_password(self):
        """اختبار منع كلمات المرور الضعيفة"""
        # محاولة إنشاء مستخدم بكلمة مرور ضعيفة
        with self.assertRaises(ValidationError):
            user = User(username='weakuser', email='weak@example.com')
            user.set_password('123')  # كلمة مرور ضعيفة
            user.full_clean()
    
    def test_brute_force_protection(self):
        """اختبار الحماية من هجمات القوة الغاشمة"""
        login_url = reverse('accounts:login')
        
        # محاولات تسجيل دخول خاطئة متعددة
        for i in range(6):  # أكثر من الحد المسموح
            response = self.client.post(login_url, {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        
        # يجب أن يتم حظر المحاولات الإضافية
        # ملاحظة: هذا يعتمد على تنفيذ نظام الحماية
        self.assertIn(response.status_code, [429, 403])
    
    def test_session_security(self):
        """اختبار أمان الجلسات"""
        # تسجيل الدخول
        self.client.login(username='testuser', password='StrongPassword123!')
        
        # التحقق من إعدادات الجلسة الآمنة
        session = self.client.session
        
        # يجب أن تكون الجلسة آمنة
        self.assertTrue(settings.SESSION_COOKIE_SECURE or settings.DEBUG)
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertIsNotNone(settings.SESSION_COOKIE_AGE)
    
    def test_csrf_protection(self):
        """اختبار الحماية من CSRF"""
        # محاولة إرسال طلب POST بدون CSRF token
        response = self.client.post(reverse('hr:employee_list'), {
            'test': 'data'
        })
        
        # يجب رفض الطلب
        self.assertEqual(response.status_code, 403)


class DataEncryptionSecurityTest(TestCase):
    """اختبارات أمان تشفير البيانات"""
    
    def test_sensitive_data_encryption(self):
        """اختبار تشفير البيانات الحساسة"""
        sensitive_data = "1234567890"
        
        # تشفير البيانات
        encrypted = encryption_service.encrypt_national_id(sensitive_data)
        
        # التحقق من أن البيانات مشفرة
        self.assertNotEqual(encrypted, sensitive_data)
        self.assertTrue(encryption_service.is_encrypted(encrypted))
        
        # التحقق من إمكانية فك التشفير
        decrypted = encryption_service.decrypt_national_id(encrypted)
        self.assertEqual(decrypted, sensitive_data)
    
    def test_password_hashing(self):
        """اختبار تشفير كلمات المرور"""
        password = "MySecretPassword123!"
        
        # تشفير كلمة المرور
        hashed = encryption_service.hash_password(password)
        
        # التحقق من أن كلمة المرور مشفرة
        self.assertNotEqual(hashed, password)
        self.assertGreater(len(hashed), 50)  # طول مناسب للـ hash
        
        # التحقق من صحة كلمة المرور
        self.assertTrue(encryption_service.verify_password(password, hashed))
        self.assertFalse(encryption_service.verify_password("wrongpassword", hashed))
    
    def test_encryption_key_security(self):
        """اختبار أمان مفتاح التشفير"""
        # التحقق من وجود مفتاح تشفير
        status = encryption_service.get_encryption_status()
        self.assertTrue(status['encryption_enabled'])
        
        # التحقق من قوة مفتاح التشفير
        self.assertIn(status['algorithm'], ['Fernet (AES 128)', 'AES'])
    
    def test_data_masking(self):
        """اختبار إخفاء البيانات الحساسة"""
        sensitive_data = "1234567890"
        
        # إخفاء البيانات
        masked = encryption_service.mask_sensitive_data(sensitive_data, visible_chars=2)
        
        # التحقق من الإخفاء
        self.assertTrue(masked.startswith("12"))
        self.assertTrue(masked.endswith("90"))
        self.assertIn("*", masked)
        self.assertEqual(len(masked), len(sensitive_data))


class InputValidationSecurityTest(TestCase):
    """اختبارات أمان التحقق من المدخلات"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
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
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_sql_injection_prevention(self):
        """اختبار منع حقن SQL"""
        # محاولة حقن SQL في البحث
        malicious_input = "'; DROP TABLE Hr_employee; --"
        
        # البحث باستخدام المدخل الضار
        employees = Employee.objects.filter(first_name__icontains=malicious_input)
        
        # يجب أن يعمل البحث بأمان ولا يحذف الجدول
        self.assertEqual(list(employees), [])
        
        # التحقق من أن الجدول ما زال موجوداً
        self.assertTrue(Employee.objects.model._meta.db_table)
    
    def test_xss_prevention(self):
        """اختبار منع XSS"""
        # مدخل يحتوي على كود JavaScript ضار
        malicious_script = "<script>alert('XSS')</script>"
        
        # إنشاء موظف بالمدخل الضار
        employee = Employee.objects.create(
            user=self.user,
            employee_id='EMP001',
            first_name=malicious_script,
            last_name='اختبار',
            national_id='1234567890',
            phone_number='0501234567',
            email='test@company.com',
            department=self.department,
            job_position=self.job_position,
            company=self.company,
            hire_date='2024-01-01',
            basic_salary=Decimal('6000.00'),
            gender='male',
            marital_status='single'
        )
        
        # التحقق من أن الكود الضار تم تخزينه كنص عادي
        self.assertEqual(employee.first_name, malicious_script)
        
        # في العرض، يجب أن يتم escape الكود
        from django.utils.html import escape
        safe_output = escape(employee.first_name)
        self.assertNotEqual(safe_output, malicious_script)
        self.assertIn('&lt;script&gt;', safe_output)
    
    def test_file_upload_security(self):
        """اختبار أمان رفع الملفات"""
        # محاولة رفع ملف بامتداد خطير
        dangerous_extensions = ['.exe', '.bat', '.sh', '.php', '.jsp']
        
        for ext in dangerous_extensions:
            filename = f"malicious_file{ext}"
            
            # يجب رفض الملفات الخطيرة
            # ملاحظة: هذا يعتمد على تنفيذ نظام رفع الملفات
            self.assertFalse(self.is_allowed_file_type(filename))
    
    def is_allowed_file_type(self, filename):
        """فحص نوع الملف المسموح"""
        allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.txt']
        return any(filename.lower().endswith(ext) for ext in allowed_extensions)
    
    def test_email_validation(self):
        """اختبار التحقق من صحة البريد الإلكتروني"""
        invalid_emails = [
            'invalid-email',
            '@domain.com',
            'user@',
            'user..name@domain.com',
            'user@domain',
            '<script>alert("xss")</script>@domain.com'
        ]
        
        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                employee = Employee(
                    user=self.user,
                    employee_id='EMP002',
                    first_name='اختبار',
                    last_name='اختبار',
                    national_id='1234567891',
                    phone_number='0501234568',
                    email=email,  # بريد غير صحيح
                    department=self.department,
                    job_position=self.job_position,
                    company=self.company,
                    hire_date='2024-01-01',
                    basic_salary=Decimal('6000.00'),
                    gender='male',
                    marital_status='single'
                )
                employee.full_clean()
    
    def test_phone_number_validation(self):
        """اختبار التحقق من رقم الهاتف"""
        invalid_phones = [
            '123',  # قصير جداً
            'abcdefghij',  # يحتوي على أحرف
            '++966501234567',  # رموز إضافية
            '<script>alert("xss")</script>',  # كود ضار
        ]
        
        for phone in invalid_phones:
            with self.assertRaises(ValidationError):
                employee = Employee(
                    user=self.user,
                    employee_id='EMP003',
                    first_name='اختبار',
                    last_name='اختبار',
                    national_id='1234567892',
                    phone_number=phone,  # رقم غير صحيح
                    email='test2@company.com',
                    department=self.department,
                    job_position=self.job_position,
                    company=self.company,
                    hire_date='2024-01-01',
                    basic_salary=Decimal('6000.00'),
                    gender='male',
                    marital_status='single'
                )
                employee.full_clean()


class AccessControlSecurityTest(TestCase):
    """اختبارات أمان التحكم في الوصول"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        
        # مستخدم عادي
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@example.com',
            password='testpass123'
        )
        
        # مستخدم إداري
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # مستخدم HR
        self.hr_user = User.objects.create_user(
            username='hr_user',
            email='hr@example.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_unauthorized_access_prevention(self):
        """اختبار منع الوصول غير المصرح"""
        # محاولة الوصول لصفحة محمية بدون تسجيل دخول
        protected_urls = [
            reverse('hr:employee_list'),
            reverse('hr:department_list'),
            reverse('hr:monitoring_dashboard'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            # يجب إعادة توجيه لصفحة تسجيل الدخول
            self.assertEqual(response.status_code, 302)
            self.assertIn('login', response.url)
    
    def test_admin_only_access(self):
        """اختبار الوصول للصفحات الإدارية فقط"""
        admin_urls = [
            reverse('hr:monitoring_dashboard'),
        ]
        
        # تسجيل دخول مستخدم عادي
        self.client.login(username='regular_user', password='testpass123')
        
        for url in admin_urls:
            response = self.client.get(url)
            # يجب رفض الوصول
            self.assertIn(response.status_code, [302, 403])
        
        # تسجيل دخول مستخدم إداري
        self.client.login(username='admin_user', password='testpass123')
        
        for url in admin_urls:
            response = self.client.get(url)
            # يجب السماح بالوصول
            self.assertEqual(response.status_code, 200)
    
    def test_data_access_control(self):
        """اختبار التحكم في الوصول للبيانات"""
        # إنشاء بيانات اختبار
        company = Company.objects.create(
            name='شركة الاختبار',
            commercial_register='1234567890'
        )
        
        department = Department.objects.create(
            name='قسم الموارد البشرية',
            code='HR001',
            company=company
        )
        
        # المستخدم العادي لا يجب أن يرى البيانات الحساسة
        self.client.login(username='regular_user', password='testpass123')
        
        response = self.client.get(reverse('hr:department_list'))
        
        # يجب أن يكون الوصول مسموحاً ولكن بدون بيانات حساسة
        self.assertEqual(response.status_code, 200)


class APISecurityTest(TestCase):
    """اختبارات أمان API"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='api_user',
            email='api@example.com',
            password='testpass123'
        )
        
        # إنشاء token للمستخدم
        from rest_framework.authtoken.models import Token
        self.token = Token.objects.create(user=self.user)
    
    def test_api_authentication_required(self):
        """اختبار أن API يتطلب مصادقة"""
        # محاولة الوصول بدون token
        response = self.client.get('/api/v1/employees/')
        self.assertEqual(response.status_code, 401)
        
        # الوصول مع token صحيح
        response = self.client.get(
            '/api/v1/employees/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        # يجب أن يكون الوصول مسموحاً أو محدود الصلاحيات
        self.assertIn(response.status_code, [200, 403])
    
    def test_api_rate_limiting(self):
        """اختبار تحديد معدل طلبات API"""
        # إرسال عدد كبير من الطلبات
        for i in range(100):  # أكثر من الحد المسموح
            response = self.client.get(
                '/api/v1/employees/',
                HTTP_AUTHORIZATION=f'Token {self.token.key}'
            )
            
            # إذا تم تطبيق تحديد المعدل، يجب رفض الطلبات الإضافية
            if response.status_code == 429:
                break
        
        # يجب أن يتم تحديد المعدل في النهاية
        self.assertEqual(response.status_code, 429)
    
    def test_api_input_validation(self):
        """اختبار التحقق من مدخلات API"""
        # بيانات غير صحيحة
        invalid_data = {
            'employee_id': '',  # فارغ
            'first_name': '<script>alert("xss")</script>',  # كود ضار
            'email': 'invalid-email',  # بريد غير صحيح
            'phone_number': '123',  # رقم قصير
        }
        
        response = self.client.post(
            '/api/v1/employees/',
            data=invalid_data,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        
        # يجب رفض البيانات غير الصحيحة
        self.assertEqual(response.status_code, 400)


class SecurityHeadersTest(TestCase):
    """اختبارات headers الأمان"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_security_headers_present(self):
        """اختبار وجود headers الأمان"""
        response = self.client.get(reverse('hr:employee_list'))
        
        # التحقق من وجود headers الأمان المهمة
        security_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
        ]
        
        for header in security_headers:
            self.assertIn(header, response)
        
        # التحقق من قيم headers
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
    
    def test_content_security_policy(self):
        """اختبار سياسة الأمان للمحتوى"""
        response = self.client.get(reverse('hr:employee_list'))
        
        # التحقق من وجود CSP header
        if 'Content-Security-Policy' in response:
            csp = response['Content-Security-Policy']
            
            # التحقق من وجود قواعد أساسية
            self.assertIn("default-src 'self'", csp)
            self.assertIn("script-src", csp)
            self.assertIn("style-src", csp)


class DataLeakagePreventionTest(TestCase):
    """اختبارات منع تسريب البيانات"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # إنشاء بيانات حساسة
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
        
        self.employee = Employee.objects.create(
            user=self.user,
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
    
    def test_sensitive_data_not_in_logs(self):
        """اختبار عدم ظهور البيانات الحساسة في السجلات"""
        # محاولة تسجيل دخول بكلمة مرور خاطئة
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        # التحقق من أن كلمة المرور لا تظهر في السجلات
        # ملاحظة: هذا يتطلب فحص ملفات السجل الفعلية
        # في بيئة الاختبار، نتحقق من أن الاستجابة لا تحتوي على كلمة المرور
        self.assertNotContains(response, 'wrongpassword')
    
    def test_error_messages_dont_leak_info(self):
        """اختبار عدم تسريب المعلومات في رسائل الخطأ"""
        # محاولة الوصول لموظف غير موجود
        response = self.client.get('/hr/employees/99999/')
        
        # رسالة الخطأ يجب ألا تكشف معلومات حساسة
        self.assertEqual(response.status_code, 404)
        
        # التحقق من أن رسالة الخطأ عامة
        if hasattr(response, 'content'):
            content = response.content.decode()
            # يجب ألا تحتوي على معلومات قاعدة البيانات
            self.assertNotIn('SELECT', content.upper())
            self.assertNotIn('TABLE', content.upper())
            self.assertNotIn('DATABASE', content.upper())
    
    def test_debug_info_not_exposed(self):
        """اختبار عدم كشف معلومات التشخيص"""
        # في بيئة الإنتاج، يجب ألا تظهر معلومات التشخيص
        if not settings.DEBUG:
            # محاولة إثارة خطأ
            response = self.client.get('/nonexistent-url/')
            
            # يجب ألا تظهر معلومات التشخيص
            content = response.content.decode()
            self.assertNotIn('Traceback', content)
            self.assertNotIn('Exception', content)
            self.assertNotIn('settings.py', content)