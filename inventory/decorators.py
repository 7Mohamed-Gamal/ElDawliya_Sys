from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

def can_manage_inventory(view_func):
    """
    مزخرف للتحقق من صلاحية إدارة المخزون
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.has_perm('inventory.change_product'):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة')
        return redirect('accounts:access_denied')
    return _wrapped_view

# اسم القسم الرئيسي للمخزن
DEPARTMENT_NAME = "مخزن قطع الغيار"

# تعريف الوحدات (الموديولات) في تطبيق المخزن
MODULES = {
    "dashboard": "لوحة التحكم",
    "products": "قطع الغيار",
    "categories": "التصنيفات",
    "units": "وحدات القياس",
    "suppliers": "الموردين",
    "customers": "العملاء",
    "invoices": "الفواتير",
    "stock_report": "تقارير المخزون",
    "settings": "إعدادات النظام",
    "departments": "الأقسام",
    "purchase_requests": "طلبات الشراء",
    "vouchers": "الأذونات",
}

# تحويل مفاتيح الوحدات إلى أسماء موديلات Django
MODEL_MAP = {
    "dashboard": "dashboard",
    "products": "product",
    "categories": "category",
    "units": "unit",
    "suppliers": "supplier",
    "customers": "customer",
    "invoices": "invoice",
    "stock_report": "stockreport",
    "settings": "settings",
    "departments": "department",
    "purchase_requests": "purchaserequest",
    "vouchers": "voucher",
}

# تحويل أنواع الصلاحيات إلى صيغة Django
PERMISSION_TYPE_MAP = {
    'view': 'view',
    'add': 'add',
    'edit': 'change',
    'delete': 'delete',
    'print': 'view',  # نستخدم view للطباعة لأنها عملية قراءة
}

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

def inventory_module_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق المخزن

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in inventory modules")

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODEL_MAP.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'inventory.{django_perm_type}_{model_name}'

    return admin_or_permission_required(permission_name)

def inventory_class_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق المخزن
    للاستخدام مع الـ Class-Based Views

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in inventory modules")

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODEL_MAP.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'inventory.{django_perm_type}_{model_name}'

    # دالة مخصصة للتحقق من الصلاحيات
    def custom_permission_check(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # المشرفون لديهم جميع الصلاحيات
            if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
                return view_func(request, *args, **kwargs)

            # التحقق من صلاحية المستخدم
            if not request.user.has_perm(permission_name):
                messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة')
                return redirect('accounts:access_denied')

            return view_func(request, *args, **kwargs)
        return _wrapped_view

    return method_decorator(
        custom_permission_check,
        name='dispatch'
    )

def has_inventory_permission(request, module_key, permission_type='view'):
    """
    التحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق المخزن

    المعلمات:
    - request: كائن الطلب
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in inventory modules")

    # المشرفون لديهم جميع الصلاحيات
    if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
        return True

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODEL_MAP.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'inventory.{django_perm_type}_{model_name}'

    # التحقق من صلاحية المستخدم
    return request.user.has_perm(permission_name)
