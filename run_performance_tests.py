#!/usr/bin/env python
"""
سكريبت تشغيل اختبارات الأداء الشاملة
Comprehensive Performance Testing Script

يقوم بتشغيل جميع اختبارات الأداء وإنتاج تقارير مفصلة
"""
import os
import sys
import argparse
import subprocess
import time
from datetime import datetime

def setup_environment():
    """إعداد البيئة للاختبارات"""
    print("🔧 إعداد بيئة اختبارات الأداء...")
    
    # التأكد من وجود المتطلبات
    try:
        import psutil
        import django
        print("✅ المتطلبات الأساسية متوفرة")
    except ImportError as e:
        print(f"❌ متطلبات مفقودة: {e}")
        print("قم بتثبيت المتطلبات: pip install -r requirements/performance.txt")
        return False
    
    # إعداد Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
    
    try:
        import django
        django.setup()
        print("✅ تم إعداد Django بنجاح")
    except Exception as e:
        print(f"❌ خطأ في إعداد Django: {e}")
        return False
    
    return True

def run_database_migrations():
    """تشغيل هجرات قاعدة البيانات"""
    print("🗄️  تشغيل هجرات قاعدة البيانات...")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate', '--run-syncdb'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ تم تشغيل الهجرات بنجاح")
            return True
        else:
            print(f"❌ فشل في تشغيل الهجرات: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ انتهت مهلة تشغيل الهجرات")
        return False
    except Exception as e:
        print(f"❌ خطأ في تشغيل الهجرات: {e}")
        return False

def create_test_data():
    """إنشاء بيانات اختبار أساسية"""
    print("📊 إنشاء بيانات اختبار...")
    
    try:
        from django.contrib.auth.models import User
        from django.db import transaction
        
        with transaction.atomic():
            # إنشاء مستخدم إداري للاختبار
            if not User.objects.filter(username='performance_admin').exists():
                User.objects.create_superuser(
                    username='performance_admin',
                    email='admin@performance.test',
                    password='performance123'
                )
                print("✅ تم إنشاء مستخدم إداري للاختبار")
            
            # إنشاء مستخدمين عاديين للاختبار
            for i in range(5):
                username = f'perf_user_{i}'
                if not User.objects.filter(username=username).exists():
                    User.objects.create_user(
                        username=username,
                        email=f'user{i}@performance.test',
                        password='performance123'
                    )
            
            print("✅ تم إنشاء بيانات الاختبار الأساسية")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء بيانات الاختبار: {e}")
        return False

def run_performance_tests(test_type='all', verbosity=1):
    """تشغيل اختبارات الأداء"""
    print(f"🚀 بدء تشغيل اختبارات الأداء - النوع: {test_type}")
    
    # تحديد الاختبارات المراد تشغيلها
    test_modules = {
        'response': 'tests.performance.test_page_response_times',
        'load': 'tests.performance.test_load_testing',
        'memory': 'tests.performance.test_memory_usage',
        'optimization': 'tests.performance.test_optimization',
        'all': 'tests.performance'
    }
    
    test_module = test_modules.get(test_type, 'tests.performance')
    
    # إعداد أمر الاختبار
    cmd = [
        sys.executable, 'manage.py', 'test',
        test_module,
        f'--verbosity={verbosity}',
        '--keepdb',  # الاحتفاظ بقاعدة البيانات
        '--parallel=1',  # تشغيل متسلسل لدقة القياسات
    ]
    
    print(f"تشغيل الأمر: {' '.join(cmd)}")
    
    try:
        start_time = time.time()
        result = subprocess.run(cmd, timeout=1800)  # 30 دقيقة مهلة
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ اكتملت اختبارات الأداء بنجاح في {execution_time:.2f} ثانية")
            return True
        else:
            print(f"❌ فشلت اختبارات الأداء (كود الخروج: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ انتهت مهلة اختبارات الأداء")
        return False
    except Exception as e:
        print(f"❌ خطأ في تشغيل اختبارات الأداء: {e}")
        return False

def run_comprehensive_performance_runner():
    """تشغيل مشغل اختبارات الأداء الشامل"""
    print("📋 تشغيل مشغل اختبارات الأداء الشامل...")
    
    try:
        cmd = [sys.executable, 'tests/performance/performance_test_runner.py']
        result = subprocess.run(cmd, timeout=2400)  # 40 دقيقة مهلة
        
        if result.returncode == 0:
            print("✅ اكتمل مشغل اختبارات الأداء الشامل بنجاح")
            return True
        else:
            print(f"❌ فشل مشغل اختبارات الأداء الشامل (كود الخروج: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ انتهت مهلة مشغل اختبارات الأداء الشامل")
        return False
    except Exception as e:
        print(f"❌ خطأ في تشغيل مشغل اختبارات الأداء الشامل: {e}")
        return False

def generate_system_info_report():
    """إنتاج تقرير معلومات النظام"""
    print("💻 جمع معلومات النظام...")
    
    try:
        import psutil
        import platform
        
        # معلومات النظام
        system_info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
            'disk_total': psutil.disk_usage('/').total / 1024 / 1024 / 1024,  # GB
        }
        
        print("📊 معلومات النظام:")
        print(f"   المنصة: {system_info['platform']}")
        print(f"   المعالج: {system_info['processor']}")
        print(f"   عدد المعالجات: {system_info['cpu_count']}")
        print(f"   إجمالي الذاكرة: {system_info['memory_total']:.2f} GB")
        print(f"   إجمالي القرص: {system_info['disk_total']:.2f} GB")
        print(f"   إصدار Python: {system_info['python_version']}")
        
        return system_info
        
    except Exception as e:
        print(f"⚠️  تعذر جمع معلومات النظام: {e}")
        return {}

def cleanup_test_data():
    """تنظيف بيانات الاختبار"""
    print("🧹 تنظيف بيانات الاختبار...")
    
    try:
        from django.contrib.auth.models import User
        from django.db import transaction
        
        with transaction.atomic():
            # حذف المستخدمين المؤقتين
            User.objects.filter(username__startswith='perf_user_').delete()
            User.objects.filter(username__startswith='loadtest_user_').delete()
            User.objects.filter(username__startswith='memtest_user').delete()
            User.objects.filter(username__startswith='optim_user_').delete()
            User.objects.filter(username__startswith='cache_test_user').delete()
            User.objects.filter(username__startswith='response_test_user').delete()
            User.objects.filter(username__startswith='batch_').delete()
            
            print("✅ تم تنظيف بيانات الاختبار")
            
    except Exception as e:
        print(f"⚠️  تعذر تنظيف بيانات الاختبار: {e}")

def main():
    """الدالة الرئيسية"""
    parser = argparse.ArgumentParser(
        description='تشغيل اختبارات الأداء الشاملة لنظام الدولية',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة الاستخدام:
  python run_performance_tests.py                    # تشغيل جميع الاختبارات
  python run_performance_tests.py --type response    # اختبارات أوقات الاستجابة فقط
  python run_performance_tests.py --type load        # اختبارات التحميل فقط
  python run_performance_tests.py --type memory      # اختبارات الذاكرة فقط
  python run_performance_tests.py --comprehensive    # تشغيل المشغل الشامل
  python run_performance_tests.py --no-setup        # تخطي الإعداد
        """
    )
    
    parser.add_argument(
        '--type', 
        choices=['all', 'response', 'load', 'memory', 'optimization'],
        default='all',
        help='نوع اختبارات الأداء المراد تشغيلها'
    )
    
    parser.add_argument(
        '--verbosity', '-v',
        type=int,
        choices=[0, 1, 2, 3],
        default=2,
        help='مستوى التفاصيل في الإخراج'
    )
    
    parser.add_argument(
        '--no-setup',
        action='store_true',
        help='تخطي إعداد البيئة وإنشاء البيانات'
    )
    
    parser.add_argument(
        '--no-cleanup',
        action='store_true',
        help='تخطي تنظيف بيانات الاختبار'
    )
    
    parser.add_argument(
        '--comprehensive',
        action='store_true',
        help='تشغيل مشغل اختبارات الأداء الشامل'
    )
    
    args = parser.parse_args()
    
    print("🎯 مشغل اختبارات الأداء الشاملة - نظام الدولية")
    print("=" * 60)
    print(f"وقت البدء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"نوع الاختبار: {args.type}")
    print(f"مستوى التفاصيل: {args.verbosity}")
    print("=" * 60)
    
    success = True
    
    # جمع معلومات النظام
    system_info = generate_system_info_report()
    
    # إعداد البيئة
    if not args.no_setup:
        if not setup_environment():
            print("❌ فشل في إعداد البيئة")
            return 1
        
        if not run_database_migrations():
            print("❌ فشل في تشغيل هجرات قاعدة البيانات")
            return 1
        
        if not create_test_data():
            print("❌ فشل في إنشاء بيانات الاختبار")
            return 1
    
    # تشغيل الاختبارات
    if args.comprehensive:
        success = run_comprehensive_performance_runner()
    else:
        success = run_performance_tests(args.type, args.verbosity)
    
    # تنظيف البيانات
    if not args.no_cleanup:
        cleanup_test_data()
    
    # النتيجة النهائية
    print("\n" + "=" * 60)
    if success:
        print("🎉 اكتملت اختبارات الأداء بنجاح!")
        print("📋 راجع التقارير في مجلد tests/performance/results/")
    else:
        print("❌ فشلت اختبارات الأداء")
        print("🔍 راجع السجلات لمزيد من التفاصيل")
    
    print(f"وقت الانتهاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())