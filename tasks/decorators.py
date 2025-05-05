from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator

from administrator.decorators import module_permission_required
from administrator.utils import check_permission

# اسم القسم الرئيسي للمهام
DEPARTMENT_NAME = "المهام"

# تعريف الوحدات (الموديولات) في تطبيق المهام
MODULES = {
    "dashboard": "لوحة التحكم",
    "tasks": "إدارة المهام",
    "my_tasks": "مهامي",
    "reports": "التقارير",
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

    module_name = MODULES[module_key]
    return check_permission(request.user, DEPARTMENT_NAME, module_name, permission_type)

def tasks_module_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق المهام

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in tasks modules")

    module_name = MODULES[module_key]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if check_permission(request.user, DEPARTMENT_NAME, module_name, permission_type):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f"ليس لديك صلاحية {permission_type} في {module_name}")
                return redirect('accounts:home')
        return _wrapped_view
    return decorator

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

    module_name = MODULES[module_key]

    return method_decorator(
        module_permission_required(
            department_name=DEPARTMENT_NAME,
            module_name=module_name,
            permission_type=permission_type
        ),
        name='dispatch'
    )
