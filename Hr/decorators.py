from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator

from administrator.utils import has_template_permission, check_permission
from administrator.decorators import module_permission_required

def template_permission_required(template_path):
    """
    ديكوريتور للتحقق من صلاحية الوصول إلى قالب معين

    الاستخدام:
    @template_permission_required('Hr/reports/monthly_salary_report.html')
    def monthly_salary_report(request):
        # عرض التقرير
        return render(request, 'Hr/reports/monthly_salary_report.html', context)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not has_template_permission(request.user, template_path):
                messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة')
                return redirect('accounts:access_denied')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def permission_required(department_name, module_name, permission_type):
    """
    ديكوريتور للتحقق من صلاحية العمليات (عرض، إضافة، تعديل، حذف، طباعة)

    الاستخدام:
    @permission_required('HR', 'إدارة الموظفين', 'عرض')
    def employee_list(request):
        # عرض قائمة الموظفين
        employees = Employee.objects.all()
        return render(request, 'Hr/employees/employee_list.html', {'employees': employees})
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            from administrator.utils import has_permission
            if not has_permission(request.user, department_name, module_name, permission_type):
                messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة')
                return redirect('accounts:access_denied')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# اسم القسم الرئيسي للموارد البشرية
DEPARTMENT_NAME = "الموارد البشرية"

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

def hr_module_permission_required(module_key, permission_type='view'):
    """
    ديكوريتور للتحقق من صلاحيات الوصول لوحدة معينة في تطبيق الموارد البشرية

    المعلمات:
    - module_key: مفتاح الوحدة من القاموس MODULES
    - permission_type: نوع الصلاحية (view, add, edit, delete, print)
    """
    if module_key not in MODULES:
        raise ValueError(f"Module key '{module_key}' not found in HR modules")

    module_name = MODULES[module_key]

    return module_permission_required(
        department_name=DEPARTMENT_NAME,
        module_name=module_name,
        permission_type=permission_type
    )

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

    module_name = MODULES[module_key]

    return method_decorator(
        module_permission_required(
            department_name=DEPARTMENT_NAME,
            module_name=module_name,
            permission_type=permission_type
        ),
        name='dispatch'
    )

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