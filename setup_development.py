#!/usr/bin/env python3
"""
سكريبت إعداد البيئة التطويرية لنظام الموارد البشرية الشامل
"""

import os
import sys
import subprocess
import django
from pathlib import Path

# إضافة مسار المشروع
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# تعيين متغير البيئة
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings_development')

def print_step(step_num, description):
    """طباعة خطوة مع تنسيق جميل"""
    print(f"\n{'='*60}")
    print(f"الخطوة {step_num}: {description}")
    print(f"{'='*60}")

def run_command(command, description=""):
    """تشغيل أمر مع معالجة الأخطاء"""
    try:
        print(f"🔄 تشغيل: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تشغيل الأمر: {e}")
        if e.stderr:
            print(f"تفاصيل الخطأ: {e.stderr}")
        return False

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    directories = [
        'logs',
        'temp',
        'temp/reports',
        'backups',
        'media',
        'media/employees',
        'media/documents',
        'media/photos',
        'media/signatures',
        'media/certificates',
        'media/contracts',
        'media/reports',
        'media/temp',
        'media/backups',
        'media/exports',
        'staticfiles',
    ]
    
    for directory in directories:
        dir_path = BASE_DIR / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 تم إنشاء المجلد: {directory}")

def create_env_file():
    """إنشاء ملف البيئة"""
    env_content = '''# إعدادات قاعدة البيانات
DB_NAME=ElDawliya_Sys
DB_HOST=DESKTOP-H36115
DB_PORT=1433
DB_USER=admin
DB_PASSWORD=hgslduhgfwdv

# إعدادات Django
DJANGO_SECRET_KEY=django-insecure-#9^46q1m(@yts%4xkw&%uy&_$t!drx$-ke^z_*ircyuhk1acs
DJANGO_DEBUG=True
DJANGO_ACTIVE_DB=default

# إعدادات Redis
REDIS_URL=redis://127.0.0.1:6379/1

# إعدادات Celery
CELERY_BROKER_URL=redis://127.0.0.1:6379/4
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/5

# إعدادات البريد الإلكتروني
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@eldawliya.com

# إعدادات التشفير
FIELD_ENCRYPTION_KEY=your-32-character-encryption-key-here

# إعدادات الذكاء الاصطناعي
GEMINI_API_KEY=your-gemini-api-key-here

# إعدادات Sentry (للإنتاج)
SENTRY_DSN=your-sentry-dsn-here
'''
    
    env_file = BASE_DIR / '.env'
    if not env_file.exists():
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("📝 تم إنشاء ملف .env")
    else:
        print("📝 ملف .env موجود بالفعل")

def setup_django():
    """إعداد Django"""
    try:
        django.setup()
        print("✅ تم إعداد Django بنجاح")
        return True
    except Exception as e:
        print(f"❌ خطأ في إعداد Django: {e}")
        return False

def run_migrations():
    """تشغيل الهجرات"""
    commands = [
        'python manage.py makemigrations',
        'python manage.py migrate',
    ]
    
    for command in commands:
        if not run_command(command):
            return False
    return True

def create_superuser():
    """إنشاء مستخدم إداري"""
    print("🔐 إنشاء مستخدم إداري...")
    print("يرجى إدخال بيانات المستخدم الإداري:")
    
    try:
        from django.contrib.auth.models import User
        
        username = input("اسم المستخدم (admin): ") or "admin"
        email = input("البريد الإلكتروني (admin@eldawliya.com): ") or "admin@eldawliya.com"
        
        if User.objects.filter(username=username).exists():
            print(f"المستخدم {username} موجود بالفعل")
            return True
        
        password = input("كلمة المرور (admin123): ") or "admin123"
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ تم إنشاء المستخدم الإداري: {username}")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء المستخدم الإداري: {e}")
        return False

def collect_static():
    """جمع الملفات الثابتة"""
    return run_command('python manage.py collectstatic --noinput')

def create_demo_data():
    """إنشاء بيانات تجريبية"""
    try:
        from Hr.management.commands.create_demo_data import Command
        command = Command()
        command.handle()
        print("✅ تم إنشاء البيانات التجريبية")
        return True
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات التجريبية: {e}")
        return False

def test_system():
    """اختبار النظام"""
    commands = [
        'python manage.py check',
        'python manage.py check --deploy',
    ]
    
    for command in commands:
        if not run_command(command):
            return False
    return True

def main():
    """الدالة الرئيسية"""
    print("🚀 مرحباً بك في سكريبت إعداد البيئة التطويرية")
    print("📋 سيتم إعداد نظام الموارد البشرية الشامل")
    
    steps = [
        (1, "إنشاء المجلدات المطلوبة", create_directories),
        (2, "إنشاء ملف البيئة", create_env_file),
        (3, "إعداد Django", setup_django),
        (4, "تشغيل الهجرات", run_migrations),
        (5, "إنشاء مستخدم إداري", create_superuser),
        (6, "جمع الملفات الثابتة", collect_static),
        (7, "إنشاء بيانات تجريبية", create_demo_data),
        (8, "اختبار النظام", test_system),
    ]
    
    success_count = 0
    
    for step_num, description, function in steps:
        print_step(step_num, description)
        
        try:
            if function():
                print(f"✅ تمت الخطوة {step_num} بنجاح")
                success_count += 1
            else:
                print(f"❌ فشلت الخطوة {step_num}")
        except Exception as e:
            print(f"❌ خطأ في الخطوة {step_num}: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 النتائج النهائية")
    print(f"{'='*60}")
    print(f"✅ الخطوات الناجحة: {success_count}/{len(steps)}")
    
    if success_count == len(steps):
        print("🎉 تم إعداد البيئة التطويرية بنجاح!")
        print("\n📋 الخطوات التالية:")
        print("1. تشغيل الخادم: python manage.py runserver")
        print("2. فتح المتصفح: http://127.0.0.1:8000")
        print("3. تسجيل الدخول بالمستخدم الإداري")
        print("4. بدء التطوير! 🚀")
        
        print("\n🔧 أوامر مفيدة:")
        print("- تشغيل Celery: celery -A ElDawliya_sys worker -l info")
        print("- تشغيل Celery Beat: celery -A ElDawliya_sys beat -l info")
        print("- مراقبة Celery: celery -A ElDawliya_sys flower")
        print("- إنشاء تطبيق جديد: python manage.py startapp app_name")
        print("- إنشاء هجرة: python manage.py makemigrations")
        print("- تشغيل الاختبارات: python manage.py test")
        
    else:
        print("⚠️ بعض الخطوات فشلت. يرجى مراجعة الأخطاء أعلاه")
        print("💡 يمكنك تشغيل السكريبت مرة أخرى لإعادة المحاولة")

if __name__ == '__main__':
    main()