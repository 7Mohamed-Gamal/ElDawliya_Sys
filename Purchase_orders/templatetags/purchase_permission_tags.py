"""
Template tags for purchase order permissions.
This module provides template tags for checking permissions in the Purchase_orders app.
It uses Django's built-in permission system.
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Mapping of modules for different purchase order applications
MODULES = {
    "dashboard": "dashboard",
    "purchase_requests": "purchaserequest",
    "purchase_orders": "purchaseorder",
    "purchase_items": "purchaseitem",
    "suppliers": "supplier",
    "reports": "report",
    "approvals": "approval",
}

# Mapping of permission types
PERMISSION_TYPE_MAP = {
    'view': 'view',
    'add': 'add',
    'edit': 'change',
    'delete': 'delete',
    'print': 'view',  # We use view for print permissions
}

@register.simple_tag(takes_context=True)
def has_purchase_module_permission(context, module_key, permission_type='view'):
    """
    Checks if a user has permission for a specific purchase module
    Usage: {% has_purchase_module_permission "purchase_requests" "add" as can_add_request %}
    """
    user = context.get('user')
    if not user or not hasattr(user, 'has_perm'):
        return False
        
    # Allow superusers, admins, and the Ragab user for purchase functionality
    if user.is_superuser or getattr(user, 'Role', '') == 'admin' or user.username == 'Ragab':
        return True
        
    if module_key not in MODULES:
        return False
    
    # Convert module key to Django model name
    model_name = MODULES.get(module_key, module_key)
    
    # Convert permission type to Django format
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    
    # Build permission name in Django format
    permission_name = f'Purchase_orders.{django_perm_type}_{model_name}'
    
    # Check the user's permission
    return user.has_perm(permission_name)

@register.filter
def has_purchase_perm(user, permission_name):
    """
    Filter to check if a user has a specific purchase permission
    Usage: {% if user|has_purchase_perm:"Purchase_orders.view_purchaserequest" %}
    """
    if not hasattr(user, 'has_perm'):
        return False
    return user.has_perm(permission_name)

@register.simple_tag(takes_context=True)
def purchase_action_buttons(context, edit_url=None, delete_url=None, print_url=None, back_url=None, 
                  edit_perm=None, delete_perm=None, print_perm=None, 
                  object_id=None, css_class="btn-group"):
    """
    Renders a group of action buttons with permission checks
    Usage: {% purchase_action_buttons edit_url="..." delete_url="..." edit_perm="Purchase_orders.change_purchaserequest" delete_perm="Purchase_orders.delete_purchaserequest" %}
    """
    user = context.get('user')
    if not user:
        return ""
        
    buttons = []
    
    if back_url:
        buttons.append(f'<a href="{back_url}" class="btn btn-secondary btn-sm">'
                      f'<i class="fas fa-arrow-right"></i> رجوع</a>')
    
    if edit_url and (not edit_perm or user.has_perm(edit_perm)):
        buttons.append(f'<a href="{edit_url}" class="btn btn-primary btn-sm">'
                      f'<i class="fas fa-edit"></i> تعديل</a>')
    
    if delete_url and (not delete_perm or user.has_perm(delete_perm)):
        buttons.append(f'<a href="{delete_url}" class="btn btn-danger btn-sm delete-btn" '
                      f'data-id="{object_id or ""}">'
                      f'<i class="fas fa-trash"></i> حذف</a>')
    
    if print_url and (not print_perm or user.has_perm(print_perm)):
        buttons.append(f'<a href="{print_url}" class="btn btn-info btn-sm" target="_blank">'
                      f'<i class="fas fa-print"></i> طباعة</a>')
    
    if not buttons:
        return ""
    
    return mark_safe(f'<div class="{css_class}">{" ".join(buttons)}</div>')
