from django import template

register = template.Library()

@register.filter
def getattribute(obj, attr):
    """
    Gets an attribute of an object dynamically from a string name.

    Usage: {{ form|getattribute:"field_name" }}
    """
    # إذا كان الكائن هو نموذج Django، فحاول الوصول إلى الحقل مباشرة
    if hasattr(obj, 'fields') and attr in obj.fields:
        return obj[attr]

    # وإلا، حاول الوصول إلى السمة بالطريقة العادية
    if hasattr(obj, str(attr)):
        return getattr(obj, attr)

    return None
