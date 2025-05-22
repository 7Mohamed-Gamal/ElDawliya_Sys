from django import template
from django.utils.safestring import mark_safe
import base64
import logging

logger = logging.getLogger(__name__)
register = template.Library()

# Add a debug log statement to verify the template tag is being loaded
logger.debug('Loading binary_to_img template filter')

@register.filter(name='binary_to_img')
def binary_to_img(value):
    """Convert binary image data to a base64 encoded image source."""
    if not value:
        return ''
    
    try:
        logger.debug(f'Processing image data of type: {type(value)}')
        
        # Handle Django FileField/ImageField
        if hasattr(value, 'url'):
            return value.url
            
        # If the value is already in bytes format
        if isinstance(value, bytes):
            image_data = value
        # If the value is stored as a string of binary data
        elif isinstance(value, str):
            image_data = value.encode()
        # If it's a file-like object
        elif hasattr(value, 'read'):
            image_data = value.read()
        else:
            logger.warning(f'Unsupported image data type: {type(value)}')
            return ''

        # Convert binary data to base64
        encoded_data = base64.b64encode(image_data).decode('utf-8')
        
        # Return the complete img src with data URI scheme
        return mark_safe(f'data:image/jpeg;base64,{encoded_data}')
    except Exception as e:
        logger.error(f'Error processing image: {str(e)}')
        # Return empty string if there's any error
        return ''
