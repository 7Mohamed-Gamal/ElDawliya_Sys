from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group

class SystemSettings(models.Model):
    """
    System-wide settings for the application
    """
    # قاعدة البيانات
    db_host = models.CharField(max_length=255, default='localhost', verbose_name=_('مضيف قاعدة البيانات'))
    db_name = models.CharField(max_length=255, default='eldawliya_db', verbose_name=_('اسم قاعدة البيانات'))
    db_user = models.CharField(max_length=255, default='root', verbose_name=_('مستخدم قاعدة البيانات'))
    db_password = models.CharField(max_length=255, blank=True, verbose_name=_('كلمة مرور قاعدة البيانات'))
    db_port = models.CharField(max_length=10, default='3306', verbose_name=_('منفذ قاعدة البيانات'))

    # معلومات الشركة
    company_name = models.CharField(max_length=255, default="الشركة الدولية", verbose_name=_('اسم الشركة'))
    company_address = models.TextField(blank=True, verbose_name=_('عنوان الشركة'))
    company_phone = models.CharField(max_length=20, blank=True, verbose_name=_('هاتف الشركة'))
    company_email = models.EmailField(blank=True, verbose_name=_('البريد الإلكتروني للشركة'))
    company_website = models.URLField(blank=True, verbose_name=_('موقع الشركة'))
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, verbose_name=_('شعار الشركة'))

    # إعدادات النظام
    system_name = models.CharField(max_length=255, default="نظام الدولية", verbose_name=_('اسم النظام'))
    enable_debugging = models.BooleanField(default=False, verbose_name=_('تفعيل وضع التصحيح'))
    maintenance_mode = models.BooleanField(default=False, verbose_name=_('وضع الصيانة'))

    # إعدادات التاريخ والمنطقة الزمنية
    TIMEZONE_CHOICES = [
        ('Asia/Riyadh', 'الرياض (Asia/Riyadh)'),
        ('Asia/Dubai', 'دبي (Asia/Dubai)'),
        ('Asia/Kuwait', 'الكويت (Asia/Kuwait)'),
        ('Asia/Qatar', 'قطر (Asia/Qatar)'),
        ('Asia/Bahrain', 'البحرين (Asia/Bahrain)'),
        ('Africa/Cairo', 'القاهرة (Africa/Cairo)'),
        ('UTC', 'التوقيت العالمي (UTC)'),
    ]

    DATE_FORMAT_CHOICES = [
        ('Y-m-d', 'YYYY-MM-DD (2024-01-15)'),
        ('d/m/Y', 'DD/MM/YYYY (15/01/2024)'),
        ('m/d/Y', 'MM/DD/YYYY (01/15/2024)'),
        ('d-m-Y', 'DD-MM-YYYY (15-01-2024)'),
    ]

    timezone = models.CharField(
        max_length=50,
        choices=TIMEZONE_CHOICES,
        default="Asia/Riyadh",
        verbose_name=_('المنطقة الزمنية')
    )
    date_format = models.CharField(
        max_length=50,
        choices=DATE_FORMAT_CHOICES,
        default="Y-m-d",
        verbose_name=_('تنسيق التاريخ')
    )

    # إعدادات اللغة وواجهة المستخدم
    LANGUAGE_CHOICES = [
        ('ar', 'العربية'),
        ('en', 'English'),
    ]

    FONT_CHOICES = [
        ('cairo', 'Cairo'),
        ('tajawal', 'Tajawal'),
        ('almarai', 'Almarai'),
        ('ibm-plex-sans-arabic', 'IBM Plex Sans Arabic'),
        ('noto-sans-arabic', 'Noto Sans Arabic'),
    ]

    DIRECTION_CHOICES = [
        ('rtl', 'من اليمين إلى اليسار'),
        ('ltr', 'من اليسار إلى اليمين'),
    ]

    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='ar',
        verbose_name=_('لغة النظام')
    )

    font_family = models.CharField(
        max_length=50,
        choices=FONT_CHOICES,
        default='cairo',
        verbose_name=_('الخط المستخدم')
    )

    text_direction = models.CharField(
        max_length=3,
        choices=DIRECTION_CHOICES,
        default='rtl',
        verbose_name=_('اتجاه النص')
    )

    # تاريخ آخر تعديل
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('آخر تحديث'))

    class Meta:
        verbose_name = _('إعدادات النظام')
        verbose_name_plural = _('إعدادات النظام')

    def __str__(self):
        return f"{self.system_name} ({self.company_name})"

class Department(models.Model):
    """System navigation department model"""
    name = models.CharField(max_length=100, verbose_name=_('اسم القسم'))
    icon = models.CharField(max_length=50, verbose_name=_('أيقونة القسم'), help_text=_('اسم الأيقونة من Font Awesome مثال: fa-user'))
    url_name = models.CharField(max_length=100, verbose_name=_('اسم الرابط'), help_text=_('الاسم المستخدم في الروابط'))
    description = models.CharField(max_length=255, blank=True, verbose_name=_('وصف القسم'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    order = models.IntegerField(default=0, verbose_name=_('الترتيب'))
    require_admin = models.BooleanField(default=False, verbose_name=_('يتطلب صلاحيات المدير'))
    groups = models.ManyToManyField(Group, blank=True, related_name='allowed_departments', verbose_name=_('المجموعات المسموح لها'))

    class Meta:
        verbose_name = _('القسم')
        verbose_name_plural = _('الأقسام')
        ordering = ['order']

    def __str__(self):
        return self.name

class Module(models.Model):
    """System navigation module model"""
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='modules', verbose_name=_('القسم'))
    name = models.CharField(max_length=100, verbose_name=_('اسم الوحدة'))
    icon = models.CharField(max_length=50, verbose_name=_('أيقونة الوحدة'))
    url = models.CharField(max_length=200, verbose_name=_('رابط الوحدة'))
    description = models.CharField(max_length=255, blank=True, verbose_name=_('وصف الوحدة'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    order = models.IntegerField(default=0, verbose_name=_('الترتيب'))
    bg_color = models.CharField(max_length=20, default='#3498db', verbose_name=_('لون الخلفية'))
    require_admin = models.BooleanField(default=False, verbose_name=_('يتطلب صلاحيات المدير'))
    groups = models.ManyToManyField(Group, blank=True, related_name='allowed_modules', verbose_name=_('المجموعات المسموح لها'))

    class Meta:
        verbose_name = _('الوحدة')
        verbose_name_plural = _('الوحدات')
        ordering = ['department__order', 'order']

    def __str__(self):
        return f"{self.department.name} - {self.name}"
