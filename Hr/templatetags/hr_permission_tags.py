from django import template
from django.utils.safestring import mark_safe
from Hr.decorators import has_hr_permission, MODULES

register = template.Library()

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
    return has_hr_permission(request, module_key, permission_type)

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
    from django.http import HttpRequest
    # إنشاء كائن طلب وهمي لاستخدامه في الدالة has_hr_permission
    request = HttpRequest()
    request.user = user
    return has_hr_permission(request, module_key, 'view')

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
    
    return {
        'can_edit': has_hr_permission(request, module_key, 'edit'),
        'can_delete': has_hr_permission(request, module_key, 'delete'),
        'can_print': has_hr_permission(request, module_key, 'print'),
        'edit_url': edit_url,
        'delete_url': delete_url,
        'print_url': print_url,
        'back_url': back_url,
    }
