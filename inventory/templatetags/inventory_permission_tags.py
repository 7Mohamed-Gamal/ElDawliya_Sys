from django import template
from django.utils.safestring import mark_safe
from inventory.decorators import has_inventory_permission, MODULES

register = template.Library()

@register.simple_tag(takes_context=True)
def has_inventory_module_permission(context, module_key, permission_type='view'):
    """
    التحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق المخزن
    
    الاستخدام في القوالب:
    {% load inventory_permission_tags %}
    {% has_inventory_module_permission "products" "add" as can_add_product %}
    {% if can_add_product %}
        <a href="{% url 'inventory:product_add' %}" class="btn btn-success">إضافة صنف جديد</a>
    {% endif %}
    """
    request = context['request']
    return has_inventory_permission(request, module_key, permission_type)

@register.filter
def can_view_inventory_module(user, module_key):
    """
    فلتر للتحقق من صلاحية العرض لوحدة معينة
    
    الاستخدام في القوالب:
    {% load inventory_permission_tags %}
    {% if user|can_view_inventory_module:"products" %}
        <a href="{% url 'inventory:product_list' %}">قائمة الأصناف</a>
    {% endif %}
    """
    from django.http import HttpRequest
    # إنشاء كائن طلب وهمي لاستخدامه في الدالة has_inventory_permission
    request = HttpRequest()
    request.user = user
    return has_inventory_permission(request, module_key, 'view')

@register.simple_tag
def get_inventory_module_name(module_key):
    """
    الحصول على اسم الوحدة بناءً على المفتاح
    
    الاستخدام في القوالب:
    {% load inventory_permission_tags %}
    {% get_inventory_module_name "products" as module_name %}
    <h1>{{ module_name }}</h1>
    """
    return MODULES.get(module_key, "")

@register.inclusion_tag('inventory/includes/action_buttons.html', takes_context=True)
def inventory_action_buttons(context, module_key, edit_url=None, delete_url=None, print_url=None, back_url=None):
    """
    عرض أزرار الإجراءات بناءً على صلاحيات المستخدم
    
    الاستخدام في القوالب:
    {% load inventory_permission_tags %}
    {% inventory_action_buttons "products" edit_url="inventory:product_edit" delete_url="inventory:product_delete" back_url="inventory:product_list" %}
    """
    request = context['request']
    
    return {
        'can_edit': has_inventory_permission(request, module_key, 'edit'),
        'can_delete': has_inventory_permission(request, module_key, 'delete'),
        'can_print': has_inventory_permission(request, module_key, 'print'),
        'edit_url': edit_url,
        'delete_url': delete_url,
        'print_url': print_url,
        'back_url': back_url,
        'object': context.get('object'),
    }
