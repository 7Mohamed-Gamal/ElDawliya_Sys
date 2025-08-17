"""
Payroll Models for HRMS
Handles salary components and payroll processing
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class SalaryComponent(models.Model):
    """
    Salary component model defining different types of
    salary elements (basic, allowances, deductions, etc.)
    """
    
    # Component Types
    BASIC = 'BASIC'
    HOUSING = 'HOUSING'
    TRANSPORT = 'TRANSPORT'
    BONUS = 'BONUS'
    DEDUCTION = 'DEDUCTION'
    OTHER = 'OTHER'
    
    TYPE_CHOICES = (
        (BASIC, _('الراتب الأساسي')),
        (HOUSING, _('بدل سكن')),
        (TRANSPORT, _('بدل مواصلات')),
        (BONUS, _('حافز')),
        (DEDUCTION, _('استقطاع')),
        (OTHER, _('أخرى'))
    )
    
    # Calculation Types
    FIXED = 'FIXED'
    PERCENTAGE = 'PERCENTAGE'
    
    CALCULATION_CHOICES = (
        (FIXED, _('قيمة ثابتة')),
        (PERCENTAGE, _('نسبة'))
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم العنصر")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("الكود")
    )
    
    component_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name=_("نوع العنصر")
    )
    
    calculation_type = models.CharField(
        max_length=20,
        choices=CALCULATION_CHOICES,
        default=FIXED,
        verbose_name=_("نوع الحساب")
    )
    
    calculation_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("قيمة العنصر")
    )
    
    is_taxable = models.BooleanField(
        default=True,
        verbose_name=_("يخضع للضريبة")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("مكون راتب")
        verbose_name_plural = _("مكونات الرواتب")
        db_table = 'hrms_salarycomponent'
        ordering = ['component_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_component_type_display()})"


class EmployeeSalary(models.Model):
    """
    Employee salary structure configuration
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    employee = models.ForeignKey(
        'employee.Employee',
        on_delete=models.CASCADE,
        related_name='salary_components',
        verbose_name=_("الموظف")
    )
    
    component = models.ForeignKey(
        'SalaryComponent',
        on_delete=models.CASCADE,
        verbose_name=_("مكون الراتب")
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("المبلغ")
    )
    
    effective_from = models.DateField(
        verbose_name=_("ساري من تاريخ")
    )
    
    effective_to = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("ساري حتى تاريخ")
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
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("راتب الموظف")
        verbose_name_plural = _("رواتب الموظفين")
        db_table = 'hrms_employeesalary'
        unique_together = ['employee', 'component']
        indexes = [
            models.Index(fields=['employee', 'is_active']),
            models.Index(fields=['effective_from', 'effective_to']),
        ]
    
    def __str__(self):
        return f"{self.employee} - {self.component}"


class PayrollPeriod(models.Model):
    """
    Payroll periods (monthly, etc.)
    """
    
    # Status Choices
    DRAFT = 'D'
    PROCESSED = 'P'
    PAID = 'S'
    CLOSED = 'C'
    
    STATUS_CHOICES = (
        (DRAFT, _('مسودة')),
        (PROCESSED, _('تم المعالجة')),
        (PAID, _('تم الصرف')),
        (CLOSED, _('مغلق'))
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الفترة")
    )
    
    start_date = models.DateField(
        verbose_name=_("تاريخ البداية")
    )
    
    end_date = models.DateField(
        verbose_name=_("تاريخ النهاية")
    )
    
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=DRAFT,
        verbose_name=_("الحالة")
    )
    
    processed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ المعالجة")
    )
    
    payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الصرف")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("فترة رواتب")
        verbose_name_plural = _("فترات الرواتب")
        db_table = 'hrms_payrollperiod'
        unique_together = ['start_date', 'end_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"


class PayrollEntry(models.Model):
    """
    Individual payroll entries for each employee per period
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    period = models.ForeignKey(
        'PayrollPeriod',
        on_delete=models.CASCADE,
        related_name='payroll_entries',
        verbose_name=_("الفترة")
    )
    
    employee = models.ForeignKey(
        'employee.Employee',
        on_delete=models.CASCADE,
        related_name='payroll_entries',
        verbose_name=_("الموظف")
    )
    
    component = models.ForeignKey(
        'SalaryComponent',
        on_delete=models.CASCADE,
        verbose_name=_("المكون")
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("المبلغ")
    )
    
    is_taxable = models.BooleanField(
        default=True,
        verbose_name=_("يخضع للضريبة")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("قيد الرواتب")
        verbose_name_plural = _("قيود الرواتب")
        db_table = 'hrms_payrollentry'
        ordering = ['period', 'employee__employee_id']
        unique_together = ['period', 'employee', 'component']
        indexes = [
            models.Index(fields=['period', 'employee']),
        ]
    
    def __str__(self):
        return f"{self.employee} - {self.component} - {self.amount}"
