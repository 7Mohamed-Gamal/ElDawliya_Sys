"""
Utility functions for Django's built-in permission system.
This replaces the custom permission system with Django's built-in permissions.
"""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)

def get_permission_name(app_label, model_name, action):
    """
    Get the full permission name in Django's format: app_label.action_modelname
    
    Args:
        app_label: Application label (e.g., 'auth')
        model_name: Model name (e.g., 'user')
        action: Action name (e.g., 'view', 'add', 'change', 'delete')
        
    Returns:
        str: Full permission name
    """
    return f"{app_label}.{action}_{model_name}"

def create_custom_permission(app_label, model_name, codename, name):
    """
    Create a custom permission.
    
    Args:
        app_label: Application label (e.g., 'auth')
        model_name: Model name (e.g., 'user')
        codename: Permission codename (e.g., 'view_user')
        name: Permission name (e.g., 'Can view user')
        
    Returns:
        Permission: Created permission object
    """
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
        
        # Check if permission already exists
        if Permission.objects.filter(content_type=content_type, codename=codename).exists():
            return Permission.objects.get(content_type=content_type, codename=codename)
        
        # Create permission
        return Permission.objects.create(
            content_type=content_type,
            codename=codename,
            name=name
        )
    except Exception as e:
        logger.error(f"Error creating custom permission: {str(e)}")
        return None
