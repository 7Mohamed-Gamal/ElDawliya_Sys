"""
نماذج التدقيق والسجلات
Audit and Logging Models
"""
import json
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import gettext_lazy as _
from .base import BaseModel


class AuditLog(BaseModel):
    """
    سجل التدقيق للعمليات
    Audit log for tracking user actions and system changes
    """
    ACTION_TYPES = [
        ('create', _('إنشاء')),
        ('read', _('قراءة')),
        ('update', _('تحديث')),
        ('delete', _('حذف')),
        ('login', _('تسجيل دخول')),
        ('logout', _('تسجيل خروج')),
        ('approve', _('موافقة')),
        ('reject', _('رفض')),
        ('export', _('تصدير')),
        ('import', _('استيراد')),
        ('print', _('طباعة')),
        ('email', _('إرسال بريد')),
        ('sms', _('إرسال رسالة')),
        ('backup', _('نسخ احتياطي')),
        ('restore', _('استعادة')),
        ('system', _('عملية نظام')),
    ]
    
    RESULT_TYPES = [
        ('success', _('نجح')),
        ('failure', _('فشل')),
        ('warning', _('تحذير')),
        ('info', _('معلومات')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name=_('المستخدم'),
        help_text=_('المستخدم الذي قام بالعملية')
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name=_('نوع العملية'),
        help_text=_('نوع العملية التي تم تنفيذها')
    )
    resource = models.CharField(
        max_length=255,
        verbose_name=_('المورد'),
        help_text=_('المورد أو الصفحة التي تم الوصول إليها')
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
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
    
    old_values = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('القيم القديمة'),
        help_text=_('القيم قبل التغيير (للتحديثات)')
    )
    new_values = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('القيم الجديدة'),
        help_text=_('القيم بعد التغيير (للتحديثات)')
    )
    details = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('تفاصيل إضافية'),
        help_text=_('معلومات إضافية حول العملية')
    )
    result = models.CharField(
        max_length=20,
        choices=RESULT_TYPES,
        default='success',
        verbose_name=_('نتيجة العملية')
    )
    message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('الرسالة'),
        help_text=_('رسالة توضيحية حول العملية')
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('عنوان IP'),
        help_text=_('عنوان IP للمستخدم')
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('معلومات المتصفح'),
        help_text=_('معلومات المتصفح والنظام')
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name=_('مفتاح الجلسة')
    )
    duration = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('مدة العملية'),
        help_text=_('مدة تنفيذ العملية بالثواني')
    )
    
    class Meta:
        verbose_name = _('سجل التدقيق')
        verbose_name_plural = _('سجلات التدقيق')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['ip_address', '-created_at']),
        ]
        
    def __str__(self):
        username = self.user.username if self.user else 'نظام'
        return f"{username} - {self.get_action_display()} - {self.resource}"
    
    def get_changes_summary(self):
        """Get a summary of changes made"""
        if not self.old_values or not self.new_values:
            return None
            
        changes = {}
        for field, new_value in self.new_values.items():
            old_value = self.old_values.get(field)
            if old_value != new_value:
                changes[field] = {
                    'old': old_value,
                    'new': new_value
                }
        return changes
    
    @classmethod
    def log_action(cls, user, action, resource, content_object=None, 
                   old_values=None, new_values=None, details=None, 
                   result='success', message=None, request=None):
        """Helper method to create audit log entries"""
        log_data = {
            'user': user,
            'action': action,
            'resource': resource,
            'old_values': old_values,
            'new_values': new_values,
            'details': details,
            'result': result,
            'message': message,
        }
        
        if content_object:
            log_data['content_object'] = content_object
            
        if request:
            log_data.update({
                'ip_address': cls._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'session_key': request.session.session_key,
            })
            
        return cls.objects.create(**log_data)
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SystemLog(BaseModel):
    """
    سجل النظام للأحداث التقنية
    System log for technical events and errors
    """
    LOG_LEVELS = [
        ('debug', _('تصحيح')),
        ('info', _('معلومات')),
        ('warning', _('تحذير')),
        ('error', _('خطأ')),
        ('critical', _('حرج')),
    ]
    
    CATEGORIES = [
        ('database', _('قاعدة البيانات')),
        ('authentication', _('المصادقة')),
        ('api', _('واجهة برمجة التطبيقات')),
        ('email', _('البريد الإلكتروني')),
        ('file_system', _('نظام الملفات')),
        ('integration', _('التكامل')),
        ('performance', _('الأداء')),
        ('security', _('الأمان')),
        ('backup', _('النسخ الاحتياطي')),
        ('general', _('عام')),
    ]
    
    level = models.CharField(
        max_length=20,
        choices=LOG_LEVELS,
        default='info',
        verbose_name=_('مستوى السجل')
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORIES,
        default='general',
        verbose_name=_('فئة السجل')
    )
    module = models.CharField(
        max_length=100,
        verbose_name=_('الوحدة'),
        help_text=_('الوحدة أو التطبيق الذي أنتج السجل')
    )
    function = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('الدالة'),
        help_text=_('اسم الدالة أو الطريقة')
    )
    message = models.TextField(
        verbose_name=_('الرسالة'),
        help_text=_('رسالة السجل')
    )
    details = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('التفاصيل'),
        help_text=_('تفاصيل إضافية في تنسيق JSON')
    )
    exception_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('نوع الاستثناء')
    )
    stack_trace = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('تتبع المكدس'),
        help_text=_('تتبع المكدس للأخطاء')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_logs',
        verbose_name=_('المستخدم المرتبط')
    )
    resolved = models.BooleanField(
        default=False,
        verbose_name=_('تم الحل'),
        help_text=_('هل تم حل هذه المشكلة')
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_logs',
        verbose_name=_('حُل بواسطة')
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الحل')
    )
    
    class Meta:
        verbose_name = _('سجل النظام')
        verbose_name_plural = _('سجلات النظام')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level', '-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['module', '-created_at']),
            models.Index(fields=['resolved', '-created_at']),
        ]
        
    def __str__(self):
        return f"{self.get_level_display()} - {self.module} - {self.message[:50]}"
    
    @classmethod
    def log(cls, level, category, module, message, function=None, 
            details=None, exception=None, user=None):
        """Helper method to create system log entries"""
        log_data = {
            'level': level,
            'category': category,
            'module': module,
            'function': function,
            'message': message,
            'details': details,
            'user': user,
        }
        
        if exception:
            import traceback
            log_data.update({
                'exception_type': type(exception).__name__,
                'stack_trace': traceback.format_exc(),
            })
            
        return cls.objects.create(**log_data)
    
    def mark_resolved(self, resolved_by=None):
        """Mark the log entry as resolved"""
        from django.utils import timezone
        self.resolved = True
        self.resolved_by = resolved_by
        self.resolved_at = timezone.now()
        self.save(update_fields=['resolved', 'resolved_by', 'resolved_at'])


class LoginAttempt(BaseModel):
    """
    محاولات تسجيل الدخول
    Login attempts tracking for security monitoring
    """
    username = models.CharField(
        max_length=150,
        verbose_name=_('اسم المستخدم')
    )
    ip_address = models.GenericIPAddressField(
        verbose_name=_('عنوان IP')
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('معلومات المتصفح')
    )
    success = models.BooleanField(
        default=False,
        verbose_name=_('نجح'),
        help_text=_('هل نجحت محاولة تسجيل الدخول')
    )
    failure_reason = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('سبب الفشل'),
        help_text=_('سبب فشل تسجيل الدخول')
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name=_('مفتاح الجلسة')
    )
    
    class Meta:
        verbose_name = _('محاولة تسجيل دخول')
        verbose_name_plural = _('محاولات تسجيل الدخول')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
            models.Index(fields=['success', '-created_at']),
        ]
        
    def __str__(self):
        status = 'نجح' if self.success else 'فشل'
        return f"{self.username} - {status} - {self.ip_address}"
    
    @classmethod
    def log_attempt(cls, username, ip_address, success, user_agent=None, 
                    failure_reason=None, session_key=None):
        """Log a login attempt"""
        return cls.objects.create(
            username=username,
            ip_address=ip_address,
            success=success,
            user_agent=user_agent,
            failure_reason=failure_reason,
            session_key=session_key
        )