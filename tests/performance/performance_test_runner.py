#!/usr/bin/env python
"""
مشغل اختبارات الأداء
Performance Test Runner

يقوم بتشغيل جميع اختبارات الأداء وإنتاج تقرير شامل
"""
import os
import sys
import time
import json
from datetime import datetime
import django
from django.test.utils import get_runner
from django.conf import settings
from django.core.management import execute_from_command_line

# إضافة مسار المشروع
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()


class PerformanceTestRunner:
    """مشغل اختبارات الأداء"""

    def __init__(self):
        """__init__ function"""
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'test_suites': {},
            'summary': {},
            'recommendations': []
        }
        self.start_time = None
        self.end_time = None

    def run_all_tests(self):
        """تشغيل جميع اختبارات الأداء"""
        print("🚀 بدء تشغيل اختبارات الأداء الشاملة")
        print("=" * 60)

        self.start_time = time.time()

        # قائمة اختبارات الأداء
        test_suites = [
            ('tests.performance.test_page_response_times', 'اختبارات أوقات الاستجابة'),
            ('tests.performance.test_load_testing', 'اختبارات التحميل المتزامن'),
            ('tests.performance.test_memory_usage', 'اختبارات استهلاك الذاكرة'),
            ('tests.performance.test_optimization', 'اختبارات التحسين'),
        ]

        for test_module, test_name in test_suites:
            print(f"\n📊 تشغيل {test_name}...")
            print("-" * 40)

            try:
                # تشغيل الاختبار
                result = self.run_test_suite(test_module)
                self.results['test_suites'][test_module] = {
                    'name': test_name,
                    'status': 'success' if result else 'failed',
                    'timestamp': datetime.now().isoformat()
                }

                if result:
                    print(f"✅ {test_name} - مكتمل بنجاح")
                else:
                    print(f"❌ {test_name} - فشل")

            except Exception as e:
                print(f"❌ خطأ في {test_name}: {str(e)}")
                self.results['test_suites'][test_module] = {
                    'name': test_name,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }

        self.end_time = time.time()
        self.generate_summary()
        self.generate_recommendations()
        self.save_results()
        self.print_final_report()

    def run_test_suite(self, test_module):
        """تشغيل مجموعة اختبارات محددة"""
        try:
            # استخدام Django test runner
            from django.test.runner import DiscoverRunner

            runner = DiscoverRunner(verbosity=1, interactive=False, keepdb=True)

            # تشغيل الاختبارات
            result = runner.run_tests([test_module])

            return result == 0  # 0 يعني نجاح

        except Exception as e:
            print(f"خطأ في تشغيل {test_module}: {str(e)}")
            return False

    def generate_summary(self):
        """إنتاج ملخص النتائج"""
        total_tests = len(self.results['test_suites'])
        successful_tests = sum(1 for suite in self.results['test_suites'].values()
                              if suite['status'] == 'success')
        failed_tests = sum(1 for suite in self.results['test_suites'].values()
                          if suite['status'] == 'failed')
        error_tests = sum(1 for suite in self.results['test_suites'].values()
                         if suite['status'] == 'error')

        total_time = self.end_time - self.start_time if self.end_time and self.start_time else 0

        self.results['summary'] = {
            'total_test_suites': total_tests,
            'successful_suites': successful_tests,
            'failed_suites': failed_tests,
            'error_suites': error_tests,
            'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_execution_time': total_time,
            'execution_time_formatted': f"{total_time:.2f}s"
        }

    def generate_recommendations(self):
        """إنتاج توصيات التحسين"""
        recommendations = []

        # تحليل النتائج وإنتاج التوصيات
        failed_suites = [suite for suite in self.results['test_suites'].values()
                        if suite['status'] in ['failed', 'error']]

        if failed_suites:
            recommendations.append({
                'priority': 'high',
                'category': 'test_failures',
                'title': 'إصلاح الاختبارات الفاشلة',
                'description': f'يوجد {len(failed_suites)} مجموعة اختبارات فاشلة تحتاج إلى إصلاح',
                'action': 'مراجعة وإصلاح الاختبارات الفاشلة قبل النشر'
            })

        # توصيات عامة للأداء
        recommendations.extend([
            {
                'priority': 'medium',
                'category': 'database',
                'title': 'تحسين استعلامات قاعدة البيانات',
                'description': 'استخدام select_related و prefetch_related لتقليل عدد الاستعلامات',
                'action': 'مراجعة الاستعلامات البطيئة وتحسينها'
            },
            {
                'priority': 'medium',
                'category': 'caching',
                'title': 'تحسين التخزين المؤقت',
                'description': 'تطبيق استراتيجيات تخزين مؤقت للبيانات المتكررة',
                'action': 'إضافة تخزين مؤقت للصفحات والاستعلامات الثقيلة'
            },
            {
                'priority': 'low',
                'category': 'monitoring',
                'title': 'مراقبة الأداء المستمرة',
                'description': 'إعداد مراقبة مستمرة لأداء النظام',
                'action': 'تطبيق أدوات مراقبة الأداء في الإنتاج'
            }
        ])

        self.results['recommendations'] = recommendations

    def save_results(self):
        """حفظ النتائج في ملف"""
        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(results_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = os.path.join(results_dir, f'performance_test_results_{timestamp}.json')

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\n💾 تم حفظ النتائج في: {results_file}")

    def print_final_report(self):
        """طباعة التقرير النهائي"""
        print("\n" + "=" * 60)
        print("📋 تقرير اختبارات الأداء النهائي")
        print("=" * 60)

        summary = self.results['summary']
        print(f"📊 الملخص:")
        print(f"   إجمالي مجموعات الاختبارات: {summary['total_test_suites']}")
        print(f"   المجموعات الناجحة: {summary['successful_suites']}")
        print(f"   المجموعات الفاشلة: {summary['failed_suites']}")
        print(f"   المجموعات بأخطاء: {summary['error_suites']}")
        print(f"   معدل النجاح: {summary['success_rate']:.1f}%")
        print(f"   وقت التنفيذ الإجمالي: {summary['execution_time_formatted']}")

        # طباعة حالة كل مجموعة اختبارات
        print(f"\n📋 تفاصيل مجموعات الاختبارات:")
        for module, suite_info in self.results['test_suites'].items():
            status_icon = "✅" if suite_info['status'] == 'success' else "❌"
            print(f"   {status_icon} {suite_info['name']}: {suite_info['status']}")

        # طباعة التوصيات
        print(f"\n💡 التوصيات:")
        for rec in self.results['recommendations']:
            priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
            print(f"   {priority_icon} {rec['title']}")
            print(f"      {rec['description']}")
            print(f"      الإجراء: {rec['action']}")

        # تقييم عام
        if summary['success_rate'] >= 80:
            print(f"\n🎉 تقييم عام: ممتاز - النظام يحقق معايير الأداء المطلوبة")
        elif summary['success_rate'] >= 60:
            print(f"\n⚠️  تقييم عام: جيد - يحتاج بعض التحسينات")
        else:
            print(f"\n🚨 تقييم عام: يحتاج تحسين - مشاكل أداء تحتاج إلى إصلاح فوري")


def main():
    """الدالة الرئيسية"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("مشغل اختبارات الأداء")
        print("الاستخدام: python performance_test_runner.py")
        print("\nالخيارات:")
        print("  --help    عرض هذه المساعدة")
        return

    runner = PerformanceTestRunner()
    runner.run_all_tests()


if __name__ == '__main__':
    main()
