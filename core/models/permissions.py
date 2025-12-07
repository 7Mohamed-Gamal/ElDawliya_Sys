"""
Hierarchical Permissions System Models
نماذج نظام الصلاحيات الهرمي

This module provides a comprehensive hierarchical permissions system
that supports module-based, role-based, and object-level permissions.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.conf import settings

User = get_user_model()


class Module(models.Model):
    """
    System modules for permission organization
    وحدات النظام لتنظيم الصلاحيات
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name=_('اسم الوحدة'))
    display_name = models.CharField(max_length=200, verbose_name=_('الاسم المعروض'))
    description = models.TextField(blank=True, verbose_name=_('الوصف'))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_('الأيقونة'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('الترتيب'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('الوحدة الأب')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        """Meta class"""
        verbose_name = _('وحدة النظام')
        verbose_name_plural = _('وحدات النظام')
        ordering = ['order', 'display_name']

    def __str__(self):
        """__str__ function"""
        return self.display_name

    def get_full_path(self):
        """Get full hierarchical path of the module"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.display_name}"
        return self.display_name

    def get_all_children(self):
        """Get all child modules recursively"""
        children = list(self.children.filter(is_active=True))
        for child in list(children):
            children.extend(child.get_all_children())
        return children


class Permission(models.Model):
    """
    Detailed permissions for modules
    الصلاحيات المفصلة للوحدات
    """
    PERMISSION_TYPES = [
        ('view', _('عرض')),
        ('add', _('إضافة')),
        ('change', _('تعديل')),
        ('delete', _('حذف')),
        ('approve', _('موافقة')),
        ('reject', _('رفض')),
        ('export', _('تصدير')),
        ('import', _('استيراد')),
        ('print', _('طباعة')),
        ('manage', _('إدارة كاملة')),
        ('admin', _('إدارة النظام')),
    ]

    SCOPE_CHOICES = [
        ('global', _('عام')),
        ('department', _('القسم')),
        ('team', _('الفريق')),
        ('personal', _('شخصي')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='permissions')
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES, verbose_name=_('نوع الصلاحية'))
    codename = models.CharField(max_length=100, verbose_name=_('الرمز'))
    name = models.CharField(max_length=200, verbose_name=_('الاسم'))
    description = models.TextField(blank=True, verbose_name=_('الوصف'))
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='global', verbose_name=_('النطاق'))
    is_sensitive = models.BooleanField(default=False, verbose_name=_('حساس'))
    requires_approval = models.BooleanField(default=False, verbose_name=_('يتطلب موافقة'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))

    class Meta:
        """Meta class"""
        verbose_name = _('صلاحية')
        verbose_name_plural = _('الصلاحيات')
        unique_together = ['module', 'codename']
        ordering = ['module__order', 'permission_type']

    def __str__(self):
        """__str__ function"""
        return f"{self.module.display_name} - {self.name}"

    @property
    def full_codename(self):
        """Get full permission codename"""
        return f"{self.module.name}.{self.codename}"


class Role(models.Model):
    """
    User roles with hierarchical permissions
    أدوار المستخدمين مع الصلاحيات الهرمية
    """
    ROLE_TYPES = [
        ('system', _('نظام')),
        ('department', _('قسم')),
        ('custom', _('مخصص')),
        ('temporary', _('مؤقت')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name=_('اسم الدور'))
    display_name = models.CharField(max_length=200, verbose_name=_('الاسم المعروض'))
    description = models.TextField(blank=True, verbose_name=_('الوصف'))
    role_type = models.CharField(max_length=20, choices=ROLE_TYPES, default='custom', verbose_name=_('نوع الدور'))
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles', verbose_name=_('الصلاحيات'))
    parent_role = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='child_roles',
        verbose_name=_('الدور الأب')
    )
    is_system_role = models.BooleanField(default=False, verbose_name=_('دور النظام'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    max_users = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('الحد الأقصى للمستخدمين'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        """Meta class"""
        verbose_name = _('دور')
        verbose_name_plural = _('الأدوار')
        ordering = ['display_name']

    def __str__(self):
        """__str__ function"""
        return self.display_name

    def get_all_permissions(self):
        """Get all permissions including inherited from parent roles"""
        permissions = set(self.permissions.filter(is_active=True))

        if self.parent_role:
            permissions.update(self.parent_role.get_all_permissions())

        return permissions

    def get_users_count(self):
        """Get count of users assigned to this role"""
        return self.user_roles.filter(is_active=True).count()

    def can_assign_more_users(self):
        """Check if more users can be assigned to this role"""
        if not self.max_users:
            return True
        return self.get_users_count() < self.max_users


class UserRole(models.Model):
    """
    User role assignments with time-based and conditional access
    تعيينات أدوار المستخدمين مع الوصول المؤقت والمشروط
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_roles', verbose_name=_('المستخدم'))
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles', verbose_name=_('الدور'))
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='granted_roles',
        verbose_name=_('منح بواسطة')
    )
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ المنح'))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الانتهاء'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    conditions = models.JSONField(default=dict, blank=True, verbose_name=_('الشروط'))
    notes = models.TextField(blank=True, verbose_name=_('ملاحظات'))

    class Meta:
        """Meta class"""
        verbose_name = _('دور المستخدم')
        verbose_name_plural = _('أدوار المستخدمين')
        unique_together = ['user', 'role']
        ordering = ['-granted_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.user.username} - {self.role.display_name}"

    def is_expired(self):
        """Check if role assignment is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def is_valid(self):
        """Check if role assignment is valid"""
        return self.is_active and not self.is_expired()


class ObjectPermission(models.Model):
    """
    Object-level permissions for fine-grained access control
    صلاحيات على مستوى الكائن للتحكم الدقيق في الوصول
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='object_permissions', verbose_name=_('المستخدم'))
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name=_('الصلاحية'))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_('نوع المحتوى'))
    object_id = models.CharField(max_length=255, verbose_name=_('معرف الكائن'))
    content_object = GenericForeignKey('content_type', 'object_id')
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='granted_object_permissions',
        verbose_name=_('منح بواسطة')
    )
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ المنح'))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الانتهاء'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))

    class Meta:
        """Meta class"""
        verbose_name = _('صلاحية الكائن')
        verbose_name_plural = _('صلاحيات الكائنات')
        unique_together = ['user', 'permission', 'content_type', 'object_id']
        ordering = ['-granted_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.user.username} - {self.permission.name} - {self.content_object}"

    def is_expired(self):
        """Check if object permission is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def is_valid(self):
        """Check if object permission is valid"""
        return self.is_active and not self.is_expired()


class ApprovalWorkflow(models.Model):
    """
    Multi-level approval workflow for sensitive operations
    سير عمل الموافقات متعددة المستويات للعمليات الحساسة
    """
    WORKFLOW_TYPES = [
        ('permission_grant', _('منح صلاحية')),
        ('role_assignment', _('تعيين دور')),
        ('data_export', _('تصدير البيانات')),
        ('user_creation', _('إنشاء مستخدم')),
        ('system_config', _('تكوين النظام')),
    ]

    STATUS_CHOICES = [
        ('pending', _('في الانتظار')),
        ('approved', _('موافق عليه')),
        ('rejected', _('مرفوض')),
        ('cancelled', _('ملغي')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_type = models.CharField(max_length=50, choices=WORKFLOW_TYPES, verbose_name=_('نوع سير العمل'))
    title = models.CharField(max_length=200, verbose_name=_('العنوان'))
    description = models.TextField(verbose_name=_('الوصف'))
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_approvals',
        verbose_name=_('طلب بواسطة')
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='target_approvals',
        verbose_name=_('المستخدم المستهدف')
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))
    data = models.JSONField(default=dict, verbose_name=_('البيانات'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        """Meta class"""
        verbose_name = _('سير عمل الموافقة')
        verbose_name_plural = _('سير عمل الموافقات')
        ordering = ['-created_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.title} - {self.get_status_display()}"

    def get_current_approvers(self):
        """Get users who need to approve at current level"""
        current_level = self.approval_steps.filter(
            status='pending'
        ).order_by('level').first()

        if current_level:
            return current_level.approvers.all()
        return User.objects.none()

    def can_approve(self, user):
        """Check if user can approve at current level"""
        return user in self.get_current_approvers()


class ApprovalStep(models.Model):
    """
    Individual approval steps in workflow
    خطوات الموافقة الفردية في سير العمل
    """
    STATUS_CHOICES = [
        ('pending', _('في الانتظار')),
        ('approved', _('موافق عليه')),
        ('rejected', _('مرفوض')),
        ('skipped', _('تم تخطيه')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name='approval_steps',
        verbose_name=_('سير العمل')
    )
    level = models.PositiveIntegerField(verbose_name=_('المستوى'))
    name = models.CharField(max_length=200, verbose_name=_('الاسم'))
    approvers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='approval_steps', verbose_name=_('المعتمدون'))
    requires_all = models.BooleanField(default=False, verbose_name=_('يتطلب الجميع'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_steps',
        verbose_name=_('اعتمد بواسطة')
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الاعتماد'))
    comments = models.TextField(blank=True, verbose_name=_('التعليقات'))

    class Meta:
        """Meta class"""
        verbose_name = _('خطوة الموافقة')
        verbose_name_plural = _('خطوات الموافقة')
        unique_together = ['workflow', 'level']
        ordering = ['level']

    def __str__(self):
        """__str__ function"""
        return f"{self.workflow.title} - المستوى {self.level}"


class PermissionCache(models.Model):
    """
    Cache for computed permissions to improve performance
    ذاكرة التخزين المؤقت للصلاحيات المحسوبة لتحسين الأداء
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='permission_cache')
    permission_hash = models.CharField(max_length=64, verbose_name=_('هاش الصلاحية'))
    permissions_data = models.JSONField(verbose_name=_('بيانات الصلاحيات'))
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name=_('تاريخ الانتهاء'))

    class Meta:
        """Meta class"""
        verbose_name = _('ذاكرة تخزين الصلاحيات')
        verbose_name_plural = _('ذاكرة تخزين الصلاحيات')
        unique_together = ['user', 'permission_hash']
        ordering = ['-created_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.user.username} - {self.permission_hash[:8]}"

    def is_expired(self):
        """Check if cache entry is expired"""
        return timezone.now() > self.expires_at

    @classmethod
    def get_user_permissions(cls, user, permission_hash):
        """Get cached permissions for user"""
        try:
            cache_entry = cls.objects.get(
                user=user,
                permission_hash=permission_hash
            )
            if not cache_entry.is_expired():
                return cache_entry.permissions_data
        except cls.DoesNotExist:
            pass
        return None

    @classmethod
    def set_user_permissions(cls, user, permission_hash, permissions_data, timeout=3600):
        """Cache permissions for user"""
        expires_at = timezone.now() + timezone.timedelta(seconds=timeout)

        cls.objects.update_or_create(
            user=user,
            permission_hash=permission_hash,
            defaults={
                'permissions_data': permissions_data,
                'expires_at': expires_at
            }
        )
