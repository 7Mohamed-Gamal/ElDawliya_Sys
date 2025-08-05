"""
مزخرفات الأداء لنظام الموارد البشرية
"""

import time
import functools
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def cache_result(timeout=300, key_prefix='hr_cache'):
    """
    مزخرف لتخزين نتائج الدوال في الذاكرة المؤقتة
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح فريد للتخزين المؤقت
            cache_key = f"{key_prefix}_{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # محاولة الحصول على النتيجة من الذاكرة المؤقتة
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # تنفيذ الدالة وحفظ النتيجة
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def monitor_performance(log_slow_queries=True, threshold=1.0):
    """
    مزخرف لمراقبة أداء الدوال
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # تسجيل الاستعلامات البطيئة
                if log_slow_queries and execution_time > threshold:
                    logger.warning(
                        f"Slow query detected: {func.__name__} took {execution_time:.2f} seconds"
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Error in {func.__name__} after {execution_time:.2f} seconds: {str(e)}"
                )
                raise
                
        return wrapper
    return decorator


def rate_limit(max_calls=100, period=3600):
    """
    مزخرف لتحديد معدل الاستدعاءات
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح فريد للمعدل
            rate_key = f"rate_limit_{func.__name__}_{hash(str(args))}"
            
            # الحصول على عدد الاستدعاءات الحالي
            current_calls = cache.get(rate_key, 0)
            
            if current_calls >= max_calls:
                raise Exception(f"Rate limit exceeded for {func.__name__}")
            
            # زيادة العداد
            cache.set(rate_key, current_calls + 1, period)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator