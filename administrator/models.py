from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django.conf import settings
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

class GroupProfile(models.Model):
    """
    معلومات إضافية للمجموعات.
    """
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='profile', verbose_name="المجموعة")
    description = models.TextField(blank=True, verbose_name="وصف المجموعة")

    def __str__(self):
        return self.group.name

    class Meta:
        verbose_name = "ملف المجموعة"
        verbose_name_plural = "ملفات المجموعات"

class SystemSettings(models.Model):
    """
    إعدادات النظام العامة التي يمكن تكوينها بواسطة المسؤول.
    يجب أن يوجد مثيل واحد فقط من هذا النموذج (singleton).
    """
    # إعدادات قاعدة البيانات
    db_host = models.CharField(max_length=255, verbose_name="قاعدة البيانات - المضيف")
    db_name = models.CharField(max_length=255, verbose_name="قاعدة البيانات - الاسم")
    db_user = models.CharField(max_length=255, verbose_name="قاعدة البيانات - اسم المستخدم")
    db_password = models.CharField(max_length=255, verbose_name="قاعدة البيانات - كلمة المرور")
    db_port = models.CharField(max_length=10, default='1433', verbose_name="قاعدة البيانات - المنفذ")

    # معلومات الشركة
    company_name = models.CharField(max_length=255, verbose_name="اسم الشركة")
    company_address = models.TextField(blank=True, verbose_name="عنوان الشركة")
    company_phone = models.CharField(max_length=50, blank=True, verbose_name="هاتف الشركة")
    company_email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني للشركة")
    company_website = models.URLField(blank=True, verbose_name="موقع الشركة الإلكتروني")
    company_logo = models.ImageField(upload_to='company/', blank=True, null=True, verbose_name="شعار الشركة")

    # تكوين النظام
    system_name = models.CharField(max_length=255, default="نظام الدولية", verbose_name="اسم النظام")
    enable_debugging = models.BooleanField(default=False, verbose_name="تفعيل وضع التصحيح")
    maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة")

    # إعدادات التاريخ والمنطقة الزمنية
    timezone = models.CharField(max_length=50, default="Asia/Riyadh", verbose_name="المنطقة الزمنية")
    date_format = models.CharField(max_length=50, default="Y-m-d", verbose_name="تنسيق التاريخ")

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

    # آخر تعديل
    last_modified = models.DateTimeField(auto_now=True, verbose_name="آخر تعديل")

    def __str__(self):
        return "إعدادات النظام"

    class Meta:
        verbose_name = "إعدادات النظام"
        verbose_name_plural = "إعدادات النظام"

    @classmethod
    def get_settings(cls):
        settings = cls.objects.first()
        if not settings:
            settings = cls.objects.create()
        return settings


class Department(models.Model):
    """
    الأقسام التي تظهر في شريط التنقل الجانبي.
    """
    name = models.CharField(max_length=100, verbose_name="اسم القسم")
    icon = models.CharField(max_length=50, verbose_name="أيقونة القسم",
                           help_text="اسم الأيقونة من Font Awesome مثال: fa-user")
    url_name = models.CharField(max_length=100, verbose_name="اسم الرابط",
                               help_text="الاسم المستخدم في الروابط")
    description = models.CharField(max_length=255, blank=True, verbose_name="وصف القسم")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    require_admin = models.BooleanField(default=False, verbose_name="يتطلب صلاحيات المدير")
    groups = models.ManyToManyField(Group, blank=True, related_name='allowed_departments', verbose_name="المجموعات المسموح لها")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "القسم"
        verbose_name_plural = "الأقسام"
        ordering = ['order']


class Module(models.Model):
    """
    الوحدات (الميزات/الروابط) المتاحة داخل كل قسم.
    """
    department = models.ForeignKey(Department, on_delete=models.CASCADE,
                                  related_name='modules', verbose_name="القسم")
    name = models.CharField(max_length=100, verbose_name="اسم الوحدة")
    icon = models.CharField(max_length=50, verbose_name="أيقونة الوحدة")
    url = models.CharField(max_length=255, verbose_name="رابط الوحدة")
    description = models.CharField(max_length=255, blank=True, verbose_name="وصف الوحدة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    bg_color = models.CharField(max_length=20, default="#3498db", verbose_name="لون الخلفية")
    require_admin = models.BooleanField(default=False, verbose_name="يتطلب صلاحيات المدير")
    groups = models.ManyToManyField(Group, blank=True, related_name='allowed_modules', verbose_name="المجموعات المسموح لها")

    def __str__(self):
        return f"{self.department.name} - {self.name}"

    class Meta:
        verbose_name = "الوحدة"
        verbose_name_plural = "الوحدات"
        ordering = ['department__order', 'order']










# Custom permission signal handlers removed as per user request to use only Django's basic permissions
