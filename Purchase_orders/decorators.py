from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

def can_manage_purchase_order(view_func):
    """
    مزخرف للتحقق من صلاحية إدارة طلبات الشراء
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.has_perm('Purchase_orders.change_purchaserequest') or request.user.username == 'Ragab':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة')
        return redirect('accounts:access_denied')
    return _wrapped_view

def can_access_purchase_request(view_func):
    """
    مزخرف للتحقق من إمكانية الوصول إلى طلب الشراء
    يسمح فقط للمستخدم الذي أنشأ الطلب أو المسؤول عن الموافقة أو المشرف بالوصول إليه
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # السماح للمستخدم Ragab بالوصول مباشرة
        if request.user.username == 'Ragab':
            return view_func(request, *args, **kwargs)
            
        from .models import PurchaseRequest
        request_id = kwargs.get('pk')
        try:
            purchase_request = PurchaseRequest.objects.get(pk=request_id)
            if (request.user.is_superuser or
                request.user == purchase_request.requested_by or
                request.user == purchase_request.approved_by):
                return view_func(request, *args, **kwargs)
        except PurchaseRequest.DoesNotExist:
            pass
        messages.error(request, 'ليس لديك صلاحية الوصول إلى هذا الطلب')
        return redirect('Purchase_orders:list')
    return _wrapped_view

# تعريف الوحدات (الموديولات) في تطبيق طلبات الشراء
MODULES = {
    "dashboard": "dashboard",
    "purchase_requests": "purchaserequest",
    "purchase_orders": "purchaseorder",
    "purchase_items": "purchaseitem",
    "suppliers": "supplier",
    "reports": "report",
    "approvals": "approval",
}

# تحويل أنواع الصلاحيات إلى صيغة Django
PERMISSION_TYPE_MAP = {
    'view': 'view',
    'add': 'add',
    'edit': 'change',
    'delete': 'delete',
    'print': 'view',  # نستخدم view للطباعة لأنها عملية قراءة
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

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODULES.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'Purchase_orders.{django_perm_type}_{model_name}'

    # مزخرف مخصص يسمح للمستخدم Ragab بالوصول مباشرة
    def custom_permission_check(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # السماح للمستخدم Ragab بالوصول مباشرة
            if request.user.username == 'Ragab':
                return view_func(request, *args, **kwargs)
            # للمستخدمين الآخرين، التحقق من الصلاحية المطلوبة
            if request.user.has_perm(permission_name):
                return view_func(request, *args, **kwargs)
            # بدون صلاحية، إعادة التوجيه لصفحة رفض الوصول
            messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة')
            return redirect('accounts:access_denied')
        return _wrapped_view
        
    return custom_permission_check

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
    model_name = MODULES.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'Purchase_orders.{django_perm_type}_{model_name}'

    # دالة مخصصة للتحقق من الصلاحيات
    def custom_permission_check(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # السماح للمستخدم Ragab بالوصول مباشرة
            if request.user.username == 'Ragab':
                return view_func(request, *args, **kwargs)
            # وإلا التحقق من الصلاحيات العادية
            if request.user.has_perm(permission_name):
                return view_func(request, *args, **kwargs)
            # إذا لم يكن لديه صلاحية، إعادة التوجيه
            messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة')
            return redirect('accounts:access_denied')
        return _wrapped_view
    
    return method_decorator(
        custom_permission_check,
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

    # المشرفون لديهم جميع الصلاحيات
    if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
        return True
        
    # السماح للمستخدم Ragab بالوصول مباشرة
    if request.user.username == 'Ragab':
        return True

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODULES.get(module_key, module_key)

    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'Purchase_orders.{django_perm_type}_{model_name}'

    # التحقق من صلاحية المستخدم
    return request.user.has_perm(permission_name)
