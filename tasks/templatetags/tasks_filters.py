"""
تم نقل من custom_filters.py لتجنب تعارضات التسمية
(Moved from custom_filters.py to avoid naming conflicts)
"""
from django import template

register = template.Library()

@register.filter(name='attr')
def set_attr(field, attr_string):
    """
    Set an attribute on a form field
    
    Usage:
    {% load tasks_filters %}
    {{ field|attr:"disabled" }}
    {{ field|attr:"class=form-control" }}
    """
    attrs = field.field.widget.attrs
    
    # Handle simple attribute (no value)
    if '=' not in attr_string:
        attrs[attr_string] = attr_string
        return field
    
    # Handle attribute with value
    attr_name, attr_value = attr_string.split('=', 1)
    attrs[attr_name] = attr_value
    return field
