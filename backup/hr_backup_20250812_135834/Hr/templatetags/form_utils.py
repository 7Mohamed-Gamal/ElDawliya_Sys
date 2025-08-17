from django import template
import base64

register = template.Library()

# Moved to image_utils.py for centralized implementation

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

@register.filter
def dict_get(dictionary, key):
    """
    Gets a value from a dictionary by key.
    
    Usage: {{ my_dict|dict_get:key }}
    """
    if not dictionary:
        return ""
    
    # Convert the key to string to ensure it matches
    key = str(key)
    
    for dict_key, value in dictionary:
        if str(dict_key) == key:
            return value
    
    return ""

@register.filter
def split(value, separator):
    """
    Splits a string by separator.
    
    Usage: {{ string|split:',' }}
    """
    if not value:
        return []
    
    return value.split(separator)

@register.filter
def get_item(dictionary, key):
    """
    Gets an item from a dictionary.
    
    Usage: {{ dict|get_item:key }}
    """
    if not dictionary:
        return ""
    
    return dictionary.get(key, "")

@register.filter
def get_field_label(field_name):
    """
    Gets a human-readable label for a field name.
    
    Usage: {{ field_name|get_field_label }}
    """
    labels = {
        'phone': 'رقم الهاتف',
        'national_id': 'الرقم القومي',
        'car': 'السيارة',
        'insurance_number': 'الرقم التأميني',
        'hire_date': 'تاريخ التعيين',
        'marital_status': 'الحالة الاجتماعية',
        # يمكن إضافة المزيد من الحقول هنا
    }
    
    return labels.get(field_name, field_name)

@register.filter
def count_active_filters(request_get, fields_str):
    """
    Counts the number of active filters in the request.GET dictionary for the specified fields.
    
    Usage: {{ request.GET|count_active_filters:"phone,national_id,car,insurance_number,hire_date,marital_status" }}
    """
    if not request_get:
        return 0
    
    count = 0
    fields = fields_str.split(',')
    
    for field in fields:
        if request_get.get(field, ''):
            count += 1
    
    return count
