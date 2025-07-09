"""
Salary Component Models for HRMS
Handles salary components, allowances, and deductions
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal


class SalaryComponent(models.Model):
    """
    Salary Component model for defining salary elements
    Includes allowances, deductions, and other salary components
    """
    
    # Basic Information
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم المكون")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود المكون")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف المكون")
    )
    
    # Component Type
    COMPONENT_TYPES = [
        ('basic_salary', _('الراتب الأساسي')),
        ('allowance', _('بدل')),
        ('bonus', _('مكافأة')),
        ('commission', _('عمولة')),
        ('overtime', _('عمل إضافي')),
        ('deduction', _('خصم')),
        ('tax', _('ضريبة')),
        ('insurance', _('تأمين')),
        ('loan', _('قرض')),
        ('advance', _('سلفة')),
        ('penalty', _('غرامة')),
        ('other', _('أخرى')),
    ]
    
    component_type = models.CharField(
        max_length=20,
        choices=COMPONENT_TYPES,
        verbose_name=_("نوع المكون")
    )
    
    # Component Category
    CATEGORIES = [
        ('earning', _('استحقاق')),
        ('deduction', _('خصم')),
        ('employer_contribution', _('مساهمة صاحب العمل')),
    ]
    
    category = models.CharField(
        max_length=25,
        choices=CATEGORIES,
        verbose_name=_("فئة المكون")
    )
    
    # Calculation Method
    CALCULATION_METHODS = [
        ('fixed', _('مبلغ ثابت')),
        ('percentage', _('نسبة مئوية')),
        ('formula', _('معادلة')),
        ('attendance_based', _('على أساس الحضور')),
        ('performance_based', _('على أساس الأداء')),
        ('slab', _('شرائح')),
    ]
    
    calculation_method = models.CharField(
        max_length=20,
        choices=CALCULATION_METHODS,
        verbose_name=_("طريقة الحساب")
    )
    
    # Calculation Values
    fixed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("المبلغ الثابت")
    )
    
    percentage_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("النسبة المئوية")
    )
    
    calculation_formula = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("معادلة الحساب"),
        help_text=_("معادلة لحساب المكون (مثل: basic_salary * 0.1)")
    )
    
    # Basis for Percentage Calculation
    PERCENTAGE_BASIS = [
        ('basic_salary', _('الراتب الأساسي')),
        ('gross_salary', _('إجمالي الراتب')),
        ('total_earnings', _('إجمالي الاستحقاقات')),
        ('specific_component', _('مكون محدد')),
        ('attendance_days', _('أيام الحضور')),
        ('working_hours', _('ساعات العمل')),
    ]
    
    percentage_basis = models.CharField(
        max_length=20,
        choices=PERCENTAGE_BASIS,
        null=True,
        blank=True,
        verbose_name=_("أساس النسبة المئوية")
    )
    
    basis_component = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dependent_components',
        verbose_name=_("المكون الأساسي")
    )
    
    # Limits and Constraints
    minimum_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأدنى")
    )
    
    maximum_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى")
    )
    
    # Tax and Insurance Settings
    is_taxable = models.BooleanField(
        default=True,
        verbose_name=_("خاضع للضريبة")
    )
    
    is_insurance_applicable = models.BooleanField(
        default=True,
        verbose_name=_("خاضع للتأمين")
    )
    
    affects_overtime = models.BooleanField(
        default=False,
        verbose_name=_("يؤثر على العمل الإضافي")
    )
    
    # Frequency and Timing
    FREQUENCIES = [
        ('monthly', _('شهري')),
        ('quarterly', _('ربع سنوي')),
        ('semi_annual', _('نصف سنوي')),
        ('annual', _('سنوي')),
        ('one_time', _('مرة واحدة')),
        ('variable', _('متغير')),
    ]
    
    frequency = models.CharField(
        max_length=15,
        choices=FREQUENCIES,
        default='monthly',
        verbose_name=_("التكرار")
    )
    
    effective_from = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("ساري من")
    )
    
    effective_to = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("ساري حتى")
    )
    
    # Conditions and Rules
    conditions = models.JSONField(
        default=dict,
        verbose_name=_("الشروط"),
        help_text=_("شروط تطبيق المكون")
    )
    
    calculation_rules = models.JSONField(
        default=dict,
        verbose_name=_("قواعد الحساب"),
        help_text=_("قواعد إضافية لحساب المكون")
    )
    
    # Slab Configuration (for slab-based calculation)
    slabs = models.JSONField(
        default=list,
        verbose_name=_("الشرائح"),
        help_text=_("تكوين الشرائح للحساب المتدرج")
    )
    
    # Display and Reporting
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("ترتيب العرض")
    )
    
    show_in_payslip = models.BooleanField(
        default=True,
        verbose_name=_("إظهار في قسيمة الراتب")
    )
    
    show_in_summary = models.BooleanField(
        default=True,
        verbose_name=_("إظهار في الملخص")
    )
    
    # Account Information
    account_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("كود الحساب")
    )
    
    cost_center = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("مركز التكلفة")
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    is_system_component = models.BooleanField(
        default=False,
        verbose_name=_("مكون نظام"),
        help_text=_("هل هذا مكون أساسي في النظام؟")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_salary_components',
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
        verbose_name = _("مكون راتب")
        verbose_name_plural = _("مكونات الرواتب")
        db_table = 'hrms_salary_component'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['component_type']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate salary component data"""
        super().clean()
        
        # Validate calculation method requirements
        if self.calculation_method == 'fixed' and not self.fixed_amount:
            raise ValidationError(_("المبلغ الثابت مطلوب للحساب الثابت"))
        
        if self.calculation_method == 'percentage':
            if not self.percentage_value:
                raise ValidationError(_("النسبة المئوية مطلوبة للحساب النسبي"))
            if not self.percentage_basis:
                raise ValidationError(_("أساس النسبة المئوية مطلوب"))
        
        if self.calculation_method == 'formula' and not self.calculation_formula:
            raise ValidationError(_("معادلة الحساب مطلوبة للحساب بالمعادلة"))
        
        # Validate limits
        if (self.minimum_amount and self.maximum_amount and 
            self.minimum_amount > self.maximum_amount):
            raise ValidationError(_("الحد الأدنى لا يمكن أن يكون أكبر من الحد الأقصى"))
        
        # Validate effective dates
        if (self.effective_from and self.effective_to and 
            self.effective_from > self.effective_to):
            raise ValidationError(_("تاريخ البداية لا يمكن أن يكون بعد تاريخ النهاية"))
    
    @property
    def is_earning(self):
        """Check if component is an earning"""
        return self.category == 'earning'
    
    @property
    def is_deduction(self):
        """Check if component is a deduction"""
        return self.category == 'deduction'
    
    def calculate_amount(self, employee, payroll_period, base_values=None):
        """Calculate component amount for an employee"""
        if base_values is None:
            base_values = {}
        
        amount = Decimal('0')
        
        if self.calculation_method == 'fixed':
            amount = self.fixed_amount or Decimal('0')
        
        elif self.calculation_method == 'percentage':
            basis_value = self.get_basis_value(employee, payroll_period, base_values)
            if basis_value and self.percentage_value:
                amount = basis_value * (self.percentage_value / 100)
        
        elif self.calculation_method == 'formula':
            amount = self.calculate_formula_amount(employee, payroll_period, base_values)
        
        elif self.calculation_method == 'attendance_based':
            amount = self.calculate_attendance_based_amount(employee, payroll_period)
        
        elif self.calculation_method == 'slab':
            amount = self.calculate_slab_amount(employee, payroll_period, base_values)
        
        # Apply limits
        if self.minimum_amount and amount < self.minimum_amount:
            amount = self.minimum_amount
        
        if self.maximum_amount and amount > self.maximum_amount:
            amount = self.maximum_amount
        
        return amount
    
    def get_basis_value(self, employee, payroll_period, base_values):
        """Get the basis value for percentage calculation"""
        if self.percentage_basis == 'basic_salary':
            return employee.basic_salary or Decimal('0')
        
        elif self.percentage_basis == 'gross_salary':
            return base_values.get('gross_salary', Decimal('0'))
        
        elif self.percentage_basis == 'total_earnings':
            return base_values.get('total_earnings', Decimal('0'))
        
        elif self.percentage_basis == 'specific_component' and self.basis_component:
            return base_values.get(f'component_{self.basis_component.code}', Decimal('0'))
        
        elif self.percentage_basis == 'attendance_days':
            return Decimal(str(base_values.get('attendance_days', 0)))
        
        elif self.percentage_basis == 'working_hours':
            return Decimal(str(base_values.get('working_hours', 0)))
        
        return Decimal('0')
    
    def calculate_formula_amount(self, employee, payroll_period, base_values):
        """Calculate amount using formula"""
        # This would implement formula evaluation
        # For now, return a placeholder
        try:
            # Simple formula evaluation (would need proper implementation)
            formula = self.calculation_formula
            # Replace variables with actual values
            # This is a simplified implementation
            return Decimal('0')
        except:
            return Decimal('0')
    
    def calculate_attendance_based_amount(self, employee, payroll_period):
        """Calculate amount based on attendance"""
        # This would calculate based on actual attendance
        # For now, return a placeholder
        return Decimal('0')
    
    def calculate_slab_amount(self, employee, payroll_period, base_values):
        """Calculate amount using slab method"""
        if not self.slabs:
            return Decimal('0')
        
        basis_value = self.get_basis_value(employee, payroll_period, base_values)
        total_amount = Decimal('0')
        
        for slab in self.slabs:
            slab_min = Decimal(str(slab.get('min', 0)))
            slab_max = Decimal(str(slab.get('max', float('inf'))))
            slab_rate = Decimal(str(slab.get('rate', 0)))
            
            if basis_value > slab_min:
                applicable_amount = min(basis_value, slab_max) - slab_min
                if applicable_amount > 0:
                    total_amount += applicable_amount * (slab_rate / 100)
        
        return total_amount
    
    def is_applicable_for_employee(self, employee):
        """Check if component is applicable for an employee"""
        # Check conditions
        if not self.conditions:
            return True
        
        # Implement condition checking logic
        # For now, return True
        return True
    
    def save(self, *args, **kwargs):
        """Override save to set default values"""
        # Set default conditions
        if not self.conditions:
            self.conditions = {
                'employment_types': ['full_time', 'part_time'],
                'minimum_service_months': 0,
                'departments': [],
                'job_positions': [],
            }
        
        # Set default calculation rules
        if not self.calculation_rules:
            self.calculation_rules = {
                'round_to_nearest': 1,
                'prorate_for_partial_month': True,
                'apply_on_leave': False,
                'apply_on_probation': True,
            }
        
        # Auto-generate code if not provided
        if not self.code:
            component_count = SalaryComponent.objects.count()
            self.code = f"SC{component_count + 1:03d}"
        
        super().save(*args, **kwargs)
