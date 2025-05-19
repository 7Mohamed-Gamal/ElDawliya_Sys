from django.contrib.auth.models import Group, Permission as DjangoPermission
from django.db.models import Q, Prefetch
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import Department, Module

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
        if not department.require_admin or department.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists():
            # البحث عن الوحدة
            try:
                module = Module.objects.get(department=department, name=module_name)
                
                # التحقق من صلاحيات الوحدة
                if module.require_admin and not (user.is_staff or user.is_superuser or getattr(user, 'Role', '') == 'admin'):
                    cache.set(cache_key, False, CACHE_TIMEOUT)
                    return False
                
                # التحقق من صلاحيات المجموعات للوحدة
                if not module.require_admin or module.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists():
                    # استخدام صلاحيات Django المدمجة بدلاً من نموذج Permission المخصص
                    # إنشاء اسم صلاحية بناءً على معيار Django: app_label.permission_type_model
                    
                    # الحصول على اسم التطبيق من القسم
                    app_label = department.url_name.lower() if department.url_name else department.name.lower()
                    # تبسيط اسم الوحدة (إزالة المسافات والأحرف الخاصة)
                    model_name = module.name.lower().replace(' ', '_')
                    
                    # بناء اسم الصلاحية: app_label.permission_type_modelname
                    permission_codename = f"{permission_type}_{model_name}"
                    django_permission = f"{app_label}.{permission_codename}"
                    
                    # التحقق من صلاحية المستخدم
                    has_perm = user.has_perm(django_permission)
                    
                    # التحقق من صلاحيات المجموعات
                    if not has_perm:
                        for group in user_groups:
                            perms = DjangoPermission.objects.filter(
                                content_type__app_label=app_label,
                                codename=permission_codename,
                                group=group
                            ).exists()
                            if perms:
                                has_perm = True
                                break
                    
                    cache.set(cache_key, has_perm, CACHE_TIMEOUT)
                    return has_perm
                    
            except Module.DoesNotExist:
                # إذا لم يتم العثور على الوحدة، نتحقق من كون المستخدم مدير للنظام
                if user.is_staff or user.is_superuser or getattr(user, 'Role', '') == 'admin':
                    cache.set(cache_key, True, CACHE_TIMEOUT)
                    return True
        
        # إذا وصلنا إلى هنا، فليس لدى المستخدم الصلاحية المطلوبة
        cache.set(cache_key, False, CACHE_TIMEOUT)
        return False
    except Exception as e:
        # تسجيل الخطأ للتصحيح
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error checking permissions: {str(e)}")
        
        # في حالة الخطأ، نُرجع False للأمان
        cache.set(cache_key, False, CACHE_TIMEOUT)
        return False

def has_permission(user, permission_name):
    """
    تحقق مما إذا كان المستخدم لديه صلاحية معينة باستخدام نظام Django الأساسي
    
    المعلمات:
    - user: المستخدم المراد التحقق من صلاحياته
    - permission_name: اسم الصلاحية مثل 'app_label.permission_name'
    
    العائد:
    - True إذا كان المستخدم لديه الصلاحية، False إذا لم يكن لديه الصلاحية
    """
    # التحقق من تسجيل دخول المستخدم
    if not user.is_authenticated:
        return False

    # المستخدمون المتميزون لديهم جميع الصلاحيات
    if user.is_superuser or getattr(user, 'Role', '') == 'admin':
        return True
    
    # استخدام نظام صلاحيات Django الأساسي
    return user.has_perm(permission_name)

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


# Signals related to Department and Module changes
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
