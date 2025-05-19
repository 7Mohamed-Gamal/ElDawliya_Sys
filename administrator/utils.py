"""
Utility functions for the administrator app.
This file provides compatibility with Django's built-in permission system.
"""

def has_permission(user, permission_name):
    """
    Check if a user has a specific permission.
    This is a compatibility function that uses Django's built-in permission system.
    
    Args:
        user: The user to check permissions for
        permission_name: The permission name in Django format (app_label.codename)
        
    Returns:
        bool: True if the user has the permission, False otherwise
    """
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True
    
    return user.has_perm(permission_name)

def check_permission(user, department_name, module_name, permission_type):
    """
    Compatibility function to map old permission checks to Django's permission system.
    
    Args:
        user: The user to check permissions for
        department_name: The department name (not used in Django's permission system)
        module_name: The module name (used to construct the model name)
        permission_type: The permission type (view, add, change, delete)
        
    Returns:
        bool: True if the user has the permission, False otherwise
    """
    # Map old permission parameters to Django permission name
    # Convert module_name to a valid model name (lowercase, no spaces)
    model_name = module_name.lower().replace(' ', '_')
    
    # Map permission types
    perm_type_map = {
        'view': 'view',
        'add': 'add',
        'edit': 'change',
        'delete': 'delete',
        'print': 'view',  # Use view for print permissions
    }
    
    # Get the Django permission type
    django_perm_type = perm_type_map.get(permission_type, permission_type)
    
    # Determine the app_label based on the department_name
    app_label_map = {
        "الموارد البشرية": "hr",
        "المهام": "tasks",
        "الاجتماعات": "meetings",
        "مهام الموظفين": "employee_tasks",
        "مخزن قطع الغيار": "inventory",
    }
    
    app_label = app_label_map.get(department_name, "administrator")
    
    # Construct the permission name
    permission_name = f"{app_label}.{django_perm_type}_{model_name}"
    
    # Check if the user has the permission
    return has_permission(user, permission_name)
