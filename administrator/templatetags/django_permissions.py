"""
Template tags for Django's built-in permission system.
"""
from django import template
from django.utils.safestring import mark_safe
from django.contrib.auth.context_processors import PermWrapper

register = template.Library()

# Mapeo de módulos para diferentes aplicaciones
HR_MODULES = {
    "dashboard": "dashboard",
    "employees": "employee",
    "jobs": "job",
    "departments": "department",
    "attendance": "attendance",
    "leaves": "leave",
    "payroll": "payroll",
    "reports": "report",
    "cars": "car",
}

EMPLOYEE_TASKS_MODULES = {
    "dashboard": "dashboard",
    "tasks": "employeetask",
    "my_tasks": "mytask",
    "calendar": "calendar",
    "analytics": "analytics",
    "notifications": "notification",
    "categories": "taskcategory",
}

TASKS_MODULES = {
    "dashboard": "dashboard",
    "tasks": "task",
    "my_tasks": "mytask",
    "reports": "report",
}

MEETINGS_MODULES = {
    "dashboard": "dashboard",
    "meetings": "meeting",
    "tasks": "meetingtask",
    "reports": "meetingreport",
}

INVENTORY_MODULES = {
    "dashboard": "dashboard",
    "products": "product",
    "categories": "category",
    "suppliers": "supplier",
    "transactions": "transaction",
    "reports": "report",
}

PURCHASE_MODULES = {
    "dashboard": "dashboard",
    "purchase_requests": "purchaserequest",
    "purchase_orders": "purchaseorder",
    "purchase_items": "purchaseitem",
    "suppliers": "supplier",
    "reports": "report",
    "approvals": "approval",
}

# Mapeo de tipos de permisos
PERMISSION_TYPE_MAP = {
    'view': 'view',
    'add': 'add',
    'edit': 'change',
    'delete': 'delete',
    'print': 'view',  # Usamos view para permisos de impresión
}

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

@register.simple_tag
def has_hr_module_permission(module_key, permission_type='view'):
    """
    Comprueba si un usuario tiene permiso para un módulo específico de HR
    Uso: {% has_hr_module_permission "jobs" "add" as can_add_job %}
    """
    if module_key not in HR_MODULES:
        return False

    # Convertir clave de módulo a nombre de modelo Django
    model_name = HR_MODULES.get(module_key, module_key)

    # Convertir tipo de permiso a formato Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)

    # Construir nombre de permiso en formato Django
    permission_name = f'Hr.{django_perm_type}_{model_name}'

    # Devolver el nombre del permiso para que se pueda verificar en la plantilla
    return permission_name

@register.simple_tag
def has_employee_tasks_module_permission(module_key, permission_type='view'):
    """
    Comprueba si un usuario tiene permiso para un módulo específico de tareas de empleados
    Uso: {% has_employee_tasks_module_permission "tasks" "add" as can_add_task %}
    """
    if module_key not in EMPLOYEE_TASKS_MODULES:
        return False

    model_name = EMPLOYEE_TASKS_MODULES.get(module_key, module_key)
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    permission_name = f'employee_tasks.{django_perm_type}_{model_name}'

    return permission_name

@register.simple_tag
def has_tasks_module_permission(module_key, permission_type='view'):
    """
    Comprueba si un usuario tiene permiso para un módulo específico de tareas
    Uso: {% has_tasks_module_permission "tasks" "add" as can_add_task %}
    """
    if module_key not in TASKS_MODULES:
        return False

    model_name = TASKS_MODULES.get(module_key, module_key)
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    permission_name = f'tasks.{django_perm_type}_{model_name}'

    return permission_name

@register.simple_tag
def has_meetings_module_permission(module_key, permission_type='view'):
    """
    Comprueba si un usuario tiene permiso para un módulo específico de reuniones
    Uso: {% has_meetings_module_permission "meetings" "add" as can_add_meeting %}
    """
    if module_key not in MEETINGS_MODULES:
        return False

    model_name = MEETINGS_MODULES.get(module_key, module_key)
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    permission_name = f'meetings.{django_perm_type}_{model_name}'

    return permission_name

@register.simple_tag
def has_inventory_module_permission(module_key, permission_type='view'):
    """
    Comprueba si un usuario tiene permiso para un módulo específico de inventario
    Uso: {% has_inventory_module_permission "products" "add" as can_add_product %}
    """
    if module_key not in INVENTORY_MODULES:
        return False

    model_name = INVENTORY_MODULES.get(module_key, module_key)
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    permission_name = f'inventory.{django_perm_type}_{model_name}'

    return permission_name

@register.simple_tag
def has_purchase_module_permission(module_key, permission_type='view'):
    """
    Comprueba si un usuario tiene permiso para un módulo específico de compras
    Uso: {% has_purchase_module_permission "purchase_requests" "add" as can_add_request %}
    """
    if module_key not in PURCHASE_MODULES:
        return False

    model_name = PURCHASE_MODULES.get(module_key, module_key)
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    permission_name = f'Purchase_orders.{django_perm_type}_{model_name}'

    return permission_name

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
