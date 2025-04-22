from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.urls import reverse
from accounts.models import Users_Login_New
from functools import wraps
from .utils import has_template_permission, check_permission
from .models import Department, Module, Permission

def admin_required(view_func):
    """Decorator to require admin role for a view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        # Check if user has admin role
        if request.user.Role != 'admin':
            messages.error(request, 'هذه الصفحة متاحة فقط للإدارة.')
            return redirect('accounts:home')

        return view_func(request, *args, **kwargs)
    return wrapper

def action_permission_required(action_type):
    """
    Decorator that checks if user has permission for a specific action type.
    Action types: add, change, delete, print

    Only admin users can perform these actions
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')

            # Allow view access for all authenticated users
            if action_type == 'view':
                return view_func(request, *args, **kwargs)

            # For other actions, only admin can perform them
            if request.user.Role != 'admin':
                if request.is_ajax():
                    return HttpResponseForbidden('ليس لديك صلاحية للقيام بهذا الإجراء')

                messages.error(request, 'ليس لديك صلاحية للقيام بهذا الإجراء')
                # Redirect to previous page or homepage
                referer = request.META.get('HTTP_REFERER')
                if referer:
                    return redirect(referer)
                return redirect('accounts:home')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def module_permission_required(department_name, module_name, permission_type='view'):
    """
    Decorator to check if user has permission to access a module.

    Args:
        department_name: Name of the department
        module_name: Name of the module
        permission_type: Type of permission (view, add, edit, delete, print)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # المشرفون لديهم جميع الصلاحيات
            if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
                return view_func(request, *args, **kwargs)

            # التحقق من صلاحية المستخدم
            has_permission = check_permission(
                user=request.user,
                department_name=department_name,
                module_name=module_name,
                permission_type=permission_type
            )

            if has_permission:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f'ليس لديك صلاحية {permission_type} في {module_name}')
                return redirect('accounts:home')

        return _wrapped_view

    return decorator


def has_module_permission(request, department_name, module_name, permission_type='view'):
    """
    Function to check if user has permission to access a module.
    Can be used in templates or views.

    Args:
        request: The request object
        department_name: Name of the department
        module_name: Name of the module
        permission_type: Type of permission (view, add, edit, delete, print)
    """
    # المشرفون لديهم جميع الصلاحيات
    if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
        return True

    # التحقق من صلاحية المستخدم
    return check_permission(
        user=request.user,
        department_name=department_name,
        module_name=module_name,
        permission_type=permission_type
    )
