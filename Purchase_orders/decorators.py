from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator

from administrator.decorators import module_permission_required
from administrator.utils import check_permission

# اسم القسم الرئيسي لطلبات الشراء
DEPARTMENT_NAME = "طلبات الشراء"

# تعريف الوحدات (الموديولات) في تطبيق طلبات الشراء
MODULES = {
    "dashboard": "لوحة التحكم",
    "purchase_requests": "طلبات الشراء",
    "purchase_items": "عناصر الطلبات",
    "approvals": "الموافقات",
    "reports": "التقارير",
}

def purchase_module_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق طلبات الشراء
    
    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in purchase modules")
    
    module_name = MODULES[module_key]
    
    return module_permission_required(
        department_name=DEPARTMENT_NAME,
        module_name=module_name,
        permission_type=permission_type
    )

def purchase_class_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق طلبات الشراء
    للاستخدام مع الـ Class-Based Views
    
    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in purchase modules")
    
    module_name = MODULES[module_key]
    
    return method_decorator(
        module_permission_required(
            department_name=DEPARTMENT_NAME,
            module_name=module_name,
            permission_type=permission_type
        ),
        name='dispatch'
    )

def has_purchase_permission(request, module_key, permission_type='view'):
    """
    التحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق طلبات الشراء
    
    المعلمات:
    - request: كائن الطلب
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in purchase modules")
    
    module_name = MODULES[module_key]
    
    # المشرفون لديهم جميع الصلاحيات
    if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
        return True
    
    # التحقق من صلاحية المستخدم
    return check_permission(
        user=request.user,
        department_name=DEPARTMENT_NAME,
        module_name=module_name,
        permission_type=permission_type
    )
