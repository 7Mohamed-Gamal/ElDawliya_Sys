"""
نماذج التكامل مع الأنظمة الخارجية
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import URLValidator
import uuid
import json


class ExternalSystem(models.Model):
    """الأنظمة الخارجية"""
    
    SYSTEM_TYPES = [
        ('attendance_device', _('جهاز حضور')),
        ('accounting_system', _('نظام محاسبة')),
        ('email_service', _('خدمة بريد إلكتروني')),
        ('payroll_system', _('نظام رواتب')),
        ('hr_system', _('نظام موارد بشرية')),
        ('erp_system', _('نظام تخطيط موارد')),
        ('time_tracking', _('تتبع الوقت')),
        ('document_management', _('إدارة الوثائق')),
        ('backup_service', _('خدمة النسخ الاحتياطي')),
        ('reporting_tool', _('أداة التقارير')),
    ]
    
    CONNECTION_TYPES = [
        ('api', _('API')),
        ('database', _('قاعدة بيانات')),
        ('file_transfer', _('نقل ملفات')),
        ('web_service', _('خدمة ويب')),
        ('tcp_socket', _('TCP Socket')),
        ('serial_port', _('منفذ تسلسلي')),
        ('webhook', _('Webhook')),
        ('sftp', _('SFTP')),
        ('email', _('بريد إلكتروني')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('error', _('خطأ')),
        ('maintenance', _('صيانة')),
        ('testing', _('اختبار')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات النظام
    name = models.CharField(_('اسم النظام'), max_length=200)
    description = models.TextField(_('الوصف'), blank=True)
    system_type = models.CharField(
        _('نوع النظام'),
        max_length=50,
        choices=SYSTEM_TYPES
    )
    
    # معلومات الاتصال
    connection_type = models.CharField(
        _('نوع الاتصال'),
        max_length=50,
        choices=CONNECTION_TYPES
    )
    endpoint_url = models.URLField(_('رابط النقطة'), blank=True)
    host = models.CharField(_('المضيف'), max_length=255, blank=True)
    port = models.PositiveIntegerField(_('المنفذ'), null=True, blank=True)
    
    # بيانات الاعتماد
    username = models.CharField(_('اسم المستخدم'), max_length=255, blank=True)
    password = models.CharField(_('كلمة المرور'), max_length=255, blank=True)
    api_key = models.TextField(_('مفتاح API'), blank=True)
    token = models.TextField(_('الرمز المميز'), blank=True)
    
    # إعدادات الاتصال
    timeout = models.PositiveIntegerField(_('مهلة الاتصال (ثانية)'), default=30)
    retry_attempts = models.PositiveIntegerField(_('محاولات الإعادة'), default=3)
    retry_delay = models.PositiveIntegerField(_('تأخير الإعادة (ثانية)'), default=5)
    
    # إعدادات إضافية
    configuration = models.JSONField(
        _('الإعدادات'),
        default=dict,
        blank=True,
        help_text=_('إعدادات إضافية خاصة بالنظام')
    )
    
    # الحالة والمراقبة
    status = models.CharField(
        _('الحالة'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='inactive'
    )
    
    last_sync_at = models.DateTimeField(_('آخر مزامنة'), null=True, blank=True)
    last_error = models.TextField(_('آخر خطأ'), blank=True)
    
    # إعدادات المزامنة
    auto_sync_enabled = models.BooleanField(_('المزامنة التلقائية'), default=False)
    sync_interval = models.PositiveIntegerField(
        _('فترة المزامنة (دقائق)'),
        default=60
    )
    
    # الصلاحيات
    is_active = models.BooleanField(_('نشط'), default=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_external_systems',
        verbose_name=_('منشئ النظام')
    )
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('نظام خارجي')
        verbose_name_plural = _('الأنظمة الخارجية')
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.get_system_type_display()})"
clas
s IntegrationMapping(models.Model):
    """خريطة التكامل بين الحقول"""
    
    MAPPING_TYPES = [
        ('field_mapping', _('ربط حقول')),
        ('data_transformation', _('تحويل بيانات')),
        ('validation_rule', _('قاعدة تحقق')),
        ('calculation', _('حساب')),
        ('lookup', _('بحث')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    external_system = models.ForeignKey(
        ExternalSystem,
        on_delete=models.CASCADE,
        related_name='mappings',
        verbose_name=_('النظام الخارجي')
    )
    
    # معلومات الربط
    mapping_name = models.CharField(_('اسم الربط'), max_length=200)
    mapping_type = models.CharField(
        _('نوع الربط'),
        max_length=50,
        choices=MAPPING_TYPES
    )
    
    # الحقل المحلي
    local_model = models.CharField(_('النموذج المحلي'), max_length=100)
    local_field = models.CharField(_('الحقل المحلي'), max_length=100)
    
    # الحقل الخارجي
    external_field = models.CharField(_('الحقل الخارجي'), max_length=100)
    external_format = models.CharField(_('تنسيق خارجي'), max_length=100, blank=True)
    
    # قواعد التحويل
    transformation_rules = models.JSONField(
        _('قواعد التحويل'),
        default=dict,
        blank=True,
        help_text=_('قواعد تحويل البيانات')
    )
    
    # اتجاه المزامنة
    sync_direction = models.CharField(
        _('اتجاه المزامنة'),
        max_length=20,
        choices=[
            ('import', _('استيراد')),
            ('export', _('تصدير')),
            ('bidirectional', _('ثنائي الاتجاه')),
        ],
        default='bidirectional'
    )
    
    # الحالة
    is_active = models.BooleanField(_('نشط'), default=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('خريطة التكامل')
        verbose_name_plural = _('خرائط التكامل')
        unique_together = ['external_system', 'mapping_name']
        
    def __str__(self):
        return f"{self.mapping_name} - {self.external_system.name}"


class SyncJob(models.Model):
    """مهام المزامنة"""
    
    JOB_TYPES = [
        ('manual', _('يدوي')),
        ('scheduled', _('مجدول')),
        ('triggered', _('مُفعل')),
        ('real_time', _('فوري')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('في الانتظار')),
        ('running', _('قيد التشغيل')),
        ('completed', _('مكتمل')),
        ('failed', _('فشل')),
        ('cancelled', _('ملغي')),
        ('partial', _('جزئي')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    external_system = models.ForeignKey(
        ExternalSystem,
        on_delete=models.CASCADE,
        related_name='sync_jobs',
        verbose_name=_('النظام الخارجي')
    )
    
    # معلومات المهمة
    job_name = models.CharField(_('اسم المهمة'), max_length=200)
    job_type = models.CharField(
        _('نوع المهمة'),
        max_length=20,
        choices=JOB_TYPES
    )
    
    # المعايير
    sync_criteria = models.JSONField(
        _('معايير المزامنة'),
        default=dict,
        blank=True,
        help_text=_('معايير تحديد البيانات للمزامنة')
    )
    
    # الحالة والتقدم
    status = models.CharField(
        _('الحالة'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    progress_percentage = models.PositiveIntegerField(_('نسبة التقدم'), default=0)
    
    # الإحصائيات
    total_records = models.PositiveIntegerField(_('إجمالي السجلات'), default=0)
    processed_records = models.PositiveIntegerField(_('السجلات المعالجة'), default=0)
    successful_records = models.PositiveIntegerField(_('السجلات الناجحة'), default=0)
    failed_records = models.PositiveIntegerField(_('السجلات الفاشلة'), default=0)
    
    # التوقيت
    scheduled_at = models.DateTimeField(_('موعد التشغيل'), null=True, blank=True)
    started_at = models.DateTimeField(_('بداية التشغيل'), null=True, blank=True)
    completed_at = models.DateTimeField(_('انتهاء التشغيل'), null=True, blank=True)
    
    # السجلات والأخطاء
    log_data = models.JSONField(
        _('بيانات السجل'),
        default=list,
        blank=True
    )
    error_details = models.TextField(_('تفاصيل الأخطاء'), blank=True)
    
    # المستخدم
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sync_jobs',
        verbose_name=_('منشئ المهمة')
    )
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('مهمة المزامنة')
        verbose_name_plural = _('مهام المزامنة')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.job_name} - {self.external_system.name}"


class DataImportTemplate(models.Model):
    """قوالب استيراد البيانات"""
    
    IMPORT_FORMATS = [
        ('excel', _('Excel')),
        ('csv', _('CSV')),
        ('json', _('JSON')),
        ('xml', _('XML')),
        ('txt', _('نص')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات القالب
    name = models.CharField(_('اسم القالب'), max_length=200)
    description = models.TextField(_('الوصف'), blank=True)
    
    # تنسيق الاستيراد
    import_format = models.CharField(
        _('تنسيق الاستيراد'),
        max_length=20,
        choices=IMPORT_FORMATS
    )
    
    # النموذج المستهدف
    target_model = models.CharField(_('النموذج المستهدف'), max_length=100)
    
    # خريطة الحقول
    field_mapping = models.JSONField(
        _('خريطة الحقول'),
        default=dict,
        help_text=_('ربط حقول الملف بحقول النموذج')
    )
    
    # قواعد التحقق
    validation_rules = models.JSONField(
        _('قواعد التحقق'),
        default=dict,
        blank=True,
        help_text=_('قواعد التحقق من صحة البيانات')
    )
    
    # إعدادات الاستيراد
    import_settings = models.JSONField(
        _('إعدادات الاستيراد'),
        default=dict,
        blank=True,
        help_text=_('إعدادات إضافية للاستيراد')
    )
    
    # ملف القالب
    template_file = models.FileField(
        _('ملف القالب'),
        upload_to='import_templates/',
        blank=True,
        help_text=_('ملف قالب للتحميل')
    )
    
    # الحالة
    is_active = models.BooleanField(_('نشط'), default=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='import_templates',
        verbose_name=_('منشئ القالب')
    )
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('قالب استيراد البيانات')
        verbose_name_plural = _('قوالب استيراد البيانات')
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.get_import_format_display()})"


class ImportJob(models.Model):
    """مهام استيراد البيانات"""
    
    STATUS_CHOICES = [
        ('pending', _('في الانتظار')),
        ('processing', _('قيد المعالجة')),
        ('validating', _('قيد التحقق')),
        ('importing', _('قيد الاستيراد')),
        ('completed', _('مكتمل')),
        ('failed', _('فشل')),
        ('cancelled', _('ملغي')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    template = models.ForeignKey(
        DataImportTemplate,
        on_delete=models.CASCADE,
        related_name='import_jobs',
        verbose_name=_('القالب')
    )
    
    # ملف البيانات
    data_file = models.FileField(
        _('ملف البيانات'),
        upload_to='import_data/'
    )
    
    # الحالة والتقدم
    status = models.CharField(
        _('الحالة'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    progress_percentage = models.PositiveIntegerField(_('نسبة التقدم'), default=0)
    
    # الإحصائيات
    total_rows = models.PositiveIntegerField(_('إجمالي الصفوف'), default=0)
    processed_rows = models.PositiveIntegerField(_('الصفوف المعالجة'), default=0)
    successful_rows = models.PositiveIntegerField(_('الصفوف الناجحة'), default=0)
    failed_rows = models.PositiveIntegerField(_('الصفوف الفاشلة'), default=0)
    
    # التوقيت
    started_at = models.DateTimeField(_('بداية المعالجة'), null=True, blank=True)
    completed_at = models.DateTimeField(_('انتهاء المعالجة'), null=True, blank=True)
    
    # السجلات والأخطاء
    validation_errors = models.JSONField(
        _('أخطاء التحقق'),
        default=list,
        blank=True
    )
    import_errors = models.JSONField(
        _('أخطاء الاستيراد'),
        default=list,
        blank=True
    )
    
    # تقرير النتائج
    result_summary = models.JSONField(
        _('ملخص النتائج'),
        default=dict,
        blank=True
    )
    
    # المستخدم
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='import_jobs',
        verbose_name=_('منشئ المهمة')
    )
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('مهمة استيراد البيانات')
        verbose_name_plural = _('مهام استيراد البيانات')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"استيراد {self.template.name} - {self.created_at.strftime('%Y-%m-%d')}"


class EmailTemplate(models.Model):
    """قوالب البريد الإلكتروني"""
    
    TEMPLATE_TYPES = [
        ('notification', _('إشعار')),
        ('welcome', _('ترحيب')),
        ('reminder', _('تذكير')),
        ('report', _('تقرير')),
        ('alert', _('تنبيه')),
        ('newsletter', _('نشرة إخبارية')),
        ('invitation', _('دعوة')),
        ('confirmation', _('تأكيد')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات القالب
    name = models.CharField(_('اسم القالب'), max_length=200)
    description = models.TextField(_('الوصف'), blank=True)
    template_type = models.CharField(
        _('نوع القالب'),
        max_length=20,
        choices=TEMPLATE_TYPES
    )
    
    # محتوى البريد
    subject_template = models.CharField(_('قالب الموضوع'), max_length=500)
    html_content = models.TextField(_('المحتوى HTML'))
    text_content = models.TextField(_('المحتوى النصي'), blank=True)
    
    # إعدادات الإرسال
    from_email = models.EmailField(_('من البريد'), blank=True)
    reply_to = models.EmailField(_('الرد إلى'), blank=True)
    
    # المتغيرات المتاحة
    available_variables = models.JSONField(
        _('المتغيرات المتاحة'),
        default=list,
        blank=True,
        help_text=_('قائمة بالمتغيرات المتاحة في القالب')
    )
    
    # المرفقات الافتراضية
    default_attachments = models.JSONField(
        _('المرفقات الافتراضية'),
        default=list,
        blank=True
    )
    
    # الحالة
    is_active = models.BooleanField(_('نشط'), default=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='email_templates',
        verbose_name=_('منشئ القالب')
    )
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('قالب البريد الإلكتروني')
        verbose_name_plural = _('قوالب البريد الإلكتروني')
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"