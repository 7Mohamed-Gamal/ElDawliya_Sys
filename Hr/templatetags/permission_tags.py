from django import template

register = template.Library()

@register.filter
def has_perm(user, perm_name):
    """
    تحقق مما إذا كان المستخدم لديه صلاحية معينة باستخدام نظام صلاحيات Django الأساسي
    
    الاستخدام في القوالب:
    {% load permission_tags %}
    {% if user|has_perm:"hr.view_employee" %}
        <a href="{% url 'hr:employee_list' %}" class="btn btn-primary">عرض الموظفين</a>
    {% endif %}
    """
    # المشرفون لديهم جميع الصلاحيات
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True
        
    return user.has_perm(perm_name)