"""
Template tags for Django's built-in permission system.
This replaces the custom permission system with Django's built-in permissions.
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def has_perm(user, permission_name):
    """
    Check if user has a specific permission.
    
    Usage:
    {% if user|has_perm:"app_name.permission_name" %}
        <a href="{% url 'some_url' %}">Link</a>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusers have all permissions
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True
    
    return user.has_perm(permission_name)

@register.simple_tag
def check_perm(user, permission_name):
    """
    Check if user has a specific permission.
    
    Usage:
    {% check_perm user "app_name.permission_name" as can_do_something %}
    {% if can_do_something %}
        <a href="{% url 'some_url' %}">Link</a>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusers have all permissions
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True
    
    return user.has_perm(permission_name)

@register.filter
def is_admin(user):
    """
    Check if user is an admin.
    
    Usage:
    {% if user|is_admin %}
        <a href="{% url 'admin:index' %}">Admin</a>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    
    return user.is_superuser or getattr(user, 'Role', '') == 'admin'

@register.simple_tag
def action_buttons(edit_url=None, delete_url=None, print_url=None, back_url=None, 
                  edit_perm=None, delete_perm=None, print_perm=None, 
                  object_id=None, css_class="btn-group"):
    """
    Render action buttons with permission checks.
    
    Usage:
    {% action_buttons edit_url="app:edit" delete_url="app:delete" print_url="app:print" back_url="app:list" 
                     edit_perm="app.change_model" delete_perm="app.delete_model" print_perm="app.view_model" 
                     object_id=object.id %}
    """
    user = getattr(template.Variable('user').resolve(template.Context()), 'user', None)
    
    buttons = []
    
    # Back button (no permission required)
    if back_url:
        buttons.append(f'<a href="{back_url}" class="btn btn-secondary"><i class="fas fa-arrow-left me-1"></i>رجوع</a>')
    
    # Edit button
    if edit_url and object_id:
        if not edit_perm or (user and (user.is_superuser or user.has_perm(edit_perm))):
            buttons.append(f'<a href="{edit_url}" class="btn btn-primary"><i class="fas fa-edit me-1"></i>تعديل</a>')
    
    # Delete button
    if delete_url and object_id:
        if not delete_perm or (user and (user.is_superuser or user.has_perm(delete_perm))):
            buttons.append(f'<a href="{delete_url}" class="btn btn-danger" onclick="return confirm(\'هل أنت متأكد من الحذف؟\');"><i class="fas fa-trash me-1"></i>حذف</a>')
    
    # Print button
    if print_url and object_id:
        if not print_perm or (user and (user.is_superuser or user.has_perm(print_perm))):
            buttons.append(f'<a href="{print_url}" class="btn btn-info" target="_blank"><i class="fas fa-print me-1"></i>طباعة</a>')
    
    # Combine buttons
    if buttons:
        return mark_safe(f'<div class="{css_class}">' + ''.join(buttons) + '</div>')
    
    return ''
