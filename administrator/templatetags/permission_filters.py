from django import template
from django.utils.safestring import mark_safe
from django.template import Node, TemplateSyntaxError

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key
    
    Usage:
    {{ my_dict|get_item:key }}
    """
    if not dictionary:
        return []
    
    try:
        return dictionary.get(key, [])
    except (AttributeError, KeyError):
        return []

@register.filter
def filter_by_code(operations, code):
    """
    Filter a list of operations by code
    
    Usage:
    {{ operations|filter_by_code:'employee' }}
    """
    if not operations:
        return None
    
    for operation in operations:
        if operation.code == code:
            return operation
    
    return None

@register.filter
def filter_by_type(operations, permission_type):
    """
    Filter a list of operations by permission type
    
    Usage:
    {{ operations|filter_by_type:'view' }}
    """
    if not operations:
        return None
    
    for operation in operations:
        if operation.permission_type == permission_type:
            return operation
    
    return None

@register.filter
def get_modules_for_department(department):
    """
    Get modules for a specific department
    
    Usage:
    {{ department|get_modules_for_department }}
    """
    from administrator.models import Module
    
    if not department:
        return []
    
    return Module.objects.filter(department=department).order_by('order')

@register.filter
def get_form_field(form, field_name):
    """
    Get a field from a form by its name
    
    Usage:
    {{ form|get_form_field:'field_name' }}
    """
    if not form or not field_name:
        return None
        
    try:
        # Try to access as BoundField (normal form field)
        return form[field_name]
    except (KeyError, AttributeError):
        # Fallback: try to access the field directly from form.fields
        try:
            if hasattr(form, 'fields') and field_name in form.fields:
                field = form.fields[field_name]
                widget = field.widget
                attrs = widget.attrs.copy()
                attrs['id'] = f'id_{field_name}'
                attrs['name'] = field_name
                if field.required:
                    attrs['required'] = 'required'
                
                initial_value = form.initial.get(field_name, field.initial)
                rendered = widget.render(field_name, initial_value, attrs)
                return mark_safe(rendered)
        except Exception as e:
            print(f"Error rendering field {field_name}: {str(e)}")
            
        return None

@register.simple_tag
def render_department_checkbox(form, department_id):
    """
    Render a checkbox for a department using its ID
    
    Usage:
    {% render_department_checkbox form department.id %}
    """
    field_name = f'dept_{department_id}'
    try:
        if field_name in form.fields:
            field = form.fields[field_name]
            widget = field.widget
            attrs = widget.attrs.copy()
            attrs['id'] = f'id_{field_name}'
            attrs['name'] = field_name
            if field.required:
                attrs['required'] = 'required'
            
            initial_value = form.initial.get(field_name, field.initial)
            rendered = widget.render(field_name, initial_value, attrs)
            return mark_safe(rendered)
    except Exception as e:
        print(f"Error rendering department checkbox: {str(e)}")
    return ''

@register.simple_tag
def render_module_checkbox(form, module_id):
    """
    Render a checkbox for a module using its ID
    
    Usage:
    {% render_module_checkbox form module.id %}
    """
    field_name = f'module_{module_id}'
    try:
        if field_name in form.fields:
            field = form.fields[field_name]
            widget = field.widget
            attrs = widget.attrs.copy()
            attrs['id'] = f'id_{field_name}'
            attrs['name'] = field_name
            if field.required:
                attrs['required'] = 'required'
            
            initial_value = form.initial.get(field_name, field.initial)
            rendered = widget.render(field_name, initial_value, attrs)
            return mark_safe(rendered)
    except Exception as e:
        print(f"Error rendering module checkbox: {str(e)}")
    return ''

@register.simple_tag
def render_permission_checkbox(form, module_id, perm_type):
    """
    Render a checkbox for a permission using module ID and permission type
    
    Usage:
    {% render_permission_checkbox form module.id perm_type %}
    """
    field_name = f'perm_{module_id}_{perm_type}'
    try:
        if field_name in form.fields:
            field = form.fields[field_name]
            widget = field.widget
            attrs = widget.attrs.copy()
            attrs['id'] = f'id_{field_name}'
            attrs['name'] = field_name
            if field.required:
                attrs['required'] = 'required'
            
            initial_value = form.initial.get(field_name, field.initial)
            rendered = widget.render(field_name, initial_value, attrs)
            return mark_safe(rendered)
    except Exception as e:
        print(f"Error rendering permission checkbox: {str(e)}")
    return ''
