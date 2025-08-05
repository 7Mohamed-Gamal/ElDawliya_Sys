"""
اختبارات الخدمات
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from Hr.models import Employee, Department, JobPosition, Company
from Hr.services.employee_service import employee_service
from Hr.services.encryption_service import encryption_service
from Hr.services.performance_service import performance_service
from Hr.services.monitoring_service import monitoring_service
from Hr.services.query_optimizer import query_optimizer
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json


class EmployeeServiceTest(TestCase):
    """اختبارات خدمة الموظفين"""
    
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
        
        self.employee_data = {
            'user': self.user,
            'employee_id': 'EMP001',
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'national_id': '1234567890',
            'phone_number': '0501234567',
            'email': 'ahmed@company.com',
            'department': self.department,
            'job_position': self.job_position,
            'company': self.company,
            'hire_date': '2024-01-01',
            'basic_salary': Decimal('6000.00'),
            'gender': 'male',
            'marital_status': 'single'
        }
    
    def test_create_employee(self):
        """اختبار إنشاء موظف عبر الخدمة"""
        employee = employee_service.create_employee(self.employee_data)
        
        self.assertIsInstance(employee, Employee)
        self.assertEqual(employee.employee_id, self.employee_data['employee_id'])
        self.assertEqual(employee.first_name, self.employee_data['first_name'])
        self.assertTrue(employee.is_active)
    
    def test_get_employee_by_id(self):
        """اختبار الحصول على موظف بالرقم"""
        employee = Employee.objects.create(**self.employee_data)
        
        found_employee = employee_service.get_employee_by_id(employee.employee_id)
        
        self.assertEqual(found_employee, employee)
    
    def test_get_employee_by_id_not_found(self):
        """اختبار البحث عن موظف غير موجود"""
        result = employee_service.get_employee_by_id('NONEXISTENT')
        self.assertIsNone(result)
    
    def test_update_employee(self):
        """اختبار تحديث بيانات الموظف"""
        employee = Employee.objects.create(**self.employee_data)
        
        update_data = {
            'first_name': 'محمد',
            'basic_salary': Decimal('7000.00')
        }
        
        updated_employee = employee_service.update_employee(employee.id, update_data)
        
        self.assertEqual(updated_employee.first_name, 'محمد')
        self.assertEqual(updated_employee.basic_salary, Decimal('7000.00'))
    
    def test_deactivate_employee(self):
        """اختبار إلغاء تفعيل الموظف"""
        employee = Employee.objects.create(**self.employee_data)
        
        deactivated = employee_service.deactivate_employee(employee.id)
        
        self.assertFalse(deactivated.is_active)
        self.assertIsNotNone(deactivated.termination_date)
    
    def test_get_employees_by_department(self):
        """اختبار الحصول على موظفي قسم معين"""
        employee1 = Employee.objects.create(**self.employee_data)
        
        # إنشاء موظف آخر في قسم مختلف
        other_dept = Department.objects.create(
            name='قسم آخر',
            code='OTHER001',
            company=self.company
        )
        
        other_employee_data = self.employee_data.copy()
        other_employee_data['employee_id'] = 'EMP002'
        other_employee_data['department'] = other_dept
        other_employee_data['user'] = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        employee2 = Employee.objects.create(**other_employee_data)
        
        # الحصول على موظفي القسم الأول
        dept_employees = employee_service.get_employees_by_department(self.department.id)
        
        self.assertIn(employee1, dept_employees)
        self.assertNotIn(employee2, dept_employees)
    
    def test_calculate_employee_age(self):
        """اختبار حساب عمر الموظف"""
        employee_data = self.employee_data.copy()
        employee_data['birth_date'] = '1990-01-01'
        
        employee = Employee.objects.create(**employee_data)
        age = employee_service.calculate_age(employee)
        
        self.assertIsInstance(age, int)
        self.assertGreater(age, 0)
    
    def test_calculate_years_of_service(self):
        """اختبار حساب سنوات الخدمة"""
        employee = Employee.objects.create(**self.employee_data)
        years = employee_service.calculate_years_of_service(employee)
        
        self.assertIsInstance(years, int)
        self.assertGreaterEqual(years, 0)
    
    def test_search_employees(self):
        """اختبار البحث في الموظفين"""
        employee = Employee.objects.create(**self.employee_data)
        
        # البحث بالاسم
        results = employee_service.search_employees('أحمد')
        self.assertIn(employee, results)
        
        # البحث برقم الموظف
        results = employee_service.search_employees('EMP001')
        self.assertIn(employee, results)
        
        # البحث بنص غير موجود
        results = employee_service.search_employees('غير موجود')
        self.assertEqual(len(results), 0)
    
    def test_get_employee_statistics(self):
        """اختبار الحصول على إحصائيات الموظفين"""
        Employee.objects.create(**self.employee_data)
        
        stats = employee_service.get_employee_statistics()
        
        self.assertIn('total_employees', stats)
        self.assertIn('active_employees', stats)
        self.assertIn('by_department', stats)
        self.assertIn('by_gender', stats)
        
        self.assertEqual(stats['total_employees'], 1)
        self.assertEqual(stats['active_employees'], 1)


class EncryptionServiceTest(TestCase):
    """اختبارات خدمة التشفير"""
    
    def test_encrypt_decrypt_text(self):
        """اختبار تشفير وفك تشفير النص"""
        original_text = "نص سري للاختبار"
        
        encrypted = encryption_service.encrypt_text(original_text)
        self.assertNotEqual(encrypted, original_text)
        
        decrypted = encryption_service.decrypt_text(encrypted)
        self.assertEqual(decrypted, original_text)
    
    def test_encrypt_decrypt_national_id(self):
        """اختبار تشفير وفك تشفير رقم الهوية"""
        national_id = "1234567890"
        
        encrypted = encryption_service.encrypt_national_id(national_id)
        self.assertNotEqual(encrypted, national_id)
        
        decrypted = encryption_service.decrypt_national_id(encrypted)
        self.assertEqual(decrypted, national_id)
    
    def test_encrypt_decrypt_phone_number(self):
        """اختبار تشفير وفك تشفير رقم الهاتف"""
        phone = "0501234567"
        
        encrypted = encryption_service.encrypt_phone_number(phone)
        self.assertNotEqual(encrypted, phone)
        
        decrypted = encryption_service.decrypt_phone_number(encrypted)
        self.assertEqual(decrypted, phone)
    
    def test_encrypt_decrypt_email(self):
        """اختبار تشفير وفك تشفير البريد الإلكتروني"""
        email = "test@example.com"
        
        encrypted = encryption_service.encrypt_email(email)
        self.assertNotEqual(encrypted, email)
        
        decrypted = encryption_service.decrypt_email(encrypted)
        self.assertEqual(decrypted, email)
    
    def test_encrypt_decrypt_salary(self):
        """اختبار تشفير وفك تشفير الراتب"""
        salary = 5000.50
        
        encrypted = encryption_service.encrypt_salary(salary)
        self.assertNotEqual(encrypted, str(salary))
        
        decrypted = encryption_service.decrypt_salary(encrypted)
        self.assertEqual(decrypted, salary)
    
    def test_hash_verify_password(self):
        """اختبار تشفير والتحقق من كلمة المرور"""
        password = "mySecretPassword123"
        
        hashed = encryption_service.hash_password(password)
        self.assertNotEqual(hashed, password)
        
        # التحقق من كلمة المرور الصحيحة
        self.assertTrue(encryption_service.verify_password(password, hashed))
        
        # التحقق من كلمة مرور خاطئة
        self.assertFalse(encryption_service.verify_password("wrongPassword", hashed))
    
    def test_is_encrypted(self):
        """اختبار التحقق من كون النص مشفراً"""
        plain_text = "نص عادي"
        encrypted_text = encryption_service.encrypt_text(plain_text)
        
        self.assertFalse(encryption_service.is_encrypted(plain_text))
        self.assertTrue(encryption_service.is_encrypted(encrypted_text))
    
    def test_mask_sensitive_data(self):
        """اختبار إخفاء البيانات الحساسة"""
        sensitive_data = "1234567890"
        
        masked = encryption_service.mask_sensitive_data(sensitive_data, visible_chars=2)
        
        self.assertTrue(masked.startswith("12"))
        self.assertTrue(masked.endswith("90"))
        self.assertIn("*", masked)
    
    def test_encrypt_sensitive_data_dict(self):
        """اختبار تشفير البيانات الحساسة في قاموس"""
        data = {
            'name': 'أحمد محمد',
            'national_id': '1234567890',
            'phone_number': '0501234567',
            'email': 'ahmed@example.com',
            'salary': 5000
        }
        
        encrypted_data = encryption_service.encrypt_sensitive_data(data)
        
        # البيانات غير الحساسة يجب أن تبقى كما هي
        self.assertEqual(encrypted_data['name'], data['name'])
        
        # البيانات الحساسة يجب أن تكون مشفرة
        self.assertNotEqual(encrypted_data['national_id'], data['national_id'])
        self.assertNotEqual(encrypted_data['phone_number'], data['phone_number'])
        self.assertNotEqual(encrypted_data['email'], data['email'])
    
    def test_empty_values_handling(self):
        """اختبار التعامل مع القيم الفارغة"""
        self.assertIsNone(encryption_service.encrypt_text(None))
        self.assertEqual(encryption_service.encrypt_text(""), "")
        
        self.assertIsNone(encryption_service.decrypt_text(None))
        self.assertEqual(encryption_service.decrypt_text(""), "")


class PerformanceServiceTest(TestCase):
    """اختبارات خدمة الأداء"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        cache.clear()  # مسح التخزين المؤقت قبل كل اختبار
    
    def test_get_cached_data(self):
        """اختبار التخزين المؤقت للبيانات"""
        def expensive_function():
            return "نتيجة مكلفة"
        
        # أول استدعاء - يجب تنفيذ الدالة
        result1 = performance_service.get_cached_data(
            'test_key', expensive_function, timeout=60
        )
        
        # ثاني استدعاء - يجب الحصول على النتيجة من التخزين المؤقت
        result2 = performance_service.get_cached_data(
            'test_key', expensive_function, timeout=60
        )
        
        self.assertEqual(result1, result2)
        self.assertEqual(result1, "نتيجة مكلفة")
    
    def test_create_cache_key(self):
        """اختبار إنشاء مفتاح التخزين المؤقت"""
        key1 = performance_service.create_cache_key('prefix', 'arg1', 'arg2')
        key2 = performance_service.create_cache_key('prefix', 'arg1', 'arg2')
        key3 = performance_service.create_cache_key('prefix', 'arg1', 'arg3')
        
        self.assertEqual(key1, key2)  # نفس المعاملات = نفس المفتاح
        self.assertNotEqual(key1, key3)  # معاملات مختلفة = مفاتيح مختلفة
    
    def test_batch_process(self):
        """اختبار المعالجة على دفعات"""
        # إنشاء قائمة من الأرقام
        numbers = list(range(1, 11))  # 1 إلى 10
        
        def process_batch(batch):
            return [x * 2 for x in batch]
        
        results = performance_service.batch_process(
            numbers, batch_size=3, process_func=process_batch
        )
        
        expected = [x * 2 for x in numbers]
        self.assertEqual(results, expected)
    
    def test_get_performance_metrics(self):
        """اختبار الحصول على مقاييس الأداء"""
        metrics = performance_service.get_performance_metrics()
        
        self.assertIn('timestamp', metrics)
        self.assertIn('database', metrics)
        self.assertIn('cache', metrics)
        self.assertIn('system', metrics)
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_system_metrics(self, mock_memory, mock_cpu):
        """اختبار مقاييس النظام"""
        # إعداد البيانات الوهمية
        mock_cpu.return_value = 50.0
        mock_memory.return_value = MagicMock(percent=60.0)
        
        metrics = performance_service.get_performance_metrics()
        
        self.assertIn('system', metrics)


class MonitoringServiceTest(TestCase):
    """اختبارات خدمة المراقبة"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        cache.clear()
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_get_system_status(self, mock_disk, mock_memory, mock_cpu):
        """اختبار الحصول على حالة النظام"""
        # إعداد البيانات الوهمية
        mock_cpu.return_value = 45.0
        mock_memory.return_value = MagicMock(
            percent=55.0,
            available=4 * 1024**3,  # 4GB
            total=8 * 1024**3       # 8GB
        )
        mock_disk.return_value = MagicMock(
            percent=70.0,
            free=100 * 1024**3,     # 100GB
            total=500 * 1024**3     # 500GB
        )
        
        status = monitoring_service.get_system_status()
        
        self.assertIn('overall_status', status)
        self.assertIn('system', status)
        self.assertIn('database', status)
        self.assertIn('application', status)
        
        # التحقق من بيانات النظام
        system_info = status['system']
        self.assertEqual(system_info['cpu']['usage_percent'], 45.0)
        self.assertEqual(system_info['memory']['usage_percent'], 55.0)
        self.assertEqual(system_info['disk']['usage_percent'], 70.0)
    
    def test_get_active_alerts(self):
        """اختبار الحصول على التنبيهات النشطة"""
        # إضافة تنبيه وهمي
        test_alert = {
            'type': 'test_alert',
            'level': 'warning',
            'message': 'تنبيه اختبار',
            'timestamp': '2024-01-01T12:00:00'
        }
        
        cache.set('active_alerts', [test_alert], 3600)
        
        alerts = monitoring_service.get_active_alerts()
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['message'], 'تنبيه اختبار')
    
    def test_save_alerts(self):
        """اختبار حفظ التنبيهات"""
        alerts = [
            {
                'type': 'cpu_high',
                'level': 'warning',
                'message': 'استخدام المعالج مرتفع',
                'timestamp': '2024-01-01T12:00:00'
            }
        ]
        
        monitoring_service.save_alerts(alerts)
        
        saved_alerts = cache.get('active_alerts', [])
        self.assertEqual(len(saved_alerts), 1)
        self.assertEqual(saved_alerts[0]['message'], 'استخدام المعالج مرتفع')
    
    def test_determine_overall_status(self):
        """اختبار تحديد الحالة العامة"""
        # حالة صحية
        healthy_status = {
            'system': {
                'cpu': {'status': 'normal'},
                'memory': {'status': 'normal'},
                'disk': {'status': 'normal'}
            },
            'database': {'status': 'normal'},
            'performance': {'status': 'normal'},
            'alerts': []
        }
        
        result = monitoring_service.determine_overall_status(healthy_status)
        self.assertEqual(result, 'healthy')
        
        # حالة تحذير
        warning_status = healthy_status.copy()
        warning_status['system']['cpu']['status'] = 'warning'
        
        result = monitoring_service.determine_overall_status(warning_status)
        self.assertEqual(result, 'warning')


class QueryOptimizerTest(TestCase):
    """اختبارات محسن الاستعلامات"""
    
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
    
    def test_optimize_employee_queries(self):
        """اختبار تحسين استعلامات الموظفين"""
        # إنشاء استعلام أساسي
        queryset = Employee.objects.all()
        
        # تحسين الاستعلام
        optimized = query_optimizer.optimize_employee_queries(queryset)
        
        # التحقق من أن الاستعلام محسن
        self.assertIn('department', str(optimized.query))
        self.assertIn('job_position', str(optimized.query))
    
    def test_get_employee_statistics(self):
        """اختبار الحصول على إحصائيات الموظفين"""
        # إنشاء موظف للاختبار
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        Employee.objects.create(
            user=user,
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
        
        stats = query_optimizer.get_employee_statistics(use_cache=False)
        
        self.assertIn('total_employees', stats)
        self.assertIn('by_department', stats)
        self.assertIn('by_job_position', stats)
        
        self.assertEqual(stats['total_employees'], 1)
        self.assertEqual(len(stats['by_department']), 1)
    
    def test_benchmark_query(self):
        """اختبار قياس أداء الاستعلام"""
        def test_query():
            return list(Employee.objects.all())
        
        result = query_optimizer.benchmark_query(test_query)
        
        self.assertIn('result', result)
        self.assertIn('execution_time', result)
        self.assertIn('is_slow', result)
        self.assertIsInstance(result['execution_time'], float)


class ServiceIntegrationTest(TestCase):
    """اختبارات التكامل بين الخدمات"""
    
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
    
    def test_employee_creation_with_encryption(self):
        """اختبار إنشاء موظف مع التشفير"""
        employee_data = {
            'user': self.user,
            'employee_id': 'EMP001',
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'national_id': '1234567890',
            'phone_number': '0501234567',
            'email': 'ahmed@company.com',
            'department': self.department,
            'job_position': self.job_position,
            'company': self.company,
            'hire_date': '2024-01-01',
            'basic_salary': Decimal('6000.00'),
            'gender': 'male',
            'marital_status': 'single'
        }
        
        # إنشاء الموظف عبر الخدمة
        employee = employee_service.create_employee(employee_data)
        
        # التحقق من أن البيانات الحساسة مشفرة
        self.assertIsNotNone(employee.national_id)
        
        # التحقق من إمكانية فك التشفير
        if encryption_service.is_encrypted(employee.national_id):
            decrypted_id = encryption_service.decrypt_national_id(employee.national_id)
            self.assertEqual(decrypted_id, '1234567890')
    
    def test_performance_monitoring_integration(self):
        """اختبار التكامل بين مراقبة الأداء والخدمات"""
        # إنشاء بيانات للاختبار
        employee_data = {
            'user': self.user,
            'employee_id': 'EMP001',
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'national_id': '1234567890',
            'phone_number': '0501234567',
            'email': 'ahmed@company.com',
            'department': self.department,
            'job_position': self.job_position,
            'company': self.company,
            'hire_date': '2024-01-01',
            'basic_salary': Decimal('6000.00'),
            'gender': 'male',
            'marital_status': 'single'
        }
        
        employee = Employee.objects.create(**employee_data)
        
        # اختبار الحصول على الإحصائيات مع مراقبة الأداء
        def get_stats():
            return employee_service.get_employee_statistics()
        
        result = query_optimizer.benchmark_query(get_stats)
        
        self.assertIn('result', result)
        self.assertIn('execution_time', result)
        self.assertIsInstance(result['result'], dict)
    
    def tearDown(self):
        """تنظيف البيانات بعد الاختبار"""
        cache.clear()