"""
هذا الملف موجود للتوافق مع الإصدارات السابقة. يرجى استخدام 'permissions.py' للتطوير المستقبلي.
(This file exists for backward compatibility. Please use 'permissions.py' for future development.)
"""

from django import template
from administrator.templatetags.permissions import (
    has_perm,
    has_module_permission,
    check_permission
)

register = template.Library()

# Re-register simplified tags using Django's permission system
@register.simple_tag(takes_context=True)
def has_op_perm(context, app_module_code, operation_code, permission_type):
    """
    Simplified compatibility wrapper for operation permissions
    """
    user = context['request'].user
    permission_name = f"{app_module_code}.{permission_type}_{operation_code}"
    return user.has_perm(permission_name)

@register.simple_tag(takes_context=True)
def has_pg_perm(context, app_module_code, url_pattern):
    """
    Simplified compatibility wrapper for page permissions
    """
    user = context['request'].user
    permission_name = f"{app_module_code}.view_{url_pattern}"
    return user.has_perm(permission_name)

@register.filter
def show_if_has_op_perm(element, perm_args):
    """
    Show an element if user has permission
    """
    from django.utils.safestring import mark_safe
    
    if not perm_args or ',' not in perm_args:
        return ''

    args = perm_args.split(',')
    if len(args) != 3:
        return ''

    app_module_code, operation_code, permission_type = args
    permission_name = f"{app_module_code}.{permission_type}_{operation_code}"

    if element.user.has_perm(permission_name):
        return mark_safe(element)
    return ''

@register.filter
def show_if_has_pg_perm(element, perm_args):
    """
    Show an element if user has page permission
    """
    from django.utils.safestring import mark_safe
    
    if not perm_args or ',' not in perm_args:
        return ''

    args = perm_args.split(',')
    if len(args) != 2:
        return ''

    app_module_code, url_pattern = args
    permission_name = f"{app_module_code}.view_{url_pattern}"

    if element.user.has_perm(permission_name):
        return mark_safe(element)
    return ''
