"""
مهام Celery للتخزين المؤقت
"""

from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
import logging

from ..services.cache_service import cache_service, warm_up_hr_cache
from ..services.cache_monitor import cache_monitor

logger = logging.getLogger('hr_cache_tasks')


@shared_task
def warm_up_cache():
    """تسخين التخزين المؤقت"""
    try:
        result = warm_up_hr_cache()
        logger.info(f'تم تسخين التخزين المؤقت: {result}')
        return result
    except Exception as e:
        logger.error(f'خطأ في تسخين التخزين المؤقت: {e}')
        return {'error': str(e)}


@shared_task
def cleanup_expired_cache():
    """تنظيف التخزين المؤقت المنتهي الصلاحية"""
    try:
        # تنظيف المقاييس القديمة
        cache_monitor._cleanup_old_metrics()
        
        # تنظيف البيانات المنتهية الصلاحية
        cleaned_count = 0
        
        # يمكن إضافة منطق تنظيف مخصص هنا
        
        logger.info(f'تم تنظيف {cleaned_count} عنصر من التخزين المؤقت')
        return {'cleaned_items': cleaned_count}
        
    except Exception as e:
        logger.error(f'خطأ في تنظيف التخزين المؤقت: {e}')
        return {'error': str(e)}


@shared_task
def generate_cache_report():
    """إنتاج تقرير التخزين المؤقت"""
    try:
        report = cache_monitor.generate_report(timedelta(days=1))
        
        # يمكن إرسال التقرير عبر البريد الإلكتروني هنا
        
        logger.info('تم إنتاج تقرير التخزين المؤقت')
        return {'report_generated': True}
        
    except Exception as e:
        logger.error(f'خطأ في إنتاج تقرير التخزين المؤقت: {e}')
        return {'error': str(e)}


@shared_task
def invalidate_cache_by_tags(tags):
    """إبطال التخزين المؤقت بالعلامات"""
    try:
        count = cache_service.invalidate_by_tags(tags)
        logger.info(f'تم إبطال {count} عنصر بالعلامات: {tags}')
        return {'invalidated_items': count}
        
    except Exception as e:
        logger.error(f'خطأ في إبطال التخزين المؤقت: {e}')
        return {'error': str(e)}