"""
خدمة تحسين الأداء العامة
"""

from django.core.cache import cache
from django.db import connection, transaction
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg, Max, Min
from datetime import timedelta
import logging
import time
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)


class PerformanceService:
    """خدمة تحسين الأداء العامة"""
    
    def __init__(self):
        self.cache_timeout = getattr(settings, 'HR_CACHE_TIMEOUT', 300)
        self.performance_metrics = defaultdict(list)
        self.lock = threading.Lock()
    
    def monitor_query_performance(self, func_name, execution_time, query_count):
        """مراقبة أداء الاستعلامات"""
        with self.lock:
            self.performance_metrics[func_name].append({
                'execution_time': execution_time,
                'query_count': query_count,
                'timestamp': timezone.now()
            })
            
            # الاحتفاظ بآخر 100 قياس فقط
            if len(self.performance_metrics[func_name]) > 100:
                self.performance_metrics[func_name] = self.performance_metrics[func_name][-100:]
    
    def get_performance_metrics(self, func_name=None):
        """الحصول على مقاييس الأداء"""
        with self.lock:
            if func_name:
                return self.performance_metrics.get(func_name, [])
            return dict(self.performance_metrics)
    
    def get_slow_queries_report(self, threshold=1.0):
        """تقرير الاستعلامات البطيئة"""
        slow_queries = {}
        
        with self.lock:
            for func_name, metrics in self.performance_metrics.items():
                slow_executions = [
                    m for m in metrics 
                    if m['execution_time'] > threshold
                ]
                
                if slow_executions:
                    slow_queries[func_name] = {
                        'count': len(slow_executions),
                        'avg_time': sum(m['execution_time'] for m in slow_executions) / len(slow_executions),
                        'max_time': max(m['execution_time'] for m in slow_executions),
                        'recent_slow': slow_executions[-5:]  # آخر 5 تنفيذات بطيئة
                    }
        
        return slow_queries
    
    def optimize_database_connections(self):
        """تحسين اتصالات قاعدة البيانات"""
        try:
            # إغلاق الاتصالات غير المستخدمة
            connection.close()
            
            # تنظيف التخزين المؤقت للاستعلامات
            if hasattr(connection, 'queries'):
                connection.queries.clear()
            
            logger.info("تم تحسين اتصالات قاعدة البيانات")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحسين اتصالات قاعدة البيانات: {e}")
            return False
    
    def clear_expired_cache(self):
        """مسح التخزين المؤقت المنتهي الصلاحية"""
        try:
            # مسح التخزين المؤقت المرتبط بالموارد البشرية
            cache_patterns = [
                'employee_*',
                'department_*',
                'attendance_*',
                'payroll_*',
                'leave_*',
                'dashboard_*'
            ]
            
            cleared_count = 0
            for pattern in cache_patterns:
                # هذا يتطلب تنفيذ مخصص حسب نوع التخزين المؤقت
                # في الوقت الحالي، سنمسح بعض المفاتيح المعروفة
                keys_to_clear = [
                    f'{pattern.replace("*", "")}summary',
                    f'{pattern.replace("*", "")}stats',
                    f'{pattern.replace("*", "")}list'
                ]
                
                for key in keys_to_clear:
                    if cache.delete(key):
                        cleared_count += 1
            
            logger.info(f"تم مسح {cleared_count} مفتاح من التخزين المؤقت")
            return cleared_count
            
        except Exception as e:
            logger.error(f"خطأ في مسح التخزين المؤقت: {e}")
            return 0
    
    def analyze_memory_usage(self):
        """تحليل استخدام الذاكرة"""
        try:
            import psutil
            import os
            
            # معلومات العملية الحالية
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            analysis = {
                'rss': memory_info.rss / 1024 / 1024,  # MB
                'vms': memory_info.vms / 1024 / 1024,  # MB
                'percent': process.memory_percent(),
                'available_memory': psutil.virtual_memory().available / 1024 / 1024,  # MB
                'total_memory': psutil.virtual_memory().total / 1024 / 1024,  # MB
            }
            
            # تحذيرات الذاكرة
            if analysis['percent'] > 80:
                logger.warning(f"استخدام ذاكرة عالي: {analysis['percent']:.1f}%")
            
            return analysis
            
        except ImportError:
            logger.warning("مكتبة psutil غير متاحة لتحليل الذاكرة")
            return {'error': 'psutil not available'}
        except Exception as e:
            logger.error(f"خطأ في تحليل الذاكرة: {e}")
            return {'error': str(e)}
    
    def optimize_queryset_for_large_data(self, queryset, batch_size=1000):
        """تحسين QuerySet للبيانات الكبيرة"""
        try:
            total_count = queryset.count()
            
            if total_count > batch_size:
                logger.info(f"استخدام التحميل المجمع للبيانات الكبيرة: {total_count} سجل")
                
                # استخدام iterator للبيانات الكبيرة
                return queryset.iterator(chunk_size=batch_size)
            else:
                return queryset
                
        except Exception as e:
            logger.error(f"خطأ في تحسين QuerySet: {e}")
            return queryset
    
    def bulk_create_optimized(self, model_class, objects_data, batch_size=1000):
        """إنشاء مجمع محسن"""
        try:
            objects_to_create = []
            created_objects = []
            
            for i, obj_data in enumerate(objects_data):
                if isinstance(obj_data, dict):
                    obj = model_class(**obj_data)
                else:
                    obj = obj_data
                
                objects_to_create.append(obj)
                
                # إنشاء دفعة عند الوصول لحجم الدفعة
                if len(objects_to_create) >= batch_size:
                    batch_created = model_class.objects.bulk_create(
                        objects_to_create,
                        ignore_conflicts=True
                    )
                    created_objects.extend(batch_created)
                    objects_to_create = []
            
            # إنشاء الدفعة الأخيرة
            if objects_to_create:
                batch_created = model_class.objects.bulk_create(
                    objects_to_create,
                    ignore_conflicts=True
                )
                created_objects.extend(batch_created)
            
            logger.info(f"تم إنشاء {len(created_objects)} كائن بشكل مجمع")
            return created_objects
            
        except Exception as e:
            logger.error(f"خطأ في الإنشاء المجمع: {e}")
            return []
    
    def bulk_update_optimized(self, model_class, updates_data, batch_size=1000):
        """تحديث مجمع محسن"""
        try:
            updated_count = 0
            
            # تجميع التحديثات حسب الحقول
            updates_by_fields = defaultdict(list)
            
            for update_data in updates_data:
                obj_id = update_data.pop('id')
                fields_key = tuple(sorted(update_data.keys()))
                updates_by_fields[fields_key].append((obj_id, update_data))
            
            # تنفيذ التحديثات المجمعة
            for fields, updates in updates_by_fields.items():
                for i in range(0, len(updates), batch_size):
                    batch = updates[i:i + batch_size]
                    
                    # إنشاء استعلام التحديث المجمع
                    ids = [update[0] for update in batch]
                    
                    # تحديث كل حقل على حدة (Django لا يدعم bulk_update متقدم)
                    for field in fields:
                        values = {update[0]: update[1][field] for update in batch}
                        
                        # استخدام case/when للتحديث المجمع
                        from django.db.models import Case, When, Value
                        
                        cases = [
                            When(id=obj_id, then=Value(value))
                            for obj_id, value in values.items()
                        ]
                        
                        updated = model_class.objects.filter(
                            id__in=ids
                        ).update(**{field: Case(*cases)})
                        
                        updated_count += updated
            
            logger.info(f"تم تحديث {updated_count} سجل بشكل مجمع")
            return updated_count
            
        except Exception as e:
            logger.error(f"خطأ في التحديث المجمع: {e}")
            return 0
    
    def optimize_database_indexes(self):
        """تحسين فهارس قاعدة البيانات"""
        try:
            optimization_results = []
            
            with connection.cursor() as cursor:
                if connection.vendor == 'mysql':
                    # تحليل الجداول
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        if table_name.startswith('Hr_'):
                            cursor.execute(f"ANALYZE TABLE {table_name}")
                            result = cursor.fetchone()
                            optimization_results.append({
                                'table': table_name,
                                'status': result[3] if result else 'unknown'
                            })
                
                elif connection.vendor == 'postgresql':
                    # تحديث إحصائيات الجداول
                    cursor.execute("""
                        SELECT tablename FROM pg_tables 
                        WHERE schemaname = 'public' AND tablename LIKE 'Hr_%'
                    """)
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        cursor.execute(f"ANALYZE {table_name}")
                        optimization_results.append({
                            'table': table_name,
                            'status': 'analyzed'
                        })
            
            logger.info(f"تم تحسين {len(optimization_results)} جدول")
            return optimization_results
            
        except Exception as e:
            logger.error(f"خطأ في تحسين الفهارس: {e}")
            return []
    
    def get_database_statistics(self):
        """الحصول على إحصائيات قاعدة البيانات"""
        try:
            stats = {
                'vendor': connection.vendor,
                'tables': {},
                'total_size': 0,
                'connection_info': {
                    'host': connection.settings_dict.get('HOST', 'localhost'),
                    'port': connection.settings_dict.get('PORT', 'default'),
                    'name': connection.settings_dict.get('NAME', 'unknown')
                }
            }
            
            with connection.cursor() as cursor:
                if connection.vendor == 'mysql':
                    # حجم قاعدة البيانات
                    cursor.execute("""
                        SELECT table_name, 
                               ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb,
                               table_rows
                        FROM information_schema.tables 
                        WHERE table_schema = DATABASE() AND table_name LIKE 'Hr_%'
                    """)
                    
                    for row in cursor.fetchall():
                        table_name, size_mb, row_count = row
                        stats['tables'][table_name] = {
                            'size_mb': float(size_mb) if size_mb else 0,
                            'row_count': int(row_count) if row_count else 0
                        }
                        stats['total_size'] += float(size_mb) if size_mb else 0
                
                elif connection.vendor == 'postgresql':
                    # حجم الجداول
                    cursor.execute("""
                        SELECT schemaname, tablename, 
                               pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                               pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                        FROM pg_tables 
                        WHERE schemaname = 'public' AND tablename LIKE 'Hr_%'
                    """)
                    
                    for row in cursor.fetchall():
                        schema, table_name, size_pretty, size_bytes = row
                        stats['tables'][table_name] = {
                            'size_mb': size_bytes / 1024 / 1024,
                            'size_pretty': size_pretty
                        }
                        stats['total_size'] += size_bytes / 1024 / 1024
                
                elif connection.vendor == 'sqlite':
                    # معلومات أساسية لـ SQLite
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Hr_%'")
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        row_count = cursor.fetchone()[0]
                        
                        stats['tables'][table_name] = {
                            'row_count': row_count,
                            'size_mb': 0  # SQLite لا يوفر معلومات حجم الجدول بسهولة
                        }
            
            return stats
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات قاعدة البيانات: {e}")
            return {'error': str(e)}
    
    def schedule_maintenance_tasks(self):
        """جدولة مهام الصيانة"""
        try:
            maintenance_results = {
                'cache_cleared': self.clear_expired_cache(),
                'connections_optimized': self.optimize_database_connections(),
                'indexes_optimized': len(self.optimize_database_indexes()),
                'timestamp': timezone.now()
            }
            
            # حفظ نتائج الصيانة في التخزين المؤقت
            cache.set('maintenance_last_run', maintenance_results, 86400)  # 24 ساعة
            
            logger.info("تم تنفيذ مهام الصيانة بنجاح")
            return maintenance_results
            
        except Exception as e:
            logger.error(f"خطأ في مهام الصيانة: {e}")
            return {'error': str(e)}
    
    def get_performance_recommendations(self):
        """الحصول على توصيات تحسين الأداء"""
        recommendations = []
        
        try:
            # تحليل الاستعلامات البطيئة
            slow_queries = self.get_slow_queries_report()
            if slow_queries:
                recommendations.append({
                    'type': 'slow_queries',
                    'priority': 'high',
                    'message': f'يوجد {len(slow_queries)} دالة بها استعلامات بطيئة',
                    'details': slow_queries
                })
            
            # تحليل الذاكرة
            memory_analysis = self.analyze_memory_usage()
            if 'percent' in memory_analysis and memory_analysis['percent'] > 70:
                recommendations.append({
                    'type': 'memory',
                    'priority': 'medium',
                    'message': f'استخدام ذاكرة عالي: {memory_analysis["percent"]:.1f}%'
                })
            
            # تحليل قاعدة البيانات
            db_stats = self.get_database_statistics()
            if 'tables' in db_stats:
                large_tables = [
                    name for name, info in db_stats['tables'].items()
                    if info.get('row_count', 0) > 10000
                ]
                
                if large_tables:
                    recommendations.append({
                        'type': 'database',
                        'priority': 'medium',
                        'message': f'يوجد {len(large_tables)} جدول كبير يحتاج تحسين',
                        'details': large_tables
                    })
            
            # توصيات التخزين المؤقت
            cache_stats = cache.get('cache_hit_rate')
            if cache_stats and cache_stats < 0.8:
                recommendations.append({
                    'type': 'cache',
                    'priority': 'low',
                    'message': f'معدل إصابة التخزين المؤقت منخفض: {cache_stats:.1%}'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"خطأ في توليد التوصيات: {e}")
            return [{'type': 'error', 'message': str(e)}]


# إنشاء مثيل الخدمة
performance_service = PerformanceService()