from django.db import ProgrammingError, OperationalError, Error as DatabaseError
from django.conf import settings as django_settings
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Import models with try/except to handle case when tables don't exist yet
MODELS_IMPORTED = False
try:
    from .models import SystemSettings
    MODELS_IMPORTED = True
except (ProgrammingError, OperationalError, DatabaseError, ImportError) as e:
    logger.warning(f"Could not import models: {str(e)}")
    # Define placeholder classes to avoid import errors
    class SystemSettings:
        @classmethod
        def get_settings(cls):
            return DefaultSystemSettings()

# Create a fallback settings class
class DefaultSystemSettings:
    """Default settings when database table doesn't exist"""
    language = 'ar'
    font_family = 'cairo'
    text_direction = 'rtl'
    system_name = 'نظام الدولية'

    def __str__(self):
        return "إعدادات النظام (افتراضية)"

def system_settings(request):
    """
    Context processor to make system settings available to all templates.
    Handles the case when the database table doesn't exist yet.
    """
    # Default settings to use if anything goes wrong
    default_settings = DefaultSystemSettings()

    # Try to get settings from database, with multiple fallbacks
    try:
        if not MODELS_IMPORTED:
            logger.info("Models not imported, using default settings")
            settings = default_settings
        else:
            try:
                settings = SystemSettings.get_settings()
                logger.info("Successfully retrieved system settings from database")
            except Exception as e:
                logger.warning(f"Error getting system settings: {str(e)}")
                settings = default_settings
    except Exception as e:
        logger.error(f"Unexpected error in system_settings context processor: {str(e)}")
        settings = default_settings

    # Safely get attributes with defaults
    try:
        return {
            'system_settings': settings,
            'current_language': getattr(settings, 'language', 'ar'),
            'current_font': getattr(settings, 'font_family', 'cairo'),
            'text_direction': getattr(settings, 'text_direction', 'rtl'),
            'is_rtl': getattr(settings, 'text_direction', 'rtl') == 'rtl',
        }
    except Exception as e:
        logger.error(f"Error creating context dictionary: {str(e)}")
        # Ultimate fallback - hardcoded values
        return {
            'system_settings': default_settings,
            'current_language': 'ar',
            'current_font': 'cairo',
            'text_direction': 'rtl',
            'is_rtl': True,
        }

def user_permissions(request):
    """
    Context processor to make user permissions available to all templates.
    Uses Django's built-in permission system.
    """
    # Default empty values
    default_response = {
        'is_admin': False,
    }

    # Wrap everything in try/except to handle any possible errors
    try:
        # Check if user is authenticated
        if not hasattr(request, 'user') or not request.user:
            logger.warning("Request has no user attribute")
            return default_response

        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            logger.info("User is not authenticated")
            return default_response

        # Check if user is admin
        try:
            is_admin = user.is_superuser or getattr(user, 'Role', '') == 'admin'
        except Exception as e:
            logger.warning(f"Error checking admin status: {str(e)}")
            is_admin = False

        # Return the response with is_admin flag
        return {
            'is_admin': is_admin,
        }

    except Exception as e:
        # Ultimate fallback for any unexpected errors
        logger.error(f"Unexpected error in user_permissions context processor: {str(e)}")
        return default_response
