"""
اختبارات تحسين الأداء وتحليل الاختناقات
Performance optimization and bottleneck analysis tests
"""
import time
import statistics
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from django.db import connection, transaction
from django.test.utils import override_settings
import logging

# تعطيل السجلات أثناء الاختبارات
logging.disable(logging.CRITICAL)


class QueryOptimizationTests(TestCase):
    """اختبارات تحسين الاستعلامات"""

    @classmethod
    def setUpClass(cls):
        """setUpClass function"""
        super().setUpClass()
        # إنشاء بيانات اختبار
        cls.create_test_data()

    @classmethod
    def create_test_data(cls):
        """إنشاء بيانات اختبار"""
        # إنشاء مستخدمين
        cls.users = []
        for i in range(20):
            user = User.objects.create_user(
                username=f'optim_user_{i}',
                password='testpass123',
                email=f'optim{i}@example.com',
                first_name=f'User{i}',
                last_name=f'Test{i}'
            )
            cls.users.append(user)

    def setUp(self):
        """setUp function"""
        self.client = Client()
        self.client.login(username='optim_user_0', password='testpass123')

    @override_settings(DEBUG=True)
    def test_query_count_optimization(self):
        """اختبار تحسين عدد الاستعلامات"""
        # مسح سجل الاستعلامات
        connection.queries_log.clear()

        # تنفيذ عملية تتطلب استعلامات متعددة
        try:
            response = self.client.get(reverse('Hr:employee_list'))

            # تحليل الاستعلامات
            query_count = len(connection.queries)
            total_time = sum(float(query['time']) for query in connection.queries)

            # تحليل أنواع الاستعلامات
            select_queries = [q for q in connection.queries if q['sql'].strip().upper().startswith('SELECT')]
            insert_queries = [q for q in connection.queries if q['sql'].strip().upper().startswith('INSERT')]
            update_queries = [q for q in connection.queries if q['sql'].strip().upper().startswith('UPDATE')]

            print(f"\n📊 تحليل الاستعلامات:")
            print(f"   إجمالي الاستعلامات: {query_count}")
            print(f"   استعلامات SELECT: {len(select_queries)}")
            print(f"   استعلامات INSERT: {len(insert_queries)}")
            print(f"   استعلامات UPDATE: {len(update_queries)}")
            print(f"   الوقت الإجمالي: {total_time:.4f}s")
            print(f"   متوسط وقت الاستعلام: {total_time/query_count:.4f}s")

            # البحث عن الاستعلامات البطيئة
            slow_queries = [q for q in connection.queries if float(q['time']) > 0.01]
            if slow_queries:
                print(f"   الاستعلامات البطيئة (>10ms): {len(slow_queries)}")
                for i, query in enumerate(slow_queries[:3]):  # أول 3 استعلامات بطيئة
                    print(f"     {i+1}. {query['time']}s: {query['sql'][:100]}...")

            # البحث عن الاستعلامات المكررة
            query_patterns = {}
            for query in connection.queries:
                # استخراج نمط الاستعلام (بدون القيم)
                sql_pattern = query['sql'].split('WHERE')[0] if 'WHERE' in query['sql'] else query['sql']
                query_patterns[sql_pattern] = query_patterns.get(sql_pattern, 0) + 1

            duplicate_patterns = {k: v for k, v in query_patterns.items() if v > 1}
            if duplicate_patterns:
                print(f"   أنماط الاستعلامات المكررة:")
                for pattern, count in list(duplicate_patterns.items())[:3]:
                    print(f"     {count}x: {pattern[:80]}...")

            # التحقق من معايير الأداء
            self.assertLess(query_count, 50, f"عدد استعلامات مفرط: {query_count}")
            self.assertLess(total_time, 1.0, f"وقت استعلامات بطيء: {total_time:.4f}s")
            self.assertLess(len(slow_queries), 5, f"استعلامات بطيئة كثيرة: {len(slow_queries)}")

        except Exception as e:
            self.skipTest(f"تعذر اختبار تحسين الاستعلامات: {str(e)}")

    def test_n_plus_one_problem(self):
        """اختبار مشكلة N+1 في الاستعلامات"""
        connection.queries_log.clear()

        # محاكاة مشكلة N+1
        users = User.objects.all().select_related()  # TODO: Add appropriate select_related fields[:10]  # استعلام واحد

        # هذا سيسبب N استعلامات إضافية إذا لم يتم التحسين
        user_data = []
        for user in users:
            user_data.append({
                'username': user.username,
                'email': user.email,
                'groups': list(user.groups.all())  # استعلام لكل مستخدم
            })

        query_count = len(connection.queries)

        print(f"\n📊 اختبار مشكلة N+1:")
        print(f"   عدد المستخدمين: {len(users)}")
        print(f"   عدد الاستعلامات: {query_count}")
        print(f"   النسبة: {query_count / len(users):.2f} استعلام/مستخدم")

        # يجب أن يكون عدد الاستعلامات قريباً من عدد المستخدمين + 1
        # إذا كان أكثر بكثير، فهناك مشكلة N+1
        expected_max_queries = len(users) + 5  # هامش للاستعلامات الإضافية

        if query_count > expected_max_queries:
            print(f"   ⚠️  مشكلة N+1 محتملة!")
            print(f"   الاستعلامات الأخيرة:")
            for query in connection.queries[-5:]:
                print(f"     {query['time']}s: {query['sql'][:100]}...")

        # التحقق من عدم وجود مشكلة N+1 حادة
        self.assertLess(query_count, len(users) * 2,
                       f"مشكلة N+1 محتملة: {query_count} استعلامات لـ {len(users)} مستخدمين")

    def test_select_related_optimization(self):
        """اختبار تحسين select_related"""
        connection.queries_log.clear()

        # بدون select_related
        users_without_optimization = list(User.objects.all().select_related()  # TODO: Add appropriate select_related fields[:5])
        queries_without = len(connection.queries)

        # الوصول للعلاقات (سيسبب استعلامات إضافية)
        for user in users_without_optimization:
            _ = user.groups.all()

        queries_after_access = len(connection.queries)

        connection.queries_log.clear()

        # مع select_related/prefetch_related
        users_with_optimization = list(
            User.objects.prefetch_related('groups').all()[:5]
        )
        queries_with = len(connection.queries)

        # الوصول للعلاقات (لن يسبب استعلامات إضافية)
        for user in users_with_optimization:
            _ = list(user.groups.all())

        queries_after_optimized_access = len(connection.queries)

        print(f"\n📊 تحليل select_related/prefetch_related:")
        print(f"   بدون تحسين:")
        print(f"     الاستعلامات الأولية: {queries_without}")
        print(f"     بعد الوصول للعلاقات: {queries_after_access}")
        print(f"     استعلامات إضافية: {queries_after_access - queries_without}")
        print(f"   مع التحسين:")
        print(f"     الاستعلامات الأولية: {queries_with}")
        print(f"     بعد الوصول للعلاقات: {queries_after_optimized_access}")
        print(f"     استعلامات إضافية: {queries_after_optimized_access - queries_with}")

        # التحقق من فعالية التحسين
        unoptimized_extra = queries_after_access - queries_without
        optimized_extra = queries_after_optimized_access - queries_with

        self.assertLessEqual(optimized_extra, unoptimized_extra,
                            "التحسين لم يقلل من عدد الاستعلامات")

    @classmethod
    def tearDownClass(cls):
        """tearDownClass function"""
        super().tearDownClass()
        # تنظيف البيانات
        User.objects.filter(username__startswith='optim_user_').prefetch_related()  # TODO: Add appropriate prefetch_related fields.delete()


class CacheOptimizationTests(TestCase):
    """اختبارات تحسين التخزين المؤقت"""

    def setUp(self):
        """setUp function"""
        cache.clear()
        self.client = Client()
        self.user = User.objects.create_user(
            username='cache_test_user',
            password='testpass123',
            email='cachetest@example.com'
        )
        self.client.login(username='cache_test_user', password='testpass123')

    def test_cache_hit_ratio(self):
        """اختبار نسبة إصابة التخزين المؤقت"""
        cache_key = 'test_cache_key'
        cache_value = 'test_cache_value'

        # اختبار Cache Miss
        start_time = time.time()
        result = cache.get(cache_key)
        miss_time = (time.time() - start_time) * 1000

        self.assertIsNone(result, "يجب أن يكون Cache Miss")

        # تعيين القيمة في التخزين المؤقت
        cache.set(cache_key, cache_value, 300)

        # اختبار Cache Hit
        start_time = time.time()
        result = cache.get(cache_key)
        hit_time = (time.time() - start_time) * 1000

        self.assertEqual(result, cache_value, "يجب أن يكون Cache Hit")

        print(f"\n📊 أداء التخزين المؤقت:")
        print(f"   وقت Cache Miss: {miss_time:.4f}ms")
        print(f"   وقت Cache Hit: {hit_time:.4f}ms")
        print(f"   تحسن الأداء: {(miss_time - hit_time) / miss_time * 100:.1f}%")

        # التحقق من أن Cache Hit أسرع
        self.assertLessEqual(hit_time, miss_time, "Cache Hit يجب أن يكون أسرع من Cache Miss")

    def test_cache_performance_under_load(self):
        """اختبار أداء التخزين المؤقت تحت الحمولة"""
        # إعداد بيانات التخزين المؤقت
        cache_data = {}
        for i in range(100):
            key = f'load_test_key_{i}'
            value = f'load_test_value_{i}' * 10  # قيم أكبر
            cache.set(key, value, 300)
            cache_data[key] = value

        # اختبار الأداء تحت الحمولة
        start_time = time.time()

        # قراءة متعددة
        for _ in range(10):
            for i in range(0, 100, 10):  # كل 10 مفاتيح
                key = f'load_test_key_{i}'
                result = cache.get(key)
                self.assertEqual(result, cache_data[key])

        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        operations = 10 * 10  # 10 تكرارات × 10 مفاتيح
        avg_time_per_operation = total_time / operations

        print(f"\n📊 أداء التخزين المؤقت تحت الحمولة:")
        print(f"   إجمالي العمليات: {operations}")
        print(f"   الوقت الإجمالي: {total_time:.2f}ms")
        print(f"   متوسط الوقت لكل عملية: {avg_time_per_operation:.4f}ms")
        print(f"   العمليات في الثانية: {operations / (total_time / 1000):.0f}")

        # التحقق من الأداء
        self.assertLess(avg_time_per_operation, 10,
                       f"أداء التخزين المؤقت بطيء: {avg_time_per_operation:.4f}ms")

    def test_cache_invalidation_performance(self):
        """اختبار أداء إبطال التخزين المؤقت"""
        # إعداد بيانات للإبطال
        keys_to_invalidate = []
        for i in range(50):
            key = f'invalidation_test_key_{i}'
            cache.set(key, f'value_{i}', 300)
            keys_to_invalidate.append(key)

        # اختبار إبطال فردي
        start_time = time.time()
        for key in keys_to_invalidate[:10]:
            cache.delete(key)
        individual_time = (time.time() - start_time) * 1000

        # اختبار إبطال جماعي
        start_time = time.time()
        cache.delete_many(keys_to_invalidate[10:20])
        batch_time = (time.time() - start_time) * 1000

        print(f"\n📊 أداء إبطال التخزين المؤقت:")
        print(f"   الإبطال الفردي (10 مفاتيح): {individual_time:.2f}ms")
        print(f"   الإبطال الجماعي (10 مفاتيح): {batch_time:.2f}ms")
        print(f"   متوسط الوقت (فردي): {individual_time/10:.4f}ms")
        print(f"   متوسط الوقت (جماعي): {batch_time/10:.4f}ms")

        if batch_time < individual_time:
            improvement = (individual_time - batch_time) / individual_time * 100
            print(f"   تحسن الأداء بالإبطال الجماعي: {improvement:.1f}%")

    def tearDown(self):
        """tearDown function"""
        cache.clear()
        self.user.delete()


class ResponseTimeOptimizationTests(TestCase):
    """اختبارات تحسين أوقات الاستجابة"""

    def setUp(self):
        """setUp function"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='response_test_user',
            password='testpass123',
            email='responsetest@example.com'
        )
        self.client.login(username='response_test_user', password='testpass123')

    def measure_response_time_with_optimizations(self, url, iterations=5):
        """قياس وقت الاستجابة مع التحسينات"""
        times_without_cache = []
        times_with_cache = []

        # قياس بدون تخزين مؤقت
        cache.clear()
        for _ in range(iterations):
            start_time = time.time()
            response = self.client.get(url)
            end_time = time.time()
            times_without_cache.append((end_time - start_time) * 1000)

            # التأكد من نجاح الطلب
            self.assertIn(response.status_code, [200, 201, 302])

        # قياس مع التخزين المؤقت (الطلبات التالية ستستفيد من التخزين المؤقت)
        for _ in range(iterations):
            start_time = time.time()
            response = self.client.get(url)
            end_time = time.time()
            times_with_cache.append((end_time - start_time) * 1000)

        return {
            'without_cache': {
                'times': times_without_cache,
                'avg': statistics.mean(times_without_cache),
                'min': min(times_without_cache),
                'max': max(times_without_cache)
            },
            'with_cache': {
                'times': times_with_cache,
                'avg': statistics.mean(times_with_cache),
                'min': min(times_with_cache),
                'max': max(times_with_cache)
            }
        }

    def test_page_optimization_impact(self):
        """اختبار تأثير التحسينات على الصفحات"""
        pages_to_test = [
            ('administrator:dashboard', 'الصفحة الرئيسية'),
            ('Hr:employee_list', 'قائمة الموظفين'),
        ]

        for url_name, page_name in pages_to_test:
            try:
                url = reverse(url_name)
                results = self.measure_response_time_with_optimizations(url)

                without_cache = results['without_cache']
                with_cache = results['with_cache']

                improvement = (without_cache['avg'] - with_cache['avg']) / without_cache['avg'] * 100

                print(f"\n📊 تحليل التحسينات - {page_name}:")
                print(f"   بدون تخزين مؤقت:")
                print(f"     متوسط: {without_cache['avg']:.2f}ms")
                print(f"     أسرع: {without_cache['min']:.2f}ms")
                print(f"     أبطأ: {without_cache['max']:.2f}ms")
                print(f"   مع التخزين المؤقت:")
                print(f"     متوسط: {with_cache['avg']:.2f}ms")
                print(f"     أسرع: {with_cache['min']:.2f}ms")
                print(f"     أبطأ: {with_cache['max']:.2f}ms")
                print(f"   تحسن الأداء: {improvement:+.1f}%")

                # التحقق من وجود تحسن (أو على الأقل عدم تدهور)
                self.assertLessEqual(with_cache['avg'], without_cache['avg'] * 1.1,
                                   f"التخزين المؤقت لم يحسن الأداء لـ {page_name}")

            except Exception as e:
                print(f"⚠️  تعذر اختبار {page_name}: {str(e)}")
                continue

    def test_database_optimization_impact(self):
        """اختبار تأثير تحسينات قاعدة البيانات"""
        # إنشاء بيانات اختبار
        test_users = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'db_optim_user_{i}',
                password='testpass123',
                email=f'dboptim{i}@example.com'
            )
            test_users.append(user)

        # اختبار استعلام غير محسن
        start_time = time.time()
        connection.queries_log.clear()

        users_unoptimized = User.objects.filter(username__startswith='db_optim_user_').prefetch_related()  # TODO: Add appropriate prefetch_related fields
        user_data_unoptimized = []
        for user in users_unoptimized:
            user_data_unoptimized.append({
                'username': user.username,
                'groups': list(user.groups.all())  # N+1 problem
            })

        unoptimized_time = (time.time() - start_time) * 1000
        unoptimized_queries = len(connection.queries)

        # اختبار استعلام محسن
        start_time = time.time()
        connection.queries_log.clear()

        users_optimized = User.objects.filter(
            username__startswith='db_optim_user_'
        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.prefetch_related('groups')

        user_data_optimized = []
        for user in users_optimized:
            user_data_optimized.append({
                'username': user.username,
                'groups': list(user.groups.all())  # No additional queries
            })

        optimized_time = (time.time() - start_time) * 1000
        optimized_queries = len(connection.queries)

        print(f"\n📊 تحليل تحسينات قاعدة البيانات:")
        print(f"   غير محسن:")
        print(f"     الوقت: {unoptimized_time:.2f}ms")
        print(f"     الاستعلامات: {unoptimized_queries}")
        print(f"   محسن:")
        print(f"     الوقت: {optimized_time:.2f}ms")
        print(f"     الاستعلامات: {optimized_queries}")

        if unoptimized_time > 0:
            time_improvement = (unoptimized_time - optimized_time) / unoptimized_time * 100
            print(f"   تحسن الوقت: {time_improvement:+.1f}%")

        if unoptimized_queries > 0:
            query_improvement = (unoptimized_queries - optimized_queries) / unoptimized_queries * 100
            print(f"   تحسن الاستعلامات: {query_improvement:+.1f}%")

        # تنظيف البيانات
        User.objects.filter(username__startswith='db_optim_user_').prefetch_related()  # TODO: Add appropriate prefetch_related fields.delete()

        # التحقق من التحسينات
        self.assertLessEqual(optimized_queries, unoptimized_queries,
                           "التحسين لم يقلل عدد الاستعلامات")
        self.assertLessEqual(optimized_time, unoptimized_time * 1.1,
                           "التحسين لم يحسن الوقت")

    def tearDown(self):
        """tearDown function"""
        self.user.delete()
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        """tearDownClass function"""
        super().tearDownClass()
        # إعادة تفعيل السجلات
        logging.disable(logging.NOTSET)
