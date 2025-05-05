from django import template
from django.utils.safestring import mark_safe
from accounts.models import Users_Login_New
from administrator.utils import has_template_permission as utils_has_template_permission
from administrator.utils import check_permission

register = template.Library()

@register.filter
def filter_by(queryset, args):
    """
    Filter a queryset by a field and value.
    Usage: {{ queryset|filter_by:"field_name,value" }}
    """
    args_list = args.split(',')
    if len(args_list) != 2:
        return queryset
    
    field_name, value = args_list
    filter_kwargs = {field_name: value}
    return queryset.filter(**filter_kwargs)

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using key.
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key)

@register.simple_tag(takes_context=True)
def is_admin(context):
    """
    Check if the current user has admin role
    """
    request = context['request']
    if not request.user.is_authenticated:
        return False

    return request.user.Role == 'admin'

@register.simple_tag(takes_context=True)
def has_permission(context, action_type):
    """
    Check if user has permission for a specific action type
    Action types: add, change, delete, print
    """
    request = context['request']
    if not request.user.is_authenticated:
        return False

    # Allow view access for all authenticated users
    if action_type == 'view':
        return True

    # For other actions (add, change, delete, print), only admin can perform them
    return request.user.Role == 'admin'

@register.filter
def hide_if_not_admin(content):
    """
    Hide content if user is not admin
    """
    return ''  # This will be replaced with actual implementation in the template

@register.simple_tag(takes_context=True)
def render_if_admin(context, content):
    """
    Render content only if user is admin
    """
    request = context['request']
    if not request.user.is_authenticated:
        return ''

    if request.user.Role == 'admin':
        return mark_safe(content)
    return ''

@register.filter
def has_template_permission(user, template_path):
    """
    تحقق مما إذا كان المستخدم لديه صلاحية الوصول إلى قالب معين

    الاستخدام في القوالب:
    {% load permission_tags %}
    {% if user|has_template_permission:"Hr/reports/monthly_salary_report.html" %}
        <a href="{% url 'hr:monthly_salary_report' %}" class="btn btn-primary">عرض تقرير الرواتب الشهري</a>
    {% endif %}
    """
    return utils_has_template_permission(user, template_path)

@register.simple_tag(takes_context=True)
def has_module_permission(context, department_name, module_name, permission_type='view'):
    """
    Check if user has permission for a specific module

    Usage in templates:
    {% load permission_tags %}
    {% has_module_permission "الموارد البشرية" "إدارة الموظفين" "add" as can_add_employee %}
    {% if can_add_employee %}
        <a href="{% url 'Hr:employee_create' %}" class="btn btn-primary">إضافة موظف جديد</a>
    {% endif %}
    """
    request = context['request']
    if not request.user.is_authenticated:
        return False

    # المشرفون لديهم جميع الصلاحيات
    if request.user.is_superuser or getattr(request.user, 'Role', '') == 'admin':
        return True

    # التحقق من صلاحية المستخدم
    return check_permission(
        user=request.user,
        department_name=department_name,
        module_name=module_name,
        permission_type=permission_type
    )

@register.inclusion_tag('administrator/includes/action_buttons.html', takes_context=True)
def action_buttons(context, edit_url=None, delete_url=None, print_url=None, back_url=None):
    """
    Render action buttons based on user permissions
    """
    request = context['request']
    is_admin = request.user.is_authenticated and request.user.Role == 'admin'

    return {
        'is_admin': is_admin,
        'edit_url': edit_url,
        'delete_url': delete_url,
        'print_url': print_url,
        'back_url': back_url,
    }
