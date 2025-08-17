"""
نماذج الإشعارات الذكية للموارد البشرية
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
import json

User = get_user_model()


class NotificationTemplate(models.Model):
    """قالب الإشعار"""
    
    NOTIFICATION_TYPES = [
        ('info', 'معلومات'),
        ('warning', 'تحذير'),
        ('error', 'خطأ'),
        ('success', 'نجاح'),
        ('reminder', 'تذكير'),
        ('urgent', 'عاجل'),
    ]
    
    name = models.CharField('اسم القالب', max_length=100)
    code = models.CharField('كود القالب', max_length=50, unique=True)
    description = models.TextField('الوصف', blank=True)
    notification_type = models.CharField('نوع الإشعار', max_length=20, choices=NOTIFICATION_TYPES)
    
    # محتوى القالب
    title_template = models.CharField('قالب العنوان', max_length=200)
    message_template = models.TextField('قالب الرسالة')
    email_template = models.TextField('قالب البريد الإلكتروني', blank=True)
    sms_template = models.TextField('قالب الرسائل النصية', blank=True)
    
    # إعدادات القالب
    is_active = models.BooleanField('نشط', default=True)
    priority = models.CharField('الأولوية', max_length=20, choices=[
        ('low', 'منخفضة'),
        ('normal', 'عادية'),
        ('high', 'عالية'),
        ('urgent', 'عاجلة'),
    ], default='normal')
    
    # تواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'قالب الإشعار'
        verbose_name_plural = 'قوالب الإشعارات'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class NotificationRule(models.Model):
    """قاعدة الإشعار"""
    
    TRIGGER_EVENTS = [
        ('employee_created', 'إنشاء موظف جديد'),
        ('employee_updated', 'تحديث بيانات موظف'),
        ('leave_request_created', 'طلب إجازة جديد'),
        ('leave_request_approved', 'موافقة على طلب إجازة'),
        ('leave_request_rejected', 'رفض طلب إجازة'),
        ('attendance_late', 'تأخير في الحضور'),
        ('document_expiry', 'انتهاء صلاحية وثيقة'),
        ('birthday', 'عيد ميلاد موظف'),
        ('work_anniversary', 'ذكرى التوظيف'),
        ('performance_review_due', 'موعد تقييم الأداء'),
        ('payroll_processed', 'معالجة الراتب'),
        ('system_alert', 'تنبيه النظام'),
    ]
    
    name = models.CharField('اسم القاعدة', max_length=100)
    description = models.TextField('الوصف', blank=True)
    trigger_event = models.CharField('حدث التشغيل', max_length=50, choices=TRIGGER_EVENTS)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, verbose_name='القالب')
    
    # شروط القاعدة
    conditions = models.JSONField('الشروط', default=dict, blank=True)
    
    # المستلمون
    recipient_rules = models.JSONField('قواعد المستلمين', default=dict, blank=True)
    
    # إعدادات التوقيت
    delay_minutes = models.IntegerField('تأخير بالدقائق', default=0)
    is_recurring = models.BooleanField('متكرر', default=False)
    recurrence_pattern = models.JSONField('نمط التكرار', default=dict, blank=True)
    
    # إعدادات القاعدة
    is_active = models.BooleanField('نشط', default=True)
    priority = models.IntegerField('الأولوية', default=1)
    
    # تواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'قاعدة الإشعار'
        verbose_name_plural = 'قواعد الإشعارات'
        ordering = ['priority', 'name']
    
    def __str__(self):
        return self.name


class Notification(models.Model):
    """الإشعار"""
    
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('sent', 'تم الإرسال'),
        ('delivered', 'تم التسليم'),
        ('read', 'تم القراءة'),
        ('failed', 'فشل'),
        ('cancelled', 'ملغي'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'منخفضة'),
        ('normal', 'عادية'),
        ('high', 'عالية'),
        ('urgent', 'عاجلة'),
    ]
    
    # معلومات أساسية
    title = models.CharField('العنوان', max_length=200)
    message = models.TextField('الرسالة')
    notification_type = models.CharField('نوع الإشعار', max_length=20)
    priority = models.CharField('الأولوية', max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # المرسل والمستلم
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='sent_notifications', verbose_name='المرسل')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, 
                                 related_name='received_notifications', verbose_name='المستلم')
    
    # العلاقة مع القالب والقاعدة
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, 
                                null=True, blank=True, verbose_name='القالب')
    rule = models.ForeignKey(NotificationRule, on_delete=models.SET_NULL, 
                            null=True, blank=True, verbose_name='القاعدة')
    
    # العلاقة مع الكائن المرتبط
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, related_name='hr_notifications')
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # حالة الإشعار
    status = models.CharField('الحالة', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # بيانات إضافية
    metadata = models.JSONField('بيانات إضافية', default=dict, blank=True)
    
    # تواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    sent_at = models.DateTimeField('تاريخ الإرسال', null=True, blank=True)
    delivered_at = models.DateTimeField('تاريخ التسليم', null=True, blank=True)
    read_at = models.DateTimeField('تاريخ القراءة', null=True, blank=True)
    scheduled_at = models.DateTimeField('موعد الإرسال', null=True, blank=True)
    
    class Meta:
        verbose_name = 'الإشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """تحديد الإشعار كمقروء"""
        if self.status != 'read':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at'])
    
    def mark_as_sent(self):
        """تحديد الإشعار كمرسل"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])
    
    def mark_as_delivered(self):
        """تحديد الإشعار كمسلم"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at'])
    
    def mark_as_failed(self, error_message=None):
        """تحديد الإشعار كفاشل"""
        self.status = 'failed'
        if error_message:
            self.metadata['error'] = error_message
        self.save(update_fields=['status', 'metadata'])


class NotificationDelivery(models.Model):
    """تسليم الإشعار"""
    
    DELIVERY_METHODS = [
        ('email', 'بريد إلكتروني'),
        ('sms', 'رسالة نصية'),
        ('push', 'إشعار فوري'),
        ('in_app', 'داخل التطبيق'),
        ('slack', 'سلاك'),
        ('teams', 'تيمز'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('sent', 'تم الإرسال'),
        ('delivered', 'تم التسليم'),
        ('failed', 'فشل'),
        ('bounced', 'مرتد'),
    ]
    
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, 
                                   related_name='deliveries', verbose_name='الإشعار')
    method = models.CharField('طريقة التسليم', max_length=20, choices=DELIVERY_METHODS)
    status = models.CharField('الحالة', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # تفاصيل التسليم
    recipient_address = models.CharField('عنوان المستلم', max_length=200)
    provider = models.CharField('مقدم الخدمة', max_length=50, blank=True)
    external_id = models.CharField('المعرف الخارجي', max_length=100, blank=True)
    
    # معلومات الاستجابة
    response_data = models.JSONField('بيانات الاستجابة', default=dict, blank=True)
    error_message = models.TextField('رسالة الخطأ', blank=True)
    
    # إحصائيات
    attempts = models.IntegerField('عدد المحاولات', default=0)
    
    # تواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    sent_at = models.DateTimeField('تاريخ الإرسال', null=True, blank=True)
    delivered_at = models.DateTimeField('تاريخ التسليم', null=True, blank=True)
    next_retry_at = models.DateTimeField('موعد المحاولة التالية', null=True, blank=True)
    
    class Meta:
        verbose_name = 'تسليم الإشعار'
        verbose_name_plural = 'تسليمات الإشعارات'
        ordering = ['-created_at']
        unique_together = ['notification', 'method']
    
    def __str__(self):
        return f"{self.notification.title} - {self.get_method_display()}"


class NotificationPreference(models.Model):
    """تفضيلات الإشعارات"""
    
    DIGEST_FREQUENCIES = [
        ('none', 'بدون ملخص'),
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                               related_name='notification_preferences', verbose_name='المستخدم')
    
    # إعدادات عامة
    enabled = models.BooleanField('تفعيل الإشعارات', default=True)
    
    # طرق التسليم
    email_enabled = models.BooleanField('البريد الإلكتروني', default=True)
    sms_enabled = models.BooleanField('الرسائل النصية', default=False)
    push_enabled = models.BooleanField('الإشعارات الفورية', default=True)
    in_app_enabled = models.BooleanField('داخل التطبيق', default=True)
    
    # إعدادات الملخص
    digest_enabled = models.BooleanField('تفعيل الملخص', default=False)
    digest_frequency = models.CharField('تكرار الملخص', max_length=20, 
                                       choices=DIGEST_FREQUENCIES, default='daily')
    
    # الساعات الهادئة
    quiet_hours_enabled = models.BooleanField('تفعيل الساعات الهادئة', default=False)
    quiet_hours_start = models.TimeField('بداية الساعات الهادئة', null=True, blank=True)
    quiet_hours_end = models.TimeField('نهاية الساعات الهادئة', null=True, blank=True)
    
    # تفضيلات حسب النوع
    notification_types = models.JSONField('تفضيلات الأنواع', default=dict, blank=True)
    
    # تواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'تفضيلات الإشعارات'
        verbose_name_plural = 'تفضيلات الإشعارات'
    
    def __str__(self):
        return f"تفضيلات {self.user.username}"
    
    def is_method_enabled(self, method):
        """التحقق من تفعيل طريقة تسليم معينة"""
        if not self.enabled:
            return False
        
        method_mapping = {
            'email': self.email_enabled,
            'sms': self.sms_enabled,
            'push': self.push_enabled,
            'in_app': self.in_app_enabled,
        }
        
        return method_mapping.get(method, False)
    
    def is_quiet_time(self):
        """التحقق من الساعات الهادئة"""
        if not self.quiet_hours_enabled or not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        now = timezone.now().time()
        return self.quiet_hours_start <= now <= self.quiet_hours_end


class NotificationDigest(models.Model):
    """ملخص الإشعارات"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('sent', 'تم الإرسال'),
        ('failed', 'فشل'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                            related_name='notification_digests', verbose_name='المستخدم')
    frequency = models.CharField('التكرار', max_length=20, choices=FREQUENCY_CHOICES)
    
    # فترة الملخص
    period_start = models.DateTimeField('بداية الفترة')
    period_end = models.DateTimeField('نهاية الفترة')
    
    # محتوى الملخص
    title = models.CharField('العنوان', max_length=200)
    content = models.TextField('المحتوى')
    notifications_count = models.IntegerField('عدد الإشعارات', default=0)
    
    # حالة الملخص
    status = models.CharField('الحالة', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # تواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    sent_at = models.DateTimeField('تاريخ الإرسال', null=True, blank=True)
    
    class Meta:
        verbose_name = 'ملخص الإشعارات'
        verbose_name_plural = 'ملخصات الإشعارات'
        ordering = ['-created_at']
        unique_together = ['user', 'frequency', 'period_start']
    
    def __str__(self):
        return f"ملخص {self.get_frequency_display()} - {self.user.username}"