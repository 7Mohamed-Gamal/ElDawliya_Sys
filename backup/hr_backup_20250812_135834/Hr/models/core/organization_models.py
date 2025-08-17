"""
نماذج الشركة والأقسام

هذا الملف يحتوي على نماذج الشركة والأقسام والمواقع
التي تشكل الهيكل التنظيمي للمؤسسة
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from mptt.models import MPTTModel, TreeForeignKey
from Hr.models.core.base_model import HrBaseModel

class Company(HrBaseModel):
    """
    نموذج الشركة

    يستخدم لتمثيل الشركة أو المؤسسة في النظام
    ويسمح بتشغيل النظام لعدة شركات في حالة المجموعات
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الشركة")
    )

    name_en = models.CharField(
        max_length=100,
        verbose_name=_("الاسم بالإنجليزية"),
        null=True,
        blank=True
    )

    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود الشركة")
    )

    registration_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("رقم السجل التجاري")
    )

    tax_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("الرقم الضريبي")
    )

    legal_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("الكيان القانوني")
    )

    establishment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التأسيس")
    )

    logo = models.ImageField(
        upload_to='companies/logos/',
        null=True,
        blank=True,
        verbose_name=_("شعار الشركة")
    )

    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني")
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم الهاتف")
    )

    website = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("الموقع الإلكتروني")
    )

    address = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("العنوان")
    )

    city = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("المدينة")
    )

    country = models.CharField(
        max_length=50,
        default="المملكة العربية السعودية",
        verbose_name=_("الدولة")
    )

    default_currency = models.CharField(
        max_length=3,
        default="SAR",
        verbose_name=_("العملة الافتراضية")
    )

    class Meta:
        verbose_name = _("شركة")
        verbose_name_plural = _("الشركات")
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def full_name(self):
        """
        الاسم الكامل للشركة بالعربية والإنجليزية
        """
        if self.name_en:
            return f"{self.name} / {self.name_en}"
        return self.name


class Department(MPTTModel, HrBaseModel):
    """
    نموذج القسم/الإدارة

    يستخدم لتمثيل الهيكل التنظيمي للشركة
    مع دعم الهيكل الشجري متعدد المستويات
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم القسم")
    )

    name_en = models.CharField(
        max_length=100,
        verbose_name=_("الاسم بالإنجليزية"),
        null=True,
        blank=True
    )

    code = models.CharField(
        max_length=20,
        verbose_name=_("كود القسم")
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name=_("الشركة")
    )

    parent = TreeForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("القسم الأب")
    )

    manager = models.ForeignKey(
        'employee.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name=_("مدير القسم")
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الوصف")
    )

    cost_center = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("مركز التكلفة")
    )

    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departments',
        verbose_name=_("الموقع")
    )

    class Meta:
        verbose_name = _("قسم")
        verbose_name_plural = _("الأقسام")
        unique_together = ['company', 'code']
        ordering = ['company', 'name']

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    @property
    def full_name(self):
        """
        الاسم الكامل للقسم بما في ذلك التسلسل الهرمي
        """
        ancestors = self.get_ancestors(include_self=True)
        return " / ".join([ancestor.name for ancestor in ancestors])

    def get_employees_count(self):
        """
        حساب عدد الموظفين في هذا القسم
        """
        return self.employees.filter(is_active=True).count()

    def get_all_employees_count(self):
        """
        حساب عدد الموظفين في هذا القسم وأقسامه الفرعية
        """
        count = self.get_employees_count()
        for child in self.get_children():
            count += child.get_all_employees_count()
        return count

    def clean(self):
        """
        التحقق من صحة البيانات قبل الحفظ
        """
        # التأكد من أن القسم الأب ينتمي لنفس الشركة
        if self.parent and self.parent.company != self.company:
            raise ValidationError({
                'parent': _("القسم الأب يجب أن يكون من نفس الشركة")
            })

        # التأكد من أن المدير موظف في نفس الشركة
        if self.manager and self.manager.company != self.company:
            raise ValidationError({
                'manager': _("مدير القسم يجب أن يكون موظفًا في نفس الشركة")
            })


class Location(HrBaseModel):
    """
    نموذج الموقع/الفرع

    يستخدم لتمثيل المواقع الجغرافية والفروع التابعة للشركة
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الموقع")
    )

    name_en = models.CharField(
        max_length=100,
        verbose_name=_("الاسم بالإنجليزية"),
        null=True,
        blank=True
    )

    code = models.CharField(
        max_length=20,
        verbose_name=_("كود الموقع")
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name=_("الشركة")
    )

    type = models.CharField(
        max_length=50,
        choices=[
            ('headquarters', _("المقر الرئيسي")),
            ('branch', _("فرع")),
            ('office', _("مكتب")),
            ('factory', _("مصنع")),
            ('warehouse', _("مستودع")),
            ('other', _("أخرى"))
        ],
        default='branch',
        verbose_name=_("نوع الموقع")
    )

    address = models.TextField(
        verbose_name=_("العنوان")
    )

    city = models.CharField(
        max_length=50,
        verbose_name=_("المدينة")
    )

    region = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("المنطقة")
    )

    country = models.CharField(
        max_length=50,
        default="المملكة العربية السعودية",
        verbose_name=_("الدولة")
    )

    postal_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("الرمز البريدي")
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم الهاتف")
    )

    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني")
    )

    manager = models.ForeignKey(
        'employee.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_locations',
        verbose_name=_("مدير الموقع")
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_("خط العرض")
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_("خط الطول")
    )

    class Meta:
        verbose_name = _("موقع")
        verbose_name_plural = _("المواقع")
        unique_together = ['company', 'code']
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()} - {self.city})"

    @property
    def full_address(self):
        """
        العنوان الكامل
        """
        address_parts = [self.address, self.city]
        if self.region:
            address_parts.append(self.region)
        address_parts.append(self.country)
        if self.postal_code:
            address_parts.append(f"الرمز البريدي: {self.postal_code}")
        return "، ".join(address_parts)
