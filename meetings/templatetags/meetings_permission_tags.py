from django import template

register = template.Library()

# تعريف الوحدات (الموديولات) في تطبيق الاجتماعات للعرض فقط
MODULES = {
    "meetings": "إدارة الاجتماعات",
    "attendees": "إدارة الحضور",
    "meeting_tasks": "مهام الاجتماعات",
    "reports": "تقارير الاجتماعات",
}

# تحويل مفاتيح الوحدات إلى أسماء موديلات Django
MODEL_MAP = {
    'meetings': 'meeting',
    'attendees': 'attendee',
    'meeting_tasks': 'meetingtask',
    'reports': 'report',
}

# تحويل أنواع الصلاحيات إلى صيغة Django
PERMISSION_TYPE_MAP = {
    'view': 'view',
    'add': 'add',
    'edit': 'change',
    'delete': 'delete',
    'print': 'view',  # نستخدم view للطباعة لأنها عملية قراءة
}

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
    user = request.user

    # المشرفون لديهم جميع الصلاحيات
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODEL_MAP.get(module_key, module_key)
    
    # تحويل نوع الصلاحية إلى صيغة Django
    django_perm_type = PERMISSION_TYPE_MAP.get(permission_type, permission_type)
    
    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'meetings.{django_perm_type}_{model_name}'
    
    return user.has_perm(permission_name)

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
    # المشرفون لديهم جميع الصلاحيات
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODEL_MAP.get(module_key, module_key)
    
    # تكوين اسم الصلاحية بصيغة Django
    permission_name = f'meetings.view_{model_name}'
    
    return user.has_perm(permission_name)

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
    user = request.user

    # المشرفون لديهم جميع الصلاحيات
    is_admin = user.is_superuser or getattr(user, 'Role', '') == 'admin'

    # تحويل مفتاح الوحدة إلى اسم موديل Django
    model_name = MODEL_MAP.get(module_key, module_key)
    
    # تكوين أسماء الصلاحيات بصيغة Django
    edit_permission = f'meetings.change_{model_name}'
    delete_permission = f'meetings.delete_{model_name}'
    view_permission = f'meetings.view_{model_name}'  # للطباعة نستخدم صلاحية العرض

    return {
        'can_edit': is_admin or user.has_perm(edit_permission),
        'can_delete': is_admin or user.has_perm(delete_permission),
        'can_print': is_admin or user.has_perm(view_permission),
        'edit_url': edit_url,
        'delete_url': delete_url,
        'print_url': print_url,
        'back_url': back_url,
        'object': context.get('object'),
    }
