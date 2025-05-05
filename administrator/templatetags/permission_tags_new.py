from django import template
from django.urls import resolve, reverse
from django.utils.safestring import mark_safe

from administrator.permission_decorators import has_operation_permission, has_page_permission

register = template.Library()

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