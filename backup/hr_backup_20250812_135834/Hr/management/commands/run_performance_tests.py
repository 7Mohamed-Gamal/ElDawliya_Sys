"""
أمر تشغيل اختبارات الأداء والحمولة
"""

from django.core.management.base import BaseCommand
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.db import connection, transaction
from Hr.models import Employee, Department, JobPosition, Company
from Hr.services.performance_service import performance_service
from Hr.services.query_optimizer import query_optimizer
from decimal import Decimal
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import json


class Command(BaseCommand):
    help = 'تشغيل اختبارات الأداء والحمولة الشاملة'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-type',
            choices=['database', 'api', 'concurrent', 'memory', 'all'],
            default='all',
            help='نوع الاختبار المراد تشغيله'
        )
        
        parser.add_argument(
            '--duration',
            type=int,
            default=60,
            help='مدة الاختبار بالثواني (افتراضي: 60)'
        )
        
        parser.add_argument(
            '--concurrent-users',
            type=int,
            default=10,
            help='عدد المستخدمين المتزامنين (افتراضي: 10)'
        )
        
        parser.add_argument(
            '--base-url',
            default='http://localhost:8000',
            help='رابط الخادم للاختبار'
        )
        
        parser.add_argument(
            '--output-file',
            help='ملف حفظ النتائج (JSON)'
        )

    def handle(self, *args, **options):
        test_type = options['test_type']
        duration = options['duration']
        concurrent_users = options['concurrent_users']
        base_url = options['base_url']
        output_file = options['output_file']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'بدء اختبارات الأداء:\n'
                f'  - نوع الاختبار: {test_type}\n'
                f'  - المدة: {duration} ثانية\n'
                f'  - المستخدمين المتزامنين: {concurrent_users}\n'
                f'  - رابط الخادم: {base_url}'
            )
        )
        
        results = {}
        
        if test_type in ['database', 'all']:
            results['database'] = self.run_database_performance_tests()
        
        if test_type in ['api', 'all']:
            results['api'] = self.run_api_performance_tests(base_url, duration)
        
        if test_type in ['concurrent', 'all']:
            results['concurrent'] = self.run_concurrent_tests(
                base_url, concurrent_users, duration
            )
        
        if test_type in ['memory', 'all']:
            results['memory'] = self.run_memory_tests()
        
        # عرض النتائج
        self.display_results(results)
        
        # حفظ النتائج في ملف
        if output_file:
            self.save_results(results, output_file)

    def run_database_performance_tests(self):
        """تشغيل اختبارات أداء قاعدة البيانات"""
        self.stdout.write('تشغيل اختبارات أداء قاعدة البيانات...')
        
        results = {}
        
        # اختبار استعلامات الموظفين
        results['employee_queries'] = self.test_employee_queries()
        
        # اختبار الاستعلامات المعقدة
        results['complex_queries'] = self.test_complex_queries()
        
        # اختبار العمليات المجمعة
        results['bulk_operations'] = self.test_bulk_operations()
        
        # اختبار التخزين المؤقت
        results['caching'] = self.test_caching_performance()
        
        return results

    def test_employee_queries(self):
        """اختبار استعلامات الموظفين"""
        results = {}
        
        # اختبار الاستعلام البسيط
        start_time = time.time()
        employees = list(Employee.objects.all()[:100])
        results['simple_query'] = {
            'time': time.time() - start_time,
            'count': len(employees)
        }
        
        # اختبار الاستعلام المحسن
        start_time = time.time()
        optimized_employees = list(
            query_optimizer.optimize_employee_queries()[:100]
        )
        results['optimized_query'] = {
            'time': time.time() - start_time,
            'count': len(optimized_employees)
        }
        
        # اختبار البحث
        start_time = time.time()
        search_results = list(
            Employee.objects.filter(first_name__icontains='أحمد')[:50]
        )
        results['search_query'] = {
            'time': time.time() - start_time,
            'count': len(search_results)
        }
        
        return results

    def test_complex_queries(self):
        """اختبار الاستعلامات المعقدة"""
        results = {}
        
        # استعلام مع joins متعددة
        start_time = time.time()
        complex_data = list(
            Employee.objects.select_related(
                'department', 'job_position', 'company'
            ).prefetch_related(
                'employee_documents'
            ).filter(
                is_active=True,
                department__is_active=True
            )[:50]
        )
        results['complex_joins'] = {
            'time': time.time() - start_time,
            'count': len(complex_data)
        }
        
        # استعلام مع تجميع
        start_time = time.time()
        aggregated_data = list(
            Employee.objects.values('department__name').annotate(
                employee_count=models.Count('id'),
                avg_salary=models.Avg('basic_salary')
            ).order_by('-employee_count')
        )
        results['aggregation'] = {
            'time': time.time() - start_time,
            'count': len(aggregated_data)
        }
        
        return results

    def test_bulk_operations(self):
        """اختبار العمليات المجمعة"""
        results = {}
        
        # إنشاء بيانات اختبار
        test_users = []
        for i in range(100):
            test_users.append(User(
                username=f'bulk_test_{i}',
                email=f'bulk_test_{i}@example.com'
            ))
        
        # اختبار الإنشاء المجمع
        start_time = time.time()
        with transaction.atomic():
            created_users = User.objects.bulk_create(test_users)
        results['bulk_create'] = {
            'time': time.time() - start_time,
            'count': len(created_users)
        }
        
        # اختبار التحديث المجمع
        for user in created_users:
            user.first_name = f'Updated_{user.username}'
        
        start_time = time.time()
        with transaction.atomic():
            User.objects.bulk_update(created_users, ['first_name'])
        results['bulk_update'] = {
            'time': time.time() - start_time,
            'count': len(created_users)
        }
        
        # تنظيف البيانات
        User.objects.filter(username__startswith='bulk_test_').delete()
        
        return results

    def test_caching_performance(self):
        """اختبار أداء التخزين المؤقت"""
        results = {}
        
        def expensive_operation():
            return Employee.objects.count()
        
        # اختبار بدون تخزين مؤقت
        start_time = time.time()
        result1 = expensive_operation()
        results['without_cache'] = time.time() - start_time
        
        # اختبار مع التخزين المؤقت
        start_time = time.time()
        result2 = performance_service.get_cached_data(
            'test_cache_key', expensive_operation, timeout=60
        )
        results['first_cache_call'] = time.time() - start_time
        
        # اختبار الحصول من التخزين المؤقت
        start_time = time.time()
        result3 = performance_service.get_cached_data(
            'test_cache_key', expensive_operation, timeout=60
        )
        results['cached_call'] = time.time() - start_time
        
        results['cache_improvement'] = (
            results['without_cache'] / results['cached_call']
            if results['cached_call'] > 0 else 0
        )
        
        return results

    def run_api_performance_tests(self, base_url, duration):
        """تشغيل اختبارات أداء API"""
        self.stdout.write('تشغيل اختبارات أداء API...')
        
        results = {}
        
        # إنشاء مستخدم للاختبار
        test_user = self.create_test_user()
        token = self.get_api_token(test_user)
        
        if not token:
            return {'error': 'فشل في الحصول على token للاختبار'}
        
        # اختبار endpoints مختلفة
        endpoints = [
            '/api/v1/employees/',
            '/api/v1/departments/',
            '/api/v1/job-positions/',
        ]
        
        for endpoint in endpoints:
            endpoint_results = self.test_api_endpoint(
                base_url + endpoint, token, duration // len(endpoints)
            )
            results[endpoint] = endpoint_results
        
        return results

    def test_api_endpoint(self, url, token, duration):
        """اختبار endpoint محدد"""
        headers = {'Authorization': f'Token {token}'}
        
        start_time = time.time()
        request_count = 0
        response_times = []
        errors = 0
        
        while time.time() - start_time < duration:
            try:
                request_start = time.time()
                response = requests.get(url, headers=headers, timeout=10)
                request_time = time.time() - request_start
                
                response_times.append(request_time)
                request_count += 1
                
                if response.status_code >= 400:
                    errors += 1
                
            except Exception as e:
                errors += 1
            
            time.sleep(0.1)  # فترة راحة قصيرة
        
        total_time = time.time() - start_time
        
        return {
            'total_requests': request_count,
            'total_time': total_time,
            'requests_per_second': request_count / total_time if total_time > 0 else 0,
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'errors': errors,
            'error_rate': (errors / request_count * 100) if request_count > 0 else 0
        }

    def run_concurrent_tests(self, base_url, concurrent_users, duration):
        """تشغيل اختبارات التزامن"""
        self.stdout.write(f'تشغيل اختبارات التزامن مع {concurrent_users} مستخدم...')
        
        # إنشاء مستخدمين للاختبار
        test_users = []
        for i in range(concurrent_users):
            user = self.create_test_user(f'concurrent_user_{i}')
            token = self.get_api_token(user)
            if token:
                test_users.append(token)
        
        if not test_users:
            return {'error': 'فشل في إنشاء مستخدمين للاختبار'}
        
        results = []
        
        def user_simulation(token):
            """محاكاة نشاط مستخدم"""
            headers = {'Authorization': f'Token {token}'}
            user_results = {
                'requests': 0,
                'errors': 0,
                'response_times': []
            }
            
            start_time = time.time()
            
            while time.time() - start_time < duration:
                try:
                    # طلبات متنوعة
                    endpoints = [
                        '/api/v1/employees/',
                        '/api/v1/departments/',
                    ]
                    
                    for endpoint in endpoints:
                        request_start = time.time()
                        response = requests.get(
                            base_url + endpoint,
                            headers=headers,
                            timeout=10
                        )
                        request_time = time.time() - request_start
                        
                        user_results['requests'] += 1
                        user_results['response_times'].append(request_time)
                        
                        if response.status_code >= 400:
                            user_results['errors'] += 1
                        
                        time.sleep(0.5)  # فترة راحة بين الطلبات
                
                except Exception as e:
                    user_results['errors'] += 1
            
            return user_results
        
        # تشغيل المحاكاة بشكل متزامن
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [
                executor.submit(user_simulation, token)
                for token in test_users
            ]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'خطأ في محاكاة المستخدم: {e}')
                    )
        
        # تجميع النتائج
        total_requests = sum(r['requests'] for r in results)
        total_errors = sum(r['errors'] for r in results)
        all_response_times = []
        for r in results:
            all_response_times.extend(r['response_times'])
        
        return {
            'concurrent_users': len(results),
            'total_requests': total_requests,
            'total_errors': total_errors,
            'error_rate': (total_errors / total_requests * 100) if total_requests > 0 else 0,
            'avg_response_time': statistics.mean(all_response_times) if all_response_times else 0,
            'requests_per_second': total_requests / duration if duration > 0 else 0,
            'successful_users': len([r for r in results if r['errors'] == 0])
        }

    def run_memory_tests(self):
        """تشغيل اختبارات الذاكرة"""
        self.stdout.write('تشغيل اختبارات الذاكرة...')
        
        try:
            import psutil
            process = psutil.Process()
        except ImportError:
            return {'error': 'psutil غير متاح لاختبار الذاكرة'}
        
        results = {}
        
        # قياس الذاكرة الأولية
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # اختبار تحميل بيانات كبيرة
        start_memory = process.memory_info().rss / 1024 / 1024
        large_dataset = list(Employee.objects.all())
        peak_memory = process.memory_info().rss / 1024 / 1024
        
        results['large_dataset_load'] = {
            'initial_memory_mb': start_memory,
            'peak_memory_mb': peak_memory,
            'memory_increase_mb': peak_memory - start_memory,
            'records_loaded': len(large_dataset)
        }
        
        # تنظيف
        del large_dataset
        
        # اختبار استخدام iterator
        start_memory = process.memory_info().rss / 1024 / 1024
        processed_count = 0
        for employee in Employee.objects.iterator(chunk_size=100):
            processed_count += 1
            if processed_count >= 1000:  # حد للاختبار
                break
        
        iterator_memory = process.memory_info().rss / 1024 / 1024
        
        results['iterator_usage'] = {
            'start_memory_mb': start_memory,
            'end_memory_mb': iterator_memory,
            'memory_increase_mb': iterator_memory - start_memory,
            'records_processed': processed_count
        }
        
        return results

    def create_test_user(self, username='test_performance_user'):
        """إنشاء مستخدم للاختبار"""
        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'is_active': True
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            return user
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'فشل في إنشاء مستخدم الاختبار: {e}')
            )
            return None

    def get_api_token(self, user):
        """الحصول على API token للمستخدم"""
        try:
            from rest_framework.authtoken.models import Token
            token, created = Token.objects.get_or_create(user=user)
            return token.key
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'فشل في الحصول على token: {e}')
            )
            return None

    def display_results(self, results):
        """عرض نتائج الاختبارات"""
        self.stdout.write(
            self.style.SUCCESS('\n=== نتائج اختبارات الأداء ===')
        )
        
        for test_type, test_results in results.items():
            self.stdout.write(f'\n{test_type.upper()}:')
            
            if isinstance(test_results, dict):
                if 'error' in test_results:
                    self.stdout.write(
                        self.style.ERROR(f'  خطأ: {test_results["error"]}')
                    )
                else:
                    self.display_dict_results(test_results, indent=2)
            else:
                self.stdout.write(f'  {test_results}')

    def display_dict_results(self, data, indent=0):
        """عرض النتائج من نوع dictionary"""
        prefix = '  ' * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                self.stdout.write(f'{prefix}{key}:')
                self.display_dict_results(value, indent + 1)
            elif isinstance(value, float):
                self.stdout.write(f'{prefix}{key}: {value:.3f}')
            else:
                self.stdout.write(f'{prefix}{key}: {value}')

    def save_results(self, results, output_file):
        """حفظ النتائج في ملف JSON"""
        try:
            # تحويل النتائج لتنسيق قابل للتسلسل
            serializable_results = self.make_serializable(results)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, ensure_ascii=False, indent=2)
            
            self.stdout.write(
                self.style.SUCCESS(f'تم حفظ النتائج في: {output_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'فشل في حفظ النتائج: {e}')
            )

    def make_serializable(self, obj):
        """تحويل الكائن لتنسيق قابل للتسلسل"""
        if isinstance(obj, dict):
            return {key: self.make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.make_serializable(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)