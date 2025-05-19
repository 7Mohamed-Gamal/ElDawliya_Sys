from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

# تعريف الوحدات (الموديولات) في تطبيق الاجتماعات
MODULES = {
    "meetings": "meeting",
    "attendees": "attendee",
    "meeting_tasks": "meetingtask",
    "reports": "meetingreport",
}

# تحويل أنواع الصلاحيات إلى صيغة Django
PERMISSION_TYPE_MAP = {
    'view': 'view',
    'add': 'add',
    'edit': 'change',
    'delete': 'delete',
    'print': 'view',  # نستخدم view للطباعة لأنها عملية قراءة
}

def meetings_module_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق الاجتماعات

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in meetings modules")

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODULES.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'meetings.{django_perm_type}_{model_name}'

    return permission_required(permission_name, login_url='accounts:access_denied')

def meetings_class_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق الاجتماعات
    للاستخدام مع الـ Class-Based Views

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in meetings modules")

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODULES.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'meetings.{django_perm_type}_{model_name}'

    return method_decorator(
        permission_required(permission_name, login_url='accounts:access_denied'),
        name='dispatch'
    )

def has_meetings_permission(request, module_key, permission_type='view'):
    """
    التحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق الاجتماعات

    المعلمات:
    - request: كائن الطلب
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in meetings modules")

    # المشرفون لديهم جميع الصلاحيات
    if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
        return True

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODULES.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'meetings.{django_perm_type}_{model_name}'

    # التحقق من صلاحية المستخدم
    return request.user.has_perm(permission_name)

def can_manage_meeting(view_func):
    """
    مزخرف للتحقق من صلاحية إدارة الاجتماعات
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.has_perm('meetings.change_meeting'):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة')
        return redirect('accounts:access_denied')
    return _wrapped_view

def can_access_meeting(view_func):
    """
    مزخرف للتحقق من إمكانية الوصول إلى الاجتماع
    يسمح فقط للمستخدم الذي أنشأ الاجتماع أو المدعو للحضور أو المشرف بالوصول إليه
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from .models import Meeting
        meeting_id = kwargs.get('pk')
        try:
            meeting = Meeting.objects.get(pk=meeting_id)
            if request.user.is_superuser or request.user == meeting.created_by or meeting.attendees.filter(user=request.user).exists():
                return view_func(request, *args, **kwargs)
        except Meeting.DoesNotExist:
            pass
        messages.error(request, 'ليس لديك صلاحية الوصول إلى هذا الاجتماع')
        return redirect('meetings:list')
    return _wrapped_view
