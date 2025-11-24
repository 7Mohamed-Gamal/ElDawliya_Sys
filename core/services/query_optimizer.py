"""
Database Query Optimization Service
==================================

This module provides comprehensive database query optimization including:
- Query analysis and optimization
- Automatic select_related and prefetch_related optimization
- Database index recommendations
- Query performance monitoring
- Data partitioning strategies
- Redis-based caching for heavy queries
"""

import logging
import time
import hashlib
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from functools import wraps
from django.db import models, connection
from django.db.models import QuerySet, Prefetch, Q, Count, Sum, Avg
from django.db.models.query import RawQuerySet
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .cache_service import cache_service, cache_result

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """محسن الاستعلامات"""

    def __init__(self):
        """__init__ function"""
        self.query_stats = {}
        self.slow_query_threshold = getattr(settings, 'SLOW_QUERY_THRESHOLD', 1.0)  # seconds

    def optimize_employee_queries(self, queryset: QuerySet) -> QuerySet:
        """تحسين استعلامات الموظفين"""
        return queryset.select_related(
            'dept',
            'job',
            'branch',
            'manager',
            'manager__dept',
            'manager__job'
        ).prefetch_related(
            'bank_accounts',
            'documents',
            'subordinates',
            'subordinates__dept',
            'subordinates__job'
        )

    def optimize_attendance_queries(self, queryset: QuerySet) -> QuerySet:
        """تحسين استعلامات الحضور"""
        return queryset.select_related(
            'employee',
            'employee__dept',
            'employee__job',
            'employee__branch'
        )

    def optimize_inventory_queries(self, queryset: QuerySet) -> QuerySet:
        """تحسين استعلامات المخزون"""
        return queryset.select_related(
            'cat',
            'unit'
        ).prefetch_related(
            'tblinvoiceitems_set',
            'tblinvoiceitems_set__invoice_number'
        )

    def optimize_invoice_queries(self, queryset: QuerySet) -> QuerySet:
        """تحسين استعلامات الفواتير"""
        return queryset.prefetch_related(
            Prefetch(
                'tblinvoiceitems_set',
                queryset=models.get_model('inventory', 'TblInvoiceitems').objects.select_related(
                    'product',
                    'product__cat',
                    'product__unit'
                )
            )
        )

    def get_optimized_queryset(self, model_class, optimization_type: str = 'default') -> QuerySet:
        """الحصول على استعلام محسن حسب نوع النموذج"""
        queryset = model_class.objects.all()

        model_name = model_class.__name__.lower()

        if 'employee' in model_name:
            return self.optimize_employee_queries(queryset)
        elif 'attendance' in model_name:
            return self.optimize_attendance_queries(queryset)
        elif 'product' in model_name or 'inventory' in model_name:
            return self.optimize_inventory_queries(queryset)
        elif 'invoice' in model_name:
            return self.optimize_invoice_queries(queryset)

        return queryset


class QueryPerformanceMonitor:
    """مراقب أداء الاستعلامات"""

    def __init__(self):
        """__init__ function"""
        self.query_log = []
        self.slow_queries = []
        self.query_stats = {}

    def log_query(self, query: str, execution_time: float, params: tuple = None):
        """تسجيل استعلام مع وقت التنفيذ"""
        query_info = {
            'query': query,
            'execution_time': execution_time,
            'params': params,
            'timestamp': timezone.now(),
            'is_slow': execution_time > getattr(settings, 'SLOW_QUERY_THRESHOLD', 1.0)
        }

        self.query_log.append(query_info)

        if query_info['is_slow']:
            self.slow_queries.append(query_info)
            logger.warning(f"Slow query detected: {execution_time:.2f}s - {query[:100]}...")

        # Keep only last 1000 queries in memory
        if len(self.query_log) > 1000:
            self.query_log = self.query_log[-1000:]

        # Update statistics
        self._update_stats(query, execution_time)

    def _update_stats(self, query: str, execution_time: float):
        """تحديث إحصائيات الاستعلامات"""
        query_hash = hashlib.md5(query.encode()).hexdigest()

        if query_hash not in self.query_stats:
            self.query_stats[query_hash] = {
                'query': query[:200],  # Store first 200 chars
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'last_executed': None
            }

        stats = self.query_stats[query_hash]
        stats['count'] += 1
        stats['total_time'] += execution_time
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['min_time'] = min(stats['min_time'], execution_time)
        stats['max_time'] = max(stats['max_time'], execution_time)
        stats['last_executed'] = timezone.now()

    def get_slow_queries(self, limit: int = 10) -> List[Dict]:
        """الحصول على أبطأ الاستعلامات"""
        return sorted(self.slow_queries, key=lambda x: x['execution_time'], reverse=True)[:limit]

    def get_query_stats(self) -> Dict:
        """الحصول على إحصائيات الاستعلامات"""
        total_queries = len(self.query_log)
        slow_queries_count = len(self.slow_queries)

        if total_queries == 0:
            return {
                'total_queries': 0,
                'slow_queries': 0,
                'slow_query_percentage': 0,
                'avg_execution_time': 0
            }

        avg_time = sum(q['execution_time'] for q in self.query_log) / total_queries

        return {
            'total_queries': total_queries,
            'slow_queries': slow_queries_count,
            'slow_query_percentage': (slow_queries_count / total_queries) * 100,
            'avg_execution_time': avg_time,
            'most_frequent_queries': self._get_most_frequent_queries()
        }

    def _get_most_frequent_queries(self, limit: int = 5) -> List[Dict]:
        """الحصول على أكثر الاستعلامات تكراراً"""
        return sorted(
            self.query_stats.values(),
            key=lambda x: x['count'],
            reverse=True
        )[:limit]


class CachedQueryManager:
    """مدير الاستعلامات المخزنة مؤقتاً"""

    def __init__(self):
        """__init__ function"""
        self.cache_prefix = 'query_cache:'
        self.default_timeout = getattr(settings, 'QUERY_CACHE_TIMEOUT', 300)  # 5 minutes

    def get_cache_key(self, query: str, params: tuple = None) -> str:
        """إنشاء مفتاح التخزين المؤقت"""
        key_data = f"{query}:{params}" if params else query
        return f"{self.cache_prefix}{hashlib.md5(key_data.encode()).hexdigest()}"

    def cache_queryset_result(self, queryset: QuerySet, timeout: int = None) -> List:
        """تخزين نتيجة الاستعلام مؤقتاً"""
        timeout = timeout or self.default_timeout

        # Create cache key from queryset SQL
        query_sql = str(queryset.query)
        cache_key = self.get_cache_key(query_sql)

        # Check if already cached
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for query: {query_sql[:100]}...")
            return cached_result

        # Execute query and cache result
        start_time = time.time()
        result = list(queryset)
        execution_time = time.time() - start_time

        # Cache the result
        cache.set(cache_key, result, timeout)

        logger.debug(f"Query cached: {execution_time:.2f}s - {query_sql[:100]}...")
        return result

    def invalidate_model_cache(self, model_class):
        """إبطال التخزين المؤقت لنموذج معين"""
        model_name = model_class.__name__.lower()
        pattern = f"{self.cache_prefix}*{model_name}*"

        # This would require Redis for pattern-based deletion
        # For now, we'll use a simple approach
        cache_keys = cache.keys(pattern) if hasattr(cache, 'keys') else []
        if cache_keys:
            cache.delete_many(cache_keys)
            logger.info(f"Invalidated {len(cache_keys)} cache entries for {model_name}")


class DatabaseIndexAnalyzer:
    """محلل فهارس قاعدة البيانات"""

    def __init__(self):
        """__init__ function"""
        self.connection = connection

    def analyze_missing_indexes(self) -> List[Dict]:
        """تحليل الفهارس المفقودة"""
        missing_indexes = []

        # Common patterns that need indexes
        index_recommendations = [
            {
                'table': 'employees_employee',
                'columns': ['emp_status', 'is_active'],
                'reason': 'Frequently filtered by status and active state'
            },
            {
                'table': 'attendance_employeeattendance',
                'columns': ['att_date', 'employee_id'],
                'reason': 'Date range queries with employee filtering'
            },
            {
                'table': 'inventory_tblproducts',
                'columns': ['cat_id', 'qte_in_stock'],
                'reason': 'Category filtering with stock level checks'
            },
            {
                'table': 'inventory_tblinvoiceitems',
                'columns': ['invoice_date', 'invoice_type'],
                'reason': 'Date and type filtering for reports'
            },
            {
                'table': 'payrolls_employeesalary',
                'columns': ['employee_id', 'is_current'],
                'reason': 'Employee salary lookups'
            }
        ]

        return index_recommendations

    def get_index_usage_stats(self) -> Dict:
        """إحصائيات استخدام الفهارس"""
        try:
            with self.connection.cursor() as cursor:
                # SQL Server specific query for index usage
                cursor.execute("""
                    SELECT
                        OBJECT_NAME(i.object_id) AS table_name,
                        i.name AS index_name,
                        s.user_seeks,
                        s.user_scans,
                        s.user_lookups,
                        s.user_updates
                    FROM sys.indexes i
                    LEFT JOIN sys.dm_db_index_usage_stats s
                        ON i.object_id = s.object_id AND i.index_id = s.index_id
                    WHERE OBJECT_NAME(i.object_id) LIKE 'Tbl_%'
                        OR OBJECT_NAME(i.object_id) LIKE '%_employee%'
                        OR OBJECT_NAME(i.object_id) LIKE '%_attendance%'
                    ORDER BY s.user_seeks DESC, s.user_scans DESC
                """)

                results = cursor.fetchall()
                return {
                    'index_stats': [
                        {
                            'table_name': row[0],
                            'index_name': row[1],
                            'seeks': row[2] or 0,
                            'scans': row[3] or 0,
                            'lookups': row[4] or 0,
                            'updates': row[5] or 0
                        }
                        for row in results
                    ]
                }
        except Exception as e:
            logger.error(f"Error getting index usage stats: {e}")
            return {'index_stats': []}

    def suggest_index_optimizations(self) -> List[Dict]:
        """اقتراح تحسينات الفهارس"""
        suggestions = []

        # Get current index usage
        stats = self.get_index_usage_stats()

        for stat in stats.get('index_stats', []):
            if stat['seeks'] == 0 and stat['scans'] == 0 and stat['lookups'] == 0:
                suggestions.append({
                    'type': 'unused_index',
                    'table': stat['table_name'],
                    'index': stat['index_name'],
                    'recommendation': 'Consider dropping this unused index',
                    'priority': 'low'
                })
            elif stat['scans'] > stat['seeks'] * 10:  # Too many scans vs seeks
                suggestions.append({
                    'type': 'inefficient_index',
                    'table': stat['table_name'],
                    'index': stat['index_name'],
                    'recommendation': 'Index may need optimization or additional columns',
                    'priority': 'medium'
                })

        # Add missing index suggestions
        for missing in self.analyze_missing_indexes():
            suggestions.append({
                'type': 'missing_index',
                'table': missing['table'],
                'columns': missing['columns'],
                'recommendation': f"Create index on {', '.join(missing['columns'])}",
                'reason': missing['reason'],
                'priority': 'high'
            })

        return suggestions


class QueryOptimizationDecorator:
    """ديكوريتر تحسين الاستعلامات"""

    def __init__(self, cache_timeout: int = 300, monitor_performance: bool = True):
        """__init__ function"""
        self.cache_timeout = cache_timeout
        self.monitor_performance = monitor_performance
        self.performance_monitor = QueryPerformanceMonitor()
        self.cached_manager = CachedQueryManager()

    def __call__(self, func):
        """__call__ function"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """wrapper function"""
            start_time = time.time()

            try:
                # Execute the function
                result = func(*args, **kwargs)

                # If result is a QuerySet, apply optimizations
                if isinstance(result, QuerySet):
                    # Apply caching if enabled
                    if self.cache_timeout > 0:
                        result = self.cached_manager.cache_queryset_result(
                            result, self.cache_timeout
                        )

                return result

            finally:
                if self.monitor_performance:
                    execution_time = time.time() - start_time
                    self.performance_monitor.log_query(
                        query=f"{func.__name__}",
                        execution_time=execution_time
                    )

        return wrapper


# Decorator instances for common use cases
@QueryOptimizationDecorator(cache_timeout=300)  # 5 minutes cache
def optimize_query(func):
    """ديكوريتر لتحسين الاستعلامات مع تخزين مؤقت"""
    return func


@QueryOptimizationDecorator(cache_timeout=0, monitor_performance=True)
def monitor_query_performance(func):
    """ديكوريتر لمراقبة أداء الاستعلامات فقط"""
    return func


# Global instances
query_optimizer = QueryOptimizer()
performance_monitor = QueryPerformanceMonitor()
cached_query_manager = CachedQueryManager()
index_analyzer = DatabaseIndexAnalyzer()


# Utility functions for common optimizations
def get_optimized_employees(filters: Dict = None) -> QuerySet:
    """الحصول على استعلام محسن للموظفين"""
    from employees.models import Employee

    queryset = Employee.objects.select_related(
        'dept', 'job', 'branch', 'manager'
    ).prefetch_related(
        'bank_accounts', 'documents'
    )

    if filters:
        queryset = queryset.filter(**filters)

    return queryset


def get_optimized_attendance(date_from: datetime = None, date_to: datetime = None) -> QuerySet:
    """الحصول على استعلام محسن للحضور"""
    from attendance.models import EmployeeAttendance

    queryset = EmployeeAttendance.objects.select_related(
        'employee', 'employee__dept', 'employee__job'
    )

    if date_from:
        queryset = queryset.filter(att_date__gte=date_from)
    if date_to:
        queryset = queryset.filter(att_date__lte=date_to)

    return queryset


def get_optimized_inventory() -> QuerySet:
    """الحصول على استعلام محسن للمخزون"""
    from inventory.models import TblProducts

    return TblProducts.objects.select_related(
        'cat', 'unit'
    ).prefetch_related(
        'tblinvoiceitems_set'
    )


def get_dashboard_stats_cached() -> Dict:
    """الحصول على إحصائيات لوحة التحكم مع التخزين المؤقت"""
    cache_key = 'dashboard_stats'
    cached_stats = cache.get(cache_key)

    if cached_stats:
        return cached_stats

    # Calculate stats
    stats = {}

    try:
        from employees.models import Employee
        stats['total_employees'] = Employee.objects.filter(emp_status='Active').count()
        stats['new_employees_this_month'] = Employee.objects.filter(
            hire_date__gte=timezone.now().replace(day=1)
        ).count()
    except ImportError:
        pass

    try:
        from attendance.models import EmployeeAttendance
        today = timezone.now().date()
        today_attendance = EmployeeAttendance.objects.filter(att_date=today)
        stats['present_today'] = today_attendance.filter(
            status__in=['Present', 'Late']
        ).count()
        stats['absent_today'] = today_attendance.filter(status='Absent').count()
    except ImportError:
        pass

    try:
        from leaves.models import EmployeeLeave
        stats['pending_leaves'] = EmployeeLeave.objects.filter(status='Pending').count()
    except ImportError:
        pass

    # Cache for 5 minutes
    cache.set(cache_key, stats, 300)
    return stats


def invalidate_dashboard_cache():
    """إبطال تخزين لوحة التحكم المؤقت"""
    cache.delete('dashboard_stats')


# Performance monitoring middleware
class QueryPerformanceMiddleware:
    """وسطاء مراقبة أداء الاستعلامات"""

    def __init__(self, get_response):
        """__init__ function"""
        self.get_response = get_response
        self.performance_monitor = QueryPerformanceMonitor()

    def __call__(self, request):
        """__call__ function"""
        # Reset query count
        initial_queries = len(connection.queries)
        start_time = time.time()

        response = self.get_response(request)

        # Calculate metrics
        end_time = time.time()
        total_time = end_time - start_time
        query_count = len(connection.queries) - initial_queries

        # Log if too many queries or too slow
        if query_count > 10 or total_time > 1.0:
            logger.warning(
                f"Performance warning: {request.path} - "
                f"{query_count} queries in {total_time:.2f}s"
            )

        # Add performance headers in debug mode
        if settings.DEBUG:
            response['X-Query-Count'] = str(query_count)
            response['X-Query-Time'] = f"{total_time:.2f}s"

        return response
