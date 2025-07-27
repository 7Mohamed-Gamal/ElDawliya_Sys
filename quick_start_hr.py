#!/usr/bin/env python3
"""
إعداد سريع لنظام الموارد البشرية الشامل
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """طباعة رأس البرنامج"""
    print("=" * 70)
    print("🏢 إعداد سريع لنظام الموارد البشرية الشامل")
    print("=" * 70)
    print()

def check_python_version():
    """فحص إصدار Python"""
    print("🐍 فحص إصدار Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ يتطلب Python 3.8 أو أحدث")
        print(f"   الإصدار الحالي: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """فحص pip"""
    print("📦 فحص pip...")
    
    try:
        import pip
        print("✅ pip متوفر")
        return True
    except ImportError:
        print("❌ pip غير متوفر")
        return False

def install_requirements():
    """تثبيت المتطلبات"""
    print("📥 تثبيت المتطلبات الأساسية...")
    
    # المتطلبات الأساسية فقط
    basic_requirements = [
        "Django>=4.2.0",
        "djangorestframework>=3.14.0",
        "django-cors-headers>=4.0.0",
        "Pillow>=10.0.0",
        "python-dotenv>=1.0.0",
    ]
    
    for requirement in basic_requirements:
        try:
            print(f"   تثبيت {requirement}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", requirement
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"   ✅ {requirement}")
        except subprocess.CalledProcessError:
            print(f"   ⚠️  فشل تثبيت {requirement}")
    
    print("✅ تم تثبيت المتطلبات الأساسية")

def setup_database():
    """إعداد قاعدة البيانات"""
    print("🗄️  إعداد قاعدة البيانات...")
    
    try:
        # تطبيق الهجرات
        subprocess.check_call([
            sys.executable, "manage.py", "migrate"
        ], stdout=subprocess.DEVNULL)
        print("✅ تم تطبيق الهجرات")
        
        return True
    except subprocess.CalledProcessError:
        print("⚠️  فشل في تطبيق الهجرات - سيتم المتابعة")
        return False

def collect_static_files():
    """جمع الملفات الثابتة"""
    print("📁 جمع الملفات الثابتة...")
    
    try:
        subprocess.check_call([
            sys.executable, "manage.py", "collectstatic", "--noinput"
        ], stdout=subprocess.DEVNULL)
        print("✅ تم جمع الملفات الثابتة")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  فشل في جمع الملفات الثابتة")
        return False

def create_superuser():
    """إنشاء مستخدم إداري"""
    print("👤 إنشاء مستخدم إداري...")
    
    try:
        print("   يرجى إدخال بيانات المستخدم الإداري:")
        subprocess.check_call([
            sys.executable, "manage.py", "createsuperuser"
        ])
        print("✅ تم إنشاء المستخدم الإداري")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  تم تخطي إنشاء المستخدم الإداري")
        return False
    except KeyboardInterrupt:
        print("⚠️  تم إلغاء إنشاء المستخدم الإداري")
        return False

def run_system_check():
    """تشغيل فحص النظام"""
    print("🔍 فحص النظام...")
    
    try:
        if os.path.exists("Hr/system_check.py"):
            subprocess.check_call([
                sys.executable, "Hr/system_check.py"
            ])
        else:
            print("⚠️  ملف فحص النظام غير موجود")
    except subprocess.CalledProcessError:
        print("⚠️  فشل في فحص النظام")

def setup_cache():
    """إعداد التخزين المؤقت"""
    print("💾 إعداد التخزين المؤقت...")
    
    try:
        if os.path.exists("Hr/setup_simple_cache.py"):
            subprocess.check_call([
                sys.executable, "Hr/setup_simple_cache.py"
            ])
        else:
            print("⚠️  ملف إعداد التخزين المؤقت غير موجود")
    except subprocess.CalledProcessError:
        print("⚠️  فشل في إعداد التخزين المؤقت")

def create_env_file():
    """إنشاء ملف البيئة"""
    print("⚙️  إنشاء ملف البيئة...")
    
    env_content = """# إعدادات نظام الموارد البشرية

# Django
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# قاعدة البيانات
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
DATABASE_HOST=
DATABASE_PORT=
DATABASE_USER=
DATABASE_PASSWORD=

# التخزين المؤقت
CACHE_BACKEND=django.core.cache.backends.locmem.LocMemCache
REDIS_URL=redis://localhost:6379/1

# البريد الإلكتروني
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# الملفات والوسائط
MEDIA_ROOT=media/
STATIC_ROOT=staticfiles/

# الأمان
INTEGRATION_ENCRYPTION_KEY=change-this-32-character-key-now

# التطوير
DJANGO_LOG_LEVEL=INFO
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ تم إنشاء ملف .env")
    except Exception as e:
        print(f"⚠️  فشل في إنشاء ملف .env: {e}")

def print_next_steps():
    """طباعة الخطوات التالية"""
    print("\n" + "=" * 70)
    print("🎉 تم الإعداد بنجاح!")
    print("=" * 70)
    
    print("\n📋 الخطوات التالية:")
    print("   1. تشغيل الخادم:")
    print("      python manage.py runserver")
    print()
    print("   2. زيارة النظام:")
    print("      http://localhost:8000/Hr/")
    print()
    print("   3. لوحة الإدارة:")
    print("      http://localhost:8000/admin/")
    print()
    print("   4. واجهة برمجة التطبيقات:")
    print("      http://localhost:8000/api/v1/hr/")
    print()
    print("   5. التوثيق:")
    print("      http://localhost:8000/api/docs/")
    
    print("\n📚 الوثائق المفيدة:")
    print("   - دليل النظام الشامل: Hr/HR_SYSTEM_COMPLETE_GUIDE.md")
    print("   - دليل التخزين المؤقت: Hr/CACHE_README.md")
    print("   - ملف المتطلبات الكاملة: requirements_hr_complete.txt")
    
    print("\n🔧 أوامر مفيدة:")
    print("   - فحص النظام: python Hr/system_check.py")
    print("   - إعداد التخزين المؤقت: python Hr/setup_simple_cache.py")
    print("   - إنشاء بيانات تجريبية: python manage.py loaddata sample_data")
    print("   - تشغيل الاختبارات: python manage.py test Hr")
    
    print("\n⚠️  ملاحظات مهمة:")
    print("   - تأكد من تحديث SECRET_KEY في ملف .env")
    print("   - راجع إعدادات قاعدة البيانات حسب احتياجاتك")
    print("   - للإنتاج، غير DEBUG إلى False")
    print("   - ثبت المتطلبات الإضافية من requirements_hr_complete.txt")

def main():
    """الدالة الرئيسية"""
    print_header()
    
    # فحص المتطلبات الأساسية
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # التأكد من وجود manage.py
    if not os.path.exists("manage.py"):
        print("❌ ملف manage.py غير موجود")
        print("   تأكد من تشغيل الأمر من مجلد المشروع الرئيسي")
        return False
    
    try:
        # الخطوات الأساسية
        install_requirements()
        create_env_file()
        setup_database()
        collect_static_files()
        
        # الخطوات الاختيارية
        print("\n" + "=" * 50)
        print("📋 خطوات إضافية (اختيارية)")
        print("=" * 50)
        
        # إنشاء مستخدم إداري
        response = input("هل تريد إنشاء مستخدم إداري؟ (y/n): ").lower()
        if response in ['y', 'yes', 'نعم']:
            create_superuser()
        
        # فحص النظام
        response = input("هل تريد تشغيل فحص النظام؟ (y/n): ").lower()
        if response in ['y', 'yes', 'نعم']:
            run_system_check()
        
        # إعداد التخزين المؤقت
        response = input("هل تريد إعداد التخزين المؤقت؟ (y/n): ").lower()
        if response in ['y', 'yes', 'نعم']:
            setup_cache()
        
        print_next_steps()
        return True
        
    except KeyboardInterrupt:
        print("\n\n⏹️  تم إيقاف الإعداد بواسطة المستخدم")
        return False
    except Exception as e:
        print(f"\n\n❌ خطأ غير متوقع: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🚀 الإعداد مكتمل! يمكنك الآن تشغيل النظام.")
    else:
        print("\n⚠️  الإعداد لم يكتمل بالكامل. راجع الأخطاء أعلاه.")
    
    print("\n" + "=" * 70)