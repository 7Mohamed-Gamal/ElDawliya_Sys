from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
import json

User = get_user_model()

class PermissionAuditLog(models.Model):
    """
    Model to track changes to permissions
    """
    ACTION_TYPES = (
        ('add', 'إضافة'),
        ('remove', 'إزالة'),
        ('modify', 'تعديل'),
        ('assign', 'تعيين'),
        ('revoke', 'سحب'),
        ('login', 'تسجيل دخول'),
        ('logout', 'تسجيل خروج'),
        ('view', 'عرض'),
    )

    OBJECT_TYPES = (
        ('user', 'مستخدم'),
        ('group', 'مجموعة'),
        ('permission', 'صلاحية'),
        ('module', 'وحدة'),
        ('department', 'قسم'),
        ('template', 'قالب'),
        ('role', 'دور'),
        ('operation', 'عملية'),
        ('page', 'صفحة'),
        ('system', 'نظام'),
    )

    # Who made the change
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='permission_audit_logs',
        verbose_name=_('المستخدم')
    )

    # When the change was made
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('وقت التغيير')
    )

    # What action was performed
    action = models.CharField(
        max_length=10,
        choices=ACTION_TYPES,
        verbose_name=_('الإجراء')
    )

    # What type of object was affected
    object_type = models.CharField(
        max_length=20,
        choices=OBJECT_TYPES,
        verbose_name=_('نوع الكائن')
    )

    # Generic foreign key to the affected object
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('نوع المحتوى')
    )
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('معرف الكائن'))
    content_object = GenericForeignKey('content_type', 'object_id')

    # Description of the change
    description = models.TextField(verbose_name=_('وصف التغيير'))

    # Additional data (stored as JSON)
    data = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('بيانات إضافية')
    )

    # IP address of the user
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('عنوان IP')
    )

    # User agent of the user
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('وكيل المستخدم')
    )

    # Success or failure
    success = models.BooleanField(
        default=True,
        verbose_name=_('نجاح')
    )

    # Error message if any
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('رسالة الخطأ')
    )

    class Meta:
        verbose_name = _('سجل تدقيق الصلاحيات')
        verbose_name_plural = _('سجلات تدقيق الصلاحيات')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['object_type']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} {self.get_object_type_display()} - {self.timestamp}"

    @classmethod
    def log_permission_change(cls, user, action, obj=None, description=None, data=None, request=None, success=True, error_message=None, object_type=None):
        """
        Helper method to create a new audit log entry

        Args:
            user: The user who made the change
            action: The action performed (add, remove, modify, assign, revoke, etc.)
            obj: The object that was affected (optional)
            description: Description of the change (optional)
            data: Additional data to store (optional)
            request: The request object for capturing IP and user agent (optional)
            success: Whether the action was successful (default: True)
            error_message: Error message if the action failed (optional)
            object_type: Override the object type detection (optional)
        """
        # Create the audit log entry
        log_entry = cls(
            user=user,
            action=action,
            description=description or f"{action} operation",
            success=success,
            error_message=error_message
        )

        # Set object type and content object if provided
        if obj:
            log_entry.object_type = object_type or cls._get_object_type(obj)
            log_entry.content_type = ContentType.objects.get_for_model(obj)
            log_entry.object_id = obj.pk
        elif object_type:
            log_entry.object_type = object_type

        # Set the data if provided
        if data:
            log_entry.data = data

        # Set the IP address and user agent if request is provided
        if request:
            log_entry.ip_address = cls._get_client_ip(request)
            log_entry.user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Save the log entry
        log_entry.save()

        return log_entry

    @staticmethod
    def _get_client_ip(request):
        """
        Get the client IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def _get_object_type(obj):
        """
        Determine the object type based on the model class
        """
        model_name = obj.__class__.__name__.lower()

        if model_name == 'user' or model_name == 'users_login_new':
            return 'user'
        elif model_name == 'group':
            return 'group'
        elif model_name == 'permission':
            return 'permission'
        elif model_name == 'module':
            return 'module'
        elif model_name == 'department':
            return 'department'
        elif model_name == 'templatepermission':
            return 'template'
        elif model_name == 'appmodule':
            return 'module'
        elif model_name == 'operationpermission':
            return 'operation'
        elif model_name == 'pagepermission':
            return 'page'
        else:
            return 'other'

    def get_data_display(self):
        """
        Get a formatted display of the data.
        """
        if not self.data:
            return ""

        try:
            return json.dumps(self.data, indent=2, ensure_ascii=False)
        except Exception:
            return str(self.data)
