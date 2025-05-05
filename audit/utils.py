import json
import logging
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .models import AuditLog

logger = logging.getLogger(__name__)


def log_action(user, action, obj=None, app_name=None, object_repr=None, 
               action_details=None, change_data=None, ip_address=None, user_agent=None):
    """
    Manually log an action for audit purposes.
    
    Parameters:
    - user: The user performing the action (can be None)
    - action: Action type (e.g., AuditLog.CREATE, AuditLog.UPDATE)
    - obj: The Django model instance being acted upon (optional)
    - app_name: Name of the application (optional, determined from obj if not provided)
    - object_repr: String representation of the object (optional, determined from obj if not provided)
    - action_details: Additional details about the action (optional)
    - change_data: Dictionary or JSON serializable data about changes (optional)
    - ip_address: IP address of the user (optional)
    - user_agent: User agent string (optional)
    
    Returns:
    - The created AuditLog instance
    """
    try:
        # Process object information if provided
        content_type = None
        object_id = None
        
        if obj is not None:
            if isinstance(obj, models.Model):
                content_type = ContentType.objects.get_for_model(obj)
                object_id = str(obj.pk)
                
                # Set app_name from object if not provided
                if not app_name:
                    app_name = obj.__class__._meta.app_label
                    
                # Set object_repr from object if not provided
                if not object_repr:
                    object_repr = str(obj)
            else:
                logger.warning(f"Object provided is not a Django model instance: {type(obj)}")
        
        # Ensure change_data is JSON serializable
        if change_data and not isinstance(change_data, (dict, list, str, int, float, bool, type(None))):
            if hasattr(change_data, '__dict__'):
                change_data = change_data.__dict__
            else:
                change_data = {'data': str(change_data)}
        
        # Create the audit log entry
        audit_log = AuditLog.objects.create(
            user=user,
            action=action,
            app_name=app_name,
            content_type=content_type,
            object_id=object_id,
            object_repr=object_repr,
            action_details=action_details,
            change_data=change_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return audit_log
    except Exception as e:
        logger.error(f"Error creating manual audit log: {e}")
        return None


def log_create(user, obj, **kwargs):
    """Log object creation action."""
    return log_action(user, AuditLog.CREATE, obj, **kwargs)


def log_update(user, obj, original_data=None, new_data=None, **kwargs):
    """
    Log object update action.
    
    original_data and new_data can be provided to log the specific changes.
    """
    change_data = kwargs.get('change_data', {})
    
    if original_data and new_data:
        change_data.update({
            'original': original_data,
            'new': new_data
        })
    
    kwargs['change_data'] = change_data
    return log_action(user, AuditLog.UPDATE, obj, **kwargs)


def log_delete(user, obj, **kwargs):
    """Log object deletion action."""
    return log_action(user, AuditLog.DELETE, obj, **kwargs)


def log_view(user, obj, **kwargs):
    """Log object view action."""
    return log_action(user, AuditLog.VIEW, obj, **kwargs)


def log_login(user, request=None, **kwargs):
    """Log user login action."""
    if request:
        kwargs.setdefault('ip_address', _get_client_ip(request))
        kwargs.setdefault('user_agent', request.META.get('HTTP_USER_AGENT', ''))
    
    kwargs.setdefault('app_name', 'accounts')
    kwargs.setdefault('action_details', f"User login: {user.username if user else 'Anonymous'}")
    
    return log_action(user, AuditLog.LOGIN, obj=None, **kwargs)


def log_logout(user, request=None, **kwargs):
    """Log user logout action."""
    if request:
        kwargs.setdefault('ip_address', _get_client_ip(request))
        kwargs.setdefault('user_agent', request.META.get('HTTP_USER_AGENT', ''))
    
    kwargs.setdefault('app_name', 'accounts')
    kwargs.setdefault('action_details', f"User logout: {user.username if user else 'Anonymous'}")
    
    return log_action(user, AuditLog.LOGOUT, obj=None, **kwargs)


def _get_client_ip(request):
    """Get the client IP address accounting for proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
