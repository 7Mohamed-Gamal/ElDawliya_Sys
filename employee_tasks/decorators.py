from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

# تعريف الوحدات (الموديولات) في تطبيق مهام الموظفين
MODULES = {
    "dashboard": "dashboard",
    "tasks": "employeetask",
    "my_tasks": "mytask",
    "calendar": "calendar",
    "analytics": "analytics",
    "notifications": "notification",
    "categories": "taskcategory",
}

# تحويل أنواع الصلاحيات إلى صيغة Django
PERMISSION_TYPE_MAP = {
    'view': 'view',
    'add': 'add',
    'edit': 'change',
    'delete': 'delete',
    'print': 'view',  # نستخدم view للطباعة لأنها عملية قراءة
}

def employee_tasks_module_permission_required(module_key, permission_type='view'):
    """
    مزخرف للتحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق مهام الموظفين

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in employee tasks modules")

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODULES.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'employee_tasks.{django_perm_type}_{model_name}'

    return permission_required(permission_name, login_url='accounts:access_denied')

def employee_tasks_class_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق مهام الموظفين
    للاستخدام مع الـ Class-Based Views

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in employee tasks modules")

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODULES.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'employee_tasks.{django_perm_type}_{model_name}'

    return method_decorator(
        permission_required(permission_name, login_url='accounts:access_denied'),
        name='dispatch'
    )

def has_employee_tasks_permission(request, module_key, permission_type='view'):
    """
    التحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق مهام الموظفين

    المعلمات:
    - request: كائن الطلب
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in employee tasks modules")

    # المشرفون لديهم جميع الصلاحيات
    if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
        return True

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODULES.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'employee_tasks.{django_perm_type}_{model_name}'

    # التحقق من صلاحية المستخدم
    return request.user.has_perm(permission_name)

def can_access_task(view_func):
    """
    مزخرف للتحقق من إمكانية الوصول إلى المهمة
    يسمح فقط للمستخدم الذي أنشأ المهمة أو المستخدم المكلف بها أو المشرف بالوصول إليها
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from .models import EmployeeTask

        # الحصول على معرف المهمة من المعلمات
        task_id = kwargs.get('pk') or kwargs.get('task_id')

        if not task_id:
            messages.error(request, "لم يتم تحديد المهمة")
            return redirect('employee_tasks:dashboard')

        try:
            task = EmployeeTask.objects.get(pk=task_id)
        except EmployeeTask.DoesNotExist:
            messages.error(request, "المهمة غير موجودة")
            return redirect('employee_tasks:dashboard')

        # التحقق من إمكانية الوصول
        user = request.user
        if user.is_superuser or user == task.created_by or user == task.assigned_to:
            # إضافة المهمة إلى المعلمات لتجنب استعلام قاعدة البيانات مرة أخرى
            kwargs['task'] = task
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "ليس لديك صلاحية للوصول إلى هذه المهمة")
            return redirect('employee_tasks:dashboard')

    return _wrapped_view
