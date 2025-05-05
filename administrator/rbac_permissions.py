from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings

User = get_user_model()

# Define permission categories
PERMISSION_CATEGORIES = {
    'content': 'إدارة المحتوى',
    'users': 'إدارة المستخدمين',
    'reports': 'التقارير',
    'settings': 'الإعدادات',
    'system': 'النظام',
    'other': 'أخرى',
}

# Cache timeout (in seconds)
RBAC_CACHE_TIMEOUT = getattr(settings, 'RBAC_CACHE_TIMEOUT', 300)  # 5 minutes by default

def get_user_roles(user):
    """
    Get all roles (groups) for a user.
    
    Args:
        user: Django User object
    
    Returns:
        QuerySet of Group objects
    """
    if not user or not user.is_authenticated:
        return Group.objects.none()
    
    return user.groups.all()

def get_role_permissions(role):
    """
    Get all permissions for a role (group).
    
    Args:
        role: Django Group object
    
    Returns:
        QuerySet of Permission objects
    """
    if not role:
        return Permission.objects.none()
    
    return role.permissions.all()

def get_all_user_permissions(user):
    """
    Get all permissions for a user across all their roles.
    
    This function aggregates permissions from all groups (roles) 
    that the user belongs to.
    
    Args:
        user: Django User object
    
    Returns:
        Set of permission codenames
    """
    if not user or not user.is_authenticated:
        return set()
    
    # Generate a cache key for this user's permissions
    cache_key = f"rbac_user_permissions_{user.id}"
    
    # Try to get from cache first
    cached_permissions = cache.get(cache_key)
    if cached_permissions is not None:
        return cached_permissions
    
    # If user is a superuser, they have all permissions
    if user.is_superuser:
        permissions = set(Permission.objects.values_list('codename', flat=True))
        cache.set(cache_key, permissions, RBAC_CACHE_TIMEOUT)
        return permissions
    
    # Get all roles (groups) for the user
    roles = get_user_roles(user)
    
    # Aggregate permissions from all roles
    permission_set = set()
    for role in roles:
        role_permissions = get_role_permissions(role)
        permission_set.update(role_permissions.values_list('codename', flat=True))
    
    # Add user-specific permissions 
    permission_set.update(user.user_permissions.values_list('codename', flat=True))
    
    # Cache the result
    cache.set(cache_key, permission_set, RBAC_CACHE_TIMEOUT)
    
    return permission_set

def has_permission(user, permission_name):
    """
    Check if a user has a specific permission.
    
    Args:
        user: Django User object
        permission_name: Permission codename as string
    
    Returns:
        Boolean indicating whether the user has the permission
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superuser always has all permissions
    if user.is_superuser:
        return True
    
    # Generate a cache key for this specific permission check
    cache_key = f"rbac_user_perm_{user.id}_{permission_name}"
    
    # Try to get from cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Get all user permissions
    user_permissions = get_all_user_permissions(user)
    
    # Check if the permission exists in the set
    result = permission_name in user_permissions
    
    # Cache the result
    cache.set(cache_key, result, RBAC_CACHE_TIMEOUT)
    
    return result

def clear_user_permissions_cache(user):
    """
    Clear the permissions cache for a user.
    This should be called whenever a user's permissions change.
    
    Args:
        user: Django User object
    """
    if not user:
        return
    
    cache_key = f"rbac_user_permissions_{user.id}"
    cache.delete(cache_key)
    
    # Also delete any specific permission checks
    # (This is a simplified approach - in production, you might want to
    # track all permission cache keys for a user to clear them properly)
    for perm in Permission.objects.values_list('codename', flat=True):
        perm_cache_key = f"rbac_user_perm_{user.id}_{perm}"
        cache.delete(perm_cache_key)

def clear_role_permissions_cache(role):
    """
    Clear the permissions cache for all users in a role.
    This should be called whenever a role's permissions change.
    
    Args:
        role: Django Group object
    """
    if not role:
        return
    
    # Get all users in this role
    users = role.user_set.all()
    
    # Clear cache for each user
    for user in users:
        clear_user_permissions_cache(user)

def create_default_permissions():
    """
    Create a set of default permissions for the system.
    
    Returns:
        Dict mapping category names to lists of created Permission objects
    """
    from django.contrib.contenttypes.models import ContentType
    
    # Get the ContentType for Group (as a generic model to associate with)
    content_type = ContentType.objects.get_for_model(Group)
    
    # Define default permissions by category
    default_permissions = {
        'content': [
            ('view_content', 'Can view content'),
            ('add_content', 'Can add content'),
            ('edit_content', 'Can edit content'),
            ('delete_content', 'Can delete content'),
            ('publish_content', 'Can publish content'),
            ('unpublish_content', 'Can unpublish content'),
            ('approve_content', 'Can approve content'),
            ('reject_content', 'Can reject content'),
        ],
        'users': [
            ('view_users', 'Can view users'),
            ('add_user', 'Can add user'),
            ('edit_user', 'Can edit user'),
            ('delete_user', 'Can delete user'),
            ('assign_roles', 'Can assign roles'),
            ('view_roles', 'Can view roles'),
            ('add_role', 'Can add role'),
            ('edit_role', 'Can edit role'),
            ('delete_role', 'Can delete role'),
        ],
        'reports': [
            ('view_reports', 'Can view reports'),
            ('generate_reports', 'Can generate reports'),
            ('export_reports', 'Can export reports'),
            ('print_reports', 'Can print reports'),
            ('share_reports', 'Can share reports'),
        ],
        'settings': [
            ('view_settings', 'Can view settings'),
            ('edit_settings', 'Can edit settings'),
            ('view_system_logs', 'Can view system logs'),
        ],
        'system': [
            ('manage_permissions', 'Can manage permissions'),
            ('system_admin', 'Full system administrator'),
            ('backup_restore', 'Can backup and restore data'),
            ('view_analytics', 'Can view analytics'),
        ],
        'other': [
            ('send_notifications', 'Can send notifications'),
            ('view_notifications', 'Can view notifications'),
        ],
    }
    
    # Create or update permissions
    created_permissions = {}
    
    for category, perms in default_permissions.items():
        created_permissions[category] = []
        
        for codename, name in perms:
            # Check if permission already exists
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults={'name': name}
            )
            
            # Add metadata (category) to the permission
            setattr(permission, 'category', category)
            created_permissions[category].append(permission)
    
    return created_permissions

def assign_default_admin_permissions(role):
    """
    Assign all default permissions to a role (typically for admin).
    
    Args:
        role: Django Group object
    
    Returns:
        List of assigned Permission objects
    """
    if not role:
        return []
    
    # Get all permissions
    permissions = Permission.objects.all()
    
    # Assign all permissions to the role
    role.permissions.add(*permissions)
    
    # Clear the permissions cache for this role
    clear_role_permissions_cache(role)
    
    return list(permissions)

def assign_category_permissions(role, category):
    """
    Assign all permissions in a category to a role.
    
    Args:
        role: Django Group object
        category: Category name (string)
    
    Returns:
        List of assigned Permission objects
    """
    if not role or not category:
        return []
    
    # Get all permissions for the category
    # This assumes permissions have a 'category' attribute
    permissions = [
        p for p in Permission.objects.all() 
        if hasattr(p, 'category') and p.category == category
    ]
    
    # Assign permissions to the role
    role.permissions.add(*permissions)
    
    # Clear the permissions cache for this role
    clear_role_permissions_cache(role)
    
    return permissions
