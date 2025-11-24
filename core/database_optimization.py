"""
Database Optimization Service for ElDawliya System
خدمة تحسين قاعدة البيانات لنظام الدولية

This module provides database optimization utilities including:
- Query optimization and analysis
- Index management and recommendations
- Connection pooling optimization
- Performance monitoring
"""

from django.db import connection, connections
from django.db.models import Q, Count, Avg, Max, Min
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager

# Temporarily disabled - will be replaced with new modular HR apps
# from Hr.models import Employee, Department
from tasks.models import Task
from meetings.models import Meeting
from inventory.models import TblProducts
from Purchase_orders.models import PurchaseRequest

logger = logging.getLogger(__name__)


class DatabaseOptimizationService:
    """
    Service for database performance optimization
    خدمة تحسين أداء قاعدة البيانات
    """

    def __init__(self):
        """__init__ function"""
        self.query_log = []
        self.performance_metrics = {}
        self.optimization_cache_timeout = 3600  # 1 hour

    @contextmanager
    def query_timer(self, query_name: str):
        """
        Context manager to time database queries
        مدير السياق لقياس وقت استعلامات قاعدة البيانات
        """
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            execution_time = end_time - start_time

            self.query_log.append({
                'query_name': query_name,
                'execution_time': execution_time,
                'timestamp': timezone.now().isoformat()
            })

            # Keep only last 100 queries
            if len(self.query_log) > 100:
                self.query_log = self.query_log[-100:]

            logger.info(f"Query '{query_name}' executed in {execution_time:.4f}s")

    def analyze_query_performance(self) -> Dict[str, Any]:
        """
        Analyze query performance metrics
        تحليل مقاييس أداء الاستعلامات
        """
        if not self.query_log:
            return {'message': 'No query data available'}

        total_queries = len(self.query_log)
        total_time = sum(q['execution_time'] for q in self.query_log)
        avg_time = total_time / total_queries

        # Find slowest queries
        slowest_queries = sorted(
            self.query_log,
            key=lambda x: x['execution_time'],
            reverse=True
        )[:10]

        # Group by query name
        query_stats = {}
        for query in self.query_log:
            name = query['query_name']
            if name not in query_stats:
                query_stats[name] = {
                    'count': 0,
                    'total_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0
                }

            stats = query_stats[name]
            stats['count'] += 1
            stats['total_time'] += query['execution_time']
            stats['min_time'] = min(stats['min_time'], query['execution_time'])
            stats['max_time'] = max(stats['max_time'], query['execution_time'])

        # Calculate averages
        for name, stats in query_stats.items():
            stats['avg_time'] = stats['total_time'] / stats['count']

        return {
            'total_queries': total_queries,
            'total_execution_time': total_time,
            'average_execution_time': avg_time,
            'slowest_queries': slowest_queries,
            'query_statistics': query_stats
        }

    def get_optimized_employee_queryset(self, filters: Dict[str, Any] = None):
        """
        Get optimized employee queryset with proper select_related and prefetch_related
        جلب مجموعة الموظفين المحسنة مع العلاقات المناسبة
        """
        with self.query_timer('optimized_employee_queryset'):
            queryset = Employee.objects.select_related(
                'department',
                'job_position',
                'direct_manager',
                'company',
                'branch'
            ).prefetch_related(
                'employeetask_set',
                'employeeleave_set',
                'attendancerecord_set__attendance_machine'
            )

            if filters:
                if 'department_id' in filters:
                    queryset = queryset.filter(department_id=filters['department_id'])
                if 'working_condition' in filters:
                    queryset = queryset.filter(working_condition=filters['working_condition'])
                if 'search' in filters:
                    search_term = filters['search']
                    queryset = queryset.filter(
                        Q(emp_full_name__icontains=search_term) |
                        Q(emp_id__icontains=search_term) |
                        Q(department__dept_name__icontains=search_term)
                    )

            return queryset

    def get_optimized_task_queryset(self, user=None, filters: Dict[str, Any] = None):
        """
        Get optimized task queryset
        جلب مجموعة المهام المحسنة
        """
        with self.query_timer('optimized_task_queryset'):
            queryset = Task.objects.select_related(
                'created_by',
                'assigned_to'
            ).prefetch_related(
                'taskstep_set'
            )

            if user and not user.is_superuser:
                queryset = queryset.filter(
                    Q(created_by=user) | Q(assigned_to=user)
                )

            if filters:
                if 'status' in filters:
                    queryset = queryset.filter(status=filters['status'])
                if 'priority' in filters:
                    queryset = queryset.filter(priority=filters['priority'])
                if 'assigned_to' in filters:
                    queryset = queryset.filter(assigned_to_id=filters['assigned_to'])

            return queryset

    def get_optimized_meeting_queryset(self, user=None, filters: Dict[str, Any] = None):
        """
        Get optimized meeting queryset
        جلب مجموعة الاجتماعات المحسنة
        """
        with self.query_timer('optimized_meeting_queryset'):
            queryset = Meeting.objects.select_related(
                'created_by'
            ).prefetch_related(
                'attendees',
                'meeting_tasks'
            )

            if user and not user.is_superuser:
                queryset = queryset.filter(
                    Q(created_by=user) | Q(attendees__user=user)
                ).distinct()

            if filters:
                if 'date_from' in filters:
                    queryset = queryset.filter(date__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(date__lte=filters['date_to'])
                if 'status' in filters:
                    queryset = queryset.filter(status=filters['status'])

            return queryset

    def get_database_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics
        جلب إحصائيات شاملة لقاعدة البيانات
        """
        cache_key = 'database_statistics'
        cached_stats = cache.get(cache_key)

        if cached_stats:
            return cached_stats

        with self.query_timer('database_statistics'):
            stats = {
                'employees': {
                    'total': Employee.objects.count(),
                    'active': Employee.objects.filter(working_condition='سارى').count(),
                    'by_department': list(
                        Employee.objects.values('department__dept_name')
                        .annotate(count=Count('emp_id'))
                        .order_by('-count')
                    )
                },
                'tasks': {
                    'total': Task.objects.count(),
                    'active': Task.objects.filter(status__in=['pending', 'in_progress']).count(),
                    'completed': Task.objects.filter(status='completed').count(),
                    'overdue': Task.objects.filter(
                        end_date__lt=timezone.now().date(),
                        status__in=['pending', 'in_progress']
                    ).count()
                },
                'meetings': {
                    'total': Meeting.objects.count(),
                    'upcoming': Meeting.objects.filter(date__gte=timezone.now()).count(),
                    'this_month': Meeting.objects.filter(
                        date__month=timezone.now().month,
                        date__year=timezone.now().year
                    ).count()
                },
                'inventory': {
                    'total_products': TblProducts.objects.count(),
                    'low_stock': TblProducts.objects.filter(qte_in_stock__lte=10).count()
                },
                'purchase_orders': {
                    'total': PurchaseRequest.objects.count(),
                    'pending': PurchaseRequest.objects.filter(status='pending').count()
                }
            }

        # Cache for 1 hour
        cache.set(cache_key, stats, self.optimization_cache_timeout)
        return stats

    def get_index_recommendations(self) -> List[Dict[str, str]]:
        """
        Get database index recommendations
        جلب توصيات فهارس قاعدة البيانات
        """
        recommendations = []

        # Analyze common query patterns
        with connection.cursor() as cursor:
            try:
                # Check for missing indexes on foreign keys
                cursor.execute("""
                    SELECT
                        t.name AS table_name,
                        c.name AS column_name
                    FROM sys.foreign_key_columns fkc
                    INNER JOIN sys.tables t ON fkc.parent_object_id = t.object_id
                    INNER JOIN sys.columns c ON fkc.parent_object_id = c.object_id
                        AND fkc.parent_column_id = c.column_id
                    WHERE NOT EXISTS (
                        SELECT 1 FROM sys.index_columns ic
                        INNER JOIN sys.indexes i ON ic.object_id = i.object_id
                            AND ic.index_id = i.index_id
                        WHERE ic.object_id = fkc.parent_object_id
                            AND ic.column_id = fkc.parent_column_id
                            AND i.is_primary_key = 0
                    )
                """)

                missing_fk_indexes = cursor.fetchall()
                for table, column in missing_fk_indexes:
                    recommendations.append({
                        'type': 'Missing Foreign Key Index',
                        'table': table,
                        'column': column,
                        'recommendation': f'CREATE INDEX IX_{table}_{column} ON {table} ({column})'
                    })

            except Exception as e:
                logger.warning(f"Could not analyze indexes: {e}")

        # Add general recommendations based on common patterns
        recommendations.extend([
            {
                'type': 'Search Optimization',
                'table': 'Hr_employee',
                'column': 'emp_full_name',
                'recommendation': 'Consider full-text index for employee name searches'
            },
            {
                'type': 'Date Range Queries',
                'table': 'tasks_task',
                'column': 'end_date',
                'recommendation': 'Ensure index exists for date range queries'
            },
            {
                'type': 'Status Filtering',
                'table': 'tasks_task',
                'column': 'status',
                'recommendation': 'Consider composite index on (status, assigned_to_id)'
            }
        ])

        return recommendations

    def clear_query_log(self):
        """Clear the query performance log"""
        self.query_log.clear()
        logger.info("Query performance log cleared")

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get database connection information
        جلب معلومات اتصال قاعدة البيانات
        """
        db_info = {}

        for alias in connections:
            conn = connections[alias]
            db_info[alias] = {
                'engine': conn.settings_dict.get('ENGINE', 'Unknown'),
                'name': conn.settings_dict.get('NAME', 'Unknown'),
                'host': conn.settings_dict.get('HOST', 'localhost'),
                'port': conn.settings_dict.get('PORT', 'default'),
                'active_db': getattr(settings, 'ACTIVE_DB', 'default')
            }

        return db_info


# Singleton instance
db_optimization_service = DatabaseOptimizationService()
