"""
Context processors for the ElDawliya system.
These processors provide additional context variables to all templates.
"""
import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def rtl_context_processor(request):
    """
    Provides RTL-related context variables to all templates.
    Uses values from SystemSettings if available.
    
    Returns:
        dict: A dictionary containing RTL-related context variables.
    """
    # Default values
    text_direction = 'rtl'
    current_language = 'ar'
    current_font = 'Cairo'
    
    # Try to get values from system_settings context processor
    try:
        from administrator.models import SystemSettings
        system_settings = SystemSettings.objects.first()
        if system_settings:
            text_direction = system_settings.text_direction or text_direction
            current_language = system_settings.language or current_language
            current_font = system_settings.font_family.capitalize() or current_font
    except Exception as e:
        logger.warning(f"Error getting system settings in rtl_context_processor: {str(e)}")
    
    return {
        'text_direction': text_direction,
        'current_language': current_language,
        'current_font': current_font,
        'current_year': datetime.datetime.now().year,
    }
