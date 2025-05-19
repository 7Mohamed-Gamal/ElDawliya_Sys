"""
Decorators for the administrator app.
This file provides compatibility with Django's built-in permission system.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

def django_permission_required(permission_name, login_url=None):
    """
    Decorator for views that checks whether a user has a particular permission.
    This is a wrapper around Django's permission_required decorator.
    
    Args:
        permission_name: The permission name in Django format (app_label.codename)
        login_url: The URL to redirect to if the user is not logged in
        
    Returns:
        The decorated view function
    """
    return permission_required(permission_name, login_url=login_url)

def module_permission_required(department_name, module_name, permission_type='view'):
    """
    Compatibility function to map old permission checks to Django's permission system.
    
    Args:
        department_name: The department name (used to determine the app_label)
        module_name: The module name (used to construct the model name)
        permission_type: The permission type (view, add, change, delete)
        
    Returns:
        The decorated view function
    """
    # Map department names to app labels
    app_label_map = {
        "الموارد البشرية": "hr",
        "المهام": "tasks",
        "الاجتماعات": "meetings",
        "مهام الموظفين": "employee_tasks",
        "مخزن قطع الغيار": "inventory",
    }
    
    # Get the app label
    app_label = app_label_map.get(department_name, "administrator")
    
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
    
    # Construct the permission name
    permission_name = f"{app_label}.{django_perm_type}_{model_name}"
    
    # Return the permission_required decorator
    return permission_required(permission_name, login_url='accounts:access_denied')

def class_permission_required(department_name, module_name, permission_type='view'):
    """
    Compatibility function to map old permission checks to Django's permission system
    for class-based views.
    
    Args:
        department_name: The department name (used to determine the app_label)
        module_name: The module name (used to construct the model name)
        permission_type: The permission type (view, add, change, delete)
        
    Returns:
        The decorated view class
    """
    # Map department names to app labels
    app_label_map = {
        "الموارد البشرية": "hr",
        "المهام": "tasks",
        "الاجتماعات": "meetings",
        "مهام الموظفين": "employee_tasks",
        "مخزن قطع الغيار": "inventory",
    }
    
    # Get the app label
    app_label = app_label_map.get(department_name, "administrator")
    
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
    
    # Construct the permission name
    permission_name = f"{app_label}.{django_perm_type}_{model_name}"
    
    # Return the method_decorator
    return method_decorator(
        permission_required(permission_name, login_url='accounts:access_denied'),
        name='dispatch'
    )
