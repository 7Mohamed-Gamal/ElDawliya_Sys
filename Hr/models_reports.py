"""
نماذج نظام التقارير الشامل
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json

User = get_user_model()


class ReportCategory(models.Model):
    """فئات التقارير"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name=_('اسم الفئة'))
    name_english = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('الأيقونة'))
    color = models.CharField(max_length=7, default='#007bff', verbose_name=_('اللون'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('الترتيب'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('فئة التقرير')
        verbose_name_plural = _('فئات التقارير')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class ReportTemplate(models.Model):
    """قوالب التقارير"""
    
    REPORT_TYPES = [
        ('employee', _('تقارير الموظفين')),
        ('attendance', _('تقارير الحضور')),
        ('payroll', _('تقارير الرواتب')),
        ('leave', _('تقارير الإجازات')),
        ('performance', _('تقارير الأداء')),
        ('analytics', _('تقارير تحليلية')),
        ('custom', _('تقارير مخصصة')),
    ]
    
    OUTPUT_FORMATS = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('html', 'HTML'),
        ('json', 'JSON'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(ReportCategory, on_delete=models.CASCADE, related_name='templates', verbose_name=_('الفئة'))
    name = models.CharField(max_length=200, verbose_name=_('اسم التقرير'))
    name_english = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name=_('نوع التقرير'))
    
    # إعدادات التقرير
    query_config = models.JSONField(default=dict, verbose_name=_('إعدادات الاستعلام'))
    filter_config = models.JSONField(default=dict, verbose_name=_('إعدادات الفلترة'))
    column_config = models.JSONField(default=dict, verbose_name=_('إعدادات الأعمدة'))
    chart_config = models.JSONField(default=dict, verbose_name=_('إعدادات الرسوم البيانية'))
    
    # إعدادات التصدير
    supported_formats = models.JSONField(default=list, verbose_name=_('الصيغ المدعومة'))
    default_format = models.CharField(max_length=10, choices=OUTPUT_FORMATS, default='pdf', verbose_name=_('الصيغة الافتراضية'))
    
    # إعدادات الأمان
    required_permissions = models.JSONField(default=list, verbose_name=_('الصلاحيات المطلوبة'))
    allowed_departments = models.JSONField(default=list, verbose_name=_('الأقسام المسموحة'))
    
    # إعدادات الجدولة
    is_schedulable = models.BooleanField(default=False, verbose_name=_('قابل للجدولة'))
    schedule_config = models.JSONField(default=dict, verbose_name=_('إعدادات الجدولة'))
    
    # معلومات إضافية
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_reports', verbose_name=_('أنشأ بواسطة'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    is_public = models.BooleanField(default=False, verbose_name=_('عام'))
    usage_count = models.PositiveIntegerField(default=0, verbose_name=_('عدد مرات الاستخدام'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('قالب التقرير')
        verbose_name_plural = _('قوالب التقارير')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def increment_usage(self):
        """زيادة عداد الاستخدام"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class ReportInstance(models.Model):
    """مثيلات التقارير المنفذة"""
    
    STATUS_CHOICES = [
        ('pending', _('في الانتظار')),
        ('processing', _('قيد المعالجة')),
        ('completed', _('مكتمل')),
        ('failed', _('فشل')),
        ('cancelled', _('ملغي')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='instances', verbose_name=_('القالب'))
    name = models.CharField(max_length=200, verbose_name=_('اسم المثيل'))
    
    # معاملات التنفيذ
    parameters = models.JSONField(default=dict, verbose_name=_('المعاملات'))
    filters_applied = models.JSONField(default=dict, verbose_name=_('الفلاتر المطبقة'))
    
    # معلومات التنفيذ
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_('بدء التنفيذ'))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('انتهاء التنفيذ'))
    execution_time = models.DurationField(null=True, blank=True, verbose_name=_('وقت التنفيذ'))
    
    # النتائج
    result_data = models.JSONField(default=dict, verbose_name=_('بيانات النتيجة'))
    record_count = models.PositiveIntegerField(default=0, verbose_name=_('عدد السجلات'))
    file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name=_('مسار الملف'))
    file_size = models.PositiveIntegerField(default=0, verbose_name=_('حجم الملف'))
    output_format = models.CharField(max_length=10, verbose_name=_('صيغة الإخراج'))
    
    # معلومات المستخدم
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_instances', verbose_name=_('أنشأ بواسطة'))
    is_shared = models.BooleanField(default=False, verbose_name=_('مشارك'))
    shared_with = models.JSONField(default=list, verbose_name=_('مشارك مع'))
    
    # رسائل الخطأ
    error_message = models.TextField(blank=True, null=True, verbose_name=_('رسالة الخطأ'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('مثيل التقرير')
        verbose_name_plural = _('مثيلات التقارير')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.template.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def mark_as_processing(self):
        """تحديد الحالة كقيد المعالجة"""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def mark_as_completed(self, file_path=None, record_count=0, file_size=0):
        """تحديد الحالة كمكتمل"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if self.started_at:
            self.execution_time = self.completed_at - self.started_at
        if file_path:
            self.file_path = file_path
        self.record_count = record_count
        self.file_size = file_size
        self.save(update_fields=['status', 'completed_at', 'execution_time', 'file_path', 'record_count', 'file_size'])

    def mark_as_failed(self, error_message):
        """تحديد الحالة كفشل"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message
        if self.started_at:
            self.execution_time = self.completed_at - self.started_at
        self.save(update_fields=['status', 'completed_at', 'execution_time', 'error_message'])


class ScheduledReport(models.Model):
    """التقارير المجدولة"""
    
    FREQUENCY_CHOICES = [
        ('daily', _('يومي')),
        ('weekly', _('أسبوعي')),
        ('monthly', _('شهري')),
        ('quarterly', _('ربع سنوي')),
        ('yearly', _('سنوي')),
        ('custom', _('مخصص')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='scheduled_reports', verbose_name=_('القالب'))
    name = models.CharField(max_length=200, verbose_name=_('اسم الجدولة'))
    
    # إعدادات الجدولة
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name=_('التكرار'))
    cron_expression = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('تعبير Cron'))
    next_run = models.DateTimeField(verbose_name=_('التشغيل التالي'))
    
    # إعدادات التنفيذ
    parameters = models.JSONField(default=dict, verbose_name=_('المعاملات'))
    output_format = models.CharField(max_length=10, verbose_name=_('صيغة الإخراج'))
    
    # إعدادات الإرسال
    email_recipients = models.JSONField(default=list, verbose_name=_('مستقبلي البريد الإلكتروني'))
    email_subject = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('موضوع البريد'))
    email_body = models.TextField(blank=True, null=True, verbose_name=_('نص البريد'))
    
    # معلومات التتبع
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_reports', verbose_name=_('أنشأ بواسطة'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    last_run = models.DateTimeField(null=True, blank=True, verbose_name=_('آخر تشغيل'))
    run_count = models.PositiveIntegerField(default=0, verbose_name=_('عدد مرات التشغيل'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('تقرير مجدول')
        verbose_name_plural = _('التقارير المجدولة')
        ordering = ['next_run']

    def __str__(self):
        return f"{self.template.name} - {self.frequency}"


class ReportFavorite(models.Model):
    """التقارير المفضلة للمستخدمين"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_reports', verbose_name=_('المستخدم'))
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='favorited_by', verbose_name=_('القالب'))
    parameters = models.JSONField(default=dict, verbose_name=_('المعاملات المحفوظة'))
    name = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('اسم مخصص'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإضافة'))

    class Meta:
        verbose_name = _('تقرير مفضل')
        verbose_name_plural = _('التقارير المفضلة')
        unique_together = ['user', 'template']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.template.name}"


class ReportShare(models.Model):
    """مشاركة التقارير"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.ForeignKey(ReportInstance, on_delete=models.CASCADE, related_name='shares', verbose_name=_('مثيل التقرير'))
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_reports', verbose_name=_('شارك بواسطة'))
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reports', verbose_name=_('مشارك مع'))
    message = models.TextField(blank=True, null=True, verbose_name=_('رسالة'))
    is_read = models.BooleanField(default=False, verbose_name=_('مقروء'))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_('ينتهي في'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ المشاركة'))

    class Meta:
        verbose_name = _('مشاركة تقرير')
        verbose_name_plural = _('مشاركات التقارير')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.shared_by.username} -> {self.shared_with.username}"

    def is_expired(self):
        """فحص انتهاء صلاحية المشاركة"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False