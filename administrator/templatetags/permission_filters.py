"""
هذا الملف موجود للتوافق مع الإصدارات السابقة. يرجى استخدام 'permissions.py' للتطوير المستقبلي.
(This file exists for backward compatibility. Please use 'permissions.py' for future development.)
"""

from django import template
from administrator.templatetags.permissions import (
    get_item,
    filter_by_code,
    filter_by_type,
    get_modules_for_department,
    get_form_field,
    render_department_checkbox,
    render_module_checkbox,
    render_permission_checkbox
)

register = template.Library()

# Re-register the imported filters and tags
register.filter('get_item', get_item)
register.filter('filter_by_code', filter_by_code)
register.filter('filter_by_type', filter_by_type)
register.filter('get_modules_for_department', get_modules_for_department)
register.filter('get_form_field', get_form_field)
register.simple_tag(render_department_checkbox)
register.simple_tag(render_module_checkbox)
register.simple_tag(render_permission_checkbox)
