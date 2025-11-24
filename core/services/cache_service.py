"""
Advanced Caching Service for ElDawliya System
============================================

This module provides comprehensive caching functionality including:
- Hierarchical caching with Redis
- Query optimization and caching
- Cache invalidation strategies
- Performance monitoring
- Session and temporary data caching
"""

import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.conf import settings
from django.db.models import QuerySet
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
import redis
import pickle

logger = logging.getLogger(__name__)


class CacheService:
    """خدمة التخزين المؤقت المتقدمة"""

    # Cache timeout configurations (in seconds)
    CACHE_TIMEOUTS = {
        'short': 300,       # 5 minutes
        'medium': 1800,     # 30 minutes
        'long': 3600,       # 1 hour
        'daily': 86400,     # 24 hours
        'weekly': 604800,   # 7 days
        'monthly': 2592000, # 30 days
    }

    # Cache key prefixes for organization
    KEY_PREFIXES = {
        'employee': 'emp',
        'department': 'dept',
        'attendance': 'att',
        'payroll': 'pay',
        'inventory': 'inv',
        'product': 'prod',
        'supplier': 'supp',
        'invoice': 'inv',
        'meeting': 'meet',
        'task': 'task',
        'report': 'rpt',
        'dashboard': 'dash',
        'query': 'qry',
        'session': 'sess',
        'user': 'usr',
    }

    def __init__(self):
        """Initialize cache service"""
        self.redis_client = None
        self._setup_redis()

    def _setup_redis(self):
        """Setup Redis connection if available"""
        try:
            if hasattr(settings, 'REDIS_URL'):
                self.redis_client = redis.from_url(settings.REDIS_URL)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis connection established successfully")
            else:
                logger.warning("Redis URL not configured, using Django cache backend")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def _generate_key(self, prefix: str, identifier: str, **kwargs) -> str:
        """Generate standardized cache key"""
        key_parts = [self.KEY_PREFIXES.get(prefix, prefix), identifier]

        # Add additional parameters to key
        if kwargs:
            sorted_params = sorted(kwargs.items())
            param_string = '_'.join([f"{k}:{v}" for k, v in sorted_params])
            key_parts.append(param_string)

        key = '_'.join(str(part) for part in key_parts)

        # Hash long keys to avoid Redis key length limits
        if len(key) > 200:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{self.KEY_PREFIXES.get(prefix, prefix)}_{key_hash}"

        return key

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value is not None:
                    return pickle.loads(value)
            else:
                return cache.get(key, default)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")

        return default

    def set(self, key: str, value: Any, timeout: Union[str, int] = 'medium') -> bool:
        """Set value in cache"""
        try:
            if isinstance(timeout, str):
                timeout = self.CACHE_TIMEOUTS.get(timeout, self.CACHE_TIMEOUTS['medium'])

            if self.redis_client:
                serialized_value = pickle.dumps(value)
                return self.redis_client.setex(key, timeout, serialized_value)
            else:
                cache.set(key, value, timeout)
                return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                cache.delete(key)
                return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # Django cache doesn't support pattern deletion natively
                # This is a limitation when not using Redis
                logger.warning("Pattern deletion not supported with Django cache backend")
                return 0
        except Exception as e:
            logger.error(f"Cache pattern delete error for pattern {pattern}: {e}")
            return 0

    def get_or_set(self, key: str, callable_func: Callable, timeout: Union[str, int] = 'medium') -> Any:
        """Get value from cache or set it using callable"""
        value = self.get(key)
        if value is not None:
            return value

        try:
            value = callable_func()
            self.set(key, value, timeout)
            return value
        except Exception as e:
            logger.error(f"Error in get_or_set for key {key}: {e}")
            return None

    def increment(self, key: str, delta: int = 1) -> int:
        """Increment counter in cache"""
        try:
            if self.redis_client:
                return self.redis_client.incr(key, delta)
            else:
                current = cache.get(key, 0)
                new_value = current + delta
                cache.set(key, new_value)
                return new_value
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'backend': 'Redis' if self.redis_client else 'Django Cache',
            'timestamp': timezone.now().isoformat(),
        }

        try:
            if self.redis_client:
                info = self.redis_client.info()
                stats.update({
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory_human', '0B'),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                })

                # Calculate hit ratio
                hits = stats['keyspace_hits']
                misses = stats['keyspace_misses']
                total = hits + misses
                stats['hit_ratio'] = (hits / total * 100) if total > 0 else 0
            else:
                stats['note'] = 'Limited statistics available with Django cache backend'
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            stats['error'] = str(e)

        return stats

    def clear_all(self) -> bool:
        """Clear all cache (use with caution)"""
        try:
            if self.redis_client:
                return self.redis_client.flushdb()
            else:
                cache.clear()
                return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False


class QueryCacheService:
    """خدمة تخزين مؤقت للاستعلامات"""

    def __init__(self):
        """__init__ function"""
        self.cache_service = CacheService()

    def cache_queryset(self, queryset: QuerySet, cache_key: str, timeout: Union[str, int] = 'medium') -> List[Dict]:
        """Cache queryset results"""
        def get_queryset_data():
            """get_queryset_data function"""
            return list(queryset.values())

        return self.cache_service.get_or_set(cache_key, get_queryset_data, timeout)

    def cache_query_result(self, query_func: Callable, cache_key: str, timeout: Union[str, int] = 'medium') -> Any:
        """Cache query function result"""
        return self.cache_service.get_or_set(cache_key, query_func, timeout)

    def invalidate_model_cache(self, model_name: str):
        """Invalidate all cache for a specific model"""
        pattern = f"*{model_name.lower()}*"
        return self.cache_service.delete_pattern(pattern)


class CacheInvalidationService:
    """خدمة إبطال التخزين المؤقت"""

    def __init__(self):
        """__init__ function"""
        self.cache_service = CacheService()

    def invalidate_employee_cache(self, employee_id: int):
        """Invalidate employee-related cache"""
        patterns = [
            f"emp_{employee_id}_*",
            f"dept_employees_*",
            "employees_summary_*",
            "dashboard_*",
        ]

        for pattern in patterns:
            self.cache_service.delete_pattern(pattern)

    def invalidate_department_cache(self, department_id: int):
        """Invalidate department-related cache"""
        patterns = [
            f"dept_{department_id}_*",
            f"dept_employees_{department_id}",
            "departments_list",
            "dashboard_*",
        ]

        for pattern in patterns:
            self.cache_service.delete_pattern(pattern)

    def invalidate_attendance_cache(self, employee_id: int = None, date: str = None):
        """Invalidate attendance-related cache"""
        patterns = ["att_*", "dashboard_*"]

        if employee_id:
            patterns.append(f"emp_{employee_id}_att_*")

        if date:
            patterns.append(f"att_date_{date}_*")

        for pattern in patterns:
            self.cache_service.delete_pattern(pattern)

    def invalidate_inventory_cache(self, product_id: str = None):
        """Invalidate inventory-related cache"""
        patterns = ["inv_*", "prod_*", "dashboard_*"]

        if product_id:
            patterns.append(f"prod_{product_id}_*")

        for pattern in patterns:
            self.cache_service.delete_pattern(pattern)


# Cache decorators
def cache_result(timeout: Union[str, int] = 'medium', key_prefix: str = 'func'):
    """Decorator to cache function results"""
    def decorator(func):
        """decorator function"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """wrapper function"""
            cache_service = CacheService()

            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend([str(arg) for arg in args])
            if kwargs:
                sorted_kwargs = sorted(kwargs.items())
                key_parts.extend([f"{k}:{v}" for k, v in sorted_kwargs])

            cache_key = '_'.join(key_parts)

            # Hash long keys
            if len(cache_key) > 200:
                cache_key = hashlib.md5(cache_key.encode()).hexdigest()

            def get_result():
                """get_result function"""
                return func(*args, **kwargs)

            return cache_service.get_or_set(cache_key, get_result, timeout)

        return wrapper
    return decorator


def cache_queryset(timeout: Union[str, int] = 'medium', key_prefix: str = 'qry'):
    """Decorator to cache queryset results"""
    def decorator(func):
        """decorator function"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """wrapper function"""
            cache_service = CacheService()

            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend([str(arg) for arg in args])
            if kwargs:
                sorted_kwargs = sorted(kwargs.items())
                key_parts.extend([f"{k}:{v}" for k, v in sorted_kwargs])

            cache_key = '_'.join(key_parts)

            def get_queryset_result():
                """get_queryset_result function"""
                result = func(*args, **kwargs)
                if hasattr(result, 'values'):
                    # It's a queryset, convert to list
                    return list(result.values())
                return result

            return cache_service.get_or_set(cache_key, get_queryset_result, timeout)

        return wrapper
    return decorator


# Performance monitoring
class CachePerformanceMonitor:
    """مراقب أداء التخزين المؤقت"""

    def __init__(self):
        """__init__ function"""
        self.cache_service = CacheService()
        self.stats_key = "cache_performance_stats"

    def record_hit(self, cache_key: str):
        """Record cache hit"""
        stats_key = f"{self.stats_key}_hits"
        self.cache_service.increment(stats_key)

        # Record hit for specific key pattern
        key_prefix = cache_key.split('_')[0]
        pattern_key = f"{self.stats_key}_hits_{key_prefix}"
        self.cache_service.increment(pattern_key)

    def record_miss(self, cache_key: str):
        """Record cache miss"""
        stats_key = f"{self.stats_key}_misses"
        self.cache_service.increment(stats_key)

        # Record miss for specific key pattern
        key_prefix = cache_key.split('_')[0]
        pattern_key = f"{self.stats_key}_misses_{key_prefix}"
        self.cache_service.increment(pattern_key)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        hits = self.cache_service.get(f"{self.stats_key}_hits", 0)
        misses = self.cache_service.get(f"{self.stats_key}_misses", 0)
        total = hits + misses

        stats = {
            'total_requests': total,
            'cache_hits': hits,
            'cache_misses': misses,
            'hit_ratio': (hits / total * 100) if total > 0 else 0,
            'timestamp': timezone.now().isoformat(),
        }

        return stats

    def reset_stats(self):
        """Reset performance statistics"""
        self.cache_service.delete(f"{self.stats_key}_hits")
        self.cache_service.delete(f"{self.stats_key}_misses")


# Session caching
class SessionCacheService:
    """خدمة تخزين مؤقت للجلسات"""

    def __init__(self):
        """__init__ function"""
        self.cache_service = CacheService()

    def set_user_session_data(self, user_id: int, key: str, value: Any, timeout: Union[str, int] = 'long'):
        """Set user session data"""
        cache_key = f"sess_{user_id}_{key}"
        return self.cache_service.set(cache_key, value, timeout)

    def get_user_session_data(self, user_id: int, key: str, default: Any = None):
        """Get user session data"""
        cache_key = f"sess_{user_id}_{key}"
        return self.cache_service.get(cache_key, default)

    def delete_user_session_data(self, user_id: int, key: str = None):
        """Delete user session data"""
        if key:
            cache_key = f"sess_{user_id}_{key}"
            return self.cache_service.delete(cache_key)
        else:
            # Delete all session data for user
            pattern = f"sess_{user_id}_*"
            return self.cache_service.delete_pattern(pattern)

    def set_temporary_data(self, key: str, value: Any, timeout: Union[str, int] = 'short'):
        """Set temporary data with short expiration"""
        cache_key = f"temp_{key}"
        return self.cache_service.set(cache_key, value, timeout)

    def get_temporary_data(self, key: str, default: Any = None):
        """Get temporary data"""
        cache_key = f"temp_{key}"
        return self.cache_service.get(cache_key, default)


# Initialize global instances
cache_service = CacheService()
query_cache_service = QueryCacheService()
cache_invalidation_service = CacheInvalidationService()
cache_performance_monitor = CachePerformanceMonitor()
session_cache_service = SessionCacheService()


# Signal handlers for automatic cache invalidation
@receiver(post_save)
def invalidate_cache_on_save(sender, instance, **kwargs):
    """Invalidate relevant cache when model is saved"""
    model_name = sender.__name__.lower()

    if 'employee' in model_name:
        if hasattr(instance, 'emp_id'):
            cache_invalidation_service.invalidate_employee_cache(instance.emp_id)
        elif hasattr(instance, 'id'):
            cache_invalidation_service.invalidate_employee_cache(instance.id)

    elif 'department' in model_name:
        if hasattr(instance, 'dept_id'):
            cache_invalidation_service.invalidate_department_cache(instance.dept_id)
        elif hasattr(instance, 'id'):
            cache_invalidation_service.invalidate_department_cache(instance.id)

    elif 'attendance' in model_name:
        employee_id = getattr(instance, 'employee_id', None) or getattr(instance, 'emp_id', None)
        if employee_id:
            cache_invalidation_service.invalidate_attendance_cache(employee_id)

    elif any(keyword in model_name for keyword in ['product', 'inventory', 'invoice']):
        product_id = getattr(instance, 'product_id', None)
        cache_invalidation_service.invalidate_inventory_cache(product_id)


@receiver(post_delete)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """Invalidate relevant cache when model is deleted"""
    # Use the same logic as post_save
    invalidate_cache_on_save(sender, instance, **kwargs)
