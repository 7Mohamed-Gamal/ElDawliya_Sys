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
    Makes system settings available to all templates.
    This is a crucial context processor that provides font settings and other
    system-wide configurations to all templates.
    """
    try:
        settings = SystemSettings.objects.first()
        if not settings:
            # Create default settings if none exist
            settings = SystemSettings()
            try:
                settings.save()
                logger.info("Created default system settings")
            except Exception as e:
                logger.error(f"Could not create default system settings: {str(e)}")
                settings = DefaultSystemSettings()
        
        return {
            'system_settings': settings
        }
    except Exception as e:
        logger.error(f"Error in system_settings context processor: {str(e)}")
        # Return default settings object if there's an error
        return {
            'system_settings': DefaultSystemSettings()
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
