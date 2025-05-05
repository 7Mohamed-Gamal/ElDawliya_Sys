from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class AuditLog(models.Model):
    """
    Model for storing audit log entries for user actions in the system.
    """
    # Action types
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    VIEW = 'VIEW'
    LOGIN = 'LOGIN'
    LOGOUT = 'LOGOUT'
    OTHER = 'OTHER'
    
    ACTION_CHOICES = [
        (CREATE, _('إنشاء')),
        (UPDATE, _('تحديث')),
        (DELETE, _('حذف')),
        (VIEW, _('عرض')),
        (LOGIN, _('تسجيل دخول')),
        (LOGOUT, _('تسجيل خروج')),
        (OTHER, _('أخرى')),
    ]
    
    # User who performed the action (can be null if action not linked to user)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('المستخدم'),
        related_name='audit_logs'
    )
    
    # Action details
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        verbose_name=_('الإجراء')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('وقت الإجراء')
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('عنوان IP')
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('معلومات المتصفح')
    )
    app_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('اسم التطبيق')
    )
    
    # Target object information using ContentType framework
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('نوع المحتوى')
    )
    object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('معرف الكائن')
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional details
    object_repr = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('وصف الكائن')
    )
    action_details = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('تفاصيل الإجراء')
    )
    change_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('بيانات التغييرات')
    )
    
    class Meta:
        verbose_name = _('سجل التدقيق')
        verbose_name_plural = _('سجلات التدقيق')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['app_name']),
        ]
    
    def __str__(self):
        if self.user:
            user_repr = self.user.get_username()
        else:
            user_repr = _('مستخدم غير معروف')
            
        return f"{user_repr} - {self.get_action_display()} - {self.timestamp}"
