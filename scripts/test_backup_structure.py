#!/usr/bin/env python
"""
ElDawliya System - Backup Structure Test
========================================

Simple test script to validate the backup system structure and commands
without requiring Django to be installed.
"""

import os
import sys
from pathlib import Path


def test_backup_system_structure():
    """Test that all backup system files are in place."""
    print("🧪 اختبار هيكل نظام النسخ الاحتياطي")
    print("=" * 50)

    # Get project root
    project_root = Path(__file__).resolve().parent.parent

    # Required files and directories
    required_files = [
        'core/management/__init__.py',
        'core/management/commands/__init__.py',
        'core/management/commands/create_system_backup.py',
        'core/management/commands/restore_system_backup.py',
        'core/management/commands/manage_backups.py',
        'core/management/commands/create_checkpoint.py',
        'core/management/commands/list_checkpoints.py',
        'scripts/validate_backup_system.py',
        'docs/BACKUP_SYSTEM.md',
        'ROLLBACK_PLAN.md',
        'CLEANUP_BACKUP_LOG.md'
    ]

    missing_files = []
    existing_files = []

    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")

    print("\n" + "=" * 50)
    print(f"📊 النتائج:")
    print(f"الملفات الموجودة: {len(existing_files)}")
    print(f"الملفات المفقودة: {len(missing_files)}")

    if missing_files:
        print(f"\n❌ الملفات المفقودة:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print(f"\n✅ جميع ملفات نظام النسخ الاحتياطي موجودة")
        return True


def test_backup_commands_syntax():
    """Test backup command files for basic syntax errors."""
    print("\n🔍 اختبار صحة ملفات الأوامر")
    print("=" * 50)

    project_root = Path(__file__).resolve().parent.parent

    command_files = [
        'core/management/commands/create_system_backup.py',
        'core/management/commands/restore_system_backup.py',
        'core/management/commands/manage_backups.py',
        'core/management/commands/create_checkpoint.py',
        'core/management/commands/list_checkpoints.py'
    ]

    syntax_errors = []
    valid_files = []

    for file_path in command_files:
        full_path = project_root / file_path

        if not full_path.exists():
            continue

        try:
            # Try to compile the file to check for syntax errors
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            compile(content, str(full_path), 'exec')
            valid_files.append(file_path)
            print(f"✅ {file_path}")

        except SyntaxError as e:
            syntax_errors.append((file_path, str(e)))
            print(f"❌ {file_path}: {e}")
        except Exception as e:
            syntax_errors.append((file_path, str(e)))
            print(f"⚠️ {file_path}: {e}")

    print(f"\nالملفات الصالحة: {len(valid_files)}")
    print(f"الملفات بها أخطاء: {len(syntax_errors)}")

    return len(syntax_errors) == 0


def test_documentation_completeness():
    """Test that documentation files are complete."""
    print("\n📚 اختبار اكتمال التوثيق")
    print("=" * 50)

    project_root = Path(__file__).resolve().parent.parent

    doc_files = [
        ('docs/BACKUP_SYSTEM.md', 'دليل نظام النسخ الاحتياطي'),
        ('ROLLBACK_PLAN.md', 'خطة التراجع'),
        ('CLEANUP_BACKUP_LOG.md', 'سجل النسخ الاحتياطية')
    ]

    complete_docs = []
    incomplete_docs = []

    for file_path, description in doc_files:
        full_path = project_root / file_path

        if not full_path.exists():
            incomplete_docs.append((file_path, "الملف غير موجود"))
            print(f"❌ {description}: الملف غير موجود")
            continue

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if file has substantial content (more than 1000 characters)
            if len(content) > 1000:
                complete_docs.append(file_path)
                print(f"✅ {description}: مكتمل ({len(content)} حرف)")
            else:
                incomplete_docs.append((file_path, f"محتوى قصير ({len(content)} حرف)"))
                print(f"⚠️ {description}: محتوى قصير ({len(content)} حرف)")

        except Exception as e:
            incomplete_docs.append((file_path, str(e)))
            print(f"❌ {description}: خطأ في القراءة - {e}")

    print(f"\nالوثائق المكتملة: {len(complete_docs)}")
    print(f"الوثائق غير المكتملة: {len(incomplete_docs)}")

    return len(incomplete_docs) == 0


def create_backup_directory():
    """Create backup directory if it doesn't exist."""
    print("\n📁 إنشاء مجلد النسخ الاحتياطية")
    print("=" * 50)

    project_root = Path(__file__).resolve().parent.parent
    backup_dir = project_root / 'backups'

    try:
        backup_dir.mkdir(exist_ok=True)
        print(f"✅ تم إنشاء مجلد النسخ الاحتياطية: {backup_dir}")

        # Create a README file in the backup directory
        readme_file = backup_dir / 'README.md'
        if not readme_file.exists():
            readme_content = """# مجلد النسخ الاحتياطية - نظام الدولية

هذا المجلد يحتوي على النسخ الاحتياطية لنظام الدولية.

## الملفات المتوقعة:
- `backup_registry.json`: سجل النسخ الاحتياطية
- `checkpoint_registry.json`: سجل نقاط التحقق
- مجلدات النسخ الاحتياطية أو ملفات مضغوطة

## الاستخدام:
```bash
# عرض النسخ المتاحة
python manage.py manage_backups list

# إنشاء نسخة احتياطية
python manage.py create_system_backup --name my_backup

# استعادة من نسخة احتياطية
python manage.py restore_system_backup backup_path --restore-all
```
"""
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print(f"✅ تم إنشاء ملف README: {readme_file}")

        return True

    except Exception as e:
        print(f"❌ فشل في إنشاء مجلد النسخ الاحتياطية: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 ElDawliya System - Backup System Structure Test")
    print("=" * 60)

    tests = [
        ("اختبار هيكل الملفات", test_backup_system_structure),
        ("اختبار صحة الأوامر", test_backup_commands_syntax),
        ("اختبار التوثيق", test_documentation_completeness),
        ("إنشاء مجلد النسخ", create_backup_directory)
    ]

    passed_tests = 0
    total_tests = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name}: نجح")
            else:
                print(f"❌ {test_name}: فشل")
        except Exception as e:
            print(f"❌ {test_name}: خطأ - {e}")

    print("\n" + "=" * 60)
    print("📊 ملخص النتائج")
    print("=" * 60)
    print(f"إجمالي الاختبارات: {total_tests}")
    print(f"الاختبارات الناجحة: {passed_tests}")
    print(f"الاختبارات الفاشلة: {total_tests - passed_tests}")

    success_rate = (passed_tests / total_tests) * 100
    print(f"معدل النجاح: {success_rate:.1f}%")

    if passed_tests == total_tests:
        print("\n✅ جميع الاختبارات نجحت - نظام النسخ الاحتياطي جاهز للاستخدام")
        print("\n📋 الخطوات التالية:")
        print("1. تأكد من تثبيت Django وتفعيل البيئة الافتراضية")
        print("2. قم بتشغيل: python manage.py create_checkpoint initial")
        print("3. ابدأ عملية التنظيف مع إنشاء نقاط تحقق منتظمة")
        return True
    else:
        print("\n❌ بعض الاختبارات فشلت - يحتاج النظام إلى مراجعة")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
