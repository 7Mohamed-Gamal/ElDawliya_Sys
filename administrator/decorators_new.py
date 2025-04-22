from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from accounts.models import Users_Login_New
from functools import wraps
from .utils import has_template_permission

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

def template_permission_required(template_path):
    """
    ديكوريتور للتحقق من صلاحية الوصول إلى قالب معين
    
    الاستخدام:
    @template_permission_required('Hr/reports/monthly_salary_report.html')
    def monthly_salary_report(request):
        # عرض التقرير
        return render(request, 'Hr/reports/monthly_salary_report.html', context)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not has_template_permission(request.user, template_path):
                messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة')
                return redirect('accounts:access_denied')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator