from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(models.Model):
    """
    نموذج التنبيهات
    """
    NOTIFICATION_TYPES = [
        ('hr', _('الموارد البشرية')),
        ('meetings', _('الاجتماعات')),
        ('inventory', _('المخزن')),
        ('purchase', _('المشتريات')),
        ('system', _('النظام')),
    ]

    PRIORITY_LEVELS = [
        ('low', _('منخفضة')),
        ('medium', _('متوسطة')),
        ('high', _('عالية')),
        ('urgent', _('عاجلة')),
    ]

    title = models.CharField(max_length=255, verbose_name=_('عنوان التنبيه'))
    message = models.TextField(verbose_name=_('نص التنبيه'))
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name=_('نوع التنبيه'))
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium', verbose_name=_('الأولوية'))

    # الربط مع أي نوع من الكائنات (مثل المهام، الاجتماعات، إلخ)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('نوع المحتوى'))
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('معرف الكائن'))
    content_object = GenericForeignKey('content_type', 'object_id')

    # المستخدم المستهدف بالتنبيه
    user = models.ForeignKey('accounts.Users_Login_New', on_delete=models.CASCADE, related_name='notifications', verbose_name=_('المستخدم'))

    # حالة التنبيه
    is_read = models.BooleanField(default=False, verbose_name=_('تمت القراءة'))
    read_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ القراءة'))

    # معلومات إضافية
    url = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('رابط التنبيه'))
    icon = models.CharField(max_length=50, default='fas fa-bell', verbose_name=_('أيقونة التنبيه'))

    # التوقيت
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        """تعليم التنبيه كمقروء"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

    class Meta:
        verbose_name = _('تنبيه')
        verbose_name_plural = _('التنبيهات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
        ]
