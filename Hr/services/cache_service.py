"""
خدمة التخزين المؤقت المتقدمة
"""

import json
import hashlib
import logging
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone
from django.core.serializers import serialize
from django.apps import apps
import redis
import pickle

logger = logging.getLogger('hr_cache')


class CacheService:
    """خدمة التخزين المؤقت المتقدمة"""
    
    # مستويات التخزين المؤقت
    CACHE_LEVELS = {
        'L1': 'default',  # ذاكرة محلية سريعة
        'L2': 'redis',    # Redis للبيانات المشتركة
        'L3': 'database', # قاعدة البيانات للبيانات الدائمة
    }
    
    # أوقات انتهاء الصلاحية الافتراضية
    DEFAULT_TIMEOUTS = {
        'short': 300,      # 5 دقائق
        'medium': 1800,    # 30 دقيقة
        'long': 3600,      # ساعة واحدة
        'daily': 86400,    # يوم واحد
        'weekly': 604800,  # أسبوع واحد
    }
    
    # بادئات المفاتيح
    KEY_PREFIXES = {
        'employee': 'emp',
        'department': 'dept',
        'attendance': 'att',
        'payroll': 'pay',
        'report': 'rpt',
        'search': 'srch',
        'api': 'api',
        'session': 'sess',
        'query': 'qry',
        'template': 'tpl',
    }
    
    def __init__(self):
        self.redis_client = self._get_redis_client()
        self.stats = CacheStats()
    
    def _get_redis_client(self):
        """الحصول على عميل Redis"""
        try:
            redis_config = getattr(settings, 'CACHES', {}).get('redis', {})
            if redis_config:
                location = redis_config.get('LOCATION', 'redis://127.0.0.1:6379/1')
                return redis.from_url(location)
            return None
        except Exception as e:
            logger.warning(f'فشل في الاتصال بـ Redis: {e}')
            return None
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """إنتاج مفتاح تخزين مؤقت فريد"""
        
        # استخدام البادئة المحددة أو الافتراضية
        key_prefix = self.KEY_PREFIXES.get(prefix, prefix)
        
        # بناء المفتاح من المعاملات
        key_parts = [key_prefix]
        
        # إضافة المعاملات الموضعية
        for arg in args:
            if isinstance(arg, (int, str)):
                key_parts.append(str(arg))
            elif isinstance(arg, (list, tuple)):
                key_parts.append('_'.join(map(str, arg)))
            else:
                key_parts.append(str(hash(str(arg))))
        
        # إضافة المعاملات المسماة
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            kwargs_str = '_'.join([f'{k}:{v}' for k, v in sorted_kwargs])
            key_parts.append(hashlib.md5(kwargs_str.encode()).hexdigest()[:8])
        
        return ':'.join(key_parts)
    
    def set(self, key: str, value: Any, timeout: Union[int, str] = 'medium', 
            level: str = 'L1', tags: List[str] = None) -> bool:
        """حفظ قيمة في التخزين المؤقت"""
        
        try:
            # تحديد وقت انتهاء الصلاحية
            if isinstance(timeout, str):
                timeout = self.DEFAULT_TIMEOUTS.get(timeout, self.DEFAULT_TIMEOUTS['medium'])
            
            # تسلسل البيانات
            serialized_value = self._serialize_value(value)
            
            # حفظ في المستوى المحدد
            success = False
            
            if level == 'L1' or level == 'default':
                success = cache.set(key, serialized_value, timeout)
            
            elif level == 'L2' and self.redis_client:
                success = self.redis_client.setex(key, timeout, serialized_value)
            
            # حفظ العلامات للإبطال الذكي
            if success and tags:
                self._save_tags(key, tags, timeout)
            
            # تسجيل الإحصائيات
            if success:
                self.stats.record_set(key, len(str(serialized_value)))
                logger.debug(f'تم حفظ المفتاح في التخزين المؤقت: {key}')
            
            return success
            
        except Exception as e:
            logger.error(f'خطأ في حفظ التخزين المؤقت {key}: {e}')
            return False
    
    def get(self, key: str, level: str = 'L1', default: Any = None) -> Any:
        """استرجاع قيمة من التخزين المؤقت"""
        
        try:
            value = None
            
            # البحث في المستوى المحدد
            if level == 'L1' or level == 'default':
                value = cache.get(key)
            
            elif level == 'L2' and self.redis_client:
                redis_value = self.redis_client.get(key)
                if redis_value:
                    value = redis_value.decode('utf-8')
            
            # إلغاء تسلسل البيانات
            if value is not None:
                deserialized_value = self._deserialize_value(value)
                self.stats.record_hit(key)
                logger.debug(f'تم العثور على المفتاح في التخزين المؤقت: {key}')
                return deserialized_value
            
            # تسجيل عدم وجود المفتاح
            self.stats.record_miss(key)
            return default
            
        except Exception as e:
            logger.error(f'خطأ في استرجاع التخزين المؤقت {key}: {e}')
            self.stats.record_miss(key)
            return default
    
    def delete(self, key: str, level: str = 'L1') -> bool:
        """حذف مفتاح من التخزين المؤقت"""
        
        try:
            success = False
            
            if level == 'L1' or level == 'default':
                success = cache.delete(key)
            
            elif level == 'L2' and self.redis_client:
                success = bool(self.redis_client.delete(key))
            
            if success:
                self.stats.record_delete(key)
                logger.debug(f'تم حذف المفتاح من التخزين المؤقت: {key}')
            
            return success
            
        except Exception as e:
            logger.error(f'خطأ في حذف التخزين المؤقت {key}: {e}')
            return False
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """إبطال التخزين المؤقت بالعلامات"""
        
        try:
            deleted_count = 0
            
            for tag in tags:
                # الحصول على جميع المفاتيح المرتبطة بالعلامة
                tag_key = f'tag:{tag}'
                tagged_keys = self.get(tag_key, level='L2', default=[])
                
                if isinstance(tagged_keys, str):
                    tagged_keys = json.loads(tagged_keys)
                
                # حذف جميع المفاتيح المرتبطة
                for key in tagged_keys:
                    if self.delete(key, level='L1'):
                        deleted_count += 1
                    if self.delete(key, level='L2'):
                        deleted_count += 1
                
                # حذف علامة العلامة نفسها
                self.delete(tag_key, level='L2')
            
            logger.info(f'تم إبطال {deleted_count} مفتاح بالعلامات: {tags}')
            return deleted_count
            
        except Exception as e:
            logger.error(f'خطأ في إبطال التخزين المؤقت بالعلامات {tags}: {e}')
            return 0
    
    def clear_pattern(self, pattern: str) -> int:
        """مسح جميع المفاتيح التي تطابق نمط معين"""
        
        try:
            deleted_count = 0
            
            # مسح من Redis
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted_count += self.redis_client.delete(*keys)
            
            # مسح من Django cache (أصعب لأنه لا يدعم البحث بالنمط)
            # نحتاج لتتبع المفاتيح يدوياً
            
            logger.info(f'تم مسح {deleted_count} مفتاح بالنمط: {pattern}')
            return deleted_count
            
        except Exception as e:
            logger.error(f'خطأ في مسح النمط {pattern}: {e}')
            return 0
    
    def get_or_set(self, key: str, callable_func, timeout: Union[int, str] = 'medium',
                   level: str = 'L1', tags: List[str] = None) -> Any:
        """استرجاع من التخزين المؤقت أو تنفيذ الدالة وحفظ النتيجة"""
        
        # محاولة الاسترجاع أولاً
        value = self.get(key, level)
        
        if value is not None:
            return value
        
        # تنفيذ الدالة وحفظ النتيجة
        try:
            result = callable_func()
            self.set(key, result, timeout, level, tags)
            return result
        except Exception as e:
            logger.error(f'خطأ في تنفيذ الدالة للمفتاح {key}: {e}')
            return None
    
    def cache_queryset(self, queryset: QuerySet, key: str, timeout: Union[int, str] = 'medium',
                      tags: List[str] = None) -> List[Dict]:
        """تخزين نتائج QuerySet مؤقتاً"""
        
        def get_queryset_data():
            # تحويل QuerySet إلى قائمة من القواميس
            return list(queryset.values())
        
        return self.get_or_set(key, get_queryset_data, timeout, tags=tags)
    
    def cache_template_fragment(self, fragment_name: str, vary_on: List[str] = None,
                               timeout: Union[int, str] = 'medium') -> str:
        """إنتاج مفتاح لتخزين جزء من القالب مؤقتاً"""
        
        if isinstance(timeout, str):
            timeout = self.DEFAULT_TIMEOUTS.get(timeout, self.DEFAULT_TIMEOUTS['medium'])
        
        return make_template_fragment_key(fragment_name, vary_on or [])
    
    def warm_up_cache(self, warm_up_functions: Dict[str, callable]) -> Dict[str, bool]:
        """تسخين التخزين المؤقت بالبيانات المهمة"""
        
        results = {}
        
        for name, func in warm_up_functions.items():
            try:
                logger.info(f'بدء تسخين التخزين المؤقت: {name}')
                func()
                results[name] = True
                logger.info(f'تم تسخين التخزين المؤقت بنجاح: {name}')
            except Exception as e:
                logger.error(f'فشل في تسخين التخزين المؤقت {name}: {e}')
                results[name] = False
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات التخزين المؤقت"""
        return self.stats.get_stats()
    
    def _serialize_value(self, value: Any) -> str:
        """تسلسل القيمة للتخزين"""
        
        if isinstance(value, (str, int, float, bool)):
            return json.dumps({'type': 'simple', 'value': value})
        
        elif isinstance(value, (list, dict, tuple)):
            return json.dumps({'type': 'json', 'value': value})
        
        else:
            # استخدام pickle للكائنات المعقدة
            pickled = pickle.dumps(value)
            return json.dumps({
                'type': 'pickle',
                'value': pickled.hex()
            })
    
    def _deserialize_value(self, serialized: str) -> Any:
        """إلغاء تسلسل القيمة من التخزين"""
        
        try:
            data = json.loads(serialized)
            value_type = data.get('type', 'simple')
            value = data.get('value')
            
            if value_type == 'simple':
                return value
            elif value_type == 'json':
                return value
            elif value_type == 'pickle':
                pickled_bytes = bytes.fromhex(value)
                return pickle.loads(pickled_bytes)
            
            return value
            
        except Exception as e:
            logger.error(f'خطأ في إلغاء تسلسل القيمة: {e}')
            return None
    
    def _save_tags(self, key: str, tags: List[str], timeout: int):
        """حفظ العلامات للمفتاح"""
        
        for tag in tags:
            tag_key = f'tag:{tag}'
            
            # الحصول على المفاتيح الحالية للعلامة
            current_keys = self.get(tag_key, level='L2', default=[])
            if isinstance(current_keys, str):
                current_keys = json.loads(current_keys)
            
            # إضافة المفتاح الجديد
            if key not in current_keys:
                current_keys.append(key)
            
            # حفظ القائمة المحدثة
            self.set(tag_key, current_keys, timeout, level='L2')


class CacheStats:
    """إحصائيات التخزين المؤقت"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.total_size = 0
        self.start_time = timezone.now()
    
    def record_hit(self, key: str):
        """تسجيل إصابة"""
        self.hits += 1
    
    def record_miss(self, key: str):
        """تسجيل عدم إصابة"""
        self.misses += 1
    
    def record_set(self, key: str, size: int):
        """تسجيل حفظ"""
        self.sets += 1
        self.total_size += size
    
    def record_delete(self, key: str):
        """تسجيل حذف"""
        self.deletes += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على الإحصائيات"""
        
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        uptime = timezone.now() - self.start_time
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'sets': self.sets,
            'deletes': self.deletes,
            'total_size': self.total_size,
            'uptime_seconds': uptime.total_seconds(),
            'requests_per_second': total_requests / uptime.total_seconds() if uptime.total_seconds() > 0 else 0
        }


class CacheDecorator:
    """مُزخرف للتخزين المؤقت"""
    
    def __init__(self, timeout: Union[int, str] = 'medium', key_prefix: str = 'func',
                 level: str = 'L1', tags: List[str] = None):
        self.timeout = timeout
        self.key_prefix = key_prefix
        self.level = level
        self.tags = tags or []
        self.cache_service = CacheService()
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # إنتاج مفتاح فريد للدالة
            key = self.cache_service.generate_key(
                self.key_prefix,
                func.__name__,
                *args,
                **kwargs
            )
            
            # محاولة الاسترجاع من التخزين المؤقت
            result = self.cache_service.get(key, self.level)
            
            if result is not None:
                return result
            
            # تنفيذ الدالة وحفظ النتيجة
            result = func(*args, **kwargs)
            self.cache_service.set(key, result, self.timeout, self.level, self.tags)
            
            return result
        
        return wrapper


# مثيل عام للخدمة
cache_service = CacheService()

# مُزخرفات جاهزة للاستخدام
def cache_result(timeout='medium', key_prefix='func', level='L1', tags=None):
    """مُزخرف لتخزين نتيجة الدالة مؤقتاً"""
    return CacheDecorator(timeout, key_prefix, level, tags)

def cache_employee_data(timeout='long'):
    """مُزخرف لتخزين بيانات الموظفين"""
    return CacheDecorator(timeout, 'employee', 'L1', ['employee'])

def cache_report_data(timeout='daily'):
    """مُزخرف لتخزين بيانات التقارير"""
    return CacheDecorator(timeout, 'report', 'L2', ['report'])

def cache_api_response(timeout='medium'):
    """مُزخرف لتخزين استجابات API"""
    return CacheDecorator(timeout, 'api', 'L1', ['api'])


# دوال مساعدة للتخزين المؤقت الذكي
def invalidate_employee_cache(employee_id: int = None):
    """إبطال تخزين بيانات الموظفين مؤقتاً"""
    tags = ['employee']
    if employee_id:
        tags.append(f'employee:{employee_id}')
    
    return cache_service.invalidate_by_tags(tags)

def invalidate_department_cache(department_id: int = None):
    """إبطال تخزين بيانات الأقسام مؤقتاً"""
    tags = ['department']
    if department_id:
        tags.append(f'department:{department_id}')
    
    return cache_service.invalidate_by_tags(tags)

def invalidate_report_cache():
    """إبطال تخزين التقارير مؤقتاً"""
    return cache_service.invalidate_by_tags(['report'])

def warm_up_hr_cache():
    """تسخين التخزين المؤقت لبيانات الموارد البشرية"""
    
    def warm_employees():
        from ..models_enhanced import Employee
        employees = Employee.objects.select_related('department', 'job_position').all()
        key = cache_service.generate_key('employee', 'all')
        cache_service.set(key, list(employees.values()), 'long', tags=['employee'])
    
    def warm_departments():
        from ..models_enhanced import Department
        departments = Department.objects.all()
        key = cache_service.generate_key('department', 'all')
        cache_service.set(key, list(departments.values()), 'long', tags=['department'])
    
    def warm_attendance_stats():
        from django.utils import timezone
        from ..models_enhanced import AttendanceRecord
        today = timezone.now().date()
        attendance_count = AttendanceRecord.objects.filter(date=today).count()
        key = cache_service.generate_key('attendance', 'today_count')
        cache_service.set(key, attendance_count, 'daily', tags=['attendance'])
    
    warm_up_functions = {
        'employees': warm_employees,
        'departments': warm_departments,
        'attendance_stats': warm_attendance_stats,
    }
    
    return cache_service.warm_up_cache(warm_up_functions)