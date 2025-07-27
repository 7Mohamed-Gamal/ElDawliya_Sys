"""
نماذج نظام الصلاحيات المتقدم للموارد البشرية
"""

from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid


class PermissionCategory(models.Model):
    """فئات الصلاحيات"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('اسم الفئة'), max_length=100)
    name_en = models.CharField(_('الاسم بالإنجليزية'), max_length=100)
    description = models.TextField(_('الوصف'), blank=True)
    icon = models.CharField(_('الأيقونة'), max_length=50, default='fas fa-shield-alt')
    color = models.CharField(_('اللون'), max_length=7, default='#3b82f6')
    order = models.PositiveIntegerField(_('الترتيب'), default=0)
    is_active = models.BooleanField(_('نشط'), default=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('فئة الصلاحيات')
        verbose_name_plural = _('فئات الصلاحيات')
        ordering = ['order', 'name']
        
    def __str__(self):
        return self.name


class HRPermission(models.Model):
    """صلاحيات الموارد البشرية المخصصة"""
    
    PERMISSION_TYPES = [
        ('view', _('عرض')),
        ('add', _('إضافة')),
        ('change', _('تعديل')),
        ('delete', _('حذف')),
        ('export', _('تصدير')),
        ('import', _('استيراد')),
        ('approve', _('موافقة')),
        ('reject', _('رفض')),
        ('manage', _('إدارة')),
        ('admin', _('إدارة كاملة')),
    ]
    
    SCOPE_LEVELS = [
        ('own', _('البيانات الشخصية فقط')),
        ('department', _('القسم')),
        ('branch', _('الفرع')),
        ('company', _('الشركة')),
        ('all', _('جميع البيانات')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        PermissionCategory, 
        on_delete=models.CASCADE,
        related_name='permissions',
        verbose_name=_('الفئة')
    )
    
    name = models.CharField(_('اسم الصلاحية'), max_length=100)
    name_en = models.CharField(_('الاسم بالإنجليزية'), max_length=100)
    codename = models.CharField(_('الرمز'), max_length=100, unique=True)
    description = models.TextField(_('الوصف'), blank=True)
    
    permission_type = models.CharField(
        _('نوع الصلاحية'), 
        max_length=20, 
        choices=PERMISSION_TYPES
    )
    scope_level = models.CharField(
        _('نطاق الصلاحية'), 
        max_length=20, 
        choices=SCOPE_LEVELS,
        default='department'
    )
    
    # ربط مع نماذج Django
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name=_('نوع المحتوى')
    )
    
    # الصلاحيات المطلوبة مسبقاً
    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='dependent_permissions',
        verbose_name=_('الصلاحيات المطلوبة')
    )
    
    is_active = models.BooleanField(_('نشط'), default=True)
    is_system = models.BooleanField(_('صلاحية نظام'), default=False)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('صلاحية الموارد البشرية')
        verbose_name_plural = _('صلاحيات الموارد البشرية')
        ordering = ['category__order', 'name']
        
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class RoleTemplate(models.Model):
    """قوالب الأدوار"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('اسم القالب'), max_length=100)
    name_en = models.CharField(_('الاسم بالإنجليزية'), max_length=100)
    description = models.TextField(_('الوصف'), blank=True)
    
    permissions = models.ManyToManyField(
        HRPermission,
        related_name='role_templates',
        verbose_name=_('الصلاحيات')
    )
    
    is_default = models.BooleanField(_('قالب افتراضي'), default=False)
    is_active = models.BooleanField(_('نشط'), default=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_role_templates',
        verbose_name=_('منشئ القالب')
    )
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('قالب الدور')
        verbose_name_plural = _('قوالب الأدوار')
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    def clean(self):
        if self.is_default:
            # التأكد من وجود قالب افتراضي واحد فقط
            existing_default = RoleTemplate.objects.filter(is_default=True)
            if self.pk:
                existing_default = existing_default.exclude(pk=self.pk)
            if existing_default.exists():
                raise ValidationError(_('يمكن أن يكون هناك قالب افتراضي واحد فقط'))


class UserRole(models.Model):
    """أدوار المستخدمين"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='hr_role',
        verbose_name=_('المستخدم')
    )
    
    role_template = models.ForeignKey(
        RoleTemplate,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='user_roles',
        verbose_name=_('قالب الدور')
    )
    
    # صلاحيات إضافية أو مخصصة
    additional_permissions = models.ManyToManyField(
        HRPermission,
        blank=True,
        related_name='user_roles_additional',
        verbose_name=_('صلاحيات إضافية')
    )
    
    # صلاحيات محذوفة من القالب
    removed_permissions = models.ManyToManyField(
        HRPermission,
        blank=True,
        related_name='user_roles_removed',
        verbose_name=_('صلاحيات محذوفة')
    )
    
    # نطاق العمل
    department_scope = models.ForeignKey(
        'Hr.Department',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='scoped_users',
        verbose_name=_('نطاق القسم')
    )
    
    branch_scope = models.ForeignKey(
        'Hr.Branch',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='scoped_users',
        verbose_name=_('نطاق الفرع')
    )
    
    is_active = models.BooleanField(_('نشط'), default=True)
    
    # تواريخ صلاحية الدور
    valid_from = models.DateTimeField(_('صالح من'), null=True, blank=True)
    valid_until = models.DateTimeField(_('صالح حتى'), null=True, blank=True)
    
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_roles',
        verbose_name=_('معين بواسطة')
    )
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('دور المستخدم')
        verbose_name_plural = _('أدوار المستخدمين')
        
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.role_template.name if self.role_template else 'مخصص'}"
    
    def get_all_permissions(self):
        """الحصول على جميع الصلاحيات الفعالة للمستخدم"""
        permissions = set()
        
        # صلاحيات من القالب
        if self.role_template:
            template_permissions = set(self.role_template.permissions.filter(is_active=True))
            permissions.update(template_permissions)
        
        # إضافة الصلاحيات الإضافية
        additional_permissions = set(self.additional_permissions.filter(is_active=True))
        permissions.update(additional_permissions)
        
        # حذف الصلاحيات المحذوفة
        removed_permissions = set(self.removed_permissions.all())
        permissions -= removed_permissions
        
        return permissions
    
    def has_permission(self, permission_codename, scope_context=None):
        """التحقق من وجود صلاحية معينة"""
        permissions = self.get_all_permissions()
        
        for perm in permissions:
            if perm.codename == permission_codename:
                # التحقق من النطاق
                if self._check_scope(perm, scope_context):
                    return True
        
        return False
    
    def _check_scope(self, permission, context):
        """التحقق من نطاق الصلاحية"""
        if permission.scope_level == 'all':
            return True
        
        if not context:
            return permission.scope_level in ['own', 'department']
        
        # التحقق من النطاق حسب السياق
        if permission.scope_level == 'own':
            return context.get('user_id') == self.user.id
        
        elif permission.scope_level == 'department':
            if self.department_scope:
                return context.get('department_id') == self.department_scope.id
            return True
        
        elif permission.scope_level == 'branch':
            if self.branch_scope:
                return context.get('branch_id') == self.branch_scope.id
            return True
        
        elif permission.scope_level == 'company':
            return True
        
        return False


class PermissionRequest(models.Model):
    """طلبات الصلاحيات"""
    
    STATUS_CHOICES = [
        ('pending', _('في الانتظار')),
        ('approved', _('موافق عليه')),
        ('rejected', _('مرفوض')),
        ('cancelled', _('ملغي')),
    ]
    
    REQUEST_TYPES = [
        ('grant', _('منح صلاحية')),
        ('revoke', _('سحب صلاحية')),
        ('modify', _('تعديل صلاحية')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='permission_requests',
        verbose_name=_('الطالب')
    )
    
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='permission_requests_for',
        verbose_name=_('المستخدم المستهدف')
    )
    
    request_type = models.CharField(
        _('نوع الطلب'),
        max_length=20,
        choices=REQUEST_TYPES
    )
    
    permissions = models.ManyToManyField(
        HRPermission,
        related_name='permission_requests',
        verbose_name=_('الصلاحيات المطلوبة')
    )
    
    reason = models.TextField(_('السبب'))
    
    status = models.CharField(
        _('الحالة'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_permission_requests',
        verbose_name=_('الموافق')
    )
    
    approval_notes = models.TextField(_('ملاحظات الموافقة'), blank=True)
    approved_at = models.DateTimeField(_('تاريخ الموافقة'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('طلب صلاحية')
        verbose_name_plural = _('طلبات الصلاحيات')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_request_type_display()} - {self.target_user.get_full_name()}"


class PermissionLog(models.Model):
    """سجل الصلاحيات"""
    
    ACTION_TYPES = [
        ('granted', _('منح')),
        ('revoked', _('سحب')),
        ('modified', _('تعديل')),
        ('used', _('استخدام')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='permission_logs',
        verbose_name=_('المستخدم')
    )
    
    permission = models.ForeignKey(
        HRPermission,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name=_('الصلاحية')
    )
    
    action = models.CharField(
        _('الإجراء'),
        max_length=20,
        choices=ACTION_TYPES
    )
    
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='performed_permission_logs',
        verbose_name=_('نفذ بواسطة')
    )
    
    ip_address = models.GenericIPAddressField(_('عنوان IP'), null=True, blank=True)
    user_agent = models.TextField(_('معلومات المتصفح'), blank=True)
    
    details = models.JSONField(_('التفاصيل'), default=dict, blank=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('سجل الصلاحية')
        verbose_name_plural = _('سجلات الصلاحيات')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_action_display()} - {self.permission.name}"