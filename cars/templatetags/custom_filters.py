from django import template
from django.template.defaultfilters import floatformat
from decimal import Decimal

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        try:
            return Decimal(value) - Decimal(arg)
        except:
            return 0

@register.filter
def add(value, arg):
    """Add the arg to the value."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        try:
            return Decimal(value) + Decimal(arg)
        except:
            return 0

@register.filter
def multiply(value, arg):
    """Multiply the value by the arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        try:
            return Decimal(value) * Decimal(arg)
        except:
            return 0

@register.filter
def divide(value, arg):
    """Divide the value by the arg."""
    try:
        arg = float(arg)
        if arg == 0:
            return 0
        return float(value) / arg
    except (ValueError, TypeError, ZeroDivisionError):
        try:
            arg = Decimal(arg)
            if arg == 0:
                return 0
            return Decimal(value) / arg
        except:
            return 0

@register.filter
def percent(value, arg):
    """Calculate the percentage of value relative to arg."""
    try:
        arg = float(arg)
        if arg == 0:
            return 0
        return (float(value) / arg) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def sum(queryset, attr):
    """Sum the attribute across all objects in the queryset."""
    if not queryset:
        return 0
    
    try:
        return sum(float(getattr(obj, attr, 0) or 0) for obj in queryset)
    except:
        return 0
