from django import template

register = template.Library()

@register.filter
def getattribute(obj, attr):
    """
    Gets an attribute of an object dynamically from a string name.
    
    Usage: {{ form|getattribute:"field_name" }}
    """
    if hasattr(obj, str(attr)):
        return getattr(obj, attr)
    return None
