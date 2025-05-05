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

        # الحصول على مجموعات المستخدم
        user_groups = Group.objects.filter(user=user)
        
        # التحقق من صلاحيات المجموعات للقسم
        # Si el departamento no requiere permisos específicos o el usuario tiene permisos a través de sus grupos
        if not department.require_admin or department.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists():
            # البحث عن الوحدة
            try:
                module = Module.objects.get(department=department, name=module_name)
                
                # التحقق من صلاحيات الوحدة
                if module.require_admin and not (user.is_staff or user.is_superuser or getattr(user, 'Role', '') == 'admin'):
                    cache.set(cache_key, False, CACHE_TIMEOUT)
                    return False
                
                # التحقق من صلاحيات المجموعات للوحدة
                # Si el módulo no requiere permisos específicos o el usuario tiene permisos a través de sus grupos
                if not module.require_admin or module.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists():
                    # البحث عن الصلاحية
                    try:
                        permission = Permission.objects.get(module=module, permission_type=permission_type)
                        
                        # التحقق من صلاحيات المستخدم المباشرة
                        if permission.users.filter(id=user.id).exists():
                            cache.set(cache_key, True, CACHE_TIMEOUT)
                            return True
                        
                        # التحقق من صلاحيات المجموعات
                        if permission.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists():
                            cache.set(cache_key, True, CACHE_TIMEOUT)
                            return True
                    except Permission.DoesNotExist:
                        # Si el permiso no existe, verificamos si el usuario es administrador del sistema
                        if user.is_staff or user.is_superuser or getattr(user, 'Role', '') == 'admin':
                            cache.set(cache_key, True, CACHE_TIMEOUT)
                            return True
            except Module.DoesNotExist:
                # Si el módulo no existe, verificamos si el usuario es administrador del sistema
                if user.is_staff or user.is_superuser or getattr(user, 'Role', '') == 'admin':
                    cache.set(cache_key, True, CACHE_TIMEOUT)
                    return True
        
        # Si llegamos aquí, el usuario no tiene permisos
        cache.set(cache_key, False, CACHE_TIMEOUT)
        return False
    except Exception as e:
        # Registrar el error para depuración
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al verificar permisos: {str(e)}")
        
        # En caso de error, devolvemos False por seguridad
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
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
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

    # إنشاء مفتاح التخزين المؤقت
    cache_key = f'perm_{user.id}_{department_name}_{module_name}_{permission_type_en}'

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

        # الحصول على مجموعات المستخدم
        user_groups = Group.objects.filter(user=user)
        
        # التحقق من صلاحيات المجموعات للقسم
        # Si el departamento no requiere permisos específicos o el usuario tiene permisos a través de sus grupos
        if not department.require_admin or department.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists():
            # البحث عن الوحدة
            try:
                module = Module.objects.get(department=department, name=module_name)
                
                # التحقق من صلاحيات الوحدة
                if module.require_admin and not (user.is_staff or user.is_superuser or getattr(user, 'Role', '') == 'admin'):
                    cache.set(cache_key, False, CACHE_TIMEOUT)
                    return False
                
                # التحقق من صلاحيات المجموعات للوحدة
                # Si el módulo no requiere permisos específicos o el usuario tiene permisos a través de sus grupos
                if not module.require_admin or module.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists():
                    # البحث عن الصلاحية
                    try:
                        permission = Permission.objects.get(module=module, permission_type=permission_type_en)
                        
                        # التحقق من صلاحيات المستخدم المباشرة
                        if permission.users.filter(id=user.id).exists():
                            cache.set(cache_key, True, CACHE_TIMEOUT)
                            return True
                        
                        # التحقق من صلاحيات المجموعات
                        if permission.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists():
                            cache.set(cache_key, True, CACHE_TIMEOUT)
                            return True
                    except Permission.DoesNotExist:
                        # Si el permiso no existe, verificamos si el usuario es administrador del sistema
                        if user.is_staff or user.is_superuser or getattr(user, 'Role', '') == 'admin':
                            cache.set(cache_key, True, CACHE_TIMEOUT)
                            return True
            except Module.DoesNotExist:
                # Si el módulo no existe, verificamos si el usuario es administrador del sistema
                if user.is_staff or user.is_superuser or getattr(user, 'Role', '') == 'admin':
                    cache.set(cache_key, True, CACHE_TIMEOUT)
                    return True
        
        # Si llegamos aquí, el usuario no tiene permisos
        cache.set(cache_key, False, CACHE_TIMEOUT)
        return False
    except Exception as e:
        # Registrar el error para depuración
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al verificar permisos: {str(e)}")
        
        # En caso de error, devolvemos False por seguridad
        cache.set(cache_key, False, CACHE_TIMEOUT)
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
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True

    # إنشاء مفتاح التخزين المؤقت
    cache_key = f'template_perm_{user.id}_{template_path}'

    # محاولة الحصول على النتيجة من التخزين المؤقت
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        # البحث عن صلاحية القالب
        template_permission = TemplatePermission.objects.get(template_path=template_path)

        # التحقق من صلاحيات المستخدم المباشرة
        if template_permission.users.filter(id=user.id).exists():
            cache.set(cache_key, True, CACHE_TIMEOUT)
            return True

        # التحقق من صلاحيات المجموعات
        user_groups = Group.objects.filter(user=user)
        if template_permission.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists():
            cache.set(cache_key, True, CACHE_TIMEOUT)
            return True

        # Si llegamos aquí, el usuario no tiene permisos
        cache.set(cache_key, False, CACHE_TIMEOUT)
        return False
    except TemplatePermission.DoesNotExist:
        # إذا لم يتم العثور على صلاحية القالب، فلا يوجد صلاحية
        cache.set(cache_key, False, CACHE_TIMEOUT)
        return False
    except Exception as e:
        # Registrar el error para depuración
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al verificar permisos de plantilla: {str(e)}")
        
        # En caso de error, devolvemos False por seguridad
        cache.set(cache_key, False, CACHE_TIMEOUT)
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

    # إنشاء مفتاح التخزين المؤقت
    cache_key = f'user_permissions_{user.id}'

    # محاولة الحصول على النتيجة من التخزين المؤقت
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        # المستخدمون المتميزون لديهم جميع الصلاحيات
        if user.is_superuser or getattr(user, 'Role', '') == 'admin':
            result = {
                'has_all_permissions': True,
                'groups': Group.objects.all(),
                'departments': Department.objects.all(),
                'modules': Module.objects.all(),
                'permissions': Permission.objects.all(),
                'template_permissions': TemplatePermission.objects.all()
            }
            cache.set(cache_key, result, CACHE_TIMEOUT)
            return result

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
            Q(users=user) | Q(groups__in=user_groups),
            module__in=modules  # Asegurarse de que solo se incluyan permisos para módulos permitidos
        ).distinct()

        # الحصول على صلاحيات القوالب
        template_permissions = TemplatePermission.objects.filter(
            Q(users=user) | Q(groups__in=user_groups)
        ).distinct()

        # Organizar permisos por tipo para facilitar su uso
        permissions_by_type = {
            'view': permissions.filter(permission_type='view'),
            'add': permissions.filter(permission_type='add'),
            'change': permissions.filter(permission_type='change'),
            'delete': permissions.filter(permission_type='delete'),
            'print': permissions.filter(permission_type='print')
        }

        # Organizar permisos por módulo para facilitar su uso
        permissions_by_module = {}
        for module in modules:
            module_perms = {
                'view': permissions.filter(module=module, permission_type='view').exists(),
                'add': permissions.filter(module=module, permission_type='add').exists(),
                'change': permissions.filter(module=module, permission_type='change').exists(),
                'delete': permissions.filter(module=module, permission_type='delete').exists(),
                'print': permissions.filter(module=module, permission_type='print').exists()
            }
            permissions_by_module[module.id] = module_perms

        result = {
            'has_all_permissions': False,
            'groups': user_groups,
            'departments': departments,
            'modules': modules,
            'permissions': permissions,
            'permissions_by_type': permissions_by_type,
            'permissions_by_module': permissions_by_module,
            'template_permissions': template_permissions
        }
        
        cache.set(cache_key, result, CACHE_TIMEOUT)
        return result
    except Exception as e:
        # Registrar el error para depuración
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al obtener permisos de usuario: {str(e)}")
        
        # En caso de error, devolvemos un diccionario vacío
        return {
            'has_all_permissions': False,
            'groups': [],
            'departments': [],
            'modules': [],
            'permissions': [],
            'permissions_by_type': {},
            'permissions_by_module': {},
            'template_permissions': []
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
    # Registrar la operación para depuración
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Limpiando caché de permisos")
    
    try:
        # Intentar usar el método de caché específico si está disponible
        if hasattr(cache, 'delete_pattern'):
            # Algunos backends como redis-cache soportan delete_pattern
            cache.delete_pattern('perm_*')
            cache.delete_pattern('template_perm_*')
            cache.delete_pattern('user_permissions_*')
        else:
            # Si no hay soporte para patrones, limpiar todo el caché
            cache.clear()
        
        logger.info("Caché de permisos limpiado correctamente")
    except Exception as e:
        logger.error(f"Error al limpiar caché de permisos: {str(e)}")
        # En caso de error, intentar limpiar todo el caché
        try:
            cache.clear()
        except:
            pass


def clear_user_permission_cache(user_id):
    """
    مسح ذاكرة التخزين المؤقت المتعلقة بمستخدم معين

    المعلمات:
    - user_id: معرف المستخدم
    """
    # Registrar la operación para depuración
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Limpiando caché de permisos para usuario {user_id}")
    
    try:
        # Intentar usar el método de caché específico si está disponible
        if hasattr(cache, 'delete_pattern'):
            # Algunos backends como redis-cache soportan delete_pattern
            cache.delete_pattern(f'perm_{user_id}_*')
            cache.delete_pattern(f'template_perm_{user_id}_*')
            cache.delete(f'user_permissions_{user_id}')
        else:
            # Si no hay soporte para patrones, eliminar claves específicas
            # Eliminar el caché de permisos de usuario
            cache.delete(f'user_permissions_{user_id}')
            
            # Para el resto, necesitamos limpiar todo el caché
            cache.clear()
        
        logger.info(f"Caché de permisos para usuario {user_id} limpiado correctamente")
    except Exception as e:
        logger.error(f"Error al limpiar caché de permisos para usuario {user_id}: {str(e)}")
        # En caso de error, intentar limpiar todo el caché
        try:
            cache.clear()
        except:
            pass


def clear_group_permission_cache(group_id):
    """
    مسح ذاكرة التخزين المؤقت المتعلقة بمجموعة معينة

    المعلمات:
    - group_id: معرف المجموعة
    """
    # Registrar la operación para depuración
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Limpiando caché de permisos para grupo {group_id}")
    
    try:
        # Obtener usuarios en el grupo
        from django.contrib.auth.models import Group, User
        try:
            group = Group.objects.get(id=group_id)
            users = User.objects.filter(groups=group)
            
            # Limpiar caché para cada usuario en el grupo
            for user in users:
                clear_user_permission_cache(user.id)
        except Group.DoesNotExist:
            pass
        
        # Limpiar caché general de permisos
        clear_permission_cache()
        
        logger.info(f"Caché de permisos para grupo {group_id} limpiado correctamente")
    except Exception as e:
        logger.error(f"Error al limpiar caché de permisos para grupo {group_id}: {str(e)}")
        # En caso de error, intentar limpiar todo el caché
        try:
            cache.clear()
        except:
            pass


# إضافة مستمعي الإشارات لمسح ذاكرة التخزين المؤقت عند تغيير الصلاحيات
@receiver(post_save, sender=Permission)
@receiver(post_delete, sender=Permission)
def clear_cache_on_permission_change(sender, instance, **kwargs):
    """
    مسح ذاكرة التخزين المؤقت عند تغيير الصلاحيات
    """
    clear_permission_cache()


@receiver(m2m_changed, sender=Permission.users.through)
def clear_cache_on_permission_users_change(sender, instance, action, pk_set, **kwargs):
    """
    مسح ذاكرة التخزين المؤقت عند تغيير علاقات المستخدمين بالصلاحيات
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Limpiar caché para cada usuario afectado
        if pk_set:
            for user_id in pk_set:
                clear_user_permission_cache(user_id)
        else:
            # Si no hay pk_set, limpiar todo el caché de permisos
            clear_permission_cache()


@receiver(m2m_changed, sender=Permission.groups.through)
def clear_cache_on_permission_groups_change(sender, instance, action, pk_set, **kwargs):
    """
    مسح ذاكرة التخزين المؤقت عند تغيير علاقات المجموعات بالصلاحيات
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Limpiar caché para cada grupo afectado
        if pk_set:
            for group_id in pk_set:
                clear_group_permission_cache(group_id)
        else:
            # Si no hay pk_set, limpiar todo el caché de permisos
            clear_permission_cache()


@receiver(m2m_changed, sender=TemplatePermission.users.through)
def clear_cache_on_template_permission_users_change(sender, instance, action, pk_set, **kwargs):
    """
    مسح ذاكرة التخزين المؤقت عند تغيير علاقات المستخدمين بصلاحيات القوالب
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Limpiar caché para cada usuario afectado
        if pk_set:
            for user_id in pk_set:
                clear_user_permission_cache(user_id)
        else:
            # Si no hay pk_set, limpiar todo el caché de permisos
            clear_permission_cache()


@receiver(m2m_changed, sender=TemplatePermission.groups.through)
def clear_cache_on_template_permission_groups_change(sender, instance, action, pk_set, **kwargs):
    """
    مسح ذاكرة التخزين المؤقت عند تغيير علاقات المجموعات بصلاحيات القوالب
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Limpiar caché para cada grupo afectado
        if pk_set:
            for group_id in pk_set:
                clear_group_permission_cache(group_id)
        else:
            # Si no hay pk_set, limpiar todo el caché de permisos
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


@receiver(m2m_changed, sender=Department.groups.through)
def clear_cache_on_department_groups_change(sender, instance, action, pk_set, **kwargs):
    """
    مسح ذاكرة التخزين المؤقت عند تغيير علاقات المجموعات بالأقسام
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Limpiar caché para cada grupo afectado
        if pk_set:
            for group_id in pk_set:
                clear_group_permission_cache(group_id)
        else:
            # Si no hay pk_set, limpiar todo el caché de permisos
            clear_permission_cache()


@receiver(m2m_changed, sender=Module.groups.through)
def clear_cache_on_module_groups_change(sender, instance, action, pk_set, **kwargs):
    """
    مسح ذاكرة التخزين المؤقت عند تغيير علاقات المجموعات بالوحدات
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Limpiar caché para cada grupo afectado
        if pk_set:
            for group_id in pk_set:
                clear_group_permission_cache(group_id)
        else:
            # Si no hay pk_set, limpiar todo el caché de permisos
            clear_permission_cache()


@receiver(m2m_changed, sender=User.groups.through)
def clear_cache_on_user_groups_change(sender, instance, action, pk_set, **kwargs):
    """
    مسح ذاكرة التخزين المؤقت عند تغيير مجموعات المستخدم
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Si instance es un usuario, limpiar su caché
        if isinstance(instance, User):
            clear_user_permission_cache(instance.id)
        # Si instance es un grupo, limpiar el caché para todos los usuarios en ese grupo
        elif isinstance(instance, Group) and pk_set:
            for user_id in pk_set:
                clear_user_permission_cache(user_id)
        else:
            # Si no podemos determinar, limpiar todo el caché
            clear_permission_cache()
