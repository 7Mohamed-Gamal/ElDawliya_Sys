"""
وسوم أذونات خاصة بتطبيق المشرف
(Permission tags specific to the administrator app)
"""
from django import template
from administrator.templatetags.permissions import (
    get_item,
    filter_by,
    is_admin,
    has_permission,
    hide_if_not_admin,
    render_if_admin,
    has_template_permission,
    has_module_permission,
    action_buttons
)

register = template.Library()

# Re-register the imported filters and tags
register.filter('get_item', get_item)
register.filter('filter_by', filter_by)
register.filter('hide_if_not_admin', hide_if_not_admin)
register.filter('has_template_permission', has_template_permission)
register.simple_tag(is_admin, takes_context=True)
register.simple_tag(has_permission, takes_context=True)
register.simple_tag(render_if_admin, takes_context=True)
register.simple_tag(has_module_permission, takes_context=True)
register.inclusion_tag('administrator/includes/action_buttons.html', takes_context=True)(action_buttons)