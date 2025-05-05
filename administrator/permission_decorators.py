from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve
from functools import wraps
from django.http import HttpResponseForbidden

from .models_new import OperationPermission, PagePermission, UserOperationPermission, UserPagePermission

def has_operation_permission(user, app_module_code, operation_code, permission_type):
    """
    Check if a user has permission to perform a specific operation
    
    Args:
        user: The user to check permissions for
        app_module_code: The code of the application module
        operation_code: The code of the operation
        permission_type: The type of permission (view, add, edit, delete, print)
    
    Returns:
        bool: True if the user has permission, False otherwise
    """
    # Admin users have all permissions
    if user.Role == 'admin':
        return True
    
    # Check if the user has the specific operation permission
    return UserOperationPermission.objects.filter(
        user=user,
        operation__app_module__code=app_module_code,
        operation__code=operation_code,
        operation__permission_type=permission_type,
        operation__is_active=True
    ).exists()

def has_page_permission(user, app_module_code, url_pattern):
    """
    Check if a user has permission to access a specific page
    
    Args:
        user: The user to check permissions for
        app_module_code: The code of the application module
        url_pattern: The URL pattern of the page
    
    Returns:
        bool: True if the user has permission, False otherwise
    """
    # Admin users have all permissions
    if user.Role == 'admin':
        return True
    
    # Check if the user has the specific page permission
    return UserPagePermission.objects.filter(
        user=user,
        page__app_module__code=app_module_code,
        page__url_pattern=url_pattern,
        page__is_active=True
    ).exists()

def operation_permission_required(app_module_code, operation_code, permission_type):
    """
    Decorator to check if a user has permission to perform a specific operation
    
    Args:
        app_module_code: The code of the application module
        operation_code: The code of the operation
        permission_type: The type of permission (view, add, edit, delete, print)
    
    Returns:
        function: The decorated function
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if has_operation_permission(request.user, app_module_code, operation_code, permission_type):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'ليس لديك صلاحية للقيام بهذه العملية')
                return redirect('home')
        return _wrapped_view
    return decorator

def page_permission_required(app_module_code, url_pattern):
    """
    Decorator to check if a user has permission to access a specific page
    
    Args:
        app_module_code: The code of the application module
        url_pattern: The URL pattern of the page
    
    Returns:
        function: The decorated function
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if has_page_permission(request.user, app_module_code, url_pattern):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة')
                return redirect('home')
        return _wrapped_view
    return decorator