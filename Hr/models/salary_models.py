from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal

class SalaryItem(models.Model):
    """نموذج لبنود الرواتب"""
    ITEM_TYPES = [
        ('addition', _('إضافة')),
        ('deduction', _('خصم')),
    ]

    item_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('كود البند')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('اسم البند')
    )
    type = models.CharField(
        max_length=20,
        choices=ITEM_TYPES,
        default='addition',
        verbose_name=_('نوع البند')
    )
    default_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('القيمة الافتراضية')
    )
    is_auto_applied = models.BooleanField(
        default=False,
        verbose_name=_('تطبيق تلقائي')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('الوصف')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )

    class Meta:
        verbose_name = _('بند راتب')
        verbose_name_plural = _('بنود الرواتب')
        ordering = ['item_code']

    def __str__(self):
        return f"{self.name} ({self.item_code})"

class EmployeeSalaryItem(models.Model):
    """نموذج لبنود رواتب الموظفين"""
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='salary_items',
        verbose_name=_('الموظف')
    )
    salary_item = models.ForeignKey(
        SalaryItem,
        on_delete=models.PROTECT,
        verbose_name=_('بند الراتب')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('القيمة')
    )
    start_date = models.DateField(
        verbose_name=_('تاريخ البدء')
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ الانتهاء')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )

    class Meta:
        verbose_name = _('بند راتب موظف')
        verbose_name_plural = _('بنود رواتب الموظفين')
        ordering = ['employee', 'salary_item']

    def __str__(self):
        return f"{self.employee} - {self.salary_item}"

class PayrollPeriod(models.Model):
    """نموذج لفترات الرواتب"""
    PERIOD_STATUSES = [
        ('draft', _('مسودة')),
        ('calculating', _('جاري الحساب')),
        ('completed', _('مكتمل')),
        ('approved', _('معتمد')),
        ('paid', _('مدفوع')),
    ]

    period = models.DateField(
        verbose_name=_('الفترة')
    )
    status = models.CharField(
        max_length=20,
        choices=PERIOD_STATUSES,
        default='draft',
        verbose_name=_('الحالة')
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('إجمالي المبلغ')
    )
    created_by = models.ForeignKey(
        'accounts.Users_Login_New',
        on_delete=models.PROTECT,
        related_name='created_payroll_periods',
        verbose_name=_('تم الإنشاء بواسطة')
    )
    approved_by = models.ForeignKey(
        'accounts.Users_Login_New',
        on_delete=models.PROTECT,
        related_name='approved_payroll_periods',
        null=True,
        blank=True,
        verbose_name=_('تم الاعتماد بواسطة')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )

    class Meta:
        verbose_name = _('فترة راتب')
        verbose_name_plural = _('فترات الرواتب')
        ordering = ['-period']
        unique_together = ['period']

    def __str__(self):
        return f"{self.period.strftime('%Y-%m')} - {self.get_status_display()}"

class PayrollEntry(models.Model):
    """نموذج لسجلات الرواتب"""
    ENTRY_STATUSES = [
        ('pending', _('قيد المراجعة')),
        ('approved', _('معتمد')),
        ('rejected', _('مرفوض')),
        ('paid', _('مدفوع')),
    ]

    period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.PROTECT,
        related_name='entries',
        verbose_name=_('فترة الراتب')
    )
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.PROTECT,
        related_name='payroll_entries',
        verbose_name=_('الموظف')
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('إجمالي المبلغ')
    )
    status = models.CharField(
        max_length=20,
        choices=ENTRY_STATUSES,
        default='pending',
        verbose_name=_('الحالة')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )

    class Meta:
        verbose_name = _('سجل راتب')
        verbose_name_plural = _('سجلات الرواتب')
        ordering = ['-period__period', 'employee']
        unique_together = ['period', 'employee']

    def __str__(self):
        return f"{self.employee} - {self.period}"

class PayrollItemDetail(models.Model):
    """نموذج لتفاصيل بنود الراتب"""
    payroll_entry = models.ForeignKey(
        PayrollEntry,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('سجل الراتب')
    )
    salary_item = models.ForeignKey(
        SalaryItem,
        on_delete=models.PROTECT,
        verbose_name=_('بند الراتب')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('القيمة')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )

    class Meta:
        verbose_name = _('تفاصيل بند راتب')
        verbose_name_plural = _('تفاصيل بنود الرواتب')
        ordering = ['payroll_entry', 'salary_item']

    def __str__(self):
        return f"{self.payroll_entry} - {self.salary_item}"
