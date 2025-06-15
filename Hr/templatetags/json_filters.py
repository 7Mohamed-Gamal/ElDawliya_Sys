from django import template
import json
from django.core.serializers.json import DjangoJSONEncoder

register = template.Library()

@register.filter(name='json')
def json_filter(value):
    """Convert a value to its JSON representation"""
    return json.dumps(value, cls=DjangoJSONEncoder)

@register.filter(name='split')
def split_filter(value, delimiter=','):
    """Split a string by delimiter"""
    if not value:
        return []
    return str(value).split(delimiter)

@register.filter(name='trim')
def trim_filter(value):
    """Trim whitespace from a string"""
    if not value:
        return ''
    return str(value).strip()
