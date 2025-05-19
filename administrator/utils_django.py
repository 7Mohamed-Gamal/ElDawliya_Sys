"""
Utility functions for Django's built-in permission system.
This replaces the custom permission system with Django's built-in permissions.
"""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

def is_admin(user):
    """
    Check if user is an admin.
    
    Args:
        user: User object
        
    Returns:
        bool: True if user is an admin, False otherwise
    """
    if not user or not user.is_authenticated:
        return False
    
    return user.is_superuser or getattr(user, 'Role', '') == 'admin'

def get_user_permissions(user):
    """
    Get all permissions for a user using Django's built-in permission system.
    
    Args:
        user: User object
        
    Returns:
        dict: Dictionary with user's permissions
    """
    if not user or not user.is_authenticated:
        return {
            'has_all_permissions': False,
            'permissions': [],
            'groups': []
        }
    
    # Superusers have all permissions
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return {
            'has_all_permissions': True,
            'permissions': Permission.objects.all(),
            'groups': Group.objects.all()
        }
    
    # Get user's permissions
    permissions = Permission.objects.filter(
        Q(user=user) | Q(group__user=user)
    ).distinct()
    
    # Get user's groups
    groups = user.groups.all()
    
    return {
        'has_all_permissions': False,
        'permissions': permissions,
        'groups': groups
    }

def get_permission_name(app_label, model_name, action):
    """
    Get the permission name in Django's format.
    
    Args:
        app_label: Application label (e.g., 'auth')
        model_name: Model name (e.g., 'user')
        action: Action (e.g., 'view', 'add', 'change', 'delete')
        
    Returns:
        str: Permission name in format 'app_label.action_model_name'
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
