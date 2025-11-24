"""
اختبارات التحميل المتزامن للمستخدمين المتعددين
Concurrent load testing for multiple users
"""
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from django.db import transaction
import logging

# تعطيل السجلات أثناء الاختبارات
logging.disable(logging.CRITICAL)


class LoadTestingMixin:
    """خليط لاختبارات التحميل"""
    
    def create_test_users(self, count=10):
        """إنشاء مستخدمين للاختبار"""
        users = []
        for i in range(count):
            user = User.objects.create_user(
                username=f'loadtest_user_{i}',
                password='testpass123',
                email=f'loadtest{i}@example.com'
            )
            users.append(user)
        return users
    
    def simulate_user_session(self, user_id, urls, iterations=5):
        """محاكاة جلسة مستخدم"""
        client = Client()
        user = User.objects.get(id=user_id)
        client.login(username=user.username, password='testpass123')
        
        results = {
            'user_id': user_id,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_time': 0,
            'response_times': [],
            'errors': []
        }
        
        for _ in range(iterations):
            for url in urls:
                try:
                    start_time = time.time()
                    response = client.get(url)
                    end_time = time.time()
                    
                    response_time = (end_time - start_time) * 1000
                    results['response_times'].append(response_time)
                    results['total_time'] += response_time
                    results['total_requests'] += 1
                    
                    if response.status_code in [200, 201, 302]:
                        results['successful_requests'] += 1
                    else:
                        results['failed_requests'] += 1
                        results['errors'].append(f"HTTP {response.status_code} for {url}")
                        
                except Exception as e:
                    results['failed_requests'] += 1
                    results['total_requests'] += 1
                    results['errors'].append(f"Exception for {url}: {str(e)}")
        
        return results
    
    def run_concurrent_load_test(self, user_count, urls, iterations_per_user=3):
        """تشغيل اختبار تحميل متزامن"""
        # إنشاء المستخدمين
        users = self.create_test_users(user_count)
        user_ids = [user.id for user in users]
        
        # تشغيل الاختبارات المتزامنة
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=user_count) as executor:
            # إرسال المهام
            future_to_user = {
                executor.submit(self.simulate_user_session, user_id, urls, iterations_per_user): user_id
                for user_id in user_ids
            }
            
            # جمع النتائج
            for future in as_completed(future_to_user):
                user_id = future_to_user[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'user_id': user_id,
                        'total_requests': 0,
                        'successful_requests': 0,
                        'failed_requests': 1,
                        'total_time': 0,
                        'response_times': [],
                        'errors': [f"Thread exception: {str(e)}"]
                    })
        
        end_time = time.time()
        total_test_time = end_time - start_time
        
        # تحليل النتائج
        analysis = self.analyze_load_test_results(results, total_test_time)
        
        # تنظيف المستخدمين
        User.objects.filter(id__in=user_ids).delete()
        
        return analysis
    
    def analyze_load_test_results(self, results, total_test_time):
        """تحليل نتائج اختبار التحميل"""
        total_requests = sum(r['total_requests'] for r in results)
        successful_requests = sum(r['successful_requests'] for r in results)
        failed_requests = sum(r['failed_requests'] for r in results)
        
        all_response_times = []
        for r in results:
            all_response_times.extend(r['response_times'])
        
        all_errors = []
        for r in results:
            all_errors.extend(r['errors'])
        
        analysis = {
            'total_users': len(results),
            'total_test_time': total_test_time,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            'requests_per_second': total_requests / total_test_time if total_test_time > 0 else 0,
            'avg_response_time': statistics.mean(all_response_times) if all_response_times else 0,
            'min_response_time': min(all_response_times) if all_response_times else 0,
            'max_response_time': max(all_response_times) if all_response_times else 0,
            'median_response_time': statistics.median(all_response_times) if all_response_times else 0,
            'response_time_95th': self.percentile(all_response_times, 95) if all_response_times else 0,
            'errors': all_errors[:10]  # أول 10 أخطاء فقط
        }
        
        return analysis
    
    def percentile(self, data, percentile):
        """حساب النسبة المئوية"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


class ConcurrentUserTests(TestCase, LoadTestingMixin):
    """اختبارات المستخدمين المتزامنين"""
    
    def setUp(self):
        cache.clear()
    
    def test_light_load_5_users(self):
        """اختبار تحميل خفيف - 5 مستخدمين"""
        urls = [
            reverse('administrator:dashboard') if self.url_exists('administrator:dashboard') else '/',
        ]
        
        # إضافة URLs إضافية إذا كانت متاحة
        additional_urls = [
            ('Hr:employee_list', 'Hr:employee_list'),
            ('inventory:product_list', 'inventory:product_list'),
        ]
        
        for url_name, _ in additional_urls:
            if self.url_exists(url_name):
                urls.append(reverse(url_name))
        
        analysis = self.run_concurrent_load_test(
            user_count=5,
            urls=urls,
            iterations_per_user=3
        )
        
        self.print_load_test_results("تحميل خفيف (5 مستخدمين)", analysis)
        
        # التحقق من معايير الأداء
        self.assertGreaterEqual(analysis['success_rate'], 95, 
                               f"معدل النجاح منخفض: {analysis['success_rate']:.1f}%")
        self.assertLess(analysis['avg_response_time'], 1000, 
                       f"متوسط وقت الاستجابة بطيء: {analysis['avg_response_time']:.2f}ms")
    
    def test_medium_load_10_users(self):
        """اختبار تحميل متوسط - 10 مستخدمين"""
        urls = [
            reverse('administrator:dashboard') if self.url_exists('administrator:dashboard') else '/',
        ]
        
        # إضافة URLs إضافية
        additional_urls = [
            ('Hr:employee_list', 'Hr:employee_list'),
            ('inventory:product_list', 'inventory:product_list'),
        ]
        
        for url_name, _ in additional_urls:
            if self.url_exists(url_name):
                urls.append(reverse(url_name))
        
        analysis = self.run_concurrent_load_test(
            user_count=10,
            urls=urls,
            iterations_per_user=2
        )
        
        self.print_load_test_results("تحميل متوسط (10 مستخدمين)", analysis)
        
        # معايير أداء أكثر تساهلاً للتحميل المتوسط
        self.assertGreaterEqual(analysis['success_rate'], 90, 
                               f"معدل النجاح منخفض: {analysis['success_rate']:.1f}%")
        self.assertLess(analysis['avg_response_time'], 2000, 
                       f"متوسط وقت الاستجابة بطيء: {analysis['avg_response_time']:.2f}ms")
    
    def test_heavy_load_20_users(self):
        """اختبار تحميل ثقيل - 20 مستخدم"""
        urls = [
            reverse('administrator:dashboard') if self.url_exists('administrator:dashboard') else '/',
        ]
        
        analysis = self.run_concurrent_load_test(
            user_count=20,
            urls=urls,
            iterations_per_user=1
        )
        
        self.print_load_test_results("تحميل ثقيل (20 مستخدم)", analysis)
        
        # معايير أداء للتحميل الثقيل
        self.assertGreaterEqual(analysis['success_rate'], 80, 
                               f"معدل النجاح منخفض جداً: {analysis['success_rate']:.1f}%")
        self.assertLess(analysis['avg_response_time'], 5000, 
                       f"متوسط وقت الاستجابة بطيء جداً: {analysis['avg_response_time']:.2f}ms")
    
    def url_exists(self, url_name):
        """فحص وجود URL"""
        try:
            reverse(url_name)
            return True
        except:
            return False
    
    def print_load_test_results(self, test_name, analysis):
        """طباعة نتائج اختبار التحميل"""
        print(f"\n📊 نتائج {test_name}:")
        print(f"   عدد المستخدمين: {analysis['total_users']}")
        print(f"   إجمالي الطلبات: {analysis['total_requests']}")
        print(f"   الطلبات الناجحة: {analysis['successful_requests']}")
        print(f"   الطلبات الفاشلة: {analysis['failed_requests']}")
        print(f"   معدل النجاح: {analysis['success_rate']:.1f}%")
        print(f"   الطلبات في الثانية: {analysis['requests_per_second']:.2f}")
        print(f"   متوسط وقت الاستجابة: {analysis['avg_response_time']:.2f}ms")
        print(f"   أسرع استجابة: {analysis['min_response_time']:.2f}ms")
        print(f"   أبطأ استجابة: {analysis['max_response_time']:.2f}ms")
        print(f"   الوسيط: {analysis['median_response_time']:.2f}ms")
        print(f"   النسبة المئوية 95: {analysis['response_time_95th']:.2f}ms")
        print(f"   وقت الاختبار الإجمالي: {analysis['total_test_time']:.2f}s")
        
        if analysis['errors']:
            print(f"   أول الأخطاء:")
            for error in analysis['errors'][:5]:
                print(f"     - {error}")


class DatabaseLoadTests(TestCase):
    """اختبارات تحميل قاعدة البيانات"""
    
    def test_concurrent_database_operations(self):
        """اختبار العمليات المتزامنة على قاعدة البيانات"""
        def create_users_batch(batch_id, count=10):
            """إنشاء مجموعة من المستخدمين"""
            users_created = 0
            errors = []
            
            for i in range(count):
                try:
                    with transaction.atomic():
                        User.objects.create_user(
                            username=f'batch_{batch_id}_user_{i}',
                            password='testpass123',
                            email=f'batch{batch_id}user{i}@example.com'
                        )
                        users_created += 1
                except Exception as e:
                    errors.append(str(e))
            
            return {
                'batch_id': batch_id,
                'users_created': users_created,
                'errors': errors
            }
        
        # تشغيل عمليات متزامنة
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(create_users_batch, batch_id, 5)
                for batch_id in range(5)
            ]
            
            for future in as_completed(futures):
                results.append(future.result())
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # تحليل النتائج
        total_users_created = sum(r['users_created'] for r in results)
        total_errors = sum(len(r['errors']) for r in results)
        
        print(f"\n📊 نتائج اختبار تحميل قاعدة البيانات:")
        print(f"   المستخدمين المنشأين: {total_users_created}")
        print(f"   الأخطاء: {total_errors}")
        print(f"   الوقت الإجمالي: {total_time:.2f}s")
        print(f"   المستخدمين في الثانية: {total_users_created/total_time:.2f}")
        
        # تنظيف البيانات
        User.objects.filter(username__startswith='batch_').delete()
        
        # التحقق من الأداء
        self.assertGreater(total_users_created, 20, "عدد قليل من المستخدمين تم إنشاؤهم")
        self.assertLess(total_errors, 5, f"أخطاء كثيرة في قاعدة البيانات: {total_errors}")
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # إعادة تفعيل السجلات
        logging.disable(logging.NOTSET)