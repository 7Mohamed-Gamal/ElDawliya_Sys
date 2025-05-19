"""
نظام الأذونات الموحد: ملف يجمع كل وسوم ومرشحات الأذونات في مكان واحد
(Unified Permissions System: File that combines all permission tags and filters in one place)
"""

from django import template
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from administrator.utils import has_template_permission as utils_has_template_permission
from administrator.utils import check_permission

# Import RBAC permissions system
from administrator.rbac_permissions import has_permission as rbac_has_permission, has_any_permission
try:
    from administrator.permission_decorators import has_operation_permission, has_page_permission
except ImportError:
    # Provide dummy functions if the module is not available
    def has_operation_permission(*args, **kwargs):
        """Dummy function when permission_decorators module is not available"""
        return False
    def has_page_permission(*args, **kwargs):
        """Dummy function when permission_decorators module is not available"""
        return False

User = get_user_model()
register = template.Library()

# ----- Common Functions ----- #

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key

    Usage:
    {{ my_dict|get_item:key }}
    """
    if not dictionary:
        return [] if isinstance(key, int) else None

    try:
        return dictionary.get(key, [] if isinstance(key, int) else None)
    except (AttributeError, KeyError):
        return [] if isinstance(key, int) else None

# ----- Permission Filters ----- #

@register.filter
def filter_by_code(operations, code):
    """
    Filter a list of operations by code

    Usage:
    {{ operations|filter_by_code:'employee' }}
    """
    if not operations:
        return None

    for operation in operations:
        if operation.code == code:
            return operation

    return None

@register.filter
def filter_by_type(operations, permission_type):
    """
    Filter a list of operations by permission type

    Usage:
    {{ operations|filter_by_type:'view' }}
    """
    if not operations:
        return None

    for operation in operations:
        if operation.permission_type == permission_type:
            return operation

    return None

@register.filter
def get_modules_for_department(department):
    """
    Get modules for a specific department

    Usage:
    {{ department|get_modules_for_department }}
    """
    from administrator.models import Module

    if not department:
        return []

    return Module.objects.filter(department=department).order_by('order')

@register.filter
def get_form_field(form, field_name):
    """
    Get a field from a form by its name

    Usage:
    {{ form|get_form_field:'field_name' }}
    """
    if not form or not field_name:
        return None

    try:
        # Try to access as BoundField (normal form field)
        return form[field_name]
    except (KeyError, AttributeError):
        # Fallback: try to access the field directly from form.fields
        try:
            if hasattr(form, 'fields') and field_name in form.fields:
                field = form.fields[field_name]
                widget = field.widget
                attrs = widget.attrs.copy()
                attrs['id'] = f'id_{field_name}'
                attrs['name'] = field_name
                if field.required:
                    attrs['required'] = 'required'

                initial_value = form.initial.get(field_name, field.initial)
                rendered = widget.render(field_name, initial_value, attrs)
                return mark_safe(rendered)
        except Exception as e:
            print(f"Error rendering field {field_name}: {str(e)}")

        return None

@register.simple_tag
def render_department_checkbox(form, department_id):
    """
    Render a checkbox for a department using its ID

    Usage:
    {% render_department_checkbox form department.id %}
    """
    field_name = f'dept_{department_id}'
    try:
        if field_name in form.fields:
            field = form.fields[field_name]
            widget = field.widget
            attrs = widget.attrs.copy()
            attrs['id'] = f'id_{field_name}'
            attrs['name'] = field_name
            if field.required:
                attrs['required'] = 'required'

            initial_value = form.initial.get(field_name, field.initial)
            rendered = widget.render(field_name, initial_value, attrs)
            return mark_safe(rendered)
    except Exception as e:
        print(f"Error rendering department checkbox: {str(e)}")
    return ''

@register.simple_tag
def render_module_checkbox(form, module_id):
    """
    Render a checkbox for a module using its ID

    Usage:
    {% render_module_checkbox form module.id %}
    """
    field_name = f'module_{module_id}'
    try:
        if field_name in form.fields:
            field = form.fields[field_name]
            widget = field.widget
            attrs = widget.attrs.copy()
            attrs['id'] = f'id_{field_name}'
            attrs['name'] = field_name
            if field.required:
                attrs['required'] = 'required'

            initial_value = form.initial.get(field_name, field.initial)
            rendered = widget.render(field_name, initial_value, attrs)
            return mark_safe(rendered)
    except Exception as e:
        print(f"Error rendering module checkbox: {str(e)}")
    return ''

@register.simple_tag
def render_permission_checkbox(form, module_id, perm_type):
    """
    Render a checkbox for a permission using module ID and permission type

    Usage:
    {% render_permission_checkbox form module.id perm_type %}
    """
    field_name = f'perm_{module_id}_{perm_type}'
    try:
        if field_name in form.fields:
            field = form.fields[field_name]
            widget = field.widget
            attrs = widget.attrs.copy()
            attrs['id'] = f'id_{field_name}'
            attrs['name'] = field_name
            if field.required:
                attrs['required'] = 'required'

            initial_value = form.initial.get(field_name, field.initial)
            rendered = widget.render(field_name, initial_value, attrs)
            return mark_safe(rendered)
    except Exception as e:
        print(f"Error rendering permission checkbox: {str(e)}")
    return ''

# ----- Permission Tags ----- #

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
    Action types: view, add, change, delete, print

    Usage:
    {% has_permission "add" as can_add %}
    {% if can_add %}
        <a href="{% url 'create' %}" class="btn btn-success">إضافة جديد</a>
    {% endif %}

    Note: This is a simplified permission check. For more granular control,
    use has_module_permission or has_rbac_permission.
    """
    request = context['request']
    if not request.user.is_authenticated:
        return False

    # Superusers and admins have all permissions
    if request.user.is_superuser or request.user.Role == 'admin':
        return True

    # Allow view access for all authenticated users by default
    if action_type == 'view':
        return True

    # For other actions (add, change, delete, print), check RBAC permissions
    # This provides a fallback to the RBAC system for more granular control
    permission_name = f"generic_{action_type}"
    return rbac_has_permission(request.user, permission_name)

@register.filter
def hide_if_not_admin(user):
    """
    Hide content if user is not admin

    Usage:
    {% if user|hide_if_not_admin %}
        <!-- This content will only be shown to admins -->
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    return user.Role == 'admin' or user.is_superuser


@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key

    Usage:
    {{ my_dict|get_item:key_variable }}
    """
    return dictionary.get(key, key)

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

# ----- RBAC Permission System Tags ----- #

@register.filter
def has_rbac_permission(user, permission_name):
    """
    Template filter to check if a user has a specific RBAC permission.

    Usage:
    {% if user|has_rbac_permission:"edit_articles" %}
        <a href="{% url 'edit_article' article.id %}">Edit</a>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Superusers always have all permissions
    if user.is_superuser:
        return True

    return rbac_has_permission(user, permission_name)

# ----- Operation and Page Permission Tags (from permission_tags_new.py) ----- #

@register.simple_tag(takes_context=True)
def has_op_perm(context, app_module_code, operation_code, permission_type):
    """
    Check if the current user has permission to perform a specific operation

    Usage:
    {% has_op_perm 'hr' 'employee' 'view' as can_view_employee %}
    {% if can_view_employee %}
        <!-- Show content -->
    {% endif %}
    """
    user = context['request'].user
    return has_operation_permission(user, app_module_code, operation_code, permission_type)

@register.simple_tag(takes_context=True)
def has_pg_perm(context, app_module_code, url_pattern):
    """
    Check if the current user has permission to access a specific page

    Usage:
    {% has_pg_perm 'hr' 'employee_list' as can_view_employee_list %}
    {% if can_view_employee_list %}
        <!-- Show link -->
    {% endif %}
    """
    user = context['request'].user
    return has_page_permission(user, app_module_code, url_pattern)

@register.filter
def show_if_has_op_perm(element, perm_args):
    """
    Show an HTML element if the user has permission to perform a specific operation

    Usage:
    {{ my_element|show_if_has_op_perm:'hr,employee,view' }}
    """
    if not perm_args or ',' not in perm_args:
        return ''

    args = perm_args.split(',')
    if len(args) != 3:
        return ''

    app_module_code, operation_code, permission_type = args

    if has_operation_permission(element.user, app_module_code, operation_code, permission_type):
        return mark_safe(element)
    return ''

@register.filter
def show_if_has_pg_perm(element, perm_args):
    """
    Show an HTML element if the user has permission to access a specific page

    Usage:
    {{ my_element|show_if_has_pg_perm:'hr,employee_list' }}
    """
    if not perm_args or ',' not in perm_args:
        return ''

    args = perm_args.split(',')
    if len(args) != 2:
        return ''

    app_module_code, url_pattern = args

    if has_page_permission(element.user, app_module_code, url_pattern):
        return mark_safe(element)
    return ''

@register.simple_tag
def check_rbac_permission(user, permission_name):
    """
    Template tag to check if a user has a specific RBAC permission.

    Usage:
    {% check_rbac_permission user "edit_articles" as can_edit %}
    {% if can_edit %}
        <a href="{% url 'edit_article' article.id %}">Edit</a>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Superusers always have all permissions
    if user.is_superuser:
        return True

    return rbac_has_permission(user, permission_name)


@register.simple_tag
def check_any_rbac_permission(user, permission_names):
    """
    Template tag to check if a user has any of the specified RBAC permissions.

    Usage:
    {% check_any_rbac_permission user "edit_articles,delete_articles,publish_articles" as can_manage %}
    {% if can_manage %}
        <div class="article-management-panel">
            <!-- Management controls -->
        </div>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Superusers always have all permissions
    if user.is_superuser:
        return True

    # Split the comma-separated permission names
    perm_list = [p.strip() for p in permission_names.split(',')]

    return has_any_permission(user, perm_list)
