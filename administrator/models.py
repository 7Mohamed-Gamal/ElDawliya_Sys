from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

User = get_user_model()

# Try to import audit models
try:
    from .models_audit import PermissionAuditLog
    HAS_AUDIT = True
except ImportError:
    HAS_AUDIT = False

class SystemSettings(models.Model):
    """
    System-wide settings that can be configured by the administrator.
    Only one instance of this model should exist (singleton).
    """
    # Database Settings
    db_host = models.CharField(max_length=255, verbose_name="قاعدة البيانات - المضيف")
    db_name = models.CharField(max_length=255, verbose_name="قاعدة البيانات - الاسم")
    db_user = models.CharField(max_length=255, verbose_name="قاعدة البيانات - اسم المستخدم")
    db_password = models.CharField(max_length=255, verbose_name="قاعدة البيانات - كلمة المرور")
    db_port = models.CharField(max_length=10, default='1433', verbose_name="قاعدة البيانات - المنفذ")

    # Company Information
    company_name = models.CharField(max_length=255, verbose_name="اسم الشركة")
    company_address = models.TextField(blank=True, verbose_name="عنوان الشركة")
    company_phone = models.CharField(max_length=50, blank=True, verbose_name="هاتف الشركة")
    company_email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني للشركة")
    company_website = models.URLField(blank=True, verbose_name="موقع الشركة الإلكتروني")
    company_logo = models.ImageField(upload_to='company/', blank=True, null=True, verbose_name="شعار الشركة")

    # System Configuration
    system_name = models.CharField(max_length=255, default="نظام الدولية", verbose_name="اسم النظام")
    enable_debugging = models.BooleanField(default=False, verbose_name="تفعيل وضع التصحيح")
    maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة")

    # Date and timezone settings
    timezone = models.CharField(max_length=50, default="Asia/Riyadh", verbose_name="المنطقة الزمنية")
    date_format = models.CharField(max_length=50, default="Y-m-d", verbose_name="تنسيق التاريخ")

    # Language and UI Settings
    LANGUAGE_CHOICES = [
        ('ar', 'العربية'),
        ('en', 'English'),
    ]

    FONT_CHOICES = [
        ('cairo', 'Cairo'),
        ('tajawal', 'Tajawal'),
        ('almarai', 'Almarai'),
        ('ibm-plex-sans-arabic', 'IBM Plex Sans Arabic'),
        ('noto-sans-arabic', 'Noto Sans Arabic'),
    ]

    DIRECTION_CHOICES = [
        ('rtl', 'من اليمين إلى اليسار'),
        ('ltr', 'من اليسار إلى اليمين'),
    ]

    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='ar',
        verbose_name=_('لغة النظام')
    )

    font_family = models.CharField(
        max_length=50,
        choices=FONT_CHOICES,
        default='cairo',
        verbose_name=_('الخط المستخدم')
    )

    text_direction = models.CharField(
        max_length=3,
        choices=DIRECTION_CHOICES,
        default='rtl',
        verbose_name=_('اتجاه النص')
    )

    # Last modified
    last_modified = models.DateTimeField(auto_now=True, verbose_name="آخر تعديل")

    def __str__(self):
        return "إعدادات النظام"

    class Meta:
        verbose_name = "إعدادات النظام"
        verbose_name_plural = "إعدادات النظام"

    @classmethod
    def get_settings(cls):
        settings = cls.objects.first()
        if not settings:
            settings = cls.objects.create()
        return settings


class Department(models.Model):
    """
    Departments that appear in the sidebar navigation.
    """
    name = models.CharField(max_length=100, verbose_name="اسم القسم")
    icon = models.CharField(max_length=50, verbose_name="أيقونة القسم",
                           help_text="اسم الأيقونة من Font Awesome مثال: fa-user")
    url_name = models.CharField(max_length=100, verbose_name="اسم الرابط",
                               help_text="الاسم المستخدم في الروابط")
    description = models.CharField(max_length=255, blank=True, verbose_name="وصف القسم")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    require_admin = models.BooleanField(default=False, verbose_name="يتطلب صلاحيات المدير")
    groups = models.ManyToManyField(Group, blank=True, related_name='allowed_departments', verbose_name="المجموعات المسموح لها")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "القسم"
        verbose_name_plural = "الأقسام"
        ordering = ['order']


class Module(models.Model):
    """
    Modules (features/links) available within each department.
    """
    department = models.ForeignKey(Department, on_delete=models.CASCADE,
                                  related_name='modules', verbose_name="القسم")
    name = models.CharField(max_length=100, verbose_name="اسم الوحدة")
    icon = models.CharField(max_length=50, verbose_name="أيقونة الوحدة")
    url = models.CharField(max_length=255, verbose_name="رابط الوحدة")
    description = models.CharField(max_length=255, blank=True, verbose_name="وصف الوحدة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    bg_color = models.CharField(max_length=20, default="#3498db", verbose_name="لون الخلفية")
    require_admin = models.BooleanField(default=False, verbose_name="يتطلب صلاحيات المدير")
    groups = models.ManyToManyField(Group, blank=True, related_name='allowed_modules', verbose_name="المجموعات المسموح لها")

    def __str__(self):
        return f"{self.department.name} - {self.name}"

    class Meta:
        verbose_name = "الوحدة"
        verbose_name_plural = "الوحدات"
        ordering = ['department__order', 'order']


class Permission(models.Model):
    """
    CRUD permissions for modules in the system
    """
    PERMISSION_TYPES = [
        ('view', 'عرض'),
        ('add', 'إضافة'),
        ('change', 'تعديل'),
        ('delete', 'حذف'),
        ('print', 'طباعة'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE,
                              related_name='permissions', verbose_name="الوحدة")
    permission_type = models.CharField(max_length=10, choices=PERMISSION_TYPES, verbose_name="نوع الصلاحية")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    groups = models.ManyToManyField(Group, blank=True, related_name='custom_permissions', verbose_name="المجموعات المسموح لها")
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                  related_name='custom_permissions', verbose_name="المستخدمين المسموح لهم")

    def __str__(self):
        return f"{self.module.name} - {self.get_permission_type_display()}"

    class Meta:
        verbose_name = "الصلاحية"
        verbose_name_plural = "الصلاحيات"
        unique_together = ['module', 'permission_type']


class TemplatePermission(models.Model):
    """
    Permissions to access specific templates/views in the system
    """
    name = models.CharField(max_length=100, verbose_name="اسم القالب")
    app_name = models.CharField(max_length=50, verbose_name="اسم التطبيق")
    template_path = models.CharField(max_length=255, verbose_name="مسار القالب")
    url_pattern = models.CharField(max_length=255, verbose_name="نمط URL", blank=True)
    description = models.TextField(blank=True, verbose_name="وصف")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    groups = models.ManyToManyField(Group, blank=True,
                                  related_name='template_permissions', verbose_name="المجموعات المسموح لها")
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                 related_name='template_permissions', verbose_name="المستخدمين المسموح لهم")

    def __str__(self):
        return f"{self.app_name} - {self.name}"

    class Meta:
        verbose_name = "صلاحية قالب"
        verbose_name_plural = "صلاحيات القوالب"
        ordering = ['app_name', 'name']


class GroupProfile(models.Model):
    """
    Extension model for the Group model to add additional fields
    """
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='profile', verbose_name="المجموعة")
    description = models.TextField(blank=True, verbose_name="وصف المجموعة")

    def __str__(self):
        return f"Profile for {self.group.name}"

    class Meta:
        verbose_name = "ملف المجموعة"
        verbose_name_plural = "ملفات المجموعات"


class UserGroup(models.Model):
    """
    Bridge model to store information about user's membership in a group
    with additional metadata
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                           related_name='group_memberships', verbose_name="المستخدم")
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                            related_name='user_memberships', verbose_name="المجموعة")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الانضمام")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"

    class Meta:
        verbose_name = "عضوية مجموعة"
        verbose_name_plural = "عضويات المجموعات"
        unique_together = ['user', 'group']


class UserDepartmentPermission(models.Model):
    """صلاحيات المستخدمين للأقسام"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="department_permissions", verbose_name="المستخدم")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="القسم")
    can_view = models.BooleanField(default=True, verbose_name="عرض")

    def __str__(self):
        return f"{self.user.username} - {self.department.name}"

    class Meta:
        verbose_name = "صلاحية قسم"
        verbose_name_plural = "صلاحيات الأقسام"
        unique_together = ('user', 'department')


class UserModulePermission(models.Model):
    """صلاحيات المستخدمين للوحدات"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="module_permissions", verbose_name="المستخدم")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, verbose_name="الوحدة")
    can_view = models.BooleanField(default=True, verbose_name="عرض")
    can_add = models.BooleanField(default=False, verbose_name="إضافة")
    can_edit = models.BooleanField(default=False, verbose_name="تعديل")
    can_delete = models.BooleanField(default=False, verbose_name="حذف")
    can_print = models.BooleanField(default=False, verbose_name="طباعة")

    def __str__(self):
        return f"{self.user.username} - {self.module.name}"

    class Meta:
        verbose_name = "صلاحية وحدة"
        verbose_name_plural = "صلاحيات الوحدات"
        unique_together = ('user', 'module')


# Signal handlers for audit logging
if HAS_AUDIT:
    @receiver(post_save, sender=Permission)
    def log_permission_save(sender, instance, created, **kwargs):
        """Log when a permission is created or updated"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get the current user from the thread local storage if available
        try:
            from threading import local
            _thread_locals = local()
            user = getattr(_thread_locals, 'user', None)
        except (ImportError, AttributeError):
            user = None

        # If we couldn't get the user, use a system user
        if not user:
            user, _ = User.objects.get_or_create(username='system')

        action = 'add' if created else 'modify'
        description = f"{'إنشاء' if created else 'تعديل'} صلاحية {instance.get_permission_type_display()} لوحدة {instance.module.name}"

        PermissionAuditLog.log_permission_change(
            user=user,
            action=action,
            obj=instance,
            description=description
        )

    @receiver(post_delete, sender=Permission)
    def log_permission_delete(sender, instance, **kwargs):
        """Log when a permission is deleted"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get the current user from the thread local storage if available
        try:
            from threading import local
            _thread_locals = local()
            user = getattr(_thread_locals, 'user', None)
        except (ImportError, AttributeError):
            user = None

        # If we couldn't get the user, use a system user
        if not user:
            user, _ = User.objects.get_or_create(username='system')

        description = f"حذف صلاحية {instance.get_permission_type_display()} لوحدة {instance.module.name}"

        PermissionAuditLog.log_permission_change(
            user=user,
            action='remove',
            obj=instance,
            description=description
        )

    @receiver(m2m_changed, sender=Permission.users.through)
    def log_permission_users_change(sender, instance, action, pk_set, **kwargs):
        """Log when users are added to or removed from a permission"""
        if action not in ['post_add', 'post_remove']:
            return

        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get the current user from the thread local storage if available
        try:
            from threading import local
            _thread_locals = local()
            user = getattr(_thread_locals, 'user', None)
        except (ImportError, AttributeError):
            user = None

        # If we couldn't get the user, use a system user
        if not user:
            user, _ = User.objects.get_or_create(username='system')

        # Get the affected users
        affected_users = User.objects.filter(pk__in=pk_set)
        usernames = ', '.join([u.username for u in affected_users])

        if action == 'post_add':
            description = f"إضافة مستخدمين ({usernames}) إلى صلاحية {instance.get_permission_type_display()} لوحدة {instance.module.name}"
            audit_action = 'add'
        else:  # post_remove
            description = f"إزالة مستخدمين ({usernames}) من صلاحية {instance.get_permission_type_display()} لوحدة {instance.module.name}"
            audit_action = 'remove'

        PermissionAuditLog.log_permission_change(
            user=user,
            action=audit_action,
            obj=instance,
            description=description,
            data={'users': list(pk_set)}
        )

    @receiver(m2m_changed, sender=Permission.groups.through)
    def log_permission_groups_change(sender, instance, action, pk_set, **kwargs):
        """Log when groups are added to or removed from a permission"""
        if action not in ['post_add', 'post_remove']:
            return

        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get the current user from the thread local storage if available
        try:
            from threading import local
            _thread_locals = local()
            user = getattr(_thread_locals, 'user', None)
        except (ImportError, AttributeError):
            user = None

        # If we couldn't get the user, use a system user
        if not user:
            user, _ = User.objects.get_or_create(username='system')

        # Get the affected groups
        affected_groups = Group.objects.filter(pk__in=pk_set)
        group_names = ', '.join([g.name for g in affected_groups])

        if action == 'post_add':
            description = f"إضافة مجموعات ({group_names}) إلى صلاحية {instance.get_permission_type_display()} لوحدة {instance.module.name}"
            audit_action = 'add'
        else:  # post_remove
            description = f"إزالة مجموعات ({group_names}) من صلاحية {instance.get_permission_type_display()} لوحدة {instance.module.name}"
            audit_action = 'remove'

        PermissionAuditLog.log_permission_change(
            user=user,
            action=audit_action,
            obj=instance,
            description=description,
            data={'groups': list(pk_set)}
        )
