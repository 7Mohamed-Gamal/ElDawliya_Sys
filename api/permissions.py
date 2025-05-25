from rest_framework import permissions
from django.contrib.auth.models import Group


class HasAPIAccess(permissions.BasePermission):
    """
    Custom permission to check if user has API access
    """
    message = 'You do not have permission to access the API.'
    
    def has_permission(self, request, view):
        """
        Check if user has API access permission
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have access
        if request.user.is_superuser:
            return True
        
        # Check if user is in API access group
        try:
            api_group = Group.objects.get(name='API_Users')
            if api_group in request.user.groups.all():
                return True
        except Group.DoesNotExist:
            pass
        
        # Check if user is staff
        if request.user.is_staff:
            return True
        
        # Check if user has active API keys
        if hasattr(request.user, 'api_keys') and request.user.api_keys.filter(is_active=True).exists():
            return True
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
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
