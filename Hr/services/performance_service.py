"""
خدمة تحسين الأداء الشاملة
"""

import logging
import time
from django.db import models, connection
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.db.models import Prefetch, Q, Count, Sum, Avg, Max, Min
from datetime import timedelta
import hashlib
import json

logger = logging.getLogger(__name__)


class PerformanceService:
    """خدمة تحسين الأداء الشاملة"""
    
    def __init__(self):
        self.cache_timeout = getattr(settings, 'PERFORMANCE_CACHE_TIMEOUT', 300)
        self.slow_query_threshold = getattr(settings, 'SLOW_QUERY_THRESHOLD', 1.0)
        self.enable_monitoring = getattr(settings, 'ENABLE_PERFORMANCE_MONITORING', True)
    
    def optimize_queryset(self, queryset, optimization_config=None):
        """
        تحسين QuerySet بناءً على التكوين المحدد
        """
        if not optimization_config:
            return queryset
        
        # تطبيق select_related
        if 'select_related' in optimization_config:
            queryset = queryset.select_related(*optimization_config['select_related'])
        
        # تطبيق prefetch_related
        if 'prefetch_related' in optimization_config:
            prefetch_list = []
            for prefetch in optimization_config['prefetch_related']:
                if isinstance(prefetch, dict):
                    # Prefetch متقدم مع queryset مخصص
                    prefetch_obj = Prefetch(
                        prefetch['lookup'],
                        queryset=prefetch.get('queryset'),
                        to_attr=prefetch.get('to_attr')
                    )
                    prefetch_list.append(prefetch_obj)
                else:
                    prefetch_list.append(prefetch)
            
            queryset = queryset.prefetch_related(*prefetch_list)
        
        # تطبيق only
        if 'only' in optimization_config:
            queryset = queryset.only(*optimization_config['only'])
        
        # تطبيق defer
        if 'defer' in optimization_config:
            queryset = queryset.defer(*optimization_config['defer'])
        
        # تطبيق distinct
        if optimization_config.get('distinct'):
            queryset = queryset.distinct()
        
        return queryset
    
    def get_optimized_employees(self, filters=None, optimization_level='full'):
        """
        الحصول على استعلام محسن للموظفين
        """
        from ..models import Employee
        
        queryset = Employee.objects.all()
        
        # تطبيق الفلاتر
        if filters:
            queryset = queryset.filter(**filters)
        
        # تحسينات حسب المستوى
        if optimization_level == 'basic':
            queryset = queryset.select_related('department', 'job_position')
        elif optimization_level == 'full':
            queryset = queryset.select_related(
                'department',
                'job_position', 
                'company',
                'branch',
                'user'
            ).prefetch_related(
                'employee_documents',
                'employee_contacts',
                'employee_emergency_contacts'
            )
        elif optimization_level == 'minimal':
            queryset = queryset.only(
                'id', 'first_name', 'last_name', 'employee_id',
                'department__name', 'job_position__name'
            ).select_related('department', 'job_position')
        
        return queryset
    
    def get_cached_data(self, cache_key, data_func, timeout=None, *args, **kwargs):
        """
        الحصول على البيانات مع التخزين المؤقت الذكي
        """
        if timeout is None:
            timeout = self.cache_timeout
        
        # محاولة الحصول على البيانات من التخزين المؤقت
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f'Cache hit for key: {cache_key}')
            return cached_data
        
        # تنفيذ الدالة وحفظ النتيجة
        start_time = time.time()
        data = data_func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # حفظ في التخزين المؤقت
        cache.set(cache_key, data, timeout)
        
        logger.debug(
            f'Cache miss for key: {cache_key}, '
            f'execution time: {execution_time:.2f}s'
        )
        
        return data
    
    def invalidate_cache_pattern(self, pattern):
        """
        إبطال التخزين المؤقت بناءً على نمط معين
        """
        try:
            # هذا يعتمد على نوع التخزين المؤقت المستخدم
            # للـ Redis يمكن استخدام KEYS pattern
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(pattern)
            else:
                # للتخزين المؤقت الافتراضي، نحتاج لحفظ قائمة المفاتيح
                cache_keys = cache.get('cache_keys_registry', set())
                keys_to_delete = [key for key in cache_keys if pattern in key]
                cache.delete_many(keys_to_delete)
                
                # تحديث السجل
                cache_keys -= set(keys_to_delete)
                cache.set('cache_keys_registry', cache_keys, 86400)
        except Exception as e:
            logger.error(f'خطأ في إبطال التخزين المؤقت: {e}')
    
    def create_cache_key(self, prefix, *args, **kwargs):
        """
        إنشاء مفتاح تخزين مؤقت فريد
        """
        # تحويل المعاملات إلى نص
        key_parts = [prefix]
        
        for arg in args:
            key_parts.append(str(arg))
        
        for key, value in sorted(kwargs.items()):
            key_parts.append(f'{key}:{value}')
        
        # إنشاء hash للمفتاح الطويل
        key_string = ':'.join(key_parts)
        if len(key_string) > 200:  # حد أقصى لطول المفتاح
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f'{prefix}:{key_hash}'
        
        return key_string
    
    def batch_process(self, queryset, batch_size=1000, process_func=None):
        """
        معالجة البيانات على دفعات لتحسين الذاكرة
        """
        if not process_func:
            return list(queryset)
        
        results = []
        total_count = queryset.count()
        
        for start in range(0, total_count, batch_size):
            batch = queryset[start:start + batch_size]
            batch_results = process_func(batch)
            
            if batch_results:
                if isinstance(batch_results, list):
                    results.extend(batch_results)
                else:
                    results.append(batch_results)
            
            logger.debug(f'Processed batch {start//batch_size + 1}/{(total_count + batch_size - 1)//batch_size}')
        
        return results
    
    def optimize_database_queries(self):
        """
        تحسين استعلامات قاعدة البيانات العامة
        """
        optimizations = []
        
        try:
            with connection.cursor() as cursor:
                # تحديث إحصائيات الجداول
                if connection.vendor == 'postgresql':
                    cursor.execute('ANALYZE;')
                    optimizations.append('تم تحديث إحصائيات PostgreSQL')
                elif connection.vendor == 'mysql':
                    cursor.execute("SHOW TABLES LIKE 'Hr_%'")
                    tables = cursor.fetchall()
                    for table in tables:
                        cursor.execute(f'ANALYZE TABLE {table[0]}')
                    optimizations.append(f'تم تحديث إحصائيات {len(tables)} جدول في MySQL')
                
                # إنشاء فهارس مفقودة
                missing_indexes = self.find_missing_indexes()
                for index_sql in missing_indexes:
                    try:
                        cursor.execute(index_sql)
                        optimizations.append(f'تم إنشاء فهرس: {index_sql}')
                    except Exception as e:
                        logger.warning(f'فشل في إنشاء الفهرس {index_sql}: {e}')
        
        except Exception as e:
            logger.error(f'خطأ في تحسين قاعدة البيانات: {e}')
        
        return optimizations
    
    def find_missing_indexes(self):
        """
        البحث عن الفهارس المفقودة
        """
        missing_indexes = []
        
        # فهارس أساسية للموظفين
        basic_indexes = [
            'CREATE INDEX IF NOT EXISTS idx_hr_employee_department ON Hr_employee(department_id);',
            'CREATE INDEX IF NOT EXISTS idx_hr_employee_active ON Hr_employee(is_active);',
            'CREATE INDEX IF NOT EXISTS idx_hr_employee_hire_date ON Hr_employee(hire_date);',
            'CREATE INDEX IF NOT EXISTS idx_hr_employee_employee_id ON Hr_employee(employee_id);',
        ]
        
        # فحص الفهارس الموجودة
        existing_indexes = self.get_existing_indexes()
        
        for index_sql in basic_indexes:
            index_name = self.extract_index_name(index_sql)
            if index_name not in existing_indexes:
                missing_indexes.append(index_sql)
        
        return missing_indexes
    
    def get_existing_indexes(self):
        """
        الحصول على قائمة الفهارس الموجودة
        """
        existing_indexes = set()
        
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT indexname FROM pg_indexes 
                        WHERE tablename LIKE 'hr_%'
                    """)
                elif connection.vendor == 'mysql':
                    cursor.execute("""
                        SELECT INDEX_NAME FROM INFORMATION_SCHEMA.STATISTICS 
                        WHERE TABLE_SCHEMA = DATABASE() 
                        AND TABLE_NAME LIKE 'Hr_%'
                    """)
                elif connection.vendor == 'sqlite':
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type = 'index' 
                        AND tbl_name LIKE 'Hr_%'
                    """)
                
                for row in cursor.fetchall():
                    existing_indexes.add(row[0])
        
        except Exception as e:
            logger.error(f'خطأ في الحصول على الفهارس الموجودة: {e}')
        
        return existing_indexes
    
    def extract_index_name(self, index_sql):
        """
        استخراج اسم الفهرس من SQL
        """
        import re
        match = re.search(r'INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)', index_sql, re.IGNORECASE)
        return match.group(1) if match else None
    
    def get_performance_metrics(self):
        """
        الحصول على مقاييس الأداء الحالية
        """
        metrics = {
            'timestamp': timezone.now().isoformat(),
            'database': {
                'query_count': len(connection.queries),
                'slow_queries': self.get_slow_queries_count(),
            },
            'cache': {
                'hit_rate': self.get_cache_hit_rate(),
                'memory_usage': self.get_cache_memory_usage(),
            },
            'system': {
                'memory_usage': self.get_system_memory_usage(),
                'cpu_usage': self.get_cpu_usage(),
            }
        }
        
        return metrics
    
    def get_slow_queries_count(self):
        """
        الحصول على عدد الاستعلامات البطيئة
        """
        slow_queries = cache.get('slow_queries_log', [])
        return len(slow_queries)
    
    def get_cache_hit_rate(self):
        """
        حساب معدل إصابة التخزين المؤقت
        """
        try:
            # هذا يعتمد على نوع التخزين المؤقت
            # يمكن تخصيصه حسب Redis أو Memcached
            stats = cache.get('cache_stats', {'hits': 0, 'misses': 0})
            total = stats['hits'] + stats['misses']
            return stats['hits'] / total if total > 0 else 0
        except Exception:
            return 0.0
    
    def get_cache_memory_usage(self):
        """
        الحصول على استخدام ذاكرة التخزين المؤقت
        """
        try:
            # هذا يحتاج تخصيص حسب نوع التخزين المؤقت
            return 0  # قيمة افتراضية
        except Exception:
            return 0
    
    def get_system_memory_usage(self):
        """
        الحصول على استخدام ذاكرة النظام
        """
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            return 0
    
    def get_cpu_usage(self):
        """
        الحصول على استخدام المعالج
        """
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            return 0
    
    def optimize_for_report(self, report_type, parameters=None):
        """
        تحسين خاص للتقارير
        """
        optimization_configs = {
            'employee_list': {
                'select_related': ['department', 'job_position', 'company'],
                'only': ['id', 'first_name', 'last_name', 'employee_id', 
                        'department__name', 'job_position__name']
            },
            'attendance_report': {
                'select_related': ['employee', 'employee__department'],
                'prefetch_related': ['employee__employee_contacts']
            },
            'payroll_report': {
                'select_related': ['employee', 'employee__department', 'employee__job_position'],
                'prefetch_related': ['payroll_allowances', 'payroll_deductions']
            }
        }
        
        return optimization_configs.get(report_type, {})
    
    def clear_expired_cache(self):
        """
        مسح التخزين المؤقت المنتهي الصلاحية
        """
        try:
            # هذا يعتمد على نوع التخزين المؤقت
            # للـ Redis يمكن استخدام TTL
            cleared_count = 0
            
            # مسح الاستعلامات البطيئة القديمة
            slow_queries = cache.get('slow_queries_log', [])
            if slow_queries:
                # الاحتفاظ بآخر 100 استعلام فقط
                if len(slow_queries) > 100:
                    cache.set('slow_queries_log', slow_queries[-100:], 3600)
                    cleared_count += len(slow_queries) - 100
            
            # مسح إحصائيات الأداء القديمة
            today = timezone.now().date()
            for i in range(7, 30):  # مسح الإحصائيات الأقدم من أسبوع
                old_date = today - timedelta(days=i)
                old_key = f'performance_stats_{old_date.isoformat()}'
                if cache.get(old_key):
                    cache.delete(old_key)
                    cleared_count += 1
            
            return cleared_count
        
        except Exception as e:
            logger.error(f'خطأ في مسح التخزين المؤقت: {e}')
            return 0


# إنشاء مثيل الخدمة
performance_service = PerformanceService()