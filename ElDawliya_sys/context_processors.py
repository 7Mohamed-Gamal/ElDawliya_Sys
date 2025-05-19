"""
Context processors for the ElDawliya system.
These processors provide additional context variables to all templates.
"""
import datetime

def rtl_context_processor(request):
    """
    Provides RTL-related context variables to all templates.
    
    Returns:
        dict: A dictionary containing RTL-related context variables.
    """
    return {
        'text_direction': 'rtl',  # Default text direction
        'current_language': 'ar',  # Default language
        'current_font': 'Cairo',  # Default font
        'current_year': datetime.datetime.now().year,
    }
