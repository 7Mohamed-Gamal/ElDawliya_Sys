"""
Decorators للتحقق من الصلاحيات المتقدمة في نظام الموارد البشرية
"""

from functools import wraps
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied
from django.conf import settings
import logging

from .models_permissions import UserRole, PermissionLog

logger = logging.getLogger(__name__)


def hr_permission_required(permission_codename, scope_context_func=None, 
                          raise_exception=True, redirect_url=None):
    """
    Decorator للتحقق من صلاحيات الموارد البشرية
    
    Args:
        permission_codename: رمز الصلاحية المطلوبة
        scope_context_func: دالة لاستخراج سياق النطاق من الطلب
        raise_exception: رفع استثناء أم إرجاع رد مناسب
        redirect_url: رابط إعادة التوجيه في حالة عدم وجود صلاحية
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            try:
                # الحصول على دور المستخدم
                user_role = UserRole.objects.get(user=request.user, is_active=True)
            except UserRole.DoesNotExist:
                logger.warning(f"User {request.user.username} has no HR role assigned")
                return _handle_permission_denied(
                    request, "لا يوجد دور محدد للمستخدم", 
                    raise_exception, redirect_url
                )
            
            # استخراج سياق النطاق
            scope_context = {}
            if scope_context_func:
                try:
                    scope_context = scope_context_func(request, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Error extracting scope context: {e}")
            
            # التحقق من الصلاحية
            if user_role.has_permission(permission_codename, scope_context):
                # تسجيل استخدام الصلاحية
                _log_permission_usage(request, permission_codename, user_role)
                return view_func(request, *args, **kwargs)
            else:
                logger.warning(
                    f"User {request.user.username} denied access to {permission_codename}"
                )
                return _handle_permission_denied(
                    request, f"ليس لديك صلاحية: {permission_codename}", 
                    raise_exception, redirect_url
                )
        
        return _wrapped_view
    return decorator


def hr_any_permission_required(*permission_codenames, scope_context_func=None,
                              raise_exception=True, redirect_url=None):
    """
    Decorator للتحقق من وجود أي من الصلاحيات المحددة
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            try:
                user_role = UserRole.objects.get(user=request.user, is_active=True)
            except UserRole.DoesNotExist:
                return _handle_permission_denied(
                    request, "لا يوجد دور محدد للمستخدم", 
                    raise_exception, redirect_url
                )
            
            scope_context = {}
            if scope_context_func:
                try:
                    scope_context = scope_context_func(request, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Error extracting scope context: {e}")
            
            # التحقق من أي من الصلاحيات
            for permission_codename in permission_codenames:
                if user_role.has_permission(permission_codename, scope_context):
                    _log_permission_usage(request, permission_codename, user_role)
                    return view_func(request, *args, **kwargs)
            
            return _handle_permission_denied(
                request, f"ليس لديك أي من الصلاحيات المطلوبة", 
                raise_exception, redirect_url
            )
        
        return _wrapped_view
    return decorator


def hr_all_permissions_required(*permission_codenames, scope_context_func=None,
                               raise_exception=True, redirect_url=None):
    """
    Decorator للتحقق من وجود جميع الصلاحيات المحددة
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            try:
                user_role = UserRole.objects.get(user=request.user, is_active=True)
            except UserRole.DoesNotExist:
                return _handle_permission_denied(
                    request, "لا يوجد دور محدد للمستخدم", 
                    raise_exception, redirect_url
                )
            
            scope_context = {}
            if scope_context_func:
                try:
                    scope_context = scope_context_func(request, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Error extracting scope context: {e}")
            
            # التحقق من جميع الصلاحيات
            missing_permissions = []
            for permission_codename in permission_codenames:
                if not user_role.has_permission(permission_codename, scope_context):
                    missing_permissions.append(permission_codename)
            
            if missing_permissions:
                return _handle_permission_denied(
                    request, f"تفتقد للصلاحيات: {', '.join(missing_permissions)}", 
                    raise_exception, redirect_url
                )
            
            # تسجيل استخدام جميع الصلاحيات
            for permission_codename in permission_codenames:
                _log_permission_usage(request, permission_codename, user_role)
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator


def hr_department_scope_required(permission_codename, department_field='department_id'):
    """
    Decorator للتحقق من صلاحية على مستوى القسم
    """
    def scope_context_func(request, *args, **kwargs):
        department_id = kwargs.get(department_field) or request.GET.get(department_field)
        return {'department_id': department_id} if department_id else {}
    
    return hr_permission_required(
        permission_codename, 
        scope_context_func=scope_context_func
    )


def hr_employee_scope_required(permission_codename, employee_field='employee_id'):
    """
    Decorator للتحقق من صلاحية على مستوى الموظف
    """
    def scope_context_func(request, *args, **kwargs):
        employee_id = kwargs.get(employee_field) or request.GET.get(employee_field)
        context = {}
        
        if employee_id:
            try:
                from .models import Employee
                employee = Employee.objects.get(id=employee_id)
                context.update({
                    'employee_id': employee_id,
                    'department_id': employee.department.id if employee.department else None,
                    'branch_id': employee.branch.id if employee.branch else None,
                    'user_id': employee.user.id if employee.user else None,
                })
            except Employee.DoesNotExist:
                pass
        
        return context
    
    return hr_permission_required(
        permission_codename, 
        scope_context_func=scope_context_func
    )


def hr_api_permission_required(permission_codename, scope_context_func=None):
    """
    Decorator للتحقق من الصلاحيات في API
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required',
                    'message': 'يجب تسجيل الدخول أولاً'
                }, status=401)
            
            try:
                user_role = UserRole.objects.get(user=request.user, is_active=True)
            except UserRole.DoesNotExist:
                return JsonResponse({
                    'error': 'No role assigned',
                    'message': 'لا يوجد دور محدد للمستخدم'
                }, status=403)
            
            scope_context = {}
            if scope_context_func:
                try:
                    scope_context = scope_context_func(request, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Error extracting scope context: {e}")
            
            if user_role.has_permission(permission_codename, scope_context):
                _log_permission_usage(request, permission_codename, user_role)
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({
                    'error': 'Permission denied',
                    'message': f'ليس لديك صلاحية: {permission_codename}'
                }, status=403)
        
        return _wrapped_view
    return decorator


def hr_admin_required(view_func):
    """
    Decorator للتحقق من صلاحيات الإدارة
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        try:
            user_role = UserRole.objects.get(user=request.user, is_active=True)
            admin_permissions = user_role.get_all_permissions().filter(
                permission_type='admin'
            )
            
            if admin_permissions.exists():
                return view_func(request, *args, **kwargs)
            else:
                return _handle_permission_denied(
                    request, "يتطلب صلاحيات إدارية"
                )
        except UserRole.DoesNotExist:
            return _handle_permission_denied(
                request, "لا يوجد دور محدد للمستخدم"
            )
    
    return _wrapped_view


def hr_conditional_permission(condition_func, permission_codename, 
                             fallback_permission=None):
    """
    Decorator للصلاحيات المشروطة
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            try:
                user_role = UserRole.objects.get(user=request.user, is_active=True)
            except UserRole.DoesNotExist:
                return _handle_permission_denied(
                    request, "لا يوجد دور محدد للمستخدم"
                )
            
            # تقييم الشرط
            try:
                condition_result = condition_func(request, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error evaluating condition: {e}")
                condition_result = False
            
            # اختيار الصلاحية المناسبة
            required_permission = permission_codename if condition_result else fallback_permission
            
            if required_permission and user_role.has_permission(required_permission):
                _log_permission_usage(request, required_permission, user_role)
                return view_func(request, *args, **kwargs)
            elif not required_permission:
                # لا توجد صلاحية مطلوبة
                return view_func(request, *args, **kwargs)
            else:
                return _handle_permission_denied(
                    request, f"ليس لديك صلاحية: {required_permission}"
                )
        
        return _wrapped_view
    return decorator


def _handle_permission_denied(request, message, raise_exception=True, redirect_url=None):
    """معالجة رفض الصلاحية"""
    
    if request.headers.get('Content-Type') == 'application/json' or \
       request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Permission denied',
            'message': message
        }, status=403)
    
    if raise_exception:
        raise PermissionDenied(message)
    
    messages.error(request, message)
    
    if redirect_url:
        return redirect(redirect_url)
    else:
        return redirect('Hr:dashboard')


def _log_permission_usage(request, permission_codename, user_role):
    """تسجيل استخدام الصلاحية"""
    try:
        from .models_permissions import HRPermission
        
        permission = HRPermission.objects.get(
            codename=permission_codename, 
            is_active=True
        )
        
        # الحصول على معلومات الطلب
        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # تسجيل الاستخدام
        PermissionLog.objects.create(
            user=request.user,
            permission=permission,
            action='used',
            performed_by=request.user,
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                'path': request.path,
                'method': request.method,
                'role_template': user_role.role_template.name if user_role.role_template else None,
            }
        )
        
    except Exception as e:
        logger.error(f"Error logging permission usage: {e}")


def _get_client_ip(request):
    """الحصول على عنوان IP الخاص بالعميل"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Helper functions for common scope contexts

def get_employee_scope_context(request, *args, **kwargs):
    """استخراج سياق نطاق الموظف"""
    employee_id = kwargs.get('employee_id') or request.GET.get('employee_id')
    if employee_id:
        try:
            from .models import Employee
            employee = Employee.objects.select_related(
                'department', 'branch', 'user'
            ).get(id=employee_id)
            
            return {
                'employee_id': employee_id,
                'department_id': employee.department.id if employee.department else None,
                'branch_id': employee.branch.id if employee.branch else None,
                'user_id': employee.user.id if employee.user else None,
            }
        except Employee.DoesNotExist:
            pass
    
    return {}


def get_department_scope_context(request, *args, **kwargs):
    """استخراج سياق نطاق القسم"""
    department_id = kwargs.get('department_id') or request.GET.get('department_id')
    return {'department_id': department_id} if department_id else {}


def get_branch_scope_context(request, *args, **kwargs):
    """استخراج سياق نطاق الفرع"""
    branch_id = kwargs.get('branch_id') or request.GET.get('branch_id')
    return {'branch_id': branch_id} if branch_id else {}


# Commonly used permission decorators

# Employee management permissions
employee_view_required = hr_permission_required('employee_view')
employee_add_required = hr_permission_required('employee_add')
employee_change_required = hr_permission_required('employee_change')
employee_delete_required = hr_permission_required('employee_delete')

# Attendance permissions
attendance_view_required = hr_permission_required('attendance_view')
attendance_manage_required = hr_permission_required('attendance_manage')

# Payroll permissions
payroll_view_required = hr_permission_required('payroll_view')
payroll_calculate_required = hr_permission_required('payroll_calculate')
payroll_approve_required = hr_permission_required('payroll_approve')

# Leave permissions
leave_view_required = hr_permission_required('leave_view')
leave_approve_required = hr_permission_required('leave_approve')

# Evaluation permissions
evaluation_view_required = hr_permission_required('evaluation_view')
evaluation_create_required = hr_permission_required('evaluation_create')
evaluation_approve_required = hr_permission_required('evaluation_approve')

# Reports permissions
reports_view_required = hr_permission_required('reports_view')
reports_export_required = hr_permission_required('reports_export')

# Admin permissions
hr_settings_required = hr_permission_required('hr_settings_manage')
user_management_required = hr_permission_required('user_management')

# Module-specific permissions (for backward compatibility)
def hr_module_permission_required(module, action):
    """
    Decorator للتحقق من صلاحيات الوحدة (للتوافق مع النسخة القديمة)
    """
    permission_codename = f'{module}_{action}'
    return hr_permission_required(permission_codename)


# Simple hr_required decorator for basic HR access
def hr_required(view_func):
    """
    Decorator بسيط للتحقق من الوصول لنظام الموارد البشرية
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # التحقق من أن المستخدم لديه صلاحية الوصول لنظام الموارد البشرية
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # التحقق من وجود دور في نظام الموارد البشرية
        try:
            user_role = UserRole.objects.get(user=request.user, is_active=True)
            return view_func(request, *args, **kwargs)
        except UserRole.DoesNotExist:
            # إذا لم يكن لديه دور، تحقق من الصلاحيات العادية
            if request.user.has_perm('Hr.view_employee') or \
               request.user.has_perm('Hr.change_employee') or \
               request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'ليس لديك صلاحية للوصول إلى نظام الموارد البشرية')
            return redirect('admin:index')
    
    return _wrapped_view