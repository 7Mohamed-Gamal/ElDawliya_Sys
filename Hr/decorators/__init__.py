# مجلد decorators لتطبيق الموارد البشرية

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def hr_module_permission_required(module_name=None, action=None):
    """
    Decorator للتحقق من صلاحيات وحدة الموارد البشرية
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # التحقق من أن المستخدم مسجل دخول
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            # السماح للمدراء بالوصول لكل شيء
            if request.user.is_superuser or request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            # التحقق من الصلاحية المحددة إذا تم تمريرها
            if module_name and action:
                permission_name = f'Hr.{action}_{module_name}'
                if not request.user.has_perm(permission_name):
                    messages.error(request, 'ليس لديك صلاحية للوصول لهذه الصفحة')
                    raise PermissionDenied
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Alias للتوافق مع الكود الموجود
hr_permission_required = hr_module_permission_required