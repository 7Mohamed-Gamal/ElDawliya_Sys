from django import template
from django.utils.safestring import mark_safe
from Purchase_orders.decorators import has_purchase_permission, MODULES

register = template.Library()

@register.simple_tag(takes_context=True)
def has_purchase_module_permission(context, module_key, permission_type='view'):
    """
    التحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق طلبات الشراء
    
    الاستخدام في القوالب:
    {% load purchase_permission_tags %}
    {% has_purchase_module_permission "purchase_requests" "add" as can_add_request %}
    {% if can_add_request %}
        <a href="{% url 'Purchase_orders:create_purchase_request' %}" class="btn btn-success">إنشاء طلب جديد</a>
    {% endif %}
    """
    request = context['request']
    return has_purchase_permission(request, module_key, permission_type)

@register.filter
def can_view_purchase_module(user, module_key):
    """
    فلتر للتحقق من صلاحية العرض لوحدة معينة
    
    الاستخدام في القوالب:
    {% load purchase_permission_tags %}
    {% if user|can_view_purchase_module:"purchase_requests" %}
        <a href="{% url 'Purchase_orders:purchase_request_list' %}">قائمة طلبات الشراء</a>
    {% endif %}
    """
    from django.http import HttpRequest
    # إنشاء كائن طلب وهمي لاستخدامه في الدالة has_purchase_permission
    request = HttpRequest()
    request.user = user
    return has_purchase_permission(request, module_key, 'view')

@register.simple_tag
def get_purchase_module_name(module_key):
    """
    الحصول على اسم الوحدة بناءً على المفتاح
    
    الاستخدام في القوالب:
    {% load purchase_permission_tags %}
    {% get_purchase_module_name "purchase_requests" as module_name %}
    <h1>{{ module_name }}</h1>
    """
    return MODULES.get(module_key, "")

@register.inclusion_tag('Purchase_orders/includes/action_buttons.html', takes_context=True)
def purchase_action_buttons(context, module_key, edit_url=None, delete_url=None, print_url=None, back_url=None):
    """
    عرض أزرار الإجراءات بناءً على صلاحيات المستخدم
    
    الاستخدام في القوالب:
    {% load purchase_permission_tags %}
    {% purchase_action_buttons "purchase_requests" edit_url="Purchase_orders:edit" delete_url="Purchase_orders:delete" back_url="Purchase_orders:purchase_request_list" %}
    """
    request = context['request']
    
    return {
        'can_edit': has_purchase_permission(request, module_key, 'edit'),
        'can_delete': has_purchase_permission(request, module_key, 'delete'),
        'can_print': has_purchase_permission(request, module_key, 'print'),
        'edit_url': edit_url,
        'delete_url': delete_url,
        'print_url': print_url,
        'back_url': back_url,
        'object': context.get('object'),
    }
