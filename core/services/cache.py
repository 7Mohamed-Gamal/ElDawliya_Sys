"""
خدمة التخزين المؤقت
Cache Service for performance optimization
"""
from django.core.cache import cache
from django.conf import settings
from .base import BaseService


class CacheService(BaseService):
    """
    خدمة التخزين المؤقت المتقدمة
    Advanced caching service for performance optimization
    """

    # Cache timeout configurations
    CACHE_TIMEOUTS = {
        'short': 300,      # 5 minutes
        'medium': 1800,    # 30 minutes
        'long': 3600,      # 1 hour
        'daily': 86400,    # 24 hours
        'weekly': 604800,  # 7 days
    }

    # Cache key prefixes
    PREFIXES = {
        'user': 'user',
        'employee': 'emp',
        'department': 'dept',
        'product': 'prod',
        'inventory': 'inv',
        'report': 'rpt',
        'settings': 'set',
        'permissions': 'perm',
    }

    @classmethod
    def get_or_set(cls, key, callable_func, timeout='medium', version=None):
        """
        الحصول على قيمة من التخزين المؤقت أو تعيينها
        Get value from cache or set it using callable function
        """
        timeout_seconds = cls.CACHE_TIMEOUTS.get(timeout, timeout)

        cached_value = cache.get(key, version=version)
        if cached_value is not None:
            return cached_value

        # Generate value using callable
        value = callable_func()
        cache.set(key, value, timeout_seconds, version=version)
        return value

    @classmethod
    def set(cls, key, value, timeout='medium', version=None):
        """
        تعيين قيمة في التخزين المؤقت
        Set value in cache
        """
        timeout_seconds = cls.CACHE_TIMEOUTS.get(timeout, timeout)
        cache.set(key, value, timeout_seconds, version=version)

    @classmethod
    def get(cls, key, default=None, version=None):
        """
        الحصول على قيمة من التخزين المؤقت
        Get value from cache
        """
        return cache.get(key, default, version=version)

    @classmethod
    def delete(cls, key, version=None):
        """
        حذف قيمة من التخزين المؤقت
        Delete value from cache
        """
        cache.delete(key, version=version)

    @classmethod
    def delete_many(cls, keys, version=None):
        """
        حذف قيم متعددة من التخزين المؤقت
        Delete multiple values from cache
        """
        cache.delete_many(keys, version=version)

    @classmethod
    def clear(cls):
        """
        مسح جميع قيم التخزين المؤقت
        Clear all cache
        """
        cache.clear()

    @classmethod
    def invalidate_pattern(cls, pattern):
        """
        إبطال التخزين المؤقت بنمط معين
        Invalidate cache entries matching pattern
        """
        try:
            # This works with Redis backend
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(pattern)
            else:
                # Fallback for other backends
                keys = cache.keys(pattern) if hasattr(cache, 'keys') else []
                if keys:
                    cache.delete_many(keys)
        except Exception as e:
            # Log error but don't fail
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Cache pattern invalidation failed: {e}")

    @classmethod
    def make_key(cls, prefix, *args):
        """
        إنشاء مفتاح التخزين المؤقت
        Generate cache key with prefix
        """
        prefix_value = cls.PREFIXES.get(prefix, prefix)
        key_parts = [prefix_value] + [str(arg) for arg in args]
        return ':'.join(key_parts)

    @classmethod
    def warm_up_cache(cls):
        """
        تسخين التخزين المؤقت بالبيانات الأساسية
        Warm up cache with essential data
        """
        from core.models.settings import SystemSetting
        from core.models.permissions import Module, Permission

        # Cache system settings
        cls.get_or_set(
            cls.make_key('settings', 'all'),
            lambda: list(SystemSetting.objects.filter(is_active=True).values()),
            'daily'
        )

        # Cache modules and permissions
        cls.get_or_set(
            cls.make_key('permissions', 'modules'),
            lambda: list(Module.objects.filter(is_active=True).values()),
            'daily'
        )

        cls.get_or_set(
            cls.make_key('permissions', 'all'),
            lambda: list(Permission.objects.filter(is_active=True).select_related('module').values(
                'id', 'module__name', 'permission_type', 'codename', 'name'
            )),
            'daily'
        )

    @classmethod
    def cache_user_data(cls, user_id):
        """
        تخزين بيانات المستخدم مؤقتاً
        Cache user-specific data
        """
        from django.contrib.auth.models import User
        from core.services.permissions import PermissionService

        try:
            user = User.objects.get(id=user_id)

            # Cache user permissions
            perm_service = PermissionService(user=user)
            user_permissions = perm_service.get_user_permissions()
            cls.set(
                cls.make_key('user', user_id, 'permissions'),
                user_permissions,
                'medium'
            )

            # Cache user roles
            user_roles = perm_service.get_user_roles()
            cls.set(
                cls.make_key('user', user_id, 'roles'),
                user_roles,
                'medium'
            )

            return True

        except User.DoesNotExist:
            return False

    @classmethod
    def invalidate_user_cache(cls, user_id):
        """
        إبطال التخزين المؤقت للمستخدم
        Invalidate user-specific cache
        """
        patterns = [
            cls.make_key('user', user_id, '*'),
        ]

        for pattern in patterns:
            cls.invalidate_pattern(pattern)

    @classmethod
    def cache_employee_data(cls, employee_id):
        """
        تخزين بيانات الموظف مؤقتاً
        Cache employee-specific data
        """
        # This will be implemented when we have employee models
        pass

    @classmethod
    def invalidate_employee_cache(cls, employee_id):
        """
        إبطال التخزين المؤقت للموظف
        Invalidate employee-specific cache
        """
        patterns = [
            cls.make_key('employee', employee_id, '*'),
            cls.make_key('dept', '*', 'employees'),  # Department employee lists
        ]

        for pattern in patterns:
            cls.invalidate_pattern(pattern)

    @classmethod
    def cache_department_data(cls, department_id):
        """
        تخزين بيانات القسم مؤقتاً
        Cache department-specific data
        """
        # This will be implemented when we have department models
        pass

    @classmethod
    def invalidate_department_cache(cls, department_id):
        """
        إبطال التخزين المؤقت للقسم
        Invalidate department-specific cache
        """
        patterns = [
            cls.make_key('dept', department_id, '*'),
        ]

        for pattern in patterns:
            cls.invalidate_pattern(pattern)

    @classmethod
    def cache_product_data(cls, product_id):
        """
        تخزين بيانات المنتج مؤقتاً
        Cache product-specific data
        """
        # This will be implemented when we have product models
        pass

    @classmethod
    def invalidate_product_cache(cls, product_id):
        """
        إبطال التخزين المؤقت للمنتج
        Invalidate product-specific cache
        """
        patterns = [
            cls.make_key('product', product_id, '*'),
            cls.make_key('inv', '*'),  # Inventory summaries
        ]

        for pattern in patterns:
            cls.invalidate_pattern(pattern)

    @classmethod
    def get_cache_stats(cls):
        """
        الحصول على إحصائيات التخزين المؤقت
        Get cache statistics
        """
        try:
            if hasattr(cache, 'get_stats'):
                return cache.get_stats()
            else:
                return {
                    'backend': cache.__class__.__name__,
                    'location': getattr(cache, '_cache', {}).get('LOCATION', 'Unknown'),
                    'stats_available': False
                }
        except Exception as e:
            return {
                'error': str(e),
                'stats_available': False
            }

    @classmethod
    def cache_report_data(cls, report_key, data, timeout='long'):
        """
        تخزين بيانات التقرير مؤقتاً
        Cache report data
        """
        cache_key = cls.make_key('report', report_key)
        cls.set(cache_key, data, timeout)
        return cache_key

    @classmethod
    def get_cached_report(cls, report_key):
        """
        الحصول على تقرير مخزن مؤقتاً
        Get cached report data
        """
        cache_key = cls.make_key('report', report_key)
        return cls.get(cache_key)

    @classmethod
    def invalidate_reports_cache(cls):
        """
        إبطال تخزين التقارير المؤقت
        Invalidate all cached reports
        """
        cls.invalidate_pattern(cls.make_key('report', '*'))

    def cache_user_preferences(self, user_id, preferences):
        """
        تخزين تفضيلات المستخدم مؤقتاً
        Cache user preferences
        """
        cache_key = self.make_key('user', user_id, 'preferences')
        self.set(cache_key, preferences, 'daily')

    def get_cached_user_preferences(self, user_id):
        """
        الحصول على تفضيلات المستخدم المخزنة مؤقتاً
        Get cached user preferences
        """
        cache_key = self.make_key('user', user_id, 'preferences')
        return self.get(cache_key, {})

    def invalidate_user_preferences(self, user_id):
        """
        إبطال تفضيلات المستخدم المخزنة مؤقتاً
        Invalidate cached user preferences
        """
        cache_key = self.make_key('user', user_id, 'preferences')
        self.delete(cache_key)
