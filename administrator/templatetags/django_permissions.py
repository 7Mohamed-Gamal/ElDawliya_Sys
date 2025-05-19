"""
Template tags for Django's built-in permission system.
"""
from django import template
from django.utils.safestring import mark_safe
from django.contrib.auth.context_processors import PermWrapper

register = template.Library()

@register.filter
def has_perm(user, permission_name):
    """
    Template filter to check if a user has a specific permission
    Usage: {% if user|has_perm:"app_label.permission_codename" %}
    """
    if not hasattr(user, 'has_perm'):
        return False
    return user.has_perm(permission_name)

@register.simple_tag(takes_context=True)
def check_perm(context, permission_name):
    """
    Template tag to check if a user has a specific permission
    Usage: {% check_perm "app_label.permission_codename" as can_do_something %}
    """
    user = context.get('user')
    if not user or not hasattr(user, 'has_perm'):
        return False
    return user.has_perm(permission_name)

@register.filter
def is_admin(user):
    """
    Template filter to check if a user is an admin/superuser
    Usage: {% if user|is_admin %}
    """
    return getattr(user, 'is_superuser', False)

@register.simple_tag(takes_context=True)
def action_buttons(context, edit_url=None, delete_url=None, print_url=None, back_url=None, 
                  edit_perm=None, delete_perm=None, print_perm=None, 
                  object_id=None, css_class="btn-group"):
    """
    Renders a group of action buttons with permission checks
    Usage: {% action_buttons edit_url="..." delete_url="..." edit_perm="app.change_model" delete_perm="app.delete_model" %}
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
