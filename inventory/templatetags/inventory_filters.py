"""
تم نقل من custom_filters.py لتجنب تعارضات التسمية
(Moved from custom_filters.py to avoid naming conflicts)
"""
from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """
    Multiplies the value by the argument
    
    Usage:
    {% load inventory_filters %}
    {{ item.price|multiply:item.quantity }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
