"""
تنظيف الملفات المكررة وغير المستخدمة

هذا البرنامج يقوم بتنفيذ المرحلة الأولى من خطة التحسين:
- تحديد وإزالة الملفات المكررة
- توحيد الملفات المتشابهة في الوظائف
- نقل النماذج القديمة إلى مجلد legacy
"""

import os
import shutil
import logging
from pathlib import Path
import sys

# إعداد السجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cleanup_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

HR_APP_PATH = Path('Hr')
MODELS_PATH = HR_APP_PATH / 'models'
LEGACY_PATH = MODELS_PATH / 'legacy'

def ensure_legacy_directory():
    """التأكد من وجود مجلد legacy"""
    if not LEGACY_PATH.exists():
        LEGACY_PATH.mkdir(parents=True, exist_ok=True)
        init_file = LEGACY_PATH / '__init__.py'
        if not init_file.exists():
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('# Legacy models module\n')
        logger.info(f"تم إنشاء مجلد legacy في {LEGACY_PATH}")

def move_to_legacy(file_path, new_name=None):
    """نقل ملف إلى مجلد legacy"""
    if not Path(file_path).exists():
        logger.warning(f"الملف {file_path} غير موجود")
        return False

    target_name = new_name or Path(file_path).name
    target_path = LEGACY_PATH / target_name

    try:
        shutil.copy2(file_path, target_path)
        logger.info(f"تم نسخ الملف {file_path} إلى {target_path}")
        return True
    except Exception as e:
        logger.error(f"خطأ أثناء نقل الملف {file_path}: {str(e)}")
        return False

def clean_module_imports(module_path):
    """تنظيف استيرادات مكررة في الوحدة"""
    if not Path(module_path).exists():
        logger.warning(f"الملف {module_path} غير موجود")
        return

    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # تنفيذ تنظيف الاستيرادات هنا
        # (هذا مثال فقط، يمكن تطويره حسب الحاجة)

        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"تم تنظيف استيرادات الوحدة {module_path}")
    except Exception as e:
        logger.error(f"خطأ أثناء تنظيف الوحدة {module_path}: {str(e)}")

def update_salary_component_imports():
    """توحيد نماذج مكونات الراتب"""
    # تحديث الاستيرادات في ملف payroll_models.py
    payroll_models_path = MODELS_PATH / 'payroll' / 'payroll_models.py'
    if not payroll_models_path.exists():
        logger.warning(f"الملف {payroll_models_path} غير موجود")
        return False

    try:
        with open(payroll_models_path, 'r', encoding='utf-8') as f:
            content = f.readlines()

        # نبحث عن تعريف فئة SalaryComponent
        start_idx = None
        end_idx = None

        for i, line in enumerate(content):
            if 'class SalaryComponent(models.Model):' in line:
                start_idx = i
            elif start_idx is not None and line.strip() == '' and i > start_idx + 1:
                # نحن نفترض أن الفئة تنتهي بسطر فارغ بعد آخر تعريف
                if 'class' in content[i+1] or i == len(content) - 1:
                    end_idx = i
                    break

        if start_idx is not None and end_idx is not None:
            # استبدال تعريف الفئة باستيراد من salary_component_models.py
            new_content = content[:start_idx]
            new_content.append('# SalaryComponent model moved to salary_component_models.py\n')
            new_content.append('from .salary_component_models import SalaryComponent\n')
            new_content.append('\n')
            new_content.extend(content[end_idx+1:])

            with open(payroll_models_path, 'w', encoding='utf-8') as f:
                f.writelines(new_content)

            logger.info(f"تم توحيد نموذج SalaryComponent في {payroll_models_path}")
            return True
    except Exception as e:
        logger.error(f"خطأ أثناء تحديث نموذج SalaryComponent: {str(e)}")

    return False

def main():
    """المهمة الرئيسية لتنظيف الملفات"""
    logger.info("بدء عملية تنظيف الملفات المكررة وغير المستخدمة")

    # التأكد من وجود مجلد legacy
    ensure_legacy_directory()

    # توحيد نماذج مكونات الراتب
    update_salary_component_imports()

    logger.info("اكتملت عملية تنظيف الملفات")

if __name__ == "__main__":
    main()
