"""
نماذج الإعدادات والتكوين
Settings and Configuration Models
"""
import json
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .base import BaseModel

User = get_user_model()


class SystemSetting(BaseModel):
    """
    إعدادات النظام المركزية
    Central system settings and configuration
    """
    SETTING_TYPES = [
        ('string', _('نص')),
        ('integer', _('رقم صحيح')),
        ('float', _('رقم عشري')),
        ('boolean', _('منطقي')),
        ('json', _('JSON')),
        ('date', _('تاريخ')),
        ('datetime', _('تاريخ ووقت')),
        ('email', _('بريد إلكتروني')),
        ('url', _('رابط')),
        ('file', _('ملف')),
        ('image', _('صورة')),
        ('color', _('لون')),
    ]

    CATEGORIES = [
        ('general', _('عام')),
        ('security', _('الأمان')),
        ('email', _('البريد الإلكتروني')),
        ('sms', _('الرسائل النصية')),
        ('notifications', _('الإشعارات')),
        ('backup', _('النسخ الاحتياطي')),
        ('integration', _('التكامل')),
        ('ui', _('واجهة المستخدم')),
        ('reports', _('التقارير')),
        ('hr', _('الموارد البشرية')),
        ('inventory', _('المخزون')),
        ('finance', _('المالية')),
        ('projects', _('المشاريع')),
    ]

    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('المفتاح'),
        help_text=_('المفتاح الفريد للإعداد')
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('الاسم'),
        help_text=_('الاسم المعروض للإعداد')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('الوصف'),
        help_text=_('وصف تفصيلي للإعداد')
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORIES,
        default='general',
        verbose_name=_('الفئة')
    )
    setting_type = models.CharField(
        max_length=20,
        choices=SETTING_TYPES,
        default='string',
        verbose_name=_('نوع الإعداد')
    )
    value = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('القيمة'),
        help_text=_('قيمة الإعداد')
    )
    default_value = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('القيمة الافتراضية'),
        help_text=_('القيمة الافتراضية للإعداد')
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name=_('مطلوب'),
        help_text=_('هل هذا الإعداد مطلوب')
    )
    is_sensitive = models.BooleanField(
        default=False,
        verbose_name=_('حساس'),
        help_text=_('هل هذا الإعداد حساس (كلمة مرور، مفتاح API، إلخ)')
    )
    validation_rules = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('قواعد التحقق'),
        help_text=_('قواعد التحقق من صحة القيمة')
    )
    choices = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('الخيارات'),
        help_text=_('قائمة الخيارات المتاحة (للقوائم المنسدلة)')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('الترتيب'),
        help_text=_('ترتيب عرض الإعداد')
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name=_('إعداد النظام'),
        help_text=_('هل هذا إعداد أساسي في النظام')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('إعداد النظام')
        verbose_name_plural = _('إعدادات النظام')
        ordering = ['category', 'order', 'name']

    def __str__(self):
        """__str__ function"""
        return f"{self.name} ({self.key})"

    def clean(self):
        """Validate the setting value"""
        if self.is_required and not self.value:
            raise ValidationError(_('هذا الإعداد مطلوب'))

        if self.value:
            self._validate_value()

    def _validate_value(self):
        """Validate value based on setting type"""
        try:
            if self.setting_type == 'integer':
                int(self.value)
            elif self.setting_type == 'float':
                float(self.value)
            elif self.setting_type == 'boolean':
                if self.value.lower() not in ['true', 'false', '1', '0']:
                    raise ValueError()
            elif self.setting_type == 'json':
                json.loads(self.value)
            elif self.setting_type == 'email':
                from django.core.validators import validate_email
                validate_email(self.value)
            elif self.setting_type == 'url':
                from django.core.validators import URLValidator
                URLValidator()(self.value)
        except (ValueError, ValidationError) as e:
            raise ValidationError(
                _('قيمة غير صحيحة لنوع الإعداد %(type)s') %
                {'type': self.get_setting_type_display()}
            )

    def get_typed_value(self):
        """Get the value converted to the appropriate type"""
        if not self.value:
            return self.get_typed_default_value()

        try:
            if self.setting_type == 'integer':
                return int(self.value)
            elif self.setting_type == 'float':
                return float(self.value)
            elif self.setting_type == 'boolean':
                return self.value.lower() in ['true', '1']
            elif self.setting_type == 'json':
                return json.loads(self.value)
            else:
                return self.value
        except (ValueError, json.JSONDecodeError):
            return self.get_typed_default_value()

    def get_typed_default_value(self):
        """Get the default value converted to the appropriate type"""
        if not self.default_value:
            return None

        try:
            if self.setting_type == 'integer':
                return int(self.default_value)
            elif self.setting_type == 'float':
                return float(self.default_value)
            elif self.setting_type == 'boolean':
                return self.default_value.lower() in ['true', '1']
            elif self.setting_type == 'json':
                return json.loads(self.default_value)
            else:
                return self.default_value
        except (ValueError, json.JSONDecodeError):
            return None

    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value by key"""
        try:
            setting = cls.objects.get(key=key, is_active=True)
            return setting.get_typed_value()
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_setting(cls, key, value, user=None):
        """Set a setting value by key"""
        try:
            setting = cls.objects.get(key=key)
            setting.value = str(value)
            if user:
                setting.updated_by = user
            setting.save()
            return setting
        except cls.DoesNotExist:
            raise ValueError(f"Setting with key '{key}' does not exist")


class UserPreference(BaseModel):
    """
    تفضيلات المستخدم الشخصية
    User personal preferences and settings
    """
    PREFERENCE_TYPES = [
        ('string', _('نص')),
        ('integer', _('رقم صحيح')),
        ('boolean', _('منطقي')),
        ('json', _('JSON')),
        ('color', _('لون')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferences',
        verbose_name=_('المستخدم')
    )
    key = models.CharField(
        max_length=100,
        verbose_name=_('المفتاح'),
        help_text=_('مفتاح التفضيل')
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('الاسم'),
        help_text=_('اسم التفضيل')
    )
    preference_type = models.CharField(
        max_length=20,
        choices=PREFERENCE_TYPES,
        default='string',
        verbose_name=_('نوع التفضيل')
    )
    value = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('القيمة')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('تفضيل المستخدم')
        verbose_name_plural = _('تفضيلات المستخدمين')
        unique_together = ['user', 'key']
        ordering = ['user__username', 'name']

    def __str__(self):
        """__str__ function"""
        return f"{self.user.username} - {self.name}"

    def get_typed_value(self):
        """Get the value converted to the appropriate type"""
        if not self.value:
            return None

        try:
            if self.preference_type == 'integer':
                return int(self.value)
            elif self.preference_type == 'boolean':
                return self.value.lower() in ['true', '1']
            elif self.preference_type == 'json':
                return json.loads(self.value)
            else:
                return self.value
        except (ValueError, json.JSONDecodeError):
            return None

    @classmethod
    def get_preference(cls, user, key, default=None):
        """Get a user preference by key"""
        try:
            preference = cls.objects.get(user=user, key=key, is_active=True)
            return preference.get_typed_value()
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_preference(cls, user, key, value, name=None, preference_type='string'):
        """Set a user preference"""
        preference, created = cls.objects.get_or_create(
            user=user,
            key=key,
            defaults={
                'name': name or key,
                'preference_type': preference_type,
                'value': str(value),
                'created_by': user,
                'updated_by': user,
            }
        )

        if not created:
            preference.value = str(value)
            preference.updated_by = user
            preference.save()

        return preference


class CompanyProfile(BaseModel):
    """
    ملف الشركة
    Company profile and basic information
    """
    name = models.CharField(
        max_length=200,
        verbose_name=_('اسم الشركة')
    )
    name_en = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('اسم الشركة بالإنجليزية')
    )
    commercial_registration = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('السجل التجاري')
    )
    tax_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('الرقم الضريبي')
    )
    logo = models.ImageField(
        upload_to='company/logos/',
        blank=True,
        null=True,
        verbose_name=_('شعار الشركة')
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('الموقع الإلكتروني')
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('البريد الإلكتروني')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('رقم الهاتف')
    )
    fax = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('رقم الفاكس')
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('العنوان')
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('المدينة')
    )
    country = models.CharField(
        max_length=100,
        default='السعودية',
        verbose_name=_('البلد')
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('الرمز البريدي')
    )
    established_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ التأسيس')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('وصف الشركة')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('ملف الشركة')
        verbose_name_plural = _('ملفات الشركات')

    def __str__(self):
        """__str__ function"""
        return self.name

    @classmethod
    def get_company(cls):
        """Get the main company profile"""
        return cls.objects.filter(is_active=True).first()


class NotificationTemplate(BaseModel):
    """
    قوالب الإشعارات
    Notification templates for system messages
    """
    TEMPLATE_TYPES = [
        ('email', _('بريد إلكتروني')),
        ('sms', _('رسالة نصية')),
        ('in_app', _('داخل التطبيق')),
        ('push', _('إشعار فوري')),
    ]

    PRIORITY_LEVELS = [
        ('low', _('منخفض')),
        ('normal', _('عادي')),
        ('high', _('عالي')),
        ('urgent', _('عاجل')),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('اسم القالب')
    )
    display_name = models.CharField(
        max_length=200,
        verbose_name=_('الاسم المعروض')
    )
    template_type = models.CharField(
        max_length=20,
        choices=TEMPLATE_TYPES,
        verbose_name=_('نوع القالب')
    )
    subject_template = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('قالب العنوان'),
        help_text=_('قالب عنوان الإشعار (للبريد الإلكتروني)')
    )
    message_template = models.TextField(
        verbose_name=_('قالب الرسالة'),
        help_text=_('قالب محتوى الإشعار مع متغيرات Django')
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_LEVELS,
        default='normal',
        verbose_name=_('الأولوية')
    )
    is_system_template = models.BooleanField(
        default=False,
        verbose_name=_('قالب النظام'),
        help_text=_('هل هذا قالب أساسي في النظام')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('قالب الإشعار')
        verbose_name_plural = _('قوالب الإشعارات')
        ordering = ['template_type', 'display_name']

    def __str__(self):
        """__str__ function"""
        return f"{self.display_name} ({self.get_template_type_display()})"

    def render_subject(self, context=None):
        """Render the subject template with context"""
        if not self.subject_template:
            return ''

        from django.template import Context, Template
        template = Template(self.subject_template)
        return template.render(Context(context or {}))

    def render_message(self, context=None):
        """Render the message template with context"""
        from django.template import Context, Template
        template = Template(self.message_template)
        return template.render(Context(context or {}))
