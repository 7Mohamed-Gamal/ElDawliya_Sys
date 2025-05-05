from django import template
from django.contrib.auth import get_user_model
from ..rbac_permissions import has_permission

User = get_user_model()

register = template.Library()

@register.filter
def has_rbac_permission(user, permission_name):
    """
    Template filter to check if a user has a specific RBAC permission.
    
    Usage: 
    {% if user|has_rbac_permission:"edit_articles" %}
        <a href="{% url 'edit_article' article.id %}">Edit</a>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
        
    # Superusers always have all permissions
    if user.is_superuser:
        return True
        
    return has_permission(user, permission_name)

@register.simple_tag
def check_rbac_permission(user, permission_name):
    """
    Template tag to check if a user has a specific RBAC permission.
    
    Usage:
    {% check_rbac_permission user "edit_articles" as can_edit %}
    {% if can_edit %}
        <a href="{% url 'edit_article' article.id %}">Edit</a>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
        
    # Superusers always have all permissions
    if user.is_superuser:
        return True
        
    return has_permission(user, permission_name)
