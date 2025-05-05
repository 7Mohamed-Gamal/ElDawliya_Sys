from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required as django_permission_required
from django.contrib.auth.decorators import login_required

# تعريف الوحدات (الموديولات) في تطبيق الموارد البشرية
MODULES = {
    "employees": "إدارة الموظفين",
    "departments": "إدارة الأقسام",
    "jobs": "إدارة الوظائف",
    "cars": "إدارة السيارات",
    "pickup_points": "إدارة نقاط التجمع",
    "insurance": "إدارة التأمين",
    "tasks": "إدارة المهام",
    "notes": "إدارة الملاحظات",
    "files": "إدارة الملفات",
    "hr_tasks": "إدارة مهام الموارد البشرية",
    "leaves": "إدارة الإجازات",
    "evaluations": "إدارة التقييمات",
    "salaries": "إدارة الرواتب",
    "attendance": "إدارة الحضور",
    "reports": "التقارير",
    "alerts": "التنبيهات",
    "analytics": "التحليلات",
    "org_chart": "الهيكل التنظيمي",
}

# تحويل مفاتيح الوحدات إلى أسماء موديلات Django
MODEL_MAP = {
    'employees': 'employee',
    'departments': 'department',
    'jobs': 'job',
    'cars': 'car',
    'pickup_points': 'pickuppoint',
    'tasks': 'employeetask',
    'notes': 'employeenote',
    'files': 'employeefile',
    'hr_tasks': 'hrtask',
    'leaves': 'employeeleave',
    'evaluations': 'employeeevaluation',
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

def hr_module_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق الموارد البشرية

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in HR modules")

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODEL_MAP.get(module_key, module_key)
    
    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    
    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'hr.{django_perm_type}_{model_name}'
    
    return admin_or_permission_required(permission_name)

def hr_class_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق الموارد البشرية
    للاستخدام مع الـ Class-Based Views

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in HR modules")

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODEL_MAP.get(module_key, module_key)
    
    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    
    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'hr.{django_perm_type}_{model_name}'

    return method_decorator(admin_or_permission_required(permission_name), name='dispatch')

def has_hr_permission(request, module_key, permission_type='view'):
    """
    التحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق الموارد البشرية

    المعلمات:
    - request: كائن الطلب
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in HR modules")

    # المشرفون لديهم جميع الصلاحيات
    if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
        return True

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODEL_MAP.get(module_key, module_key)
    
    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    
    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'hr.{django_perm_type}_{model_name}'
    
    return request.user.has_perm(permission_name)