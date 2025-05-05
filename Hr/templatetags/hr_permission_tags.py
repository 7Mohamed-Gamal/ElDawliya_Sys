from django import template
from django.utils.safestring import mark_safe

register = template.Library()

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

@register.simple_tag(takes_context=True)
def has_hr_module_permission(context, module_key, permission_type='view'):
    """
    التحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق الموارد البشرية
    
    الاستخدام في القوالب:
    {% load hr_permission_tags %}
    {% has_hr_module_permission "employees" "add" as can_add_employee %}
    {% if can_add_employee %}
        <a href="{% url 'Hr:employees:create' %}" class="btn btn-success">إضافة موظف جديد</a>
    {% endif %}
    """
    request = context['request']
    user = request.user
    
    # المشرفون لديهم جميع الصلاحيات
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True
    
    # تحويل نوع الصلاحية إلى الصيغة المناسبة لنظام Django
    perm_map = {
        'view': 'view',
        'add': 'add',
        'edit': 'change',
        'delete': 'delete',
    }
    
    django_perm_type = perm_map.get(permission_type, permission_type)
    
    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_map = {
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
    
    model_name = model_map.get(module_key, module_key)
    
    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'hr.{django_perm_type}_{model_name}'
    
    return user.has_perm(permission_name)

@register.filter
def can_view_hr_module(user, module_key):
    """
    فلتر للتحقق من صلاحية العرض لوحدة معينة
    
    الاستخدام في القوالب:
    {% load hr_permission_tags %}
    {% if user|can_view_hr_module:"employees" %}
        <a href="{% url 'Hr:employees:list' %}">قائمة الموظفين</a>
    {% endif %}
    """
    # المشرفون لديهم جميع الصلاحيات
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True
    
    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_map = {
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
    
    model_name = model_map.get(module_key, module_key)
    
    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'hr.view_{model_name}'
    
    return user.has_perm(permission_name)

@register.simple_tag
def get_hr_module_name(module_key):
    """
    الحصول على اسم الوحدة بناءً على المفتاح
    
    الاستخدام في القوالب:
    {% load hr_permission_tags %}
    {% get_hr_module_name "employees" as module_name %}
    <h1>{{ module_name }}</h1>
    """
    return MODULES.get(module_key, "")

@register.inclusion_tag('Hr/includes/action_buttons.html', takes_context=True)
def hr_action_buttons(context, module_key, edit_url=None, delete_url=None, print_url=None, back_url=None):
    """
    عرض أزرار الإجراءات بناءً على صلاحيات المستخدم
    
    الاستخدام في القوالب:
    {% load hr_permission_tags %}
    {% hr_action_buttons "employees" edit_url="Hr:employees:edit" delete_url="Hr:employees:delete" back_url="Hr:employees:list" %}
    """
    request = context['request']
    user = request.user
    
    # المشرفون لديهم جميع الصلاحيات
    is_admin = user.is_superuser or getattr(user, 'Role', '') == 'admin'
    
    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_map = {
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
    
    model_name = model_map.get(module_key, module_key)
    
    return {
        'can_edit': is_admin or user.has_perm(f'hr.change_{model_name}'),
        'can_delete': is_admin or user.has_perm(f'hr.delete_{model_name}'),
        'can_print': is_admin,
        'edit_url': edit_url,
        'delete_url': delete_url,
        'print_url': print_url,
        'back_url': back_url,
    }
