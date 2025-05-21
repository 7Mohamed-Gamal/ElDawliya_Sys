from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def has_report_permission(user, report_type):
    """Check if user has permission to view a specific report type"""
    if user.is_superuser:
        return True
    return user.has_perm(f'hr.view_{report_type}_report')

def has_export_permission(user, report_type):
    """Check if user has permission to export a specific report type"""
    if user.is_superuser:
        return True
    return user.has_perm(f'hr.export_{report_type}_report')

def requires_report_permission(report_type):
    """Decorator to check if user has permission to view a specific report"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if has_report_permission(request.user, report_type):
                return view_func(request, *args, **kwargs)
            return redirect('accounts:access_denied')
        return wrapper
    return decorator

def requires_export_permission(report_type):
    """Decorator to check if user has permission to export a specific report"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if has_export_permission(request.user, report_type):
                return view_func(request, *args, **kwargs)
            return redirect('accounts:access_denied')
        return wrapper
    return decorator

# Alias for backward compatibility
require_report_permission = requires_report_permission
require_export_permission = requires_export_permission
