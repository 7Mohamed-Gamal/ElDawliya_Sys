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
        logger.debug('binary_to_img called with empty value')
        return ''
    
    try:
        logger.debug(f'Processing image data of type: {type(value)}')
        
        # Handle Django FileField/ImageField
        if hasattr(value, 'url'):
            logger.debug('Value has url attribute, returning FileField/ImageField URL')
            return value.url
            
        # Get the binary image data
        if isinstance(value, bytes):
            logger.debug('Value is bytes, using directly')
            image_data = value
        elif isinstance(value, str):
            logger.debug('Value is string, encoding to bytes')
            try:
                image_data = value.encode()
            except UnicodeEncodeError:
                # The string might already be base64
                logger.debug('String appears to be base64 encoded, using as is')
                return f'data:image/jpeg;base64,{value}'
        elif hasattr(value, 'read'):
            logger.debug('Value is file-like object, reading')
            image_data = value.read()
        else:
            logger.warning(f'Unsupported image data type: {type(value)}')
            return ''

        # Convert binary data to base64
        logger.debug('Converting binary data to base64')
        encoded_data = base64.b64encode(image_data).decode('utf-8')
        
        # Return the complete img src with data URI scheme
        return mark_safe(f'data:image/jpeg;base64,{encoded_data}')
    except Exception as e:
        logger.error(f'Error processing image: {str(e)}')
        # Return empty string if there's any error
        return ''
