from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class PermissionAuditLog(models.Model):
    """
    Model to track changes to permissions
    """
    ACTION_TYPES = (
        ('add', 'إضافة'),
        ('remove', 'إزالة'),
        ('modify', 'تعديل'),
    )
    
    OBJECT_TYPES = (
        ('user', 'مستخدم'),
        ('group', 'مجموعة'),
        ('permission', 'صلاحية'),
        ('module', 'وحدة'),
        ('department', 'قسم'),
        ('template', 'قالب'),
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
        verbose_name=_('نوع المحتوى')
    )
    object_id = models.PositiveIntegerField(verbose_name=_('معرف الكائن'))
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Description of the change
    description = models.TextField(verbose_name=_('وصف التغيير'))
    
    # Additional data (stored as JSON)
    data = models.JSONField(
        null=True, 
        blank=True,
        verbose_name=_('بيانات إضافية')
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
    def log_permission_change(cls, user, action, obj, description, data=None):
        """
        Helper method to create a new audit log entry
        
        Args:
            user: The user who made the change
            action: The action performed (add, remove, modify)
            obj: The object that was affected
            description: Description of the change
            data: Additional data to store (optional)
        """
        # Determine object type
        object_type = cls._get_object_type(obj)
        
        # Create the audit log entry
        return cls.objects.create(
            user=user,
            action=action,
            object_type=object_type,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.pk,
            description=description,
            data=data
        )
    
    @staticmethod
    def _get_object_type(obj):
        """
        Determine the object type based on the model class
        """
        model_name = obj.__class__.__name__.lower()
        
        if model_name == 'user':
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
        else:
            return 'other'
