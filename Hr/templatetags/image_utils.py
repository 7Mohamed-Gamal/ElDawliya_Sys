from django import template
from django.utils.safestring import mark_safe
import base64

register = template.Library()

@register.filter(name='binary_to_img')
def binary_to_img(value):
    """Convert binary image data to a base64 encoded image source."""
    if not value:
        return ''
    
    try:
        # If the value is already in bytes format
        if isinstance(value, bytes):
            image_data = value
        # If the value is stored as a string of binary data
        elif isinstance(value, str):
            image_data = value.encode()
        else:
            return ''

        # Convert binary data to base64
        encoded_data = base64.b64encode(image_data).decode('utf-8')
        
        # Return the complete img src with data URI scheme
        return mark_safe(f'data:image/jpeg;base64,{encoded_data}')
    except Exception:
        # Return empty string if there's any error
        return ''
