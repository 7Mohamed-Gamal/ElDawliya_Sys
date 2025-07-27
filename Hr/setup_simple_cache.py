"""
إعداد مبسط لنظام التخزين المؤقت
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def setup_simple_cache():
    """إعداد نظام التخزين المؤقت المبسط"""
    
    print("🚀 بدء إعداد نظام التخزين المؤقت المبسط...")
    
    try:
        # إعداد Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
        django.setup()
        
        # استيراد الخدمات
        from Hr.cache_init import initialize_cache_system, get_cache_status
        
        # تهيئة النظام
        cache_backend = initialize_cache_system()
        print(f"✅ تم تهيئة نظام التخزين المؤقت: {cache_backend}")
        
        # فحص الحالة
        status = get_cache_status()
        print("\n📊 حالة النظام:")
        print(f"   مفعل: {'نعم' if status['enabled'] else 'لا'}")
        print(f"   النوع: {status['backend']}")
        print(f"   Redis متاح: {'نعم' if status['redis_available'] else 'لا'}")
        print(f"   Celery متاح: {'نعم' if status['celery_available'] else 'لا'}")
        print(f"   التشفير متاح: {'نعم' if status['encryption_available'] else 'لا'}")
        
        # اختبار التخزين المؤقت
        print("\n🧪 اختبار التخزين المؤقت...")
        from django.core.cache import cache
        
        test_key = 'setup_test_key'
        test_value = 'setup_test_value'
        
        cache.set(test_key, test_value, 60)
        retrieved_value = cache.get(test_key)
        
        if retrieved_value == test_value:
            print("✅ اختبار التخزين المؤقت نجح")
        else:
            print("❌ اختبار التخزين المؤقت فشل")
        
        cache.delete(test_key)
        
        # تشغيل أمر إدارة التخزين المؤقت
        print("\n🔧 تشغيل أوامر الإدارة...")
        execute_from_command_line(['manage.py', 'cache_management', 'status'])
        
        print("\n🎉 تم إعداد نظام التخزين المؤقت بنجاح!")
        print("\n📝 الخطوات التالية:")
        print("   1. تشغيل الخادم: python manage.py runserver")
        print("   2. زيارة لوحة التحكم: http://localhost:8000/Hr/cache/")
        print("   3. مراجعة الوثائق: Hr/CACHE_README.md")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الإعداد: {e}")
        print("\n🔧 حلول مقترحة:")
        print("   1. تأكد من تثبيت Django")
        print("   2. تأكد من إعدادات قاعدة البيانات")
        print("   3. راجع ملف requirements_cache.txt للمتطلبات الاختيارية")
        return False

def install_optional_packages():
    """تثبيت الحزم الاختيارية"""
    
    optional_packages = [
        'redis',
        'django-redis', 
        'celery',
        'cryptography',
        'psutil'
    ]
    
    print("📦 تثبيت الحزم الاختيارية...")
    
    for package in optional_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} مثبت بالفعل")
        except ImportError:
            print(f"⚠️  {package} غير مثبت - سيتم استخدام البديل المحلي")
    
    print("\n💡 لتثبيت الحزم الاختيارية:")
    print("   pip install -r Hr/requirements_cache.txt")

if __name__ == '__main__':
    print("=" * 60)
    print("🏗️  إعداد نظام التخزين المؤقت المتقدم لنظام الموارد البشرية")
    print("=" * 60)
    
    # فحص الحزم الاختيارية
    install_optional_packages()
    
    print("\n" + "=" * 60)
    
    # إعداد النظام
    success = setup_simple_cache()
    
    print("=" * 60)
    
    if success:
        print("🎊 الإعداد مكتمل بنجاح!")
    else:
        print("⚠️  الإعداد مكتمل مع تحذيرات")
    
    print("=" * 60)