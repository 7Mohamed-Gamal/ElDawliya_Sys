from django import template

register = template.Library()

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
