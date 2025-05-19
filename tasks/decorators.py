from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

# تعريف الوحدات (الموديولات) في تطبيق المهام
MODULES = {
    "dashboard": "dashboard",
    "tasks": "task",
    "my_tasks": "mytask",
    "reports": "report",
}

# تحويل أنواع الصلاحيات إلى صيغة Django
PERMISSION_TYPE_MAP = {
    'view': 'view',
    'add': 'add',
    'edit': 'change',
    'delete': 'delete',
    'print': 'view',  # نستخدم view للطباعة لأنها عملية قراءة
}

def has_tasks_permission(request, module_key, permission_type='view'):
    """
    التحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق المهام

    المعلمات:
    - request: طلب HTTP
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        return False

    # المشرفون لديهم جميع الصلاحيات
    if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
        return True

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODULES.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'tasks.{django_perm_type}_{model_name}'

    # التحقق من صلاحية المستخدم
    return request.user.has_perm(permission_name)

def tasks_module_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق المهام

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in tasks modules")

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODULES.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'tasks.{django_perm_type}_{model_name}'

    return permission_required(permission_name, login_url='accounts:access_denied')

def tasks_class_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق المهام
    للاستخدام مع الـ Class-Based Views

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in tasks modules")

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODULES.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'tasks.{django_perm_type}_{model_name}'

    return method_decorator(
        permission_required(permission_name, login_url='accounts:access_denied'),
        name='dispatch'
    )

def can_manage_task(view_func):
    """
    مزخرف للتحقق من صلاحية إدارة المهام
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.has_perm('tasks.change_task'):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة')
        return redirect('accounts:access_denied')
    return _wrapped_view

def can_access_task(view_func):
    """
    مزخرف للتحقق من إمكانية الوصول إلى المهمة
    يسمح فقط للمستخدم الذي أنشأ المهمة أو المسند إليه المهمة أو المشرف بالوصول إليها
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from .models import Task
        task_id = kwargs.get('pk')
        try:
            task = Task.objects.get(pk=task_id)
            if request.user.is_superuser or request.user == task.created_by or request.user == task.assigned_to:
                return view_func(request, *args, **kwargs)
        except Task.DoesNotExist:
            pass
        messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه المهمة')
        return redirect('tasks:list')
    return _wrapped_view
