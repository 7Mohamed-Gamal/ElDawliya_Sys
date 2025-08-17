"""
فحص شامل لنظام الموارد البشرية
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def check_django_setup():
    """فحص إعداد Django"""
    
    print("🔍 فحص إعداد Django...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
        django.setup()
        print("✅ Django مُعد بشكل صحيح")
        return True
    except Exception as e:
        print(f"❌ خطأ في إعداد Django: {e}")
        return False

def check_database_connection():
    """فحص الاتصال بقاعدة البيانات"""
    
    print("🔍 فحص الاتصال بقاعدة البيانات...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ الاتصال بقاعدة البيانات يعمل")
        return True
    except Exception as e:
        print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
        return False

def check_hr_models():
    """فحص نماذج الموارد البشرية"""
    
    print("🔍 فحص نماذج الموارد البشرية...")
    
    try:
        from Hr.models import Employee, Department, JobPosition
        
        # فحص الجداول الأساسية
        models_to_check = [
            ('Employee', Employee),
            ('Department', Department), 
            ('JobPosition', JobPosition),
        ]
        
        for name, model in models_to_check:
            try:
                count = model.objects.count()
                print(f"✅ {name}: {count} سجل")
            except Exception as e:
                print(f"⚠️  {name}: خطأ في الوصول - {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد النماذج: {e}")
        return False

def check_hr_services():
    """فحص خدمات الموارد البشرية"""
    
    print("🔍 فحص خدمات الموارد البشرية...")
    
    services_to_check = [
        'Hr.services.employee_service',
        'Hr.services.cache_service',
        'Hr.services.notification_service',
        'Hr.services.search_service',
    ]
    
    working_services = 0
    
    for service_name in services_to_check:
        try:
            __import__(service_name)
            print(f"✅ {service_name}")
            working_services += 1
        except ImportError as e:
            print(f"⚠️  {service_name}: {e}")
    
    print(f"📊 {working_services}/{len(services_to_check)} خدمات تعمل")
    return working_services > 0

def check_cache_system():
    """فحص نظام التخزين المؤقت"""
    
    print("🔍 فحص نظام التخزين المؤقت...")
    
    try:
        from django.core.cache import cache
        
        # اختبار أساسي
        test_key = 'system_check_key'
        test_value = 'system_check_value'
        
        cache.set(test_key, test_value, 60)
        retrieved_value = cache.get(test_key)
        
        if retrieved_value == test_value:
            print("✅ نظام التخزين المؤقت يعمل")
            cache.delete(test_key)
            return True
        else:
            print("❌ نظام التخزين المؤقت لا يعمل بشكل صحيح")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في نظام التخزين المؤقت: {e}")
        return False

def check_static_files():
    """فحص الملفات الثابتة"""
    
    print("🔍 فحص الملفات الثابتة...")
    
    static_files_to_check = [
        'Hr/static/Hr/css/hr-design-system.css',
        'Hr/static/Hr/js/hr-design-system.js',
        'Hr/static/Hr/css/search.css',
        'Hr/static/Hr/js/search.js',
    ]
    
    existing_files = 0
    
    for file_path in static_files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            existing_files += 1
        else:
            print(f"⚠️  {file_path}: غير موجود")
    
    print(f"📊 {existing_files}/{len(static_files_to_check)} ملفات ثابتة موجودة")
    return existing_files > 0

def check_templates():
    """فحص القوالب"""
    
    print("🔍 فحص القوالب...")
    
    templates_to_check = [
        'Hr/templates/Hr/components/navbar.html',
        'Hr/templates/Hr/components/sidebar.html',
        'Hr/templates/Hr/search/advanced_search.html',
        'Hr/templates/Hr/notifications/notification_center.html',
    ]
    
    existing_templates = 0
    
    for template_path in templates_to_check:
        if os.path.exists(template_path):
            print(f"✅ {template_path}")
            existing_templates += 1
        else:
            print(f"⚠️  {template_path}: غير موجود")
    
    print(f"📊 {existing_templates}/{len(templates_to_check)} قوالب موجودة")
    return existing_templates > 0

def check_migrations():
    """فحص الهجرات"""
    
    print("🔍 فحص الهجرات...")
    
    try:
        from django.core.management import execute_from_command_line
        from io import StringIO
        import sys
        
        # التقاط الإخراج
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            execute_from_command_line(['manage.py', 'showmigrations', 'Hr', '--plan'])
            output = captured_output.getvalue()
            
            if 'Hr' in output:
                print("✅ هجرات الموارد البشرية موجودة")
                return True
            else:
                print("⚠️  لا توجد هجرات للموارد البشرية")
                return False
                
        finally:
            sys.stdout = old_stdout
            
    except Exception as e:
        print(f"❌ خطأ في فحص الهجرات: {e}")
        return False

def check_permissions():
    """فحص الصلاحيات"""
    
    print("🔍 فحص الصلاحيات...")
    
    try:
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        # فحص صلاحيات الموارد البشرية
        hr_permissions = Permission.objects.filter(
            content_type__app_label='Hr'
        ).count()
        
        print(f"✅ صلاحيات الموارد البشرية: {hr_permissions}")
        return hr_permissions > 0
        
    except Exception as e:
        print(f"❌ خطأ في فحص الصلاحيات: {e}")
        return False

def generate_system_report():
    """إنتاج تقرير شامل للنظام"""
    
    print("\n" + "="*60)
    print("📋 تقرير حالة نظام الموارد البشرية")
    print("="*60)
    
    checks = [
        ("إعداد Django", check_django_setup),
        ("الاتصال بقاعدة البيانات", check_database_connection),
        ("نماذج الموارد البشرية", check_hr_models),
        ("خدمات الموارد البشرية", check_hr_services),
        ("نظام التخزين المؤقت", check_cache_system),
        ("الملفات الثابتة", check_static_files),
        ("القوالب", check_templates),
        ("الهجرات", check_migrations),
        ("الصلاحيات", check_permissions),
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_function in checks:
        print(f"\n🔍 {check_name}:")
        try:
            if check_function():
                passed_checks += 1
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")
    
    print("\n" + "="*60)
    print("📊 ملخص التقرير")
    print("="*60)
    
    success_rate = (passed_checks / total_checks) * 100
    print(f"نجح: {passed_checks}/{total_checks} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 النظام في حالة ممتازة!")
    elif success_rate >= 60:
        print("✅ النظام في حالة جيدة مع بعض التحذيرات")
    else:
        print("⚠️  النظام يحتاج إلى إصلاحات")
    
    print("\n💡 التوصيات:")
    if success_rate < 100:
        print("   - راجع الأخطاء والتحذيرات أعلاه")
        print("   - تأكد من تشغيل الهجرات: python manage.py migrate")
        print("   - تأكد من جمع الملفات الثابتة: python manage.py collectstatic")
    
    print("   - راجع الوثائق في Hr/CACHE_README.md")
    print("   - استخدم python Hr/setup_simple_cache.py للإعداد")
    
    return success_rate

if __name__ == '__main__':
    print("🏥 فحص شامل لنظام الموارد البشرية")
    print("="*60)
    
    try:
        success_rate = generate_system_report()
        
        print("\n" + "="*60)
        if success_rate >= 80:
            print("🚀 النظام جاهز للاستخدام!")
        else:
            print("🔧 النظام يحتاج إلى إعداد إضافي")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  تم إيقاف الفحص بواسطة المستخدم")
    except Exception as e:
        print(f"\n\n❌ خطأ عام في الفحص: {e}")
        print("💡 تأكد من تشغيل الأمر من مجلد المشروع الرئيسي")