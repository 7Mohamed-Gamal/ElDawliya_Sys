"""
تحسينات النماذج الأساسية للموارد البشرية

يحتوي هذا الملف على تحسينات للنماذج الأساسية التي تشكل العمود الفقري لنظام الموارد البشرية.
هذه التحسينات تدعم التكامل بين مختلف أجزاء النظام.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
import logging

# نظام التسجيل
logger = logging.getLogger(__name__)
User = get_user_model()

class HrBaseModel(models.Model):
    """
    النموذج الأساسي لجميع نماذج الموارد البشرية.
    يتضمن الحقول المشتركة التي تستخدمها جميع النماذج.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        verbose_name=_("أنشئ بواسطة")
    )

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        verbose_name=_("عدل بواسطة")
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )

    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        تخصيص عملية الحفظ لتسجيل التغييرات
        """
        super().save(*args, **kwargs)
        # يمكن إضافة تسجيل للتغييرات هنا إذا لزم الأمر

    def delete(self, *args, **kwargs):
        """
        تخصيص عملية الحذف لتنفيذ حذف افتراضي
        """
        self.is_active = False
        self.updated_at = timezone.now()
        self.save()

    def hard_delete(self, *args, **kwargs):
        """
        تنفيذ الحذف الحقيقي من قاعدة البيانات
        """
        super().delete(*args, **kwargs)

class HrCompany(HrBaseModel):
    """
    نموذج الشركة
    يُستخدم في الأنظمة متعددة الشركات
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الشركة")
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

    logo = models.ImageField(
        upload_to='company_logos/',
        null=True,
        blank=True,
        verbose_name=_("شعار الشركة")
    )

    address = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("العنوان")
    )

    phone = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("رقم الهاتف")
    )

    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني")
    )

    website = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("الموقع الإلكتروني")
    )

    class Meta:
        verbose_name = _("الشركة")
        verbose_name_plural = _("الشركات")
        ordering = ['name']

    def __str__(self):
        return self.name

class HrDepartment(HrBaseModel):
    """
    نموذج القسم/الإدارة
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم القسم")
    )

    code = models.CharField(
        max_length=20,
        verbose_name=_("كود القسم")
    )

    company = models.ForeignKey(
        'HrCompany',
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name=_("الشركة")
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_departments',
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

    class Meta:
        verbose_name = _("القسم")
        verbose_name_plural = _("الأقسام")
        unique_together = ['company', 'code']
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    def get_all_children(self):
        """
        الحصول على جميع الأقسام الفرعية
        """
        children = list(self.child_departments.all())
        for child in list(children):
            children.extend(child.get_all_children())
        return children

    def get_employees(self):
        """
        الحصول على جميع الموظفين في هذا القسم
        """
        return self.employees.filter(is_active=True)

    def get_all_employees(self):
        """
        الحصول على جميع الموظفين في هذا القسم وأقسامه الفرعية
        """
        from Hr.models.employee.employee_models import Employee

        # الموظفون في هذا القسم
        employees = list(self.get_employees())

        # الموظفون في الأقسام الفرعية
        child_departments = self.get_all_children()
        for dept in child_departments:
            employees.extend(list(dept.get_employees()))

        return employees

class HrLocation(HrBaseModel):
    """
    نموذج الموقع/المقر
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الموقع")
    )

    company = models.ForeignKey(
        'HrCompany',
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name=_("الشركة")
    )

    address = models.TextField(
        verbose_name=_("العنوان")
    )

    city = models.CharField(
        max_length=50,
        verbose_name=_("المدينة")
    )

    country = models.CharField(
        max_length=50,
        default="Saudi Arabia",
        verbose_name=_("الدولة")
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
        verbose_name = _("الموقع")
        verbose_name_plural = _("المواقع")
        unique_together = ['company', 'name']
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"

class HrJobPosition(HrBaseModel):
    """
    نموذج المنصب الوظيفي
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("المسمى الوظيفي")
    )

    code = models.CharField(
        max_length=20,
        verbose_name=_("كود الوظيفة")
    )

    company = models.ForeignKey(
        'HrCompany',
        on_delete=models.CASCADE,
        related_name='job_positions',
        verbose_name=_("الشركة")
    )

    department = models.ForeignKey(
        'HrDepartment',
        on_delete=models.CASCADE,
        related_name='job_positions',
        verbose_name=_("القسم")
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الوصف الوظيفي")
    )

    requirements = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("المتطلبات")
    )

    grade = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("الدرجة الوظيفية")
    )

    min_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأدنى للراتب")
    )

    max_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى للراتب")
    )

    class Meta:
        verbose_name = _("المنصب الوظيفي")
        verbose_name_plural = _("المناصب الوظيفية")
        unique_together = ['company', 'code']
        ordering = ['company', 'department', 'name']

    def __str__(self):
        return f"{self.name} ({self.department.name})"

# يمكن إضافة المزيد من النماذج الأساسية حسب الحاجة
