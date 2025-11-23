"""
نماذج الصلاحيات والأدوار
Permissions and Roles Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .base import BaseModel


class Module(BaseModel):
    """
    وحدات النظام
    System modules for permission management
    """
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name=_('اسم الوحدة'),
        help_text=_('الاسم التقني للوحدة')
    )
    display_name = models.CharField(
        max_length=200,
        verbose_name=_('الاسم المعروض'),
        help_text=_('الاسم المعروض للمستخدمين')
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('الوصف'),
        help_text=_('وصف تفصيلي للوحدة')
    )
    icon = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name=_('الأيقونة'),
        help_text=_('اسم الأيقونة المستخدمة في الواجهة')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('الترتيب'),
        help_text=_('ترتيب عرض الوحدة في القوائم')
    )
    parent_module = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_modules',
        verbose_name=_('الوحدة الأب'),
        help_text=_('الوحدة الرئيسية إن وجدت')
    )
    
    class Meta:
        verbose_name = _('وحدة النظام')
        verbose_name_plural = _('وحدات النظام')
        ordering = ['order', 'display_name']
        
    def __str__(self):
        return self.display_name


class Permission(BaseModel):
    """
    الصلاحيات المفصلة
    Detailed permissions for system operations
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
    ]
    
    module = models.ForeignKey(
        Module, 
        on_delete=models.CASCADE,
        related_name='permissions',
        verbose_name=_('الوحدة')
    )
    permission_type = models.CharField(
        max_length=20, 
        choices=PERMISSION_TYPES,
        verbose_name=_('نوع الصلاحية')
    )
    codename = models.CharField(
        max_length=100,
        verbose_name=_('الاسم الرمزي'),
        help_text=_('الاسم التقني للصلاحية')
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('اسم الصلاحية'),
        help_text=_('الاسم المعروض للصلاحية')
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('الوصف'),
        help_text=_('وصف تفصيلي للصلاحية')
    )
    
    class Meta:
        verbose_name = _('صلاحية')
        verbose_name_plural = _('الصلاحيات')
        unique_together = ['module', 'codename']
        ordering = ['module__order', 'permission_type', 'name']
        
    def __str__(self):
        return f"{self.module.display_name} - {self.name}"


class Role(BaseModel):
    """
    الأدوار
    User roles with assigned permissions
    """
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name=_('اسم الدور'),
        help_text=_('الاسم التقني للدور')
    )
    display_name = models.CharField(
        max_length=200,
        verbose_name=_('الاسم المعروض'),
        help_text=_('الاسم المعروض للمستخدمين')
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('الوصف'),
        help_text=_('وصف تفصيلي للدور ومسؤولياته')
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='roles',
        verbose_name=_('الصلاحيات'),
        help_text=_('الصلاحيات المخصصة لهذا الدور')
    )
    is_system_role = models.BooleanField(
        default=False,
        verbose_name=_('دور النظام'),
        help_text=_('هل هذا دور أساسي في النظام لا يمكن حذفه')
    )
    level = models.PositiveIntegerField(
        default=1,
        verbose_name=_('مستوى الدور'),
        help_text=_('مستوى الدور في التسلسل الهرمي')
    )
    
    class Meta:
        verbose_name = _('دور')
        verbose_name_plural = _('الأدوار')
        ordering = ['level', 'display_name']
        
    def __str__(self):
        return self.display_name
    
    def has_permission(self, permission_codename, module_name=None):
        """Check if role has specific permission"""
        if module_name:
            return self.permissions.filter(
                codename=permission_codename,
                module__name=module_name
            ).exists()
        return self.permissions.filter(codename=permission_codename).exists()


class UserRole(BaseModel):
    """
    أدوار المستخدمين
    User role assignments with expiration and audit trail
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name=_('المستخدم')
    )
    role = models.ForeignKey(
        Role, 
        on_delete=models.CASCADE,
        related_name='user_assignments',
        verbose_name=_('الدور')
    )
    granted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='granted_roles',
        verbose_name=_('منح بواسطة'),
        help_text=_('المستخدم الذي منح هذا الدور')
    )
    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ المنح'),
        help_text=_('تاريخ ووقت منح الدور')
    )
    expires_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_('تاريخ الانتهاء'),
        help_text=_('تاريخ انتهاء صلاحية الدور (اختياري)')
    )
    revoked_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_('تاريخ الإلغاء'),
        help_text=_('تاريخ إلغاء الدور')
    )
    revoked_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='revoked_roles',
        verbose_name=_('ألغي بواسطة'),
        help_text=_('المستخدم الذي ألغى هذا الدور')
    )
    reason = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('السبب'),
        help_text=_('سبب منح أو إلغاء الدور')
    )
    
    class Meta:
        verbose_name = _('دور المستخدم')
        verbose_name_plural = _('أدوار المستخدمين')
        unique_together = ['user', 'role']
        ordering = ['-granted_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.role.display_name}"
    
    @property
    def is_expired(self):
        """Check if role assignment is expired"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_revoked(self):
        """Check if role assignment is revoked"""
        return self.revoked_at is not None
    
    @property
    def is_active_assignment(self):
        """Check if role assignment is currently active"""
        return (
            self.is_active and 
            not self.is_expired and 
            not self.is_revoked
        )
    
    def revoke(self, revoked_by=None, reason=None):
        """Revoke the role assignment"""
        from django.utils import timezone
        self.revoked_at = timezone.now()
        self.revoked_by = revoked_by
        if reason:
            self.reason = reason
        self.is_active = False
        self.save(update_fields=['revoked_at', 'revoked_by', 'reason', 'is_active'])


class ObjectPermission(BaseModel):
    """
    صلاحيات على مستوى الكائن
    Object-level permissions for fine-grained access control
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='object_permissions',
        verbose_name=_('المستخدم')
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='object_assignments',
        verbose_name=_('الصلاحية')
    )
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        verbose_name=_('نوع المحتوى')
    )
    object_id = models.CharField(
        max_length=255,
        verbose_name=_('معرف الكائن')
    )
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_object_permissions',
        verbose_name=_('منح بواسطة')
    )
    
    class Meta:
        verbose_name = _('صلاحية الكائن')
        verbose_name_plural = _('صلاحيات الكائنات')
        unique_together = ['user', 'permission', 'content_type', 'object_id']
        
    def __str__(self):
        return f"{self.user.username} - {self.permission.name} - {self.content_type.name}:{self.object_id}"