from django.contrib.auth.models import Group
from django.db.models import Q, Prefetch
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import Department, Module, Permission, TemplatePermission

User = get_user_model()

# Cache timeout in seconds (1 hour)
CACHE_TIMEOUT = 60 * 60

def check_permission(user, department_name, module_name, permission_type):
    """
    تحقق مما إذا كان المستخدم لديه صلاحية محددة لوحدة معينة في قسم معين

    المعلمات:
    - user: المستخدم المراد التحقق من صلاحياته
    - department_name: اسم القسم (مثل 'الموارد البشرية')
    - module_name: اسم الوحدة (مثل 'إدارة الموظفين')
    - permission_type: نوع الصلاحية ('view', 'add', 'edit', 'delete', 'print')

    العائد:
    - True إذا كان المستخدم لديه الصلاحية، False إذا لم يكن لديه الصلاحية
    """
    # التحقق من تسجيل دخول المستخدم
    if not user.is_authenticated:
        return False

    # المستخدمون المتميزون لديهم جميع الصلاحيات
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True

    # تحويل نوع الصلاحية من 'edit' إلى 'change' للتوافق مع نظام الصلاحيات
    if permission_type == 'edit':
        permission_type = 'change'

    # إنشاء مفتاح التخزين المؤقت
    cache_key = f'perm_{user.id}_{department_name}_{module_name}_{permission_type}'

    # محاولة الحصول على النتيجة من التخزين المؤقت
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        # البحث عن القسم
        department = Department.objects.get(name=department_name)

        # التحقق من صلاحيات القسم
        if department.require_admin and not (user.is_staff or user.is_superuser or getattr(user, 'Role', '') == 'admin'):
            cache.set(cache_key, False, CACHE_TIMEOUT)
            return False

        # البحث عن الوحدة
        module = Module.objects.get(department=department, name=module_name)

        # التحقق من صلاحيات الوحدة
        if module.require_admin and not (user.is_staff or user.is_superuser or getattr(user, 'Role', '') == 'admin'):
            cache.set(cache_key, False, CACHE_TIMEOUT)
            return False

        # البحث عن الصلاحية
        permission = Permission.objects.get(module=module, permission_type=permission_type)

        # التحقق من صلاحيات المستخدم المباشرة
        if user in permission.users.all():
            cache.set(cache_key, True, CACHE_TIMEOUT)
            return True

        # التحقق من صلاحيات المجموعات
        user_groups = Group.objects.filter(user=user)
        for group in user_groups:
            if group in permission.groups.all():
                cache.set(cache_key, True, CACHE_TIMEOUT)
                return True

        cache.set(cache_key, False, CACHE_TIMEOUT)
        return False
    except (Department.DoesNotExist, Module.DoesNotExist, Permission.DoesNotExist):
        # إذا لم يتم العثور على القسم أو الوحدة أو الصلاحية، فلا يوجد صلاحية
        cache.set(cache_key, False, CACHE_TIMEOUT)
        return False

def has_permission(user, department_name, module_name, permission_type):
    """
    تحقق مما إذا كان المستخدم لديه صلاحية محددة لوحدة معينة في قسم معين

    المعلمات:
    - user: المستخدم المراد التحقق من صلاحياته
    - department_name: اسم القسم (مثل 'HR')
    - module_name: اسم الوحدة (مثل 'إدارة الموظفين')
    - permission_type: نوع الصلاحية ('عرض'، 'إضافة'، 'تعديل'، 'حذف'، 'طباعة')

    العائد:
    - True إذا كان المستخدم لديه الصلاحية، False إذا لم يكن لديه الصلاحية
    """
    # التحقق من تسجيل دخول المستخدم
    if not user.is_authenticated:
        return False

    # المستخدمون المتميزون لديهم جميع الصلاحيات
    if user.is_superuser:
        return True

    # تحويل نوع الصلاحية من العربية إلى الإنجليزية
    permission_type_map = {
        'عرض': 'view',
        'إضافة': 'add',
        'تعديل': 'change',
        'حذف': 'delete',
        'طباعة': 'print'
    }

    permission_type_en = permission_type_map.get(permission_type, permission_type)

    try:
        # البحث عن القسم
        department = Department.objects.get(name=department_name)

        # التحقق من صلاحيات القسم
        if department.require_admin and not (user.is_staff or user.is_superuser):
            return False

        # البحث عن الوحدة
        module = Module.objects.get(department=department, name=module_name)

        # التحقق من صلاحيات الوحدة
        if module.require_admin and not (user.is_staff or user.is_superuser):
            return False

        # البحث عن الصلاحية
        permission = Permission.objects.get(module=module, permission_type=permission_type_en)

        # التحقق من صلاحيات المستخدم المباشرة
        if user in permission.users.all():
            return True

        # التحقق من صلاحيات المجموعات
        user_groups = Group.objects.filter(user=user)
        for group in user_groups:
            if group in permission.groups.all():
                return True

        return False
    except (Department.DoesNotExist, Module.DoesNotExist, Permission.DoesNotExist):
        # إذا لم يتم العثور على القسم أو الوحدة أو الصلاحية، فلا يوجد صلاحية
        return False

def has_template_permission(user, template_path):
    """
    تحقق مما إذا كان المستخدم لديه صلاحية الوصول إلى قالب معين

    المعلمات:
    - user: المستخدم المراد التحقق من صلاحياته
    - template_path: مسار القالب (مثل 'Hr/reports/monthly_salary_report.html')

    العائد:
    - True إذا كان المستخدم لديه الصلاحية، False إذا لم يكن لديه الصلاحية
    """
    # التحقق من تسجيل دخول المستخدم
    if not user.is_authenticated:
        return False

    # المستخدمون المتميزون لديهم جميع الصلاحيات
    if user.is_superuser:
        return True

    try:
        # البحث عن صلاحية القالب
        template_permission = TemplatePermission.objects.get(template_path=template_path)

        # التحقق من صلاحيات المستخدم المباشرة
        if user in template_permission.users.all():
            return True

        # التحقق من صلاحيات المجموعات
        user_groups = Group.objects.filter(user=user)
        for group in user_groups:
            if group in template_permission.groups.all():
                return True

        return False
    except TemplatePermission.DoesNotExist:
        # إذا لم يتم العثور على صلاحية القالب، فلا يوجد صلاحية
        return False

def get_user_permissions(user):
    """
    الحصول على جميع صلاحيات المستخدم

    المعلمات:
    - user: المستخدم المراد الحصول على صلاحياته

    العائد:
    - قاموس يحتوي على صلاحيات المستخدم مقسمة حسب النوع
    """
    if not user.is_authenticated:
        return {}

    # المستخدمون المتميزون لديهم جميع الصلاحيات
    if user.is_superuser:
        return {
            'has_all_permissions': True,
            'groups': Group.objects.all(),
            'departments': Department.objects.all(),
            'modules': Module.objects.all(),
            'permissions': Permission.objects.all(),
            'template_permissions': TemplatePermission.objects.all()
        }

    # الحصول على مجموعات المستخدم
    user_groups = Group.objects.filter(user=user)

    # الحصول على الأقسام المسموح بها
    departments = Department.objects.filter(
        Q(groups__in=user_groups) | Q(require_admin=False)
    ).distinct()

    # الحصول على الوحدات المسموح بها
    modules = Module.objects.filter(
        Q(groups__in=user_groups) | Q(department__in=departments, require_admin=False)
    ).distinct()

    # الحصول على الصلاحيات المباشرة والمجموعات
    permissions = Permission.objects.filter(
        Q(users=user) | Q(groups__in=user_groups)
    ).distinct()

    # الحصول على صلاحيات القوالب
    template_permissions = TemplatePermission.objects.filter(
        Q(users=user) | Q(groups__in=user_groups)
    ).distinct()

    return {
        'has_all_permissions': False,
        'groups': user_groups,
        'departments': departments,
        'modules': modules,
        'permissions': permissions,
        'template_permissions': template_permissions
    }

def get_module_permissions_matrix():
    """
    إنشاء مصفوفة بجميع الوحدات والصلاحيات المتاحة
    مفيد لعرض جدول الصلاحيات الكامل

    العائد:
    - قاموس يحتوي على مصفوفة الصلاحيات
    """
    # الحصول على جميع الأقسام والوحدات
    departments = Department.objects.all().prefetch_related('modules')

    # إنشاء بنية البيانات للمصفوفة
    matrix = []

    # إضافة كل وحدة واحدة تلو الأخرى
    for department in departments:
        department_dict = {
            'id': department.id,
            'name': department.name,
            'modules': []
        }

        for module in department.modules.all():
            module_dict = {
                'id': module.id,
                'name': module.name,
                'permissions': {}
            }

            # الحصول على صلاحيات الوحدة
            permissions = Permission.objects.filter(module=module)
            for permission in permissions:
                module_dict['permissions'][permission.permission_type] = {
                    'id': permission.id,
                    'name': permission.get_permission_type_display()
                }

            department_dict['modules'].append(module_dict)

        matrix.append(department_dict)

    return matrix

def auto_create_permissions_for_module(module_id):
    """
    إنشاء الصلاحيات تلقائياً لوحدة معينة

    المعلمات:
    - module_id: معرف الوحدة

    العائد:
    - عدد الصلاحيات التي تم إنشاؤها
    """
    try:
        module = Module.objects.get(id=module_id)
    except Module.DoesNotExist:
        return 0

    created_count = 0
    for perm_type, _ in Permission.PERMISSION_TYPES:
        # تحقق مما إذا كانت الصلاحية موجودة بالفعل
        if not Permission.objects.filter(module=module, permission_type=perm_type).exists():
            Permission.objects.create(
                module=module,
                permission_type=perm_type,
                is_active=True
            )
            created_count += 1

    return created_count

def get_unified_permission_data():
    """
    الحصول على بيانات موحدة للصلاحيات لعرضها في واجهة إدارة الصلاحيات الموحدة

    العائد:
    - قاموس يحتوي على بيانات الصلاحيات الموحدة
    """
    # الحصول على جميع المستخدمين
    users = User.objects.filter(is_active=True).order_by('username')

    # الحصول على جميع المجموعات
    groups = Group.objects.all().order_by('name')

    # الحصول على مصفوفة الصلاحيات
    permissions_matrix = get_module_permissions_matrix()

    # الحصول على صلاحيات القوالب
    template_permissions = TemplatePermission.objects.all().order_by('app_name', 'name')

    return {
        'users': users,
        'groups': groups,
        'permissions_matrix': permissions_matrix,
        'template_permissions': template_permissions
    }


def clear_permission_cache():
    """
    مسح جميع ذاكرة التخزين المؤقت المتعلقة بالصلاحيات
    """
    # مسح جميع مفاتيح التخزين المؤقت التي تبدأ بـ 'perm_'
    # ملاحظة: لا يوجد طريقة مباشرة لحذف مفاتيح بنمط معين في Django
    # لذلك نقوم بمسح التخزين المؤقت بالكامل
    cache.clear()


def clear_user_permission_cache(user_id):
    """
    مسح ذاكرة التخزين المؤقت المتعلقة بمستخدم معين

    المعلمات:
    - user_id: معرف المستخدم
    """
    # مسح جميع مفاتيح التخزين المؤقت التي تتعلق بالمستخدم
    # للأسف، لا يمكننا حذف مفاتيح محددة بنمط معين
    # لذلك نقوم بمسح التخزين المؤقت بالكامل
    cache.clear()


# إضافة مستمعي الإشارات لمسح ذاكرة التخزين المؤقت عند تغيير الصلاحيات
@receiver(post_save, sender=Permission)
@receiver(post_delete, sender=Permission)
def clear_cache_on_permission_change(sender, instance, **kwargs):
    """
    مسح ذاكرة التخزين المؤقت عند تغيير الصلاحيات
    """
    clear_permission_cache()


@receiver(m2m_changed, sender=Permission.users.through)
@receiver(m2m_changed, sender=Permission.groups.through)
def clear_cache_on_permission_m2m_change(sender, instance, action, **kwargs):
    """
    مسح ذاكرة التخزين المؤقت عند تغيير علاقات الصلاحيات
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        clear_permission_cache()


@receiver(post_save, sender=Module)
@receiver(post_delete, sender=Module)
def clear_cache_on_module_change(sender, instance, **kwargs):
    """
    مسح ذاكرة التخزين المؤقت عند تغيير الوحدات
    """
    clear_permission_cache()


@receiver(post_save, sender=Department)
@receiver(post_delete, sender=Department)
def clear_cache_on_department_change(sender, instance, **kwargs):
    """
    مسح ذاكرة التخزين المؤقت عند تغيير الأقسام
    """
    clear_permission_cache()
