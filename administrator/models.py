from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

User = get_user_model()

# Non-permission related models added back
class UserGroup(models.Model):
    """
    عضوية المستخدمين في المجموعات مع معلومات إضافية مثل تاريخ الانضمام والملاحظات.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships', verbose_name="المستخدم")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='user_memberships', verbose_name="المجموعة")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الانضمام")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"

    class Meta:
        verbose_name = "عضوية مجموعة"
        verbose_name_plural = "عضويات المجموعات"
        unique_together = ['user', 'group']

class UserDepartmentPermission(models.Model):
    """
    صلاحيات المستخدمين على الأقسام.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='department_permissions', verbose_name="المستخدم")
    department = models.ForeignKey('Department', on_delete=models.CASCADE, verbose_name="القسم")
    can_view = models.BooleanField(default=True, verbose_name="عرض")

    def __str__(self):
        return f"{self.user.username} - {self.department.name}"

    class Meta:
        verbose_name = "صلاحية قسم"
        verbose_name_plural = "صلاحيات الأقسام"
        unique_together = ['user', 'department']

class UserModulePermission(models.Model):
    """
    صلاحيات المستخدمين على الوحدات (الميزات).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_permissions', verbose_name="المستخدم")
    module = models.ForeignKey('Module', on_delete=models.CASCADE, verbose_name="الوحدة")
    can_view = models.BooleanField(default=True, verbose_name="عرض")
    can_add = models.BooleanField(default=False, verbose_name="إضافة")
    can_edit = models.BooleanField(default=False, verbose_name="تعديل")
    can_delete = models.BooleanField(default=False, verbose_name="حذف")
    can_print = models.BooleanField(default=False, verbose_name="طباعة")

    def __str__(self):
        return f"{self.user.username} - {self.module.name}"

    class Meta:
        verbose_name = "صلاحية وحدة"
        verbose_name_plural = "صلاحيات الوحدات"
        unique_together = ['user', 'module']

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
