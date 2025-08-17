"""
Payroll Entry Models for HRMS
Handles payroll entries for individual employees
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class PayrollEntry(models.Model):
    """
    Payroll Entry model for individual employee payroll processing
    Represents a single payroll record for an employee in a specific period
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Relationships
    payroll_period = models.ForeignKey(
        'PayrollPeriod',
        on_delete=models.CASCADE,
        related_name='payroll_entries',
        verbose_name=_("فترة الراتب"),
        null=True,
        blank=True
    )
    
    employee = models.ForeignKey(
        'Hr.Employee',
        on_delete=models.PROTECT,
        related_name='payroll_entries',
        verbose_name=_("الموظف"),
        null=True,
        blank=True
    )
    
    salary_structure = models.ForeignKey(
        'EmployeeSalaryStructure',
        on_delete=models.PROTECT,
        related_name='payroll_entries',
        verbose_name=_("هيكل الراتب"),
        null=True,
        blank=True
    )
    
    # Status
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('calculated', _('محسوب')),
        ('reviewed', _('تمت المراجعة')),
        ('approved', _('معتمد')),
        ('paid', _('مدفوع')),
        ('cancelled', _('ملغي')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_("الحالة")
    )
    
    # Salary Information
    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("الراتب الأساسي")
    )
    
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
    
    # Attendance Information
    working_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        verbose_name=_("أيام العمل")
    )
    
    present_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        verbose_name=_("أيام الحضور")
    )
    
    absent_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        verbose_name=_("أيام الغياب")
    )
    
    leave_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        verbose_name=_("أيام الإجازة")
    )
    
    overtime_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name=_("ساعات العمل الإضافي")
    )
    
    # Payment Information
    payment_method = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("طريقة الدفع")
    )
    
    bank_account = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("الحساب البنكي")
    )
    
    payment_reference = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("مرجع الدفع")
    )
    
    payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الدفع")
    )
    
    # Calculation Information
    calculation_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات الحساب")
    )
    
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
    
    # Approval Information
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_payroll_entries',
        verbose_name=_("تمت المراجعة بواسطة")
    )
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_payroll_entries',
        verbose_name=_("تمت الموافقة بواسطة")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_payroll_entries',
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
        verbose_name = _("قيد راتب")
        verbose_name_plural = _("قيود الرواتب")
        db_table = 'hrms_payroll_entry'
        unique_together = [['payroll_period', 'employee']]
        ordering = ['payroll_period', 'employee__employee_number']
        indexes = [
            models.Index(fields=['payroll_period', 'employee']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.payroll_period.name}"
    
    def clean(self):
        """Validate payroll entry data"""
        super().clean()
        
        # Validate employee has active salary structure
        if not self.salary_structure:
            raise ValidationError(_("الموظف ليس لديه هيكل راتب نشط"))
    
    def calculate_payroll(self):
        """Calculate payroll for this entry"""
        if self.status not in ['draft', 'calculated']:
            raise ValidationError(_("لا يمكن إعادة حساب قيد راتب تمت الموافقة عليه"))
        
        # Set basic values
        self.basic_salary = self.salary_structure.basic_salary
        
        # Calculate attendance
        self.calculate_attendance()
        
        # Calculate proration if needed
        self.calculate_proration()
        
        # Calculate components
        self.calculate_components()
        
        # Update status
        self.status = 'calculated'
        self.save()
    
    def calculate_attendance(self):
        """Calculate attendance metrics for payroll period"""
        # This would typically query attendance records
        # For now, set default values
        self.working_days = Decimal('22')  # Default working days in a month
        self.present_days = Decimal('22')  # Assume full attendance
        self.absent_days = Decimal('0')
        self.leave_days = Decimal('0')
        self.overtime_hours = Decimal('0')
    
    def calculate_proration(self):
        """Calculate proration factor if needed"""
        # Check if employee joined or left during the period
        if (self.employee.hire_date > self.payroll_period.start_date or
            (self.employee.termination_date and 
             self.employee.termination_date < self.payroll_period.end_date)):
            
            self.is_prorated = True
            
            # Calculate actual days worked in period
            start_date = max(self.employee.hire_date, self.payroll_period.start_date)
            end_date = min(
                self.employee.termination_date or self.payroll_period.end_date,
                self.payroll_period.end_date
            )
            
            actual_days = (end_date - start_date).days + 1
            total_days = (self.payroll_period.end_date - self.payroll_period.start_date).days + 1
            
            self.proration_factor = Decimal(actual_days) / Decimal(total_days)
            self.calculation_notes = f"تم حساب الراتب نسبياً ({actual_days}/{total_days} يوم)"
        else:
            self.is_prorated = False
            self.proration_factor = Decimal('1.0000')
    
    def calculate_components(self):
        """Calculate all salary components"""
        # Reset totals
        self.total_earnings = Decimal('0')
        self.total_deductions = Decimal('0')
        
        # Get base values for calculations
        base_values = {
            'basic_salary': self.basic_salary,
            'attendance_days': float(self.present_days),
            'working_days': float(self.working_days),
            'proration_factor': float(self.proration_factor),
        }
        
        # Delete existing details
        self.payroll_details.all().delete()
        
        # Calculate each component
        for component in self.salary_structure.salary_components.filter(is_active=True):
            amount = component.calculate_amount(self.payroll_period, base_values)
            
            # Apply proration if needed
            if self.is_prorated and component.salary_component.component_type != 'deduction':
                amount = amount * self.proration_factor
            
            # Create detail record
            detail = PayrollDetail.objects.create(
                payroll_entry=self,
                salary_component=component.salary_component,
                amount=amount,
                is_prorated=self.is_prorated,
                proration_factor=self.proration_factor
            )
            
            # Update totals
            if component.salary_component.is_earning:
                self.total_earnings += amount
            elif component.salary_component.is_deduction:
                self.total_deductions += amount
        
        # Calculate net salary
        self.net_salary = self.total_earnings - self.total_deductions
    
    def review_payroll(self, reviewed_by_user):
        """Mark payroll as reviewed"""
        if self.status != 'calculated':
            raise ValidationError(_("يمكن مراجعة قيود الرواتب المحسوبة فقط"))
        
        self.status = 'reviewed'
        self.reviewed_by = reviewed_by_user
        self.save()
    
    def approve_payroll(self, approved_by_user):
        """Approve payroll entry"""
        if self.status != 'reviewed':
            raise ValidationError(_("يمكن الموافقة على قيود الرواتب التي تمت مراجعتها فقط"))
        
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.save()
    
    def mark_as_paid(self, payment_reference=None, payment_date=None):
        """Mark payroll as paid"""
        if self.status != 'approved':
            raise ValidationError(_("يمكن تسجيل دفع قيود الرواتب المعتمدة فقط"))
        
        self.status = 'paid'
        self.payment_reference = payment_reference or self.payment_reference
        self.payment_date = payment_date or timezone.now().date()
        self.save()
    
    def cancel_payroll(self):
        """Cancel payroll entry"""
        if self.status == 'paid':
            raise ValidationError(_("لا يمكن إلغاء قيد راتب تم دفعه"))
        
        self.status = 'cancelled'
        self.save()
    
    def generate_payslip(self):
        """Generate payslip for this entry"""
        # This would generate a payslip document
        # For now, return a placeholder
        return None
    
    def save(self, *args, **kwargs):
        """Override save to ensure data consistency"""
        # Set basic salary from structure if not set
        if not self.basic_salary and self.salary_structure:
            self.basic_salary = self.salary_structure.basic_salary
        
        super().save(*args, **kwargs)