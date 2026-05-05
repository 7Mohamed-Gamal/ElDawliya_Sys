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


def system_info(request):
    """
    Provides system information context variables to all templates.
    
    Returns:
        dict: A dictionary containing system information.
    """
    return {
        'system_name': 'نظام الدولية',
        'system_version': '1.0.0',
        'current_year': datetime.datetime.now().year,
        'debug_mode': settings.DEBUG,
    }


def ui_shell(request):
    """
    Provides safe default UI shell values for the global Tailwind base.
    View-level context can override these values when a page needs a focused
    layout such as login or access-denied screens.
    """
    path = request.path or ''

    return {
        'show_sidebar': True,
        'show_navbar': True,
        'show_footer': True,
        'active_path': path,
        'default_menu_items': [
            {
                'title': 'لوحة التحكم',
                'icon': 'fas fa-gauge-high',
                'url': '/dashboard/',
                'active': path.startswith('/dashboard/'),
            },
            {
                'title': 'الحسابات',
                'icon': 'fas fa-users-gear',
                'url': '/accounts/dashboard/',
                'active': path.startswith('/accounts/'),
            },
            {
                'title': 'الموارد البشرية',
                'icon': 'fas fa-users',
                'url': '/hr/',
                'active': path.startswith('/hr/'),
            },
            {
                'title': 'المخزون',
                'icon': 'fas fa-boxes-stacked',
                'url': '/inventory/',
                'active': path.startswith('/inventory/'),
            },
            {
                'title': 'المشتريات',
                'icon': 'fas fa-cart-shopping',
                'url': '/purchase/',
                'active': path.startswith('/purchase/') or path.startswith('/procurement/'),
            },
            {
                'title': 'المشاريع',
                'icon': 'fas fa-diagram-project',
                'url': '/projects/',
                'active': path.startswith('/projects/') or path.startswith('/meetings/'),
            },
            {
                'title': 'التقارير',
                'icon': 'fas fa-chart-line',
                'url': '/reports/',
                'active': path.startswith('/reports/'),
            },
            {
                'title': 'إدارة النظام',
                'icon': 'fas fa-shield-halved',
                'url': '/administrator/',
                'active': path.startswith('/administrator/'),
            },
        ],
    }
