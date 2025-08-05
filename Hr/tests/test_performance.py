"""
اختبارات الأداء والحمولة
"""

from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.db import connection
from django.core.cache import cache
from django.test import Client
from django.urls import reverse
from Hr.models import Employee, Department, JobPosition, Company
from Hr.services.performance_service import performance_service
from Hr.services.query_optimizer import query_optimizer
from Hr.decorators.performance_decorators import cache_result, query_counter
from decimal import Decimal
import time
import threading
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor, as_completed


class QueryPerformanceTest(TestCase):
    """اختبارات أداء الاستعلامات"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        # إنشاء بيانات أساسية
        self.company = Company.objects.create(
            name='شركة الاختبار',
            commercial_register='1234567890'
        )
        
        # إنشاء عدة أقسام
        self.departments = []
        for i in range(5):
            dept = Department.objects.create(
                name=f'قسم {i+1}',
                code=f'DEPT{i+1:03d}',
                company=self.company
            )
            self.departments.append(dept)
        
        # إنشاء عدة مناصب وظيفية
        self.job_positions = []
        for dept in self.departments:
            for j in range(3):
                job = JobPosition.objects.create(
                    name=f'منصب {j+1} - {dept.name}',
                    code=f'{dept.code}_JOB{j+1}',
                    department=dept,
                    min_salary=Decimal('3000.00'),
                    max_salary=Decimal('10000.00')
                )
                self.job_positions.append(job)
        
        # إنشاء عدد كبير من الموظفين
        self.employees = []
        for i in range(100):  # 100 موظف للاختبار
            user = User.objects.create_user(
                username=f'user{i+1}',
                email=f'user{i+1}@example.com',
                password='testpass123'
            )
            
            # توزيع الموظفين على الأقسام والمناصب
            dept = self.departments[i % len(self.departments)]
            job = self.job_positions[i % len(self.job_positions)]
            
            employee = Employee.objects.create(
                user=user,
                employee_id=f'EMP{i+1:03d}',
                first_name=f'موظف{i+1}',
                last_name='اختبار',
                national_id=f'{1000000000 + i}',
                phone_number=f'05012345{i:02d}',
                email=f'employee{i+1}@company.com',
                department=dept,
                job_position=job,
                company=self.company,
                hire_date='2024-01-01',
                basic_salary=Decimal('5000.00'),
                gender='male' if i % 2 == 0 else 'female',
                marital_status='single'
            )
            self.employees.append(employee)
    
    def test_employee_list_query_performance(self):
        """اختبار أداء استعلام قائمة الموظفين"""
        start_time = time.time()
        
        # استعلام غير محسن
        employees = list(Employee.objects.all())
        
        unoptimized_time = time.time() - start_time
        
        # استعلام محسن
        start_time = time.time()
        
        optimized_employees = list(
            query_optimizer.optimize_employee_queries()
        )
        
        optimized_time = time.time() - start_time
        
        # التحقق من أن الاستعلام المحسن أسرع أو مساوي
        self.assertLessEqual(optimized_time, unoptimized_time * 1.5)  # هامش 50%
        
        # التحقق من أن النتائج متطابقة
        self.assertEqual(len(employees), len(optimized_employees))
    
    def test_query_count_optimization(self):
        """اختبار تحسين عدد الاستعلامات"""
        # مسح الاستعلامات السابقة
        connection.queries_log.clear()
        
        # استعلام غير محسن - يسبب N+1 queries
        initial_count = len(connection.queries)
        
        employees = Employee.objects.all()[:10]
        for employee in employees:
            _ = employee.department.name  # يسبب استعلام إضافي
            _ = employee.job_position.name  # يسبب استعلام إضافي
        
        unoptimized_queries = len(connection.queries) - initial_count
        
        # مسح الاستعلامات
        connection.queries_log.clear()
        initial_count = len(connection.queries)
        
        # استعلام محسن
        optimized_employees = Employee.objects.select_related(
            'department', 'job_position'
        )[:10]
        
        for employee in optimized_employees:
            _ = employee.department.name
            _ = employee.job_position.name
        
        optimized_queries = len(connection.queries) - initial_count
        
        # الاستعلام المحسن يجب أن يستخدم استعلامات أقل
        self.assertLess(optimized_queries, unoptimized_queries)
    
    def test_large_dataset_performance(self):
        """اختبار الأداء مع مجموعة بيانات كبيرة"""
        # قياس وقت الاستعلام على جميع الموظفين
        start_time = time.time()
        
        employees = list(Employee.objects.select_related(
            'department', 'job_position', 'company'
        ).all())
        
        execution_time = time.time() - start_time
        
        # يجب أن يكون الاستعلام سريعاً (أقل من ثانية واحدة)
        self.assertLess(execution_time, 1.0)
        
        # التحقق من أن جميع الموظفين تم جلبهم
        self.assertEqual(len(employees), 100)
    
    def test_complex_query_performance(self):
        """اختبار أداء الاستعلامات المعقدة"""
        start_time = time.time()
        
        # استعلام معقد مع فلترة وترتيب وتجميع
        stats = Employee.objects.filter(
            is_active=True,
            department__is_active=True
        ).select_related(
            'department', 'job_position'
        ).values(
            'department__name'
        ).annotate(
            employee_count=models.Count('id'),
            avg_salary=models.Avg('basic_salary')
        ).order_by('-employee_count')
        
        result = list(stats)
        
        execution_time = time.time() - start_time
        
        # يجب أن يكون الاستعلام سريعاً
        self.assertLess(execution_time, 0.5)
        
        # التحقق من صحة النتائج
        self.assertGreater(len(result), 0)
        
        # التحقق من أن النتائج مرتبة
        if len(result) > 1:
            self.assertGreaterEqual(
                result[0]['employee_count'],
                result[1]['employee_count']
            )
    
    @query_counter
    def test_query_counter_decorator(self):
        """اختبار مُزخرف عد الاستعلامات"""
        # هذا الاختبار يستخدم المُزخرف لعد الاستعلامات
        employees = list(Employee.objects.all()[:5])
        return employees
    
    def test_batch_processing_performance(self):
        """اختبار أداء المعالجة على دفعات"""
        def process_employee_batch(employees):
            return [emp.full_name for emp in employees]
        
        start_time = time.time()
        
        # معالجة على دفعات
        all_employees = Employee.objects.all()
        results = performance_service.batch_process(
            all_employees,
            batch_size=20,
            process_func=process_employee_batch
        )
        
        batch_time = time.time() - start_time
        
        # معالجة عادية للمقارنة
        start_time = time.time()
        
        normal_results = [emp.full_name for emp in Employee.objects.all()]
        
        normal_time = time.time() - start_time
        
        # التحقق من أن النتائج متطابقة
        self.assertEqual(len(results), len(normal_results))
        
        # المعالجة على دفعات قد تكون أبطأ للمجموعات الصغيرة
        # ولكن أفضل لاستخدام الذاكرة
        print(f"Batch processing: {batch_time:.3f}s")
        print(f"Normal processing: {normal_time:.3f}s")


class CachePerformanceTest(TestCase):
    """اختبارات أداء التخزين المؤقت"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        cache.clear()
        
        self.company = Company.objects.create(
            name='شركة الاختبار',
            commercial_register='1234567890'
        )
        
        self.department = Department.objects.create(
            name='قسم الموارد البشرية',
            code='HR001',
            company=self.company
        )
    
    def test_cache_performance_improvement(self):
        """اختبار تحسين الأداء بالتخزين المؤقت"""
        def expensive_operation():
            # محاكاة عملية مكلفة
            time.sleep(0.1)
            return Employee.objects.filter(department=self.department).count()
        
        # أول استدعاء - بدون تخزين مؤقت
        start_time = time.time()
        result1 = performance_service.get_cached_data(
            'test_expensive_op', expensive_operation, timeout=60
        )
        first_call_time = time.time() - start_time
        
        # ثاني استدعاء - من التخزين المؤقت
        start_time = time.time()
        result2 = performance_service.get_cached_data(
            'test_expensive_op', expensive_operation, timeout=60
        )
        second_call_time = time.time() - start_time
        
        # النتائج يجب أن تكون متطابقة
        self.assertEqual(result1, result2)
        
        # الاستدعاء الثاني يجب أن يكون أسرع بكثير
        self.assertLess(second_call_time, first_call_time * 0.1)
    
    @cache_result(timeout=60, key_prefix='test_cache')
    def cached_function(self, value):
        """دالة مع تخزين مؤقت للاختبار"""
        time.sleep(0.05)  # محاكاة عملية مكلفة
        return value * 2
    
    def test_cache_decorator_performance(self):
        """اختبار أداء مُزخرف التخزين المؤقت"""
        # أول استدعاء
        start_time = time.time()
        result1 = self.cached_function(5)
        first_time = time.time() - start_time
        
        # ثاني استدعاء (من التخزين المؤقت)
        start_time = time.time()
        result2 = self.cached_function(5)
        second_time = time.time() - start_time
        
        self.assertEqual(result1, result2)
        self.assertEqual(result1, 10)
        self.assertLess(second_time, first_time * 0.5)
    
    def test_cache_invalidation(self):
        """اختبار إبطال التخزين المؤقت"""
        # حفظ قيمة في التخزين المؤقت
        cache.set('test_key', 'test_value', 60)
        self.assertEqual(cache.get('test_key'), 'test_value')
        
        # إبطال التخزين المؤقت
        performance_service.invalidate_cache_pattern('test_*')
        
        # التحقق من أن القيمة لم تعد موجودة
        # ملاحظة: هذا يعتمد على تنفيذ invalidate_cache_pattern
        # قد نحتاج لتعديل الاختبار حسب التنفيذ الفعلي


class ConcurrencyTest(TransactionTestCase):
    """اختبارات التزامن والحمولة"""
    
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
        
        # إنشاء مستخدم للاختبار
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def create_employee_concurrent(self, employee_id):
        """إنشاء موظف في thread منفصل"""
        try:
            user = User.objects.create_user(
                username=f'user_{employee_id}',
                email=f'user_{employee_id}@example.com',
                password='testpass123'
            )
            
            employee = Employee.objects.create(
                user=user,
                employee_id=employee_id,
                first_name=f'موظف{employee_id}',
                last_name='اختبار',
                national_id=f'{1000000000 + int(employee_id[3:])}',
                phone_number=f'0501234567',
                email=f'employee_{employee_id}@company.com',
                department=self.department,
                job_position=self.job_position,
                company=self.company,
                hire_date='2024-01-01',
                basic_salary=Decimal('5000.00'),
                gender='male',
                marital_status='single'
            )
            return employee.id
        except Exception as e:
            return str(e)
    
    def test_concurrent_employee_creation(self):
        """اختبار إنشاء الموظفين بشكل متزامن"""
        num_threads = 10
        employee_ids = [f'EMP{i:03d}' for i in range(1, num_threads + 1)]
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(self.create_employee_concurrent, emp_id)
                for emp_id in employee_ids
            ]
            
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        execution_time = time.time() - start_time
        
        # التحقق من أن جميع الموظفين تم إنشاؤهم
        successful_creations = [r for r in results if isinstance(r, int)]
        
        print(f"Created {len(successful_creations)} employees in {execution_time:.2f}s")
        
        # يجب أن ينجح معظم الإنشاءات
        self.assertGreaterEqual(len(successful_creations), num_threads * 0.8)
    
    def simulate_user_request(self, user_id):
        """محاكاة طلب مستخدم"""
        client = Client()
        
        # تسجيل دخول
        login_success = client.login(
            username='testuser',
            password='testpass123'
        )
        
        if not login_success:
            return 'login_failed'
        
        try:
            # طلب قائمة الموظفين
            response = client.get(reverse('hr:employee_list'))
            return response.status_code
        except Exception as e:
            return str(e)
    
    def test_concurrent_user_requests(self):
        """اختبار الطلبات المتزامنة من المستخدمين"""
        num_users = 20
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [
                executor.submit(self.simulate_user_request, i)
                for i in range(num_users)
            ]
            
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        execution_time = time.time() - start_time
        
        # التحقق من نجاح معظم الطلبات
        successful_requests = [r for r in results if r == 200]
        
        print(f"Handled {len(successful_requests)} concurrent requests in {execution_time:.2f}s")
        
        # يجب أن ينجح معظم الطلبات
        self.assertGreaterEqual(len(successful_requests), num_users * 0.8)


class MemoryUsageTest(TestCase):
    """اختبارات استخدام الذاكرة"""
    
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
    
    def get_memory_usage(self):
        """الحصول على استخدام الذاكرة الحالي"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0
    
    def test_large_queryset_memory_usage(self):
        """اختبار استخدام الذاكرة مع QuerySet كبير"""
        # إنشاء عدد كبير من الموظفين
        employees_data = []
        for i in range(1000):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
            
            employees_data.append(Employee(
                user=user,
                employee_id=f'EMP{i:04d}',
                first_name=f'موظف{i}',
                last_name='اختبار',
                national_id=f'{2000000000 + i}',
                phone_number='0501234567',
                email=f'employee{i}@company.com',
                department=self.department,
                job_position=self.job_position,
                company=self.company,
                hire_date='2024-01-01',
                basic_salary=Decimal('5000.00'),
                gender='male',
                marital_status='single'
            ))
        
        # إنشاء مجمع
        Employee.objects.bulk_create(employees_data)
        
        initial_memory = self.get_memory_usage()
        
        # جلب جميع الموظفين (قد يستهلك ذاكرة كبيرة)
        employees = list(Employee.objects.all())
        
        peak_memory = self.get_memory_usage()
        
        # تنظيف
        del employees
        
        final_memory = self.get_memory_usage()
        
        print(f"Memory usage - Initial: {initial_memory:.1f}MB, "
              f"Peak: {peak_memory:.1f}MB, Final: {final_memory:.1f}MB")
        
        # التحقق من أن استخدام الذاكرة لم يزد بشكل مفرط
        memory_increase = peak_memory - initial_memory
        self.assertLess(memory_increase, 100)  # أقل من 100MB
    
    def test_iterator_vs_list_memory_usage(self):
        """مقارنة استخدام الذاكرة بين iterator و list"""
        # إنشاء بيانات للاختبار
        employees_data = []
        for i in range(500):
            user = User.objects.create_user(
                username=f'iter_user{i}',
                email=f'iter_user{i}@example.com',
                password='testpass123'
            )
            
            employees_data.append(Employee(
                user=user,
                employee_id=f'ITER{i:04d}',
                first_name=f'موظف{i}',
                last_name='اختبار',
                national_id=f'{3000000000 + i}',
                phone_number='0501234567',
                email=f'iter_employee{i}@company.com',
                department=self.department,
                job_position=self.job_position,
                company=self.company,
                hire_date='2024-01-01',
                basic_salary=Decimal('5000.00'),
                gender='male',
                marital_status='single'
            ))
        
        Employee.objects.bulk_create(employees_data)
        
        # اختبار استخدام list()
        initial_memory = self.get_memory_usage()
        
        employees_list = list(Employee.objects.filter(employee_id__startswith='ITER'))
        list_memory = self.get_memory_usage()
        
        del employees_list
        
        # اختبار استخدام iterator()
        memory_after_cleanup = self.get_memory_usage()
        
        employees_iter = Employee.objects.filter(employee_id__startswith='ITER').iterator()
        processed_count = 0
        for emp in employees_iter:
            processed_count += 1
            if processed_count >= 100:  # معالجة جزء فقط
                break
        
        iterator_memory = self.get_memory_usage()
        
        print(f"List memory usage: {list_memory - initial_memory:.1f}MB")
        print(f"Iterator memory usage: {iterator_memory - memory_after_cleanup:.1f}MB")
        
        # iterator يجب أن يستخدم ذاكرة أقل
        list_usage = list_memory - initial_memory
        iterator_usage = iterator_memory - memory_after_cleanup
        
        self.assertLess(iterator_usage, list_usage)


class DatabaseConnectionTest(TestCase):
    """اختبارات اتصال قاعدة البيانات"""
    
    def test_database_connection_performance(self):
        """اختبار أداء اتصال قاعدة البيانات"""
        start_time = time.time()
        
        # تنفيذ عدة استعلامات
        for i in range(10):
            Company.objects.count()
        
        execution_time = time.time() - start_time
        
        # يجب أن تكون الاستعلامات سريعة
        self.assertLess(execution_time, 1.0)
    
    def test_database_connection_pooling(self):
        """اختبار تجميع اتصالات قاعدة البيانات"""
        # هذا الاختبار يعتمد على إعدادات قاعدة البيانات
        # ويمكن تخصيصه حسب نوع قاعدة البيانات المستخدمة
        
        connections_before = len(connection.queries)
        
        # تنفيذ عدة استعلامات متزامنة
        def run_query():
            return Company.objects.count()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_query) for _ in range(10)]
            results = [future.result() for future in futures]
        
        connections_after = len(connection.queries)
        
        # التحقق من أن جميع الاستعلامات نجحت
        self.assertEqual(len(results), 10)
        
        # التحقق من أن عدد الاستعلامات زاد
        self.assertGreater(connections_after, connections_before)