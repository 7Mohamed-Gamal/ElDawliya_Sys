"""
Employee Salary Structure Models for HRMS
Handles employee salary structures and component assignments
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from datetime import date


class EmployeeSalaryStructure(models.Model):
    """
    Employee Salary Structure model for assigning salary components to employees
    Defines the complete salary structure for each employee
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Employee Information
    employee = models.ForeignKey(
        'Hr.Employee',
        on_delete=models.CASCADE,
        related_name='salary_structures',
        verbose_name=_("الموظف")
    )
    
    # Structure Information
    structure_name = models.CharField(
        max_length=200,
        verbose_name=_("اسم هيكل الراتب")
    )
    
    structure_code = models.CharField(
        max_length=20,
        verbose_name=_("كود هيكل الراتب")
    )
    
    # Effective Period
    effective_from = models.DateField(
        verbose_name=_("ساري من")
    )
    
    effective_to = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("ساري حتى")
    )
    
    # Basic Salary Information
    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("الراتب الأساسي")
    )
    
    currency = models.CharField(
        max_length=3,
        default="EGP",
        verbose_name=_("العملة")
    )
    
    # Calculated Totals
    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("إجمالي الاستحقاقات")
    )
    
    total_deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("إجمالي الخصومات")
    )
    
    net_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("صافي الراتب")
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    is_current = models.BooleanField(
        default=False,
        verbose_name=_("الهيكل الحالي")
    )
    
    # Approval Information
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_salary_structures',
        verbose_name=_("تمت الموافقة بواسطة")
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الموافقة")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_salary_structures',
        verbose_name=_("أنشئ بواسطة")
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
        verbose_name = _("هيكل راتب موظف")
        verbose_name_plural = _("هياكل رواتب الموظفين")
        db_table = 'hrms_employee_salary_structure'
        ordering = ['-effective_from']
        indexes = [
            models.Index(fields=['employee', 'effective_from']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_current']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.structure_name}"
    
    def clean(self):
        """Validate salary structure data"""
        super().clean()
        
        # Validate effective dates
        if self.effective_to and self.effective_from > self.effective_to:
            raise ValidationError(_("تاريخ البداية لا يمكن أن يكون بعد تاريخ النهاية"))
    
    def calculate_totals(self):
        """Calculate total earnings, deductions, and net salary"""
        earnings = Decimal('0')
        deductions = Decimal('0')
        
        for component in self.salary_components.filter(is_active=True):
            if component.salary_component.is_earning:
                earnings += component.amount
            elif component.salary_component.is_deduction:
                deductions += component.amount
        
        self.total_earnings = earnings
        self.total_deductions = deductions
        self.net_salary = earnings - deductions
    
    def set_as_current(self):
        """Set this structure as the current one for the employee"""
        # Deactivate other current structures
        EmployeeSalaryStructure.objects.filter(
            employee=self.employee,
            is_current=True
        ).exclude(pk=self.pk).update(is_current=False)
        
        self.is_current = True
        self.save()
    
    def approve_structure(self, approved_by_user):
        """Approve the salary structure"""
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to calculate totals and set defaults"""
        # Auto-generate structure code if not provided
        if not self.structure_code:
            emp_code = self.employee.employee_number
            date_str = self.effective_from.strftime('%Y%m')
            self.structure_code = f"{emp_code}-{date_str}"
        
        # Auto-generate structure name if not provided
        if not self.structure_name:
            self.structure_name = f"هيكل راتب {self.employee.full_name} - {self.effective_from}"
        
        super().save(*args, **kwargs)
        
        # Calculate totals after saving
        self.calculate_totals()
        if self.total_earnings != 0 or self.total_deductions != 0:
            super().save(update_fields=['total_earnings', 'total_deductions', 'net_salary'])


class EmployeeSalaryComponent(models.Model):
    """
    Employee Salary Component model for individual component assignments
    Links salary components to employee salary structures with specific amounts
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Relationships
    salary_structure = models.ForeignKey(
        EmployeeSalaryStructure,
        on_delete=models.CASCADE,
        related_name='salary_components',
        verbose_name=_("هيكل الراتب")
    )
    
    salary_component = models.ForeignKey(
        'SalaryComponent',
        on_delete=models.CASCADE,
        related_name='employee_assignments',
        verbose_name=_("مكون الراتب")
    )
    
    # Amount Information
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("المبلغ")
    )
    
    # Override Settings
    override_calculation = models.BooleanField(
        default=False,
        verbose_name=_("تجاوز الحساب التلقائي")
    )
    
    custom_formula = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("معادلة مخصصة")
    )
    
    # Conditions
    conditions = models.JSONField(
        default=dict,
        verbose_name=_("الشروط"),
        help_text=_("شروط خاصة لهذا المكون")
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("مكون راتب موظف")
        verbose_name_plural = _("مكونات رواتب الموظفين")
        db_table = 'hrms_employee_salary_component'
        unique_together = [['salary_structure', 'salary_component']]
        ordering = ['salary_component__display_order']
        indexes = [
            models.Index(fields=['salary_structure']),
            models.Index(fields=['salary_component']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.salary_structure.employee.full_name} - {self.salary_component.name}"
    
    def calculate_amount(self, payroll_period=None, base_values=None):
        """استدعاء خدمة الرواتب لحساب قيمة مكون الراتب لهذا الموظف والفترة"""
        from Hr.services.payroll_service import PayrollService
        if self.override_calculation:
            return self.amount
        return PayrollService.calculate_employee_salary_component_amount(self, payroll_period, base_values)
    
    def save(self, *args, **kwargs):
        """Override save to recalculate structure totals"""
        super().save(*args, **kwargs)
        
        # Recalculate salary structure totals
        self.salary_structure.calculate_totals()
        self.salary_structure.save(update_fields=['total_earnings', 'total_deductions', 'net_salary'])