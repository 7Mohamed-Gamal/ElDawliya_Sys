from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator

from administrator.decorators import module_permission_required
from administrator.utils import check_permission

# اسم القسم الرئيسي لمهام الموظفين
DEPARTMENT_NAME = "مهام الموظفين"

# تعريف الوحدات (الموديولات) في تطبيق مهام الموظفين
MODULES = {
    "dashboard": "لوحة التحكم",
    "tasks": "إدارة المهام",
    "my_tasks": "مهامي",
    "calendar": "التقويم",
    "analytics": "التحليلات",
    "notifications": "التنبيهات",
    "categories": "التصنيفات",
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
    
    module_name = MODULES[module_key]
    
    return module_permission_required(
        department_name=DEPARTMENT_NAME,
        module_name=module_name,
        permission_type=permission_type
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
