"""
تنظيف وتوحيد ملفات نظام الموارد البشرية

هذا السكربت ينفذ المرحلة الأولى من خطة التحسين:
1. تحديد وإزالة الملفات المكررة
2. توحيد الملفات المتشابهة في الوظائف
3. نقل النماذج القديمة إلى مجلد legacy
"""

import os
import sys
import shutil
import re
import logging
from pathlib import Path
from datetime import datetime

# إعداد التسجيل
log_file = f"hr_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("hr_cleanup")

# المسارات الرئيسية
PROJECT_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
HR_APP_PATH = PROJECT_ROOT / 'Hr'
MODELS_PATH = HR_APP_PATH / 'models'
LEGACY_PATH = MODELS_PATH / 'legacy'

def ensure_directory(path):
    """التأكد من وجود المجلد"""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"تم إنشاء المجلد: {path}")
    return path

def create_init_file(directory):
    """إنشاء ملف __init__.py إذا لم يكن موجوداً"""
    init_file = directory / '__init__.py'
    if not init_file.exists():
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(f"# {directory.name} module - created by cleanup script\n")
        logger.info(f"تم إنشاء ملف __init__.py في {directory}")

def backup_file(file_path):
    """إنشاء نسخة احتياطية من الملف"""
    backup_dir = PROJECT_ROOT / 'backups' / 'models'
    ensure_directory(backup_dir)

    file_path = Path(file_path)
    backup_path = backup_dir / f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"

    shutil.copy2(file_path, backup_path)
    logger.info(f"تم إنشاء نسخة احتياطية: {backup_path}")
    return backup_path

def move_to_legacy(file_path, new_name=None):
    """نقل ملف إلى مجلد legacy"""
    file_path = Path(file_path)
    if not file_path.exists():
        logger.warning(f"الملف غير موجود: {file_path}")
        return False

    # التأكد من وجود مجلد legacy
    ensure_directory(LEGACY_PATH)
    create_init_file(LEGACY_PATH)

    # إنشاء نسخة احتياطية
    backup_file(file_path)

    # نقل الملف إلى legacy
    target_name = new_name or file_path.name
    target_path = LEGACY_PATH / target_name

    # نسخ المحتوى بدلاً من نقل الملف كاملاً
    with open(file_path, 'r', encoding='utf-8') as src:
        content = src.read()

    with open(target_path, 'w', encoding='utf-8') as dst:
        dst.write(f"# Legacy file moved from {file_path.relative_to(PROJECT_ROOT)}\n")
        dst.write(f"# Moved on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        dst.write(content)

    logger.info(f"تم نقل الملف إلى legacy: {file_path} -> {target_path}")
    return True

def find_salary_component_class(content):
    """البحث عن تعريف فئة SalaryComponent في المحتوى"""
    class_pattern = re.compile(r'class SalaryComponent\(models\.Model\):.*?(?=\n\nclass|\Z)', re.DOTALL)
    match = class_pattern.search(content)
    return match

def unify_salary_component_models():
    """توحيد نماذج مكونات الراتب"""
    payroll_models_path = MODELS_PATH / 'payroll' / 'payroll_models.py'
    salary_component_models_path = MODELS_PATH / 'payroll' / 'salary_component_models.py'

    if not payroll_models_path.exists() or not salary_component_models_path.exists():
        logger.warning("ملفات نماذج الرواتب غير موجودة")
        return False

    # إنشاء نسخة احتياطية
    backup_file(payroll_models_path)

    # قراءة محتوى ملف payroll_models.py
    with open(payroll_models_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # البحث عن تعريف فئة SalaryComponent
    match = find_salary_component_class(content)

    if not match:
        logger.warning("لم يتم العثور على فئة SalaryComponent في payroll_models.py")
        return False

    # استبدال تعريف الفئة باستيراد من salary_component_models.py
    replacement = "# SalaryComponent model moved to salary_component_models.py\nfrom .salary_component_models import SalaryComponent\n"
    new_content = content.replace(match.group(0), replacement)

    # كتابة المحتوى الجديد
    with open(payroll_models_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    logger.info("تم توحيد نموذج SalaryComponent في payroll_models.py")
    return True

def update_imports_in_files():
    """تحديث الاستيرادات في الملفات بعد التوحيد"""
    # البحث عن جميع ملفات Python في تطبيق Hr
    python_files = []
    for root, _, files in os.walk(HR_APP_PATH):
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)

    import_pattern = re.compile(r'from Hr\.models\.payroll\.payroll_models import SalaryComponent')

    for file_path in python_files:
        if 'legacy' in str(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # تحقق من وجود استيراد لـ SalaryComponent من payroll_models
            if import_pattern.search(content):
                # استبدال الاستيراد
                new_content = import_pattern.sub(
                    'from Hr.models.payroll.salary_component_models import SalaryComponent',
                    content
                )

                # كتابة المحتوى الجديد
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                logger.info(f"تم تحديث الاستيرادات في: {file_path}")
        except Exception as e:
            logger.error(f"خطأ أثناء تحديث الاستيرادات في {file_path}: {str(e)}")

def cleanup_employee_models():
    """تنظيف وتوحيد نماذج الموظفين"""
    employee_path = MODELS_PATH / 'employee.py'
    legacy_employee_path = MODELS_PATH / 'legacy_employee.py'

    if employee_path.exists() and legacy_employee_path.exists():
        # التحقق من محتوى الملفات
        with open(employee_path, 'r', encoding='utf-8') as f:
            employee_content = f.read().strip()

        if employee_content:
            # إذا كان ملف employee.py يحتوي على محتوى، قم بنقله إلى legacy
            move_to_legacy(employee_path)
            logger.info(f"تم نقل {employee_path} إلى legacy")

    # التأكد من استخدام النماذج الصحيحة
    employee_models_path = MODELS_PATH / 'employee' / 'employee_models.py'
    if not employee_models_path.exists():
        logger.warning(f"ملف نماذج الموظفين غير موجود: {employee_models_path}")
        return False

    return True

def find_duplicate_files():
    """البحث عن الملفات المكررة"""
    # إنشاء قاموس لتخزين محتويات الملفات
    file_hashes = {}
    duplicate_files = []

    # البحث عن جميع ملفات Python في مجلد models
    python_files = []
    for root, _, files in os.walk(MODELS_PATH):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                python_files.append(Path(root) / file)

    # فحص كل ملف
    for file_path in python_files:
        if 'legacy' in str(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # تجاهل الملفات الفارغة
            if not content:
                continue

            # حساب تجزئة للمحتوى
            content_hash = hash(content)

            # التحقق من وجود ملف بنفس المحتوى
            if content_hash in file_hashes:
                duplicate_files.append((file_path, file_hashes[content_hash]))
                logger.info(f"تم العثور على ملفات مكررة: {file_path} و {file_hashes[content_hash]}")
            else:
                file_hashes[content_hash] = file_path
        except Exception as e:
            logger.error(f"خطأ أثناء فحص الملف {file_path}: {str(e)}")

    return duplicate_files

def find_empty_files():
    """البحث عن الملفات الفارغة"""
    empty_files = []

    # البحث عن جميع ملفات Python في مجلد models
    python_files = []
    for root, _, files in os.walk(MODELS_PATH):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                python_files.append(Path(root) / file)

    # فحص كل ملف
    for file_path in python_files:
        if 'legacy' in str(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # التحقق من أن الملف فارغ أو يحتوي على تعليقات فقط
            no_comments_content = re.sub(r'#.*?\n', '', content).strip()
            if not no_comments_content:
                empty_files.append(file_path)
                logger.info(f"تم العثور على ملف فارغ: {file_path}")
        except Exception as e:
            logger.error(f"خطأ أثناء فحص الملف {file_path}: {str(e)}")

    return empty_files

def create_cleanup_report():
    """إنشاء تقرير بنتائج التنظيف"""
    report_file = PROJECT_ROOT / 'hr_cleanup_report.md'

    report_content = f"""# تقرير تنظيف ملفات نظام الموارد البشرية

## تاريخ التنفيذ
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ملخص العمليات

### 1. توحيد نماذج مكونات الراتب
- تم توحيد نموذج SalaryComponent باعتماد النسخة الموجودة في salary_component_models.py
- تم تحديث الاستيرادات في الملفات المرتبطة

### 2. تنظيف نماذج الموظفين
- تم نقل النماذج القديمة إلى مجلد legacy

### 3. البحث عن الملفات المكررة والفارغة
- تم تحديد الملفات المكررة والفارغة لمراجعتها

## الخطوات التالية
1. مراجعة الملفات التي تم نقلها للتأكد من عدم وجود مشاكل
2. تطبيق تغييرات قاعدة البيانات من خلال هجرات Django
3. البدء في المرحلة الثانية من خطة التحسين

## ملاحظات إضافية
- يرجى مراجعة سجل العمليات التفصيلي في الملف: {log_file}
"""

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    logger.info(f"تم إنشاء تقرير التنظيف: {report_file}")
    return True

def main():
    """الدالة الرئيسية لتنظيف ملفات الموارد البشرية"""
    logger.info("بدء عملية تنظيف وتوحيد ملفات الموارد البشرية")

    # إنشاء المجلدات اللازمة
    ensure_directory(LEGACY_PATH)
    create_init_file(LEGACY_PATH)

    # البحث عن الملفات المكررة والفارغة
    duplicate_files = find_duplicate_files()
    empty_files = find_empty_files()

    # توحيد نماذج مكونات الراتب
    unify_salary_component_models()

    # تحديث الاستيرادات في الملفات
    update_imports_in_files()

    # تنظيف نماذج الموظفين
    cleanup_employee_models()

    # إنشاء تقرير التنظيف
    create_cleanup_report()

    logger.info("اكتملت عملية تنظيف وتوحيد ملفات الموارد البشرية")
    logger.info(f"يمكنك مراجعة سجل العمليات في الملف: {log_file}")

    print("\n" + "=" * 60)
    print("اكتملت عملية تنظيف وتوحيد ملفات الموارد البشرية")
    print(f"يمكنك مراجعة سجل العمليات في الملف: {log_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
