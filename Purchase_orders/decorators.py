from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required as django_permission_required

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

# تحويل مفاتيح الوحدات إلى أسماء موديلات Django
MODEL_MAP = {
    'dashboard': 'dashboard',
    'purchase_requests': 'purchaserequest',
    'purchase_items': 'purchaseitem',
    'approvals': 'approval',
    'reports': 'report',
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

def purchase_module_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق طلبات الشراء

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in purchase modules")

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODEL_MAP.get(module_key, module_key)
    
    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    
    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'purchase_orders.{django_perm_type}_{model_name}'
    
    return admin_or_permission_required(permission_name)

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

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODEL_MAP.get(module_key, module_key)
    
    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    
    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'purchase_orders.{django_perm_type}_{model_name}'
    
    return method_decorator(admin_or_permission_required(permission_name), name='dispatch')

def has_purchase_permission(request_or_obj, module_key, permission_type='view'):
    """
    التحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق طلبات الشراء

    المعلمات:
    - request_or_obj: كائن الطلب أو كائن العرض (في حالة Class-Based Views)
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in purchase modules")

    # التأكد من أن لدينا كائن طلب صالح
    # في حالة Class-Based Views، قد نحصل على كائن العرض بدلاً من كائن الطلب
    if hasattr(request_or_obj, 'user'):
        user = request_or_obj.user
    elif hasattr(request_or_obj, 'request') and hasattr(request_or_obj.request, 'user'):
        user = request_or_obj.request.user
    else:
        # إذا لم نتمكن من العثور على المستخدم، نرفض الوصول
        return False

    # المشرفون لديهم جميع الصلاحيات
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODEL_MAP.get(module_key, module_key)
    
    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    
    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'purchase_orders.{django_perm_type}_{model_name}'

    # التحقق من صلاحية المستخدم
    return user.has_perm(permission_name)
