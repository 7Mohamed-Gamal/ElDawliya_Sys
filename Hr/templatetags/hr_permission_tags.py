"""تم نقل إلى نظام الأذونات الموحد. يُفضل استخدام permissions.py في المستقبل.
(Moved to the unified permissions system. Please use permissions.py for future development.)
"""
from django import template
from Hr.decorators import has_hr_permission

register = template.Library()

@register.filter
def has_perm(user, perm_name):
    """
    تحقق مما إذا كان المستخدم لديه صلاحية معينة باستخدام نظام صلاحيات Django الأساسي

    الاستخدام في القوالب:
    {% load hr_permission_tags %}
    {% if user|has_perm:"hr.view_employee" %}
        <a href="{% url 'hr:employee_list' %}" class="btn btn-primary">عرض الموظفين</a>
    {% endif %}
    """
    # المشرفون لديهم جميع الصلاحيات
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True

    return user.has_perm(perm_name)

@register.simple_tag(takes_context=True)
def has_hr_module_permission(context, module_key, permission_type='view'):
    """
    التحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق الموارد البشرية

    الاستخدام في القوالب:
    {% load hr_permission_tags %}
    {% has_hr_module_permission "departments" "add" as can_add_department %}
    {% if can_add_department %}
        <a href="{% url 'Hr:departments:create' %}" class="btn btn-primary">إضافة قسم جديد</a>
    {% endif %}
    """
    request = context['request']
    return has_hr_permission(request, module_key, permission_type)
