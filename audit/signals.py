import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .utils import log_login, log_logout, log_action
from .models import AuditLog

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """Log user login events."""
    try:
        log_login(user, request, action_details=f"User logged in: {user.username}")
    except Exception as e:
        logger.error(f"Error logging user login: {e}")


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """Log user logout events."""
    try:
        log_logout(user, request, action_details=f"User logged out: {user.username if user else 'Anonymous'}")
    except Exception as e:
        logger.error(f"Error logging user logout: {e}")


@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request=None, **kwargs):
    """Log failed login attempts."""
    try:
        # Get username from credentials
        username = credentials.get('username', 'unknown')
        
        # Extract IP and user agent if available
        ip_address = None
        user_agent = None
        if request:
            from .utils import _get_client_ip
            ip_address = _get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
        # Log the failed attempt
        log_action(
            user=None,  # No user since login failed
            action=AuditLog.LOGIN,
            app_name='accounts',
            action_details=f"Failed login attempt for user: {username}",
            ip_address=ip_address,
            user_agent=user_agent,
            change_data={
                'username': username,
                'failed_reason': 'Invalid credentials'
            }
        )
    except Exception as e:
        logger.error(f"Error logging failed login attempt: {e}")
