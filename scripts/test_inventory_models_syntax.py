#!/usr/bin/env python
"""
سكريبت لاختبار صحة بناء الجملة لنماذج المخزون والمشتريات
Script to test syntax correctness of inventory and procurement models
"""
import ast
import os
import sys


def check_python_syntax(file_path):
    """فحص صحة بناء الجملة لملف Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # محاولة تحليل الملف
        ast.parse(content)
        return True, None

    except SyntaxError as e:
        return False, f"خطأ في بناء الجملة في السطر {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"خطأ في قراءة الملف: {str(e)}"


def check_imports(file_path):
    """فحص صحة الاستيرادات"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # البحث عن الاستيرادات المشكوك فيها
        problematic_imports = [
            'from .base import',
            'from .inventory import',
            'from .procurement import',
        ]

        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            for imp in problematic_imports:
                if imp in line and not line.strip().startswith('#'):
                    # التحقق من وجود الملفات المستوردة
                    if '.base import' in line:
                        base_file = os.path.join(os.path.dirname(file_path), 'base.py')
                        if not os.path.exists(base_file):
                            issues.append(f"السطر {i}: ملف base.py غير موجود")

        return len(issues) == 0, issues

    except Exception as e:
        return False, [f"خطأ في فحص الاستيرادات: {str(e)}"]


def check_model_structure(file_path):
    """فحص هيكل النماذج"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # فحص وجود الكلاسات الأساسية
        required_patterns = [
            'class.*Model.*:',
            'class Meta:',
            'def __str__',
            'verbose_name',
        ]

        issues = []

        for pattern in required_patterns:
            import re
            if not re.search(pattern, content):
                issues.append(f"لم يتم العثور على النمط المطلوب: {pattern}")

        return len(issues) == 0, issues

    except Exception as e:
        return False, [f"خطأ في فحص هيكل النماذج: {str(e)}"]


def main():
    """الدالة الرئيسية"""
    print("🔍 فحص صحة بناء الجملة لنماذج المخزون والمشتريات")
    print("=" * 60)

    # الملفات المراد فحصها
    files_to_check = [
        'core/models/inventory.py',
        'core/models/procurement.py',
        'core/management/commands/migrate_inventory_models.py',
    ]

    all_files_valid = True

    for file_path in files_to_check:
        print(f"\n📁 فحص الملف: {file_path}")

        if not os.path.exists(file_path):
            print(f"  ❌ الملف غير موجود: {file_path}")
            all_files_valid = False
            continue

        # فحص بناء الجملة
        syntax_ok, syntax_error = check_python_syntax(file_path)
        if syntax_ok:
            print("  ✅ بناء الجملة صحيح")
        else:
            print(f"  ❌ خطأ في بناء الجملة: {syntax_error}")
            all_files_valid = False

        # فحص الاستيرادات
        imports_ok, import_issues = check_imports(file_path)
        if imports_ok:
            print("  ✅ الاستيرادات صحيحة")
        else:
            print("  ❌ مشاكل في الاستيرادات:")
            for issue in import_issues:
                print(f"    - {issue}")
            all_files_valid = False

        # فحص هيكل النماذج (للملفات التي تحتوي على نماذج)
        if 'models' in file_path and not 'commands' in file_path:
            structure_ok, structure_issues = check_model_structure(file_path)
            if structure_ok:
                print("  ✅ هيكل النماذج صحيح")
            else:
                print("  ⚠️  تحذيرات في هيكل النماذج:")
                for issue in structure_issues:
                    print(f"    - {issue}")

    print("\n" + "=" * 60)
    if all_files_valid:
        print("🎉 جميع الملفات صحيحة من ناحية بناء الجملة!")
    else:
        print("❌ توجد أخطاء في بعض الملفات. يرجى مراجعتها.")

    return all_files_valid


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
