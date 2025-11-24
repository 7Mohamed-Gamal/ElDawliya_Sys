"""
نماذج نظام التقارير الشامل
=========================

يحتوي على نماذج إدارة التقارير والتصدير المختلفة
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date, datetime
import json

from employees.models import Employee
from org.models import Department


class ReportCategory(models.Model):
    """فئات التقارير"""
    CATEGORY_TYPES = [
        ('attendance', 'تقارير الحضور'),
        ('payroll', 'تقارير الرواتب'),
        ('leaves', 'تقارير الإجازات'),
        ('employees', 'تقارير الموظفين'),
        ('departments', 'تقارير الأقسام'),
        ('performance', 'تقارير الأداء'),
        ('training', 'تقارير التدريب'),
        ('disciplinary', 'تقارير التأديب'),
        ('loans', 'تقارير القروض'),
        ('insurance', 'تقارير التأمين'),
        ('analytics', 'تقارير تحليلية'),
    ]

    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='اسم الفئة')
    code = models.CharField(max_length=20, unique=True, verbose_name='رمز الفئة')
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, verbose_name='نوع الفئة')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    icon = models.CharField(max_length=50, default='fas fa-chart-bar', verbose_name='الأيقونة')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='اللون')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    sort_order = models.IntegerField(default=0, verbose_name='ترتيب العرض')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class"""
        verbose_name = 'فئة تقرير'
        verbose_name_plural = 'فئات التقارير'
        ordering = ['sort_order', 'name']

    def __str__(self):
        """__str__ function"""
        return self.name


class ReportTemplate(models.Model):
    """قوالب التقارير"""
    OUTPUT_FORMATS = [
        ('html', 'HTML'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]

    PARAMETER_TYPES = [
        ('date_range', 'نطاق تاريخ'),
        ('employee_filter', 'فلتر موظفين'),
        ('department_filter', 'فلتر أقسام'),
        ('status_filter', 'فلتر حالة'),
        ('custom_filter', 'فلتر مخصص'),
    ]

    template_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(ReportCategory, on_delete=models.CASCADE, verbose_name='الفئة')
    name = models.CharField(max_length=200, verbose_name='اسم التقرير')
    code = models.CharField(max_length=50, unique=True, verbose_name='رمز التقرير')
    description = models.TextField(verbose_name='وصف التقرير')

    # Report configuration
    query_sql = models.TextField(blank=True, null=True, verbose_name='استعلام SQL')
    python_code = models.TextField(blank=True, null=True, verbose_name='كود Python')
    template_file = models.CharField(max_length=200, blank=True, null=True, verbose_name='ملف القالب')

    # Parameters and filters
    parameters = models.JSONField(default=list, verbose_name='معاملات التقرير')
    default_filters = models.JSONField(default=dict, verbose_name='الفلاتر الافتراضية')

    # Output settings
    supported_formats = models.JSONField(default=list, verbose_name='الصيغ المدعومة')
    default_format = models.CharField(max_length=20, choices=OUTPUT_FORMATS, default='html', verbose_name='الصيغة الافتراضية')

    # Access control
    is_public = models.BooleanField(default=True, verbose_name='متاح للجميع')
    allowed_roles = models.JSONField(default=list, verbose_name='الأدوار المسموحة')
    allowed_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, verbose_name='المستخدمون المسموحون')

    # Metadata
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    is_featured = models.BooleanField(default=False, verbose_name='مميز')
    estimated_time = models.IntegerField(default=5, verbose_name='الوقت المتوقع (ثواني)')
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='أنشئ بواسطة')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class"""
        verbose_name = 'قالب تقرير'
        verbose_name_plural = 'قوالب التقارير'
        ordering = ['category', 'name']

    def __str__(self):
        """__str__ function"""
        return f"{self.category.name} - {self.name}"

    def get_parameters(self):
        """الحصول على معاملات التقرير"""
        return self.parameters or []

    def get_supported_formats(self):
        """الحصول على الصيغ المدعومة"""
        return self.supported_formats or ['html']


class ReportSchedule(models.Model):
    """جدولة التقارير"""
    FREQUENCY_CHOICES = [
        ('once', 'مرة واحدة'),
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري'),
        ('quarterly', 'ربع سنوي'),
        ('yearly', 'سنوي'),
    ]

    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('paused', 'متوقف'),
        ('completed', 'مكتمل'),
        ('error', 'خطأ'),
    ]

    schedule_id = models.AutoField(primary_key=True)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, verbose_name='قالب التقرير')
    name = models.CharField(max_length=200, verbose_name='اسم الجدولة')

    # Schedule settings
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name='التكرار')
    start_date = models.DateTimeField(verbose_name='تاريخ البداية')
    end_date = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ النهاية')
    next_run = models.DateTimeField(verbose_name='التشغيل التالي')

    # Report parameters
    parameters = models.JSONField(default=dict, verbose_name='معاملات التقرير')
    output_format = models.CharField(max_length=20, default='pdf', verbose_name='صيغة الإخراج')

    # Email settings
    email_recipients = models.JSONField(default=list, verbose_name='مستقبلو البريد')
    email_subject = models.CharField(max_length=200, blank=True, verbose_name='موضوع البريد')
    email_body = models.TextField(blank=True, verbose_name='محتوى البريد')

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='الحالة')
    last_run = models.DateTimeField(blank=True, null=True, verbose_name='آخر تشغيل')
    run_count = models.IntegerField(default=0, verbose_name='عدد مرات التشغيل')
    error_count = models.IntegerField(default=0, verbose_name='عدد الأخطاء')
    last_error = models.TextField(blank=True, null=True, verbose_name='آخر خطأ')

    # Metadata
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='أنشئ بواسطة')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class"""
        verbose_name = 'جدولة تقرير'
        verbose_name_plural = 'جدولة التقارير'
        ordering = ['-created_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.name} - {self.get_frequency_display()}"


class GeneratedReport(models.Model):
    """التقارير المُنتجة"""
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('processing', 'جاري المعالجة'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
        ('expired', 'منتهي الصلاحية'),
    ]

    report_id = models.AutoField(primary_key=True)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, verbose_name='قالب التقرير')
    schedule = models.ForeignKey(ReportSchedule, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='الجدولة')

    # Generation details
    name = models.CharField(max_length=200, verbose_name='اسم التقرير')
    parameters = models.JSONField(default=dict, verbose_name='معاملات التقرير')
    output_format = models.CharField(max_length=20, verbose_name='صيغة الإخراج')

    # File information
    file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name='مسار الملف')
    file_size = models.BigIntegerField(default=0, verbose_name='حجم الملف (بايت)')
    download_count = models.IntegerField(default=0, verbose_name='عدد مرات التحميل')

    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    started_at = models.DateTimeField(blank=True, null=True, verbose_name='بدء التنفيذ')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='انتهاء التنفيذ')
    execution_time = models.FloatField(default=0, verbose_name='وقت التنفيذ (ثانية)')
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ انتهاء الصلاحية')

    # Error handling
    error_message = models.TextField(blank=True, null=True, verbose_name='رسالة الخطأ')
    error_details = models.JSONField(default=dict, verbose_name='تفاصيل الخطأ')

    # Metadata
    generated_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='أُنتج بواسطة')
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنتاج')

    class Meta:
        """Meta class"""
        verbose_name = 'تقرير منتج'
        verbose_name_plural = 'التقارير المنتجة'
        ordering = ['-generated_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.name} - {self.get_status_display()}"

    @property
    def is_expired(self):
        """فحص انتهاء صلاحية التقرير"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def duration_display(self):
        """عرض مدة التنفيذ"""
        if self.execution_time:
            if self.execution_time < 60:
                return f"{self.execution_time:.1f} ثانية"
            else:
                minutes = self.execution_time / 60
                return f"{minutes:.1f} دقيقة"
        return "غير محدد"


class ReportAccessLog(models.Model):
    """سجل الوصول للتقارير"""
    ACCESS_TYPES = [
        ('view', 'عرض'),
        ('download', 'تحميل'),
        ('export', 'تصدير'),
        ('schedule', 'جدولة'),
        ('share', 'مشاركة'),
    ]

    log_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(GeneratedReport, on_delete=models.CASCADE, verbose_name='التقرير')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='المستخدم')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='الموظف')

    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES, verbose_name='نوع الوصول')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='عنوان IP')
    user_agent = models.TextField(blank=True, null=True, verbose_name='معرف المتصفح')

    # Additional data
    parameters = models.JSONField(default=dict, verbose_name='معاملات إضافية')
    success = models.BooleanField(default=True, verbose_name='نجح الوصول')
    error_message = models.TextField(blank=True, null=True, verbose_name='رسالة الخطأ')

    accessed_at = models.DateTimeField(auto_now_add=True, verbose_name='وقت الوصول')

    class Meta:
        """Meta class"""
        verbose_name = 'سجل وصول تقرير'
        verbose_name_plural = 'سجلات الوصول للتقارير'
        ordering = ['-accessed_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.user} - {self.get_access_type_display()} - {self.accessed_at}"


class ReportDashboard(models.Model):
    """لوحات تحكم التقارير"""
    dashboard_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='اسم لوحة التحكم')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')

    # Layout and configuration
    layout = models.JSONField(default=dict, verbose_name='تخطيط لوحة التحكم')
    widgets = models.JSONField(default=list, verbose_name='الودجات')
    refresh_interval = models.IntegerField(default=300, verbose_name='فترة التحديث (ثانية)')

    # Access control
    is_public = models.BooleanField(default=False, verbose_name='متاح للجميع')
    owner = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='المالك')
    shared_with = models.ManyToManyField(Employee, blank=True, related_name='shared_dashboards', verbose_name='مشارك مع')

    # Metadata
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    is_default = models.BooleanField(default=False, verbose_name='افتراضية')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class"""
        verbose_name = 'لوحة تحكم تقارير'
        verbose_name_plural = 'لوحات تحكم التقارير'
        ordering = ['name']

    def __str__(self):
        """__str__ function"""
        return self.name
