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
    timezone = models.CharField(max_length=50, default="Asia/Riyadh", verbose_name=_('المنطقة الزمنية'))
    date_format = models.CharField(max_length=50, default="Y-m-d", verbose_name=_('تنسيق التاريخ'))

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
