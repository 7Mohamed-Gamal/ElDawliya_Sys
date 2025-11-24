"""
Enhanced permissions system for API with granular access control
نظام الصلاحيات المحسن لـ API مع التحكم الدقيق في الوصول
"""

import logging
from rest_framework import permissions
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.utils import timezone

from core.services.permission_service import HierarchicalPermissionService

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

        # Check if user is in API access group
        try:
            api_group = Group.objects.get(name='API_Users')
            if api_group in user.groups.all():
                return True
        except Group.DoesNotExist:
            pass

        # Check if user is staff
        if user.is_staff:
            return True

        # Check if user has active API keys
        if hasattr(user, 'api_keys') and user.api_keys.filter(is_active=True).exists():
            return True

        # Check if user has specific API permissions
        api_permissions = [
            'api.view_data',
            'api.access_endpoints',
            'api.use_api',
        ]

        if any(user.has_perm(perm) for perm in api_permissions):
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

        # Check group-based permission
        try:
            module_group = Group.objects.get(name=f"{self.module_name.upper()}_Users")
            if module_group in request.user.groups.all():
                return True
        except Group.DoesNotExist:
            pass

        return False


class DynamicPermission(permissions.BasePermission):
    """
    Dynamic permission that can be configured per view
    صلاحية ديناميكية يمكن تكوينها لكل عرض
    """

    def has_permission(self, request, view):
        """
        Check permissions based on view configuration
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Get required permissions from view
        required_permissions = getattr(view, 'required_permissions', [])

        if not required_permissions:
            return True  # No specific permissions required

        # Check if user has all required permissions
        for permission in required_permissions:
            if not request.user.has_perm(permission):
                return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions
        """
        # Get required object permissions from view
        required_object_permissions = getattr(view, 'required_object_permissions', [])

        if not required_object_permissions:
            return True

        # Check object-level permissions
        for permission in required_object_permissions:
            if not request.user.has_perm(permission, obj):
                return False

        return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """has_object_permission function"""
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff users to edit objects.
    """

    def has_permission(self, request, view):
        """has_permission function"""
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions only for staff
        return request.user and request.user.is_staff


class CanAccessHRData(permissions.BasePermission):
    """
    Permission for accessing HR data
    """
    message = 'You do not have permission to access HR data.'

    def has_permission(self, request, view):
        """has_permission function"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers always have access
        if request.user.is_superuser:
            return True

        # Check if user is in HR group
        try:
            hr_group = Group.objects.get(name='HR_Users')
            if hr_group in request.user.groups.all():
                return True
        except Group.DoesNotExist:
            pass

        return False


class CanAccessInventoryData(permissions.BasePermission):
    """
    Permission for accessing inventory data
    """
    message = 'You do not have permission to access inventory data.'

    def has_permission(self, request, view):
        """has_permission function"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers always have access
        if request.user.is_superuser:
            return True

        # Check if user is in inventory group
        try:
            inventory_group = Group.objects.get(name='Inventory_Users')
            if inventory_group in request.user.groups.all():
                return True
        except Group.DoesNotExist:
            pass

        return False


class CanAccessTaskData(permissions.BasePermission):
    """
    Permission for accessing task data
    """
    message = 'You do not have permission to access task data.'

    def has_permission(self, request, view):
        """has_permission function"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers always have access
        if request.user.is_superuser:
            return True

        # Users can access their own tasks
        if hasattr(view, 'get_queryset'):
            return True

        return False


class CanUseMeetingData(permissions.BasePermission):
    """
    Permission for accessing meeting data
    """
    message = 'You do not have permission to access meeting data.'

    def has_permission(self, request, view):
        """has_permission function"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers always have access
        if request.user.is_superuser:
            return True

        # Check if user is in meetings group
        try:
            meetings_group = Group.objects.get(name='Meeting_Users')
            if meetings_group in request.user.groups.all():
                return True
        except Group.DoesNotExist:
            pass

        return False


class CanUseGeminiAI(permissions.BasePermission):
    """
    Permission for using Gemini AI features
    """
    message = 'You do not have permission to use AI features.'

    def has_permission(self, request, view):
        """has_permission function"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers always have access
        if request.user.is_superuser:
            return True

        # Check if user is in AI users group
        try:
            ai_group = Group.objects.get(name='AI_Users')
            if ai_group in request.user.groups.all():
                return True
        except Group.DoesNotExist:
            pass

        # Staff users can use AI
        if request.user.is_staff:
            return True

        return False


class HasModulePermission(permissions.BasePermission):
    """
    Enhanced permission class using hierarchical permission system
    فئة الصلاحيات المحسنة باستخدام نظام الصلاحيات الهرمي
    """

    def __init__(self, module_name: str = None, action: str = 'view'):
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

        # Get module and action from view if not provided
        module_name = self.module_name or getattr(view, 'permission_module', None)
        action = self.action or getattr(view, 'permission_action', 'view')

        if not module_name:
            # If no module specified, allow access (backward compatibility)
            return True

        # Use hierarchical permission service
        permission_service = HierarchicalPermissionService(request.user)
        return permission_service.has_module_permission(module_name, action)

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions using hierarchical system
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Get module and action from view
        module_name = self.module_name or getattr(view, 'permission_module', None)
        action = self.action or getattr(view, 'permission_action', 'view')

        if not module_name:
            return True

        # Use hierarchical permission service for object-level check
        permission_service = HierarchicalPermissionService(request.user)
        return permission_service.has_module_permission(module_name, action, obj)


class HierarchicalPermission(permissions.BasePermission):
    """
    Permission class that uses the full hierarchical permission system
    فئة الصلاحيات التي تستخدم نظام الصلاحيات الهرمي الكامل
    """

    def has_permission(self, request, view):
        """
        Check permissions using hierarchical system
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Get required permissions from view
        required_permissions = getattr(view, 'required_permissions', [])

        if not required_permissions:
            return True

        # Use hierarchical permission service
        permission_service = HierarchicalPermissionService(request.user)

        # Check all required permissions
        for permission_codename in required_permissions:
            if not permission_service.has_permission(permission_codename):
                return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions using hierarchical system
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Get required object permissions from view
        required_object_permissions = getattr(view, 'required_object_permissions', [])

        if not required_object_permissions:
            return True

        # Use hierarchical permission service
        permission_service = HierarchicalPermissionService(request.user)

        # Check all required object permissions
        for permission_codename in required_object_permissions:
            if not permission_service.has_permission(permission_codename, obj):
                return False

        return True


class RoleBasedPermission(permissions.BasePermission):
    """
    Permission class based on user roles
    فئة الصلاحيات القائمة على أدوار المستخدمين
    """

    def __init__(self, required_roles: list = None):
        """__init__ function"""
        self.required_roles = required_roles or []
        super().__init__()

    def has_permission(self, request, view):
        """
        Check if user has any of the required roles
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Get required roles from view if not provided
        required_roles = self.required_roles or getattr(view, 'required_roles', [])

        if not required_roles:
            return True

        # Use hierarchical permission service
        permission_service = HierarchicalPermissionService(request.user)
        user_roles = permission_service.get_user_roles()

        # Check if user has any of the required roles
        user_role_names = [role.role.name for role in user_roles if role.is_valid()]

        return any(role_name in user_role_names for role_name in required_roles)


class ApprovalRequiredPermission(permissions.BasePermission):
    """
    Permission class for operations that require approval
    فئة الصلاحيات للعمليات التي تتطلب موافقة
    """

    def has_permission(self, request, view):
        """
        Check if operation requires approval workflow
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # For write operations on sensitive data, check if approval is required
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            sensitive_operations = getattr(view, 'sensitive_operations', [])

            if request.method.lower() in sensitive_operations:
                # This would typically create an approval workflow
                # For now, we'll check if user has admin privileges
                return request.user.is_superuser or request.user.is_staff

        return True


class ConditionalPermission(permissions.BasePermission):
    """
    Permission class with conditional access based on context
    فئة الصلاحيات مع الوصول المشروط بناءً على السياق
    """

    def has_permission(self, request, view):
        """
        Check permissions based on conditions
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Get conditions from view
        permission_conditions = getattr(view, 'permission_conditions', {})

        if not permission_conditions:
            return True

        # Check time-based conditions
        if 'time_restrictions' in permission_conditions:
            time_restrictions = permission_conditions['time_restrictions']
            current_time = timezone.now().time()

            if 'start_time' in time_restrictions and 'end_time' in time_restrictions:
                start_time = time_restrictions['start_time']
                end_time = time_restrictions['end_time']

                if not (start_time <= current_time <= end_time):
                    return False

        # Check IP-based conditions
        if 'allowed_ips' in permission_conditions:
            client_ip = self._get_client_ip(request)
            allowed_ips = permission_conditions['allowed_ips']

            if client_ip not in allowed_ips:
                return False

        # Check department-based conditions
        if 'allowed_departments' in permission_conditions:
            # This would need to be implemented based on your user-department relationship
            pass

        return True

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
