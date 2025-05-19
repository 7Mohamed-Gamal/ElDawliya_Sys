from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils.translation import gettext as _

from .utils import check_permission

def module_permission_required(department_name, module_name, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في قسم معين

    المعلمات:
    - department_name: اسم القسم (مثل 'الموارد البشرية')
    - module_name: اسم الوحدة (مثل 'إدارة الموظفين')
    - permission_type: نوع الصلاحية ('view', 'add', 'change', 'delete', 'print')

    الاستخدام:
    @module_permission_required('الموارد البشرية', 'إدارة الموظفين', 'view')
    def employee_list(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # التحقق من تسجيل دخول المستخدم
            if not request.user.is_authenticated:
                messages.error(request, _('الرجاء تسجيل الدخول للوصول لهذه الصفحة.'))
                return redirect('accounts:login')
                
            # المستخدمون المتميزون لديهم جميع الصلاحيات
            if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
                return view_func(request, *args, **kwargs)

            # التحقق من صلاحية المستخدم باستخدام دالة check_permission
            has_perm = check_permission(
                user=request.user,
                department_name=department_name,
                module_name=module_name,
                permission_type=permission_type
            )

            if has_perm:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, _(
                    'لا تملك الصلاحية للوصول لهذه الصفحة. '
                    'الرجاء التواصل مع مدير النظام للحصول على الصلاحيات المناسبة.'
                ))
                # العودة للصفحة الرئيسية أو صفحة رفض الوصول
                if 'access_denied' in request.path:
                    # لتجنب التكرار إذا كنا بالفعل في صفحة رفض الوصول
                    return HttpResponseForbidden("Access Denied")
                return redirect('accounts:access_denied')
                
        return _wrapped_view
    return decorator


def template_permission_required(template_path):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لقالب معين

    المعلمات:
    - template_path: مسار القالب (مثل 'Hr/reports/monthly_salary_report.html')

    الاستخدام:
    @template_permission_required('Hr/reports/monthly_salary_report.html')
    def monthly_salary_report(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            from .utils import has_template_permission
            
            # التحقق من تسجيل دخول المستخدم
            if not request.user.is_authenticated:
                messages.error(request, _('الرجاء تسجيل الدخول للوصول لهذه الصفحة.'))
                return redirect('accounts:login')
                
            # المستخدمون المتميزون لديهم جميع الصلاحيات
            if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
                return view_func(request, *args, **kwargs)

            # التحقق من صلاحية المستخدم باستخدام دالة has_template_permission
            has_perm = has_template_permission(
                user=request.user,
                template_path=template_path
            )

            if has_perm:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, _(
                    'لا تملك الصلاحية للوصول لهذا القالب. '
                    'الرجاء التواصل مع مدير النظام للحصول على الصلاحيات المناسبة.'
                ))
                # العودة للصفحة الرئيسية أو صفحة رفض الوصول
                if 'access_denied' in request.path:
                    # لتجنب التكرار إذا كنا بالفعل في صفحة رفض الوصول
                    return HttpResponseForbidden("Access Denied")
                return redirect('accounts:access_denied')
                
        return _wrapped_view
    return decorator
