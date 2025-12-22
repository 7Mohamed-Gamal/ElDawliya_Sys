"""
Query Optimization Middleware
============================

Middleware to automatically apply query optimization and performance monitoring
"""

import time
import logging
from django.db import connection
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

from core.services.query_optimizer import performance_monitor
from core.services.cache_service import cache_performance_monitor

logger = logging.getLogger(__name__)


class QueryOptimizationMiddleware(MiddlewareMixin):
    """
    Middleware for automatic query optimization and performance monitoring
    """

    def __init__(self, get_response):
        """__init__ function"""
        self.get_response = get_response
        self.slow_query_threshold = getattr(settings, 'SLOW_QUERY_THRESHOLD', 1.0)
        self.max_queries_warning = getattr(settings, 'MAX_QUERIES_WARNING', 20)
        super().__init__(get_response)

    def process_request(self, request):
        """Process request - record start time and initial query count"""
        request._query_start_time = time.time()
        request._initial_query_count = len(connection.queries)
        return None

    def process_response(self, request, response):
        """Process response - analyze query performance"""

        # Skip if not in debug mode or if this is a static file request
        if not settings.DEBUG or request.path.startswith('/static/'):
            return response

        # Calculate request metrics
        end_time = time.time()
        start_time = getattr(request, '_query_start_time', end_time)
        initial_query_count = getattr(request, '_initial_query_count', 0)

        total_time = end_time - start_time
        query_count = len(connection.queries) - initial_query_count

        # Log performance metrics
        self._log_performance_metrics(request, total_time, query_count)

        # Add performance headers in debug mode
        if settings.DEBUG:
            response['X-Query-Count'] = str(query_count)
            response['X-Query-Time'] = f"{total_time:.3f}s"
            response['X-DB-Queries'] = str(len(connection.queries))

        # Check for performance issues
        self._check_performance_issues(request, total_time, query_count)

        # Record cache performance if applicable
        self._record_cache_performance(request, response)

        return response

    def _log_performance_metrics(self, request, total_time, query_count):
        """Log performance metrics"""

        # Log slow requests
        if total_time > self.slow_query_threshold:
            logger.warning(
                f"Slow request: {request.method} {request.path} - "
                f"{total_time:.3f}s with {query_count} queries"
            )

        # Log requests with too many queries
        if query_count > self.max_queries_warning:
            logger.warning(
                f"High query count: {request.method} {request.path} - "
                f"{query_count} queries in {total_time:.3f}s"
            )

        # Record in performance monitor
        performance_monitor.log_query(
            query=f"{request.method} {request.path}",
            execution_time=total_time,
            params=(query_count,)
        )

    def _check_performance_issues(self, request, total_time, query_count):
        """Check for common performance issues"""

        issues = []

        # Check for N+1 query problems
        if query_count > 10 and total_time > 0.5:
            issues.append("Possible N+1 query problem detected")

        # Check for missing select_related/prefetch_related
        if query_count > 5:
            similar_queries = self._find_similar_queries()
            if similar_queries:
                issues.append("Similar queries detected - consider using select_related/prefetch_related")

        # Check for unindexed queries
        slow_queries = [q for q in connection.queries if float(q['time']) > 0.1]
        if slow_queries:
            issues.append(f"{len(slow_queries)} slow queries detected")

        # Log issues
        if issues:
            logger.info(
                f"Performance issues for {request.path}: {', '.join(issues)}"
            )

    def _find_similar_queries(self):
        """Find similar queries that might benefit from optimization"""

        queries = connection.queries
        if len(queries) < 5:
            return []

        # Group queries by table
        table_queries = {}
        for query in queries[-20:]:  # Check last 20 queries
            sql = query['sql'].lower()

            # Extract table name (simple approach)
            if 'from ' in sql:
                try:
                    table_part = sql.split('from ')[1].split(' ')[0]
                    table_name = table_part.strip('`"[]')

                    if table_name not in table_queries:
                        table_queries[table_name] = []
                    table_queries[table_name].append(query)
                except IndexError:
                    continue

        # Find tables with multiple queries
        similar_queries = []
        for table, queries in table_queries.items():
            if len(queries) > 3:
                similar_queries.append({
                    'table': table,
                    'count': len(queries),
                    'queries': queries
                })

        return similar_queries

    def _record_cache_performance(self, request, response):
        """Record cache performance metrics"""

        # Check if response was served from cache
        cache_header = response.get('X-Cache-Status')
        if cache_header:
            if cache_header == 'HIT':
                cache_performance_monitor.record_hit(request.path)
            elif cache_header == 'MISS':
                cache_performance_monitor.record_miss(request.path)


class DatabaseQueryLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all database queries in debug mode
    """

    def __init__(self, get_response):
        """__init__ function"""
        self.get_response = get_response
        super().__init__(get_response)

    def process_response(self, request, response):
        """Log database queries if in debug mode"""

        if not settings.DEBUG:
            return response

        # Skip static files
        if request.path.startswith('/static/'):
            return response

        queries = connection.queries
        if not queries:
            return response

        # Log query summary
        total_time = sum(float(q['time']) for q in queries)
        logger.debug(
            f"Database queries for {request.path}: "
            f"{len(queries)} queries in {total_time:.3f}s"
        )

        # Log slow queries
        slow_queries = [q for q in queries if float(q['time']) > 0.1]
        for query in slow_queries:
            logger.debug(
                f"Slow query ({query['time']}s): {query['sql'][:200]}..."
            )

        return response


class CacheHeaderMiddleware(MiddlewareMixin):
    """
    Middleware to add cache-related headers
    """

    def __init__(self, get_response):
        """__init__ function"""
        self.get_response = get_response
        super().__init__(get_response)

    def process_response(self, request, response):
        """Add cache headers"""

        # Skip for non-GET requests
        if request.method != 'GET':
            return response

        # Skip for admin and API requests
        if request.path.startswith('/admin/') or request.path.startswith('/api/'):
            return response

        # Add cache control headers for static content
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            response['Cache-Control'] = 'public, max-age=31536000'  # 1 year
            return response

        # Add cache headers for regular pages
        if response.status_code == 200:
            # Check if user is authenticated
            if request.user.is_authenticated:
                response['Cache-Control'] = 'private, max-age=300'  # 5 minutes for authenticated users
            else:
                response['Cache-Control'] = 'public, max-age=600'   # 10 minutes for anonymous users

        return response


class QueryOptimizationSuggestionMiddleware(MiddlewareMixin):
    """
    Middleware to suggest query optimizations
    """

    def __init__(self, get_response):
        """__init__ function"""
        self.get_response = get_response
        self.suggestion_threshold = 5  # Suggest optimization after 5 similar queries
        super().__init__(get_response)

    def process_response(self, request, response):
        """Analyze queries and suggest optimizations"""

        if not settings.DEBUG:
            return response

        queries = connection.queries
        if len(queries) < self.suggestion_threshold:
            return response

        suggestions = self._analyze_queries(queries)

        if suggestions and settings.DEBUG:
            # Add suggestions as a header in debug mode
            response['X-Query-Suggestions'] = '; '.join(suggestions)

            # Log suggestions
            logger.info(
                f"Query optimization suggestions for {request.path}: "
                f"{', '.join(suggestions)}"
            )

        return response

    def _analyze_queries(self, queries):
        """Analyze queries and generate optimization suggestions"""

        suggestions = []

        # Check for repeated SELECT queries
        select_queries = [q for q in queries if q['sql'].strip().upper().startswith('SELECT')]

        if len(select_queries) > 10:
            suggestions.append("Consider using select_related() or prefetch_related() to reduce query count")

        # Check for queries without WHERE clauses
        full_table_scans = [
            q for q in select_queries
            if 'WHERE' not in q['sql'].upper() and 'LIMIT' not in q['sql'].upper()
        ]

        if full_table_scans:
            suggestions.append(f"{len(full_table_scans)} queries without WHERE clause - consider adding filters")

        # Check for slow queries
        slow_queries = [q for q in queries if float(q['time']) > 0.1]

        if slow_queries:
            suggestions.append(f"{len(slow_queries)} slow queries detected - consider adding database indexes")

        # Check for repeated similar queries
        query_patterns = {}
        for query in queries:
            # Normalize query by removing specific values
            normalized = self._normalize_query(query['sql'])
            if normalized in query_patterns:
                query_patterns[normalized] += 1
            else:
                query_patterns[normalized] = 1

        repeated_patterns = [pattern for pattern, count in query_patterns.items() if count > 3]
        if repeated_patterns:
            suggestions.append(f"{len(repeated_patterns)} repeated query patterns - consider caching")

        return suggestions

    def _normalize_query(self, sql):
        """Normalize SQL query by removing specific values"""
        import re

        # Remove specific numeric values
        sql = re.sub(r'\b\d+\b', '?', sql)

        # Remove string literals
        sql = re.sub(r"'[^']*'", '?', sql)
        sql = re.sub(r'"[^"]*"', '?', sql)

        # Remove extra whitespace
        sql = ' '.join(sql.split())

        return sql
