"""
Template tags for inventory permissions.
This module provides template tags for checking permissions in the inventory app.
It uses Django's built-in permission system.
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Mapeo de módulos para diferentes aplicaciones de inventario
INVENTORY_MODULES = {
    "dashboard": "dashboard",
    "products": "product",
    "categories": "category",
    "units": "unit",
    "suppliers": "supplier",
    "customers": "customer",
    "departments": "department",
    "vouchers": "voucher",
    "invoices": "voucher",  # Alias para compatibilidad
    "purchase_requests": "purchaserequest",
    "reports": "report",
}

# Mapeo de tipos de permisos
PERMISSION_TYPE_MAP = {
    'view': 'view',
    'add': 'add',
    'edit': 'change',
    'delete': 'delete',
    'print': 'view',  # Usamos view para permisos de impresión
}

@register.simple_tag
def has_inventory_module_permission(module_key, permission_type='view'):
    """
    Comprueba si un usuario tiene permiso para un módulo específico de inventario
    Uso: {% has_inventory_module_permission "products" "add" as can_add_product %}
    """
    if module_key not in INVENTORY_MODULES:
        return False
    
    # Convertir clave de módulo a nombre de modelo Django
    model_name = INVENTORY_MODULES.get(module_key, module_key)
    
    # Convertir tipo de permiso a formato Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    
    # Construir nombre de permiso en formato Django
    permission_name = f'inventory.{django_perm_type}_{model_name}'
    
    # Devolver el nombre del permiso para que se pueda verificar en la plantilla
    return permission_name

@register.filter
def has_inventory_perm(user, permission_name):
    """
    Filtro para comprobar si un usuario tiene un permiso específico de inventario
    Uso: {% if user|has_inventory_perm:"inventory.view_product" %}
    """
    if not hasattr(user, 'has_perm'):
        return False
    return user.has_perm(permission_name)

@register.simple_tag(takes_context=True)
def inventory_action_buttons(context, edit_url=None, delete_url=None, print_url=None, back_url=None, 
                  edit_perm=None, delete_perm=None, print_perm=None, 
                  object_id=None, css_class="btn-group"):
    """
    Renderiza un grupo de botones de acción con comprobación de permisos
    Uso: {% inventory_action_buttons edit_url="..." delete_url="..." edit_perm="inventory.change_product" delete_perm="inventory.delete_product" %}
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
