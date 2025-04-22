from django import template
from django.utils.safestring import mark_safe
from meetings.decorators import has_meetings_permission, MODULES

register = template.Library()

@register.simple_tag(takes_context=True)
def has_meetings_module_permission(context, module_key, permission_type='view'):
    """
    التحقق من صلاحيات المستخدم للوصول لوحدة معينة في تطبيق الاجتماعات
    
    الاستخدام في القوالب:
    {% load meetings_permission_tags %}
    {% has_meetings_module_permission "meetings" "add" as can_add_meeting %}
    {% if can_add_meeting %}
        <a href="{% url 'meetings:create' %}" class="btn btn-success">إنشاء اجتماع جديد</a>
    {% endif %}
    """
    request = context['request']
    return has_meetings_permission(request, module_key, permission_type)

@register.filter
def can_view_meetings_module(user, module_key):
    """
    فلتر للتحقق من صلاحية العرض لوحدة معينة
    
    الاستخدام في القوالب:
    {% load meetings_permission_tags %}
    {% if user|can_view_meetings_module:"meetings" %}
        <a href="{% url 'meetings:list' %}">قائمة الاجتماعات</a>
    {% endif %}
    """
    from django.http import HttpRequest
    # إنشاء كائن طلب وهمي لاستخدامه في الدالة has_meetings_permission
    request = HttpRequest()
    request.user = user
    return has_meetings_permission(request, module_key, 'view')

@register.simple_tag
def get_meetings_module_name(module_key):
    """
    الحصول على اسم الوحدة بناءً على المفتاح
    
    الاستخدام في القوالب:
    {% load meetings_permission_tags %}
    {% get_meetings_module_name "meetings" as module_name %}
    <h1>{{ module_name }}</h1>
    """
    return MODULES.get(module_key, "")

@register.inclusion_tag('meetings/includes/action_buttons.html', takes_context=True)
def meetings_action_buttons(context, module_key, edit_url=None, delete_url=None, print_url=None, back_url=None):
    """
    عرض أزرار الإجراءات بناءً على صلاحيات المستخدم
    
    الاستخدام في القوالب:
    {% load meetings_permission_tags %}
    {% meetings_action_buttons "meetings" edit_url="meetings:edit" delete_url="meetings:delete" back_url="meetings:list" %}
    """
    request = context['request']
    
    return {
        'can_edit': has_meetings_permission(request, module_key, 'edit'),
        'can_delete': has_meetings_permission(request, module_key, 'delete'),
        'can_print': has_meetings_permission(request, module_key, 'print'),
        'edit_url': edit_url,
        'delete_url': delete_url,
        'print_url': print_url,
        'back_url': back_url,
        'object': context.get('object'),
    }
