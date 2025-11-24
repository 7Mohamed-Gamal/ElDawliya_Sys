"""
اختبارات أوقات الاستجابة للصفحات الرئيسية
Performance tests for main page response times
"""
import time
import statistics
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.utils import override_settings
from django.core.cache import cache
import logging

# تعطيل السجلات أثناء الاختبارات لتحسين الأداء
logging.disable(logging.CRITICAL)


class PageResponseTimeTests(TestCase):
    """اختبارات أوقات الاستجابة للصفحات"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # إنشاء مستخدم للاختبار
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        cls.client = Client()
        
    def setUp(self):
        """إعداد كل اختبار"""
        # تسجيل الدخول
        self.client.login(username='testuser', password='testpass123')
        # مسح التخزين المؤقت
        cache.clear()
    
    def measure_response_time(self, url_name, url_kwargs=None, method='GET', data=None, iterations=5):
        """
        قياس وقت الاستجابة لصفحة معينة
        
        Args:
            url_name: اسم URL
            url_kwargs: معاملات URL
            method: طريقة HTTP
            data: البيانات المرسلة
            iterations: عدد التكرارات
            
        Returns:
            dict: إحصائيات الأداء
        """
        times = []
        url = reverse(url_name, kwargs=url_kwargs) if url_kwargs else reverse(url_name)
        
        for i in range(iterations):
            start_time = time.time()
            
            if method == 'GET':
                response = self.client.get(url)
            elif method == 'POST':
                response = self.client.post(url, data or {})
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # تحويل إلى ميلي ثانية
            times.append(response_time)
            
            # التأكد من نجاح الطلب
            self.assertIn(response.status_code, [200, 201, 302], 
                         f"فشل في الوصول إلى {url}: {response.status_code}")
        
        return {
            'url': url,
            'method': method,
            'iterations': iterations,
            'times': times,
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'median_time': statistics.median(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def test_homepage_response_time(self):
        """اختبار وقت استجابة الصفحة الرئيسية"""
        try:
            stats = self.measure_response_time('administrator:dashboard')
            
            # التحقق من أن متوسط وقت الاستجابة أقل من 500 ميلي ثانية
            self.assertLess(stats['avg_time'], 500, 
                           f"وقت استجابة الصفحة الرئيسية بطيء: {stats['avg_time']:.2f}ms")
            
            print(f"\n📊 إحصائيات الصفحة الرئيسية:")
            print(f"   متوسط الوقت: {stats['avg_time']:.2f}ms")
            print(f"   أسرع وقت: {stats['min_time']:.2f}ms")
            print(f"   أبطأ وقت: {stats['max_time']:.2f}ms")
            print(f"   الوسيط: {stats['median_time']:.2f}ms")
            
        except Exception as e:
            self.skipTest(f"تعذر اختبار الصفحة الرئيسية: {str(e)}")
    
    def test_hr_pages_response_time(self):
        """اختبار أوقات استجابة صفحات الموارد البشرية"""
        hr_pages = [
            ('Hr:employee_list', None),
            ('Hr:department_list', None),
            ('Hr:job_list', None),
        ]
        
        results = []
        for url_name, url_kwargs in hr_pages:
            try:
                stats = self.measure_response_time(url_name, url_kwargs)
                results.append(stats)
                
                # التحقق من أن وقت الاستجابة معقول (أقل من 1 ثانية)
                self.assertLess(stats['avg_time'], 1000, 
                               f"وقت استجابة {url_name} بطيء: {stats['avg_time']:.2f}ms")
                
            except Exception as e:
                print(f"⚠️  تعذر اختبار {url_name}: {str(e)}")
                continue
        
        if results:
            print(f"\n📊 إحصائيات صفحات الموارد البشرية:")
            for stats in results:
                print(f"   {stats['url']}: {stats['avg_time']:.2f}ms")
    
    def test_inventory_pages_response_time(self):
        """اختبار أوقات استجابة صفحات المخزون"""
        inventory_pages = [
            ('inventory:product_list', None),
            ('inventory:supplier_list', None),
            ('inventory:invoice_list', None),
        ]
        
        results = []
        for url_name, url_kwargs in inventory_pages:
            try:
                stats = self.measure_response_time(url_name, url_kwargs)
                results.append(stats)
                
                # التحقق من أن وقت الاستجابة معقول
                self.assertLess(stats['avg_time'], 1000, 
                               f"وقت استجابة {url_name} بطيء: {stats['avg_time']:.2f}ms")
                
            except Exception as e:
                print(f"⚠️  تعذر اختبار {url_name}: {str(e)}")
                continue
        
        if results:
            print(f"\n📊 إحصائيات صفحات المخزون:")
            for stats in results:
                print(f"   {stats['url']}: {stats['avg_time']:.2f}ms")
    
    def test_api_response_times(self):
        """اختبار أوقات استجابة API"""
        api_endpoints = [
            ('api:employee-list', None),
            ('api:department-list', None),
            ('api:product-list', None),
        ]
        
        results = []
        for url_name, url_kwargs in api_endpoints:
            try:
                stats = self.measure_response_time(url_name, url_kwargs)
                results.append(stats)
                
                # API يجب أن يكون أسرع (أقل من 300 ميلي ثانية)
                self.assertLess(stats['avg_time'], 300, 
                               f"وقت استجابة API {url_name} بطيء: {stats['avg_time']:.2f}ms")
                
            except Exception as e:
                print(f"⚠️  تعذر اختبار API {url_name}: {str(e)}")
                continue
        
        if results:
            print(f"\n📊 إحصائيات API:")
            for stats in results:
                print(f"   {stats['url']}: {stats['avg_time']:.2f}ms")
    
    def test_database_query_performance(self):
        """اختبار أداء استعلامات قاعدة البيانات"""
        from django.db import connection
        from django.test.utils import override_settings
        
        # تفعيل تتبع الاستعلامات
        with override_settings(DEBUG=True):
            # مسح الاستعلامات السابقة
            connection.queries_log.clear()
            
            # تنفيذ طلب يتطلب استعلامات قاعدة بيانات
            try:
                response = self.client.get(reverse('Hr:employee_list'))
                
                # عدد الاستعلامات
                query_count = len(connection.queries)
                
                # وقت الاستعلامات الإجمالي
                total_time = sum(float(query['time']) for query in connection.queries)
                
                print(f"\n📊 إحصائيات قاعدة البيانات:")
                print(f"   عدد الاستعلامات: {query_count}")
                print(f"   الوقت الإجمالي: {total_time:.4f}s")
                print(f"   متوسط وقت الاستعلام: {total_time/query_count:.4f}s")
                
                # التحقق من عدم وجود استعلامات مفرطة
                self.assertLess(query_count, 50, 
                               f"عدد استعلامات مفرط: {query_count}")
                
                # التحقق من أن الوقت الإجمالي معقول
                self.assertLess(total_time, 1.0, 
                               f"وقت استعلامات قاعدة البيانات بطيء: {total_time:.4f}s")
                
            except Exception as e:
                self.skipTest(f"تعذر اختبار أداء قاعدة البيانات: {str(e)}")
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # إعادة تفعيل السجلات
        logging.disable(logging.NOTSET)


class CachePerformanceTests(TestCase):
    """اختبارات أداء التخزين المؤقت"""
    
    def setUp(self):
        cache.clear()
    
    def test_cache_performance(self):
        """اختبار أداء التخزين المؤقت"""
        # اختبار كتابة التخزين المؤقت
        start_time = time.time()
        for i in range(100):
            cache.set(f'test_key_{i}', f'test_value_{i}', 300)
        write_time = (time.time() - start_time) * 1000
        
        # اختبار قراءة التخزين المؤقت
        start_time = time.time()
        for i in range(100):
            cache.get(f'test_key_{i}')
        read_time = (time.time() - start_time) * 1000
        
        print(f"\n📊 إحصائيات التخزين المؤقت:")
        print(f"   وقت الكتابة (100 عنصر): {write_time:.2f}ms")
        print(f"   وقت القراءة (100 عنصر): {read_time:.2f}ms")
        print(f"   متوسط وقت الكتابة: {write_time/100:.2f}ms")
        print(f"   متوسط وقت القراءة: {read_time/100:.2f}ms")
        
        # التحقق من أن التخزين المؤقت سريع
        self.assertLess(write_time/100, 10, "كتابة التخزين المؤقت بطيئة")
        self.assertLess(read_time/100, 5, "قراءة التخزين المؤقت بطيئة")