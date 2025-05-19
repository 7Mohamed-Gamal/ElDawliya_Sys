from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required as django_permission_required

from administrator.utils import check_permission

def admin_or_permission_required(perm):
    """
    ديكوريتور للتحقق من أن المستخدم إما مشرف أو لديه صلاحية معينة
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # المشرفون لديهم جميع الصلاحيات
            if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
                return view_func(request, *args, **kwargs)
                
            # التحقق من صلاحية المستخدم
            if not request.user.has_perm(perm):
                messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة')
                return redirect('accounts:access_denied')
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def module_permission_required(department_name, module_name, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة

    المعلمات:
    - department_name: اسم القسم (مثل 'الموارد البشرية')
    - module_name: اسم الوحدة (مثل 'إدارة الموظفين')
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if check_permission(request.user, department_name, module_name, permission_type):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f"ليس لديك صلاحية {permission_type} في {module_name}")
                return redirect('accounts:access_denied')
        return _wrapped_view
    return decorator

def class_permission_required(department_name, module_name, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة
    للاستخدام مع الـ Class-Based Views

    المعلمات:
    - department_name: اسم القسم (مثل 'الموارد البشرية')
    - module_name: اسم الوحدة (مثل 'إدارة الموظفين')
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    return method_decorator(
        module_permission_required(
            department_name=department_name,
            module_name=module_name,
            permission_type=permission_type
        ),
        name='dispatch'
    )
