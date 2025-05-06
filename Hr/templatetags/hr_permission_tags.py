"""تم نقل إلى نظام الأذونات الموحد. يُفضل استخدام permissions.py في المستقبل.
(Moved to the unified permissions system. Please use permissions.py for future development.)
"""
from django import template
from administrator.templatetags.permissions import has_rbac_permission

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
