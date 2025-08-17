"""
Salary Component Models for HRMS
Handles salary components, allowances, and deductions
"""

import uuid
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
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
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
        """استدعاء خدمة الرواتب لحساب قيمة المكون لهذا الموظف والفترة"""
        from Hr.services.payroll_service import PayrollService
        return PayrollService.calculate_salary_component_amount(self, employee, payroll_period, base_values)
    
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
