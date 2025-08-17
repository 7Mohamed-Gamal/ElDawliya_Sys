"""
Payroll Detail Models for HRMS
Handles payroll entry component details
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class PayrollDetail(models.Model):
    """
    Payroll Detail model for individual salary component entries
    Represents a single component calculation in a payroll entry
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Relationships
    payroll_entry = models.ForeignKey(
        'PayrollEntry',
        on_delete=models.CASCADE,
        related_name='payroll_details',
        verbose_name=_("قيد الراتب")
    )
    
    salary_component = models.ForeignKey(
        'SalaryComponent',
        on_delete=models.PROTECT,
        related_name='payroll_details',
        verbose_name=_("مكون الراتب")
    )
    
    # Amount Information
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("المبلغ")
    )
    
    # Calculation Information
    is_prorated = models.BooleanField(
        default=False,
        verbose_name=_("محسوب نسبياً")
    )
    
    proration_factor = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=1.0000,
        verbose_name=_("معامل الحساب النسبي")
    )
    
    original_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("المبلغ الأصلي"),
        help_text=_("المبلغ قبل الحساب النسبي")
    )
    
    calculation_basis = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("أساس الحساب")
    )
    
    calculation_method = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("طريقة الحساب")
    )
    
    formula_used = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("المعادلة المستخدمة")
    )
    
    # Manual Override
    is_manually_adjusted = models.BooleanField(
        default=False,
        verbose_name=_("معدل يدوياً")
    )
    
    adjustment_reason = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("سبب التعديل")
    )
    
    adjusted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adjusted_payroll_details',
        verbose_name=_("عدل بواسطة")
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
        verbose_name = _("تفاصيل الراتب")
        verbose_name_plural = _("تفاصيل الرواتب")
        db_table = 'hrms_payroll_detail'
        unique_together = [['payroll_entry', 'salary_component']]
        ordering = ['salary_component__display_order']
        indexes = [
            models.Index(fields=['payroll_entry']),
            models.Index(fields=['salary_component']),
        ]
    
    def __str__(self):
        return f"{self.payroll_entry.employee.full_name} - {self.salary_component.name}"
    
    def save(self, *args, **kwargs):
        """Override save to set original amount"""
        if not self.original_amount and self.is_prorated:
            self.original_amount = self.amount / self.proration_factor
        
        super().save(*args, **kwargs)
    
    @property
    def is_earning(self):
        """Check if detail is an earning"""
        return self.salary_component.is_earning
    
    @property
    def is_deduction(self):
        """Check if detail is a deduction"""
        return self.salary_component.is_deduction
    
    @property
    def component_type_display(self):
        """Get component type display"""
        return self.salary_component.get_component_type_display()
    
    def manually_adjust(self, new_amount, reason, adjusted_by_user):
        """Manually adjust the component amount"""
        self.is_manually_adjusted = True
        self.original_amount = self.amount
        self.amount = new_amount
        self.adjustment_reason = reason
        self.adjusted_by = adjusted_by_user
        self.save()
        
        # Update payroll entry totals
        self.payroll_entry.calculate_components()


class PayrollDetailHistory(models.Model):
    """
    Payroll Detail History model for tracking changes to payroll details
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Relationships
    payroll_detail = models.ForeignKey(
        PayrollDetail,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_("تفاصيل الراتب")
    )
    
    # Change Information
    previous_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("المبلغ السابق")
    )
    
    new_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("المبلغ الجديد")
    )
    
    change_reason = models.CharField(
        max_length=200,
        verbose_name=_("سبب التغيير")
    )
    
    # Metadata
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payroll_detail_changes',
        verbose_name=_("غير بواسطة")
    )
    
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ التغيير")
    )
    
    class Meta:
        verbose_name = _("سجل تغييرات تفاصيل الراتب")
        verbose_name_plural = _("سجلات تغييرات تفاصيل الرواتب")
        db_table = 'hrms_payroll_detail_history'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.payroll_detail} - {self.changed_at}"