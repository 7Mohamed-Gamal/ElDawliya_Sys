"""
اختبارات استهلاك الذاكرة والموارد
Memory usage and resource consumption tests
"""
import gc
import psutil
import os
import time
import threading
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from django.db import connection
import logging

# تعطيل السجلات أثناء الاختبارات
logging.disable(logging.CRITICAL)


class MemoryUsageTests(TestCase):
    """اختبارات استهلاك الذاكرة"""

    def setUp(self):
        """إعداد الاختبار"""
        # تنظيف الذاكرة قبل البدء
        gc.collect()
        cache.clear()

        # إنشاء مستخدم للاختبار
        self.user = User.objects.create_user(
            username='memtest_user',
            password='testpass123',
            email='memtest@example.com'
        )
        self.client = Client()
        self.client.login(username='memtest_user', password='testpass123')

        # الحصول على معرف العملية
        self.process = psutil.Process(os.getpid())

    def get_memory_usage(self):
        """الحصول على استهلاك الذاكرة الحالي"""
        memory_info = self.process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': self.process.memory_percent(),
            'available': psutil.virtual_memory().available / 1024 / 1024  # MB
        }

    def test_page_memory_usage(self):
        """اختبار استهلاك الذاكرة للصفحات"""
        # قياس الذاكرة قبل البدء
        initial_memory = self.get_memory_usage()

        # قائمة الصفحات للاختبار
        pages_to_test = [
            ('administrator:dashboard', 'الصفحة الرئيسية'),
            ('Hr:employee_list', 'قائمة الموظفين'),
            ('inventory:product_list', 'قائمة المنتجات'),
        ]

        memory_usage_per_page = []

        for url_name, page_name in pages_to_test:
            try:
                # تنظيف الذاكرة قبل كل صفحة
                gc.collect()

                # قياس الذاكرة قبل تحميل الصفحة
                before_memory = self.get_memory_usage()

                # تحميل الصفحة
                response = self.client.get(reverse(url_name))

                # قياس الذاكرة بعد تحميل الصفحة
                after_memory = self.get_memory_usage()

                memory_diff = after_memory['rss'] - before_memory['rss']

                memory_usage_per_page.append({
                    'page': page_name,
                    'url_name': url_name,
                    'memory_before': before_memory['rss'],
                    'memory_after': after_memory['rss'],
                    'memory_diff': memory_diff,
                    'status_code': response.status_code
                })

            except Exception as e:
                print(f"⚠️  تعذر اختبار {page_name}: {str(e)}")
                continue

        # قياس الذاكرة النهائية
        final_memory = self.get_memory_usage()
        total_memory_increase = final_memory['rss'] - initial_memory['rss']

        # طباعة النتائج
        print(f"\n📊 تحليل استهلاك الذاكرة:")
        print(f"   الذاكرة الأولية: {initial_memory['rss']:.2f} MB")
        print(f"   الذاكرة النهائية: {final_memory['rss']:.2f} MB")
        print(f"   الزيادة الإجمالية: {total_memory_increase:.2f} MB")
        print(f"   النسبة المئوية للذاكرة: {final_memory['percent']:.2f}%")
        print(f"   الذاكرة المتاحة: {final_memory['available']:.2f} MB")

        print(f"\n📄 استهلاك الذاكرة لكل صفحة:")
        for usage in memory_usage_per_page:
            print(f"   {usage['page']}: {usage['memory_diff']:+.2f} MB")

        # التحقق من عدم وجود تسريب ذاكرة كبير
        self.assertLess(total_memory_increase, 100,
                       f"زيادة كبيرة في استهلاك الذاكرة: {total_memory_increase:.2f} MB")

        # التحقق من أن استهلاك الذاكرة لكل صفحة معقول
        for usage in memory_usage_per_page:
            self.assertLess(abs(usage['memory_diff']), 50,
                           f"استهلاك ذاكرة مفرط لصفحة {usage['page']}: {usage['memory_diff']:.2f} MB")

    def test_repeated_requests_memory_leak(self):
        """اختبار تسريب الذاكرة في الطلبات المتكررة"""
        # قياس الذاكرة الأولية
        initial_memory = self.get_memory_usage()

        # تنفيذ طلبات متكررة
        url = reverse('administrator:dashboard') if self.url_exists('administrator:dashboard') else '/'
        memory_measurements = []

        for i in range(20):
            # تنفيذ الطلب
            response = self.client.get(url)

            # قياس الذاكرة كل 5 طلبات
            if i % 5 == 0:
                gc.collect()  # تنظيف الذاكرة
                memory = self.get_memory_usage()
                memory_measurements.append({
                    'iteration': i,
                    'memory': memory['rss'],
                    'memory_increase': memory['rss'] - initial_memory['rss']
                })

        # تحليل النتائج
        print(f"\n📊 تحليل تسريب الذاكرة:")
        print(f"   الذاكرة الأولية: {initial_memory['rss']:.2f} MB")

        for measurement in memory_measurements:
            print(f"   التكرار {measurement['iteration']}: "
                  f"{measurement['memory']:.2f} MB "
                  f"(+{measurement['memory_increase']:+.2f} MB)")

        # التحقق من عدم وجود تسريب ذاكرة كبير
        final_increase = memory_measurements[-1]['memory_increase']
        self.assertLess(final_increase, 50,
                       f"تسريب ذاكرة محتمل: {final_increase:.2f} MB")

        # التحقق من أن الزيادة في الذاكرة ليست خطية (مما يشير لتسريب)
        increases = [m['memory_increase'] for m in memory_measurements]
        if len(increases) >= 3:
            # إذا كانت الزيادة مستمرة، فقد يكون هناك تسريب
            increasing_trend = all(increases[i] <= increases[i+1] for i in range(len(increases)-1))
            if increasing_trend and final_increase > 20:
                self.fail(f"تسريب ذاكرة محتمل - زيادة مستمرة: {increases}")

    def test_concurrent_requests_memory_usage(self):
        """اختبار استهلاك الذاكرة مع الطلبات المتزامنة"""
        initial_memory = self.get_memory_usage()

        def make_requests(thread_id, request_count=10):
            """تنفيذ طلبات في خيط منفصل"""
            client = Client()
            client.login(username='memtest_user', password='testpass123')

            url = reverse('administrator:dashboard') if self.url_exists('administrator:dashboard') else '/'

            for i in range(request_count):
                try:
                    response = client.get(url)
                except Exception as e:
                    print(f"خطأ في الخيط {thread_id}: {str(e)}")

        # تشغيل خيوط متعددة
        threads = []
        thread_count = 5

        for i in range(thread_count):
            thread = threading.Thread(target=make_requests, args=(i, 5))
            threads.append(thread)
            thread.start()

        # انتظار انتهاء جميع الخيوط
        for thread in threads:
            thread.join()

        # تنظيف الذاكرة وقياسها
        gc.collect()
        final_memory = self.get_memory_usage()
        memory_increase = final_memory['rss'] - initial_memory['rss']

        print(f"\n📊 استهلاك الذاكرة مع الطلبات المتزامنة:")
        print(f"   عدد الخيوط: {thread_count}")
        print(f"   الطلبات لكل خيط: 5")
        print(f"   إجمالي الطلبات: {thread_count * 5}")
        print(f"   الذاكرة الأولية: {initial_memory['rss']:.2f} MB")
        print(f"   الذاكرة النهائية: {final_memory['rss']:.2f} MB")
        print(f"   الزيادة: {memory_increase:+.2f} MB")

        # التحقق من أن الزيادة في الذاكرة معقولة
        self.assertLess(memory_increase, 100,
                       f"زيادة مفرطة في الذاكرة مع الطلبات المتزامنة: {memory_increase:.2f} MB")

    def test_database_connection_memory(self):
        """اختبار استهلاك الذاكرة لاتصالات قاعدة البيانات"""
        initial_memory = self.get_memory_usage()

        # تنفيذ استعلامات متعددة
        for i in range(50):
            try:
                # استعلام بسيط
                list(User.objects.all().select_related()  # TODO: Add appropriate select_related fields[:10])

                # إغلاق الاتصالات القديمة
                if i % 10 == 0:
                    connection.close()

            except Exception as e:
                print(f"خطأ في الاستعلام {i}: {str(e)}")

        # تنظيف وقياس الذاكرة
        connection.close()
        gc.collect()
        final_memory = self.get_memory_usage()
        memory_increase = final_memory['rss'] - initial_memory['rss']

        print(f"\n📊 استهلاك الذاكرة لاتصالات قاعدة البيانات:")
        print(f"   عدد الاستعلامات: 50")
        print(f"   الذاكرة الأولية: {initial_memory['rss']:.2f} MB")
        print(f"   الذاكرة النهائية: {final_memory['rss']:.2f} MB")
        print(f"   الزيادة: {memory_increase:+.2f} MB")

        # التحقق من عدم وجود تسريب في اتصالات قاعدة البيانات
        self.assertLess(memory_increase, 30,
                       f"تسريب محتمل في اتصالات قاعدة البيانات: {memory_increase:.2f} MB")

    def url_exists(self, url_name):
        """فحص وجود URL"""
        try:
            reverse(url_name)
            return True
        except:
            return False

    def tearDown(self):
        """تنظيف بعد كل اختبار"""
        # إغلاق اتصالات قاعدة البيانات
        connection.close()

        # تنظيف التخزين المؤقت
        cache.clear()

        # تنظيف الذاكرة
        gc.collect()

        # حذف المستخدم
        if hasattr(self, 'user'):
            self.user.delete()

    @classmethod
    def tearDownClass(cls):
        """tearDownClass function"""
        super().tearDownClass()
        # إعادة تفعيل السجلات
        logging.disable(logging.NOTSET)


class ResourceMonitoringTests(TestCase):
    """اختبارات مراقبة الموارد"""

    def setUp(self):
        """setUp function"""
        self.process = psutil.Process(os.getpid())

    def test_cpu_usage_monitoring(self):
        """اختبار مراقبة استهلاك المعالج"""
        # قياس استهلاك المعالج قبل البدء
        initial_cpu = self.process.cpu_percent()

        # تنفيذ عمليات تستهلك المعالج
        client = Client()
        user = User.objects.create_user(
            username='cpu_test_user',
            password='testpass123',
            email='cputest@example.com'
        )
        client.login(username='cpu_test_user', password='testpass123')

        start_time = time.time()

        # تنفيذ طلبات متعددة
        for i in range(20):
            try:
                url = reverse('administrator:dashboard') if self.url_exists('administrator:dashboard') else '/'
                response = client.get(url)
            except Exception as e:
                print(f"خطأ في الطلب {i}: {str(e)}")

        end_time = time.time()

        # قياس استهلاك المعالج بعد العمليات
        final_cpu = self.process.cpu_percent()

        # معلومات النظام
        cpu_count = psutil.cpu_count()
        system_cpu = psutil.cpu_percent(interval=1)

        print(f"\n📊 مراقبة استهلاك المعالج:")
        print(f"   عدد المعالجات: {cpu_count}")
        print(f"   استهلاك المعالج للنظام: {system_cpu:.2f}%")
        print(f"   استهلاك المعالج للعملية (قبل): {initial_cpu:.2f}%")
        print(f"   استهلاك المعالج للعملية (بعد): {final_cpu:.2f}%")
        print(f"   وقت التنفيذ: {end_time - start_time:.2f}s")
        print(f"   الطلبات في الثانية: {20 / (end_time - start_time):.2f}")

        # تنظيف
        user.delete()

        # التحقق من أن استهلاك المعالج معقول
        self.assertLess(final_cpu, 80, f"استهلاك مفرط للمعالج: {final_cpu:.2f}%")

    def test_disk_io_monitoring(self):
        """اختبار مراقبة عمليات القرص"""
        # قياس عمليات القرص قبل البدء
        initial_io = psutil.disk_io_counters()

        # تنفيذ عمليات تتطلب قراءة/كتابة القرص
        client = Client()
        user = User.objects.create_user(
            username='io_test_user',
            password='testpass123',
            email='iotest@example.com'
        )
        client.login(username='io_test_user', password='testpass123')

        # تنفيذ عمليات قاعدة البيانات
        for i in range(10):
            try:
                # إنشاء وحذف مستخدمين (عمليات كتابة)
                temp_user = User.objects.create_user(
                    username=f'temp_user_{i}',
                    password='temppass',
                    email=f'temp{i}@example.com'
                )
                temp_user.delete()

                # قراءة البيانات
                list(User.objects.all().select_related()  # TODO: Add appropriate select_related fields[:5])

            except Exception as e:
                print(f"خطأ في عملية القرص {i}: {str(e)}")

        # قياس عمليات القرص بعد العمليات
        final_io = psutil.disk_io_counters()

        if initial_io and final_io:
            read_bytes = final_io.read_bytes - initial_io.read_bytes
            write_bytes = final_io.write_bytes - initial_io.write_bytes
            read_count = final_io.read_count - initial_io.read_count
            write_count = final_io.write_count - initial_io.write_count

            print(f"\n📊 مراقبة عمليات القرص:")
            print(f"   البايتات المقروءة: {read_bytes / 1024:.2f} KB")
            print(f"   البايتات المكتوبة: {write_bytes / 1024:.2f} KB")
            print(f"   عمليات القراءة: {read_count}")
            print(f"   عمليات الكتابة: {write_count}")

            # التحقق من أن عمليات القرص معقولة
            self.assertLess(read_bytes / 1024 / 1024, 100,
                           f"قراءة مفرطة من القرص: {read_bytes / 1024 / 1024:.2f} MB")
            self.assertLess(write_bytes / 1024 / 1024, 100,
                           f"كتابة مفرطة على القرص: {write_bytes / 1024 / 1024:.2f} MB")

        # تنظيف
        user.delete()

    def url_exists(self, url_name):
        """فحص وجود URL"""
        try:
            reverse(url_name)
            return True
        except:
            return False
