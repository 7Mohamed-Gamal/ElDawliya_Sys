"""
Enhanced permissions system for API with granular access control
نظام الصلاحيات المحسن لـ API مع التحكم الدقيق في الوصول
"""

import logging
from rest_framework import permissions
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.utils import timezone

# Import with error handling
try:
    from core.services.permission_service import HierarchicalPermissionService
except ImportError:
    # Create a dummy service if not available
    class HierarchicalPermissionService:
        def __init__(self, user):
            self.user = user
        
        def has_module_permission(self, module_name, action, obj=None):
            return self.user.is_superuser
        
        def has_permission(self, permission_codename, obj=None):
            return self.user.is_superuser
        
        def get_user_roles(self):
            return []

logger = logging.getLogger(__name__)


class HasAPIAccess(permissions.BasePermission):
    """
    Enhanced permission to check if user has API access
    صلاحية محسنة للتحقق من وصول المستخدم لـ API
    """
    message = 'ليس لديك صلاحية للوصول إلى API.'

    def has_permission(self, request, view):
        """
        Check if user has API access permission with caching
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Cache permission check for performance
        cache_key = f"api_access_{request.user.id}"
        has_access = cache.get(cache_key)

        if has_access is None:
            has_access = self._check_api_access(request.user)
            cache.set(cache_key, has_access, 300)  # Cache for 5 minutes

        if has_access:
            # Log API access
            logger.info(f"API access granted to user: {request.user.username}")
        else:
            logger.warning(f"API access denied to user: {request.user.username}")

        return has_access

    def _check_api_access(self, user):
        """
        Internal method to check API access
        """
        # Superusers always have access
        if user.is_superuser:
            return True

        # Check if user is staff
        if user.is_staff:
            return True

        return False


class ModulePermission(permissions.BasePermission):
    """
    Permission class for module-based access control
    فئة الصلاحيات للتحكم في الوصول القائم على الوحدات
    """

    def __init__(self, module_name, action='view'):
        """__init__ function"""
        self.module_name = module_name
        self.action = action
        super().__init__()

    def has_permission(self, request, view):
        """
        Check if user has permission for specific module and action
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers have all permissions
        if request.user.is_superuser:
            return True

        # Check module-specific permission
        permission_name = f"{self.module_name}.{self.action}"

        # Check direct permission
        if request.user.has_perm(permission_name):
            return True

        return False