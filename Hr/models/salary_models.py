from django.db import models
from django.utils.translation import gettext_lazy as _
from .employee_model import Employee

class SalaryItem(models.Model):
    """
    Model for defining different types of salary items (fixed, variable, allowances, deductions)
    """
    ITEM_TYPE_CHOICES = [
        ('fixed', _('ثابت')),
        ('variable', _('متغير')),
        ('allowance', _('استحقاق')),
        ('deduction', _('استقطاع')),
    ]

    CALCULATION_METHOD_CHOICES = [
        ('fixed_amount', _('مبلغ ثابت')),
        ('percentage', _('نسبة مئوية')),
    ]

    name = models.CharField(max_length=100, verbose_name=_('اسم البند'))
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, verbose_name=_('نوع البند'))
    calculation_method = models.CharField(max_length=20, choices=CALCULATION_METHOD_CHOICES, verbose_name=_('طريقة الحساب'))
    affects_total = models.BooleanField(default=True, verbose_name=_('يؤثر على الإجمالي'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('بند الراتب')
        verbose_name_plural = _('بنود الرواتب')
        managed = True
        db_table = 'Hr_SalaryItem'


class EmployeeSalaryItem(models.Model):
    """
    Model to link salary items to employees with specific values
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_items', verbose_name=_('الموظف'))
    salary_item = models.ForeignKey(SalaryItem, on_delete=models.CASCADE, related_name='employee_items', verbose_name=_('بند الراتب'))
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('القيمة'))
    effective_date = models.DateField(verbose_name=_('تاريخ السريان'))
    end_date = models.DateField(null=True, blank=True, verbose_name=_('تاريخ الانتهاء'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return f"{self.employee} - {self.salary_item}"

    class Meta:
        verbose_name = _('بند راتب الموظف')
        verbose_name_plural = _('بنود رواتب الموظفين')
        managed = True
        db_table = 'Hr_EmployeeSalaryItem'


class PayrollPeriod(models.Model):
    """
    Model for defining payroll periods
    """
    STATUS_CHOICES = [
        ('draft', _('قيد الإعداد')),
        ('calculated', _('تم الاحتساب')),
        ('approved', _('تم الاعتماد')),
        ('paid', _('تم الدفع')),
    ]

    name = models.CharField(max_length=100, verbose_name=_('اسم الفترة'))
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('الحالة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('فترة الراتب')
        verbose_name_plural = _('فترات الرواتب')
        managed = True
        db_table = 'Hr_PayrollPeriod'


class PayrollEntry(models.Model):
    """
    Model for storing calculated payroll entries
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_entries', verbose_name=_('الموظف'))
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='entries', verbose_name=_('فترة الراتب'))
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('الراتب الأساسي'))
    variable_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('الراتب المتغير'))
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('الاستحقاقات'))
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('الاستقطاعات'))
    overtime = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('العمل الإضافي'))
    penalties = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('الجزاءات'))
    total_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('إجمالي الراتب'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return f"{self.employee} - {self.payroll_period}"

    class Meta:
        verbose_name = _('سجل الراتب')
        verbose_name_plural = _('سجلات الرواتب')
        managed = True
        db_table = 'Hr_PayrollEntry'


class PayrollItemDetail(models.Model):
    """
    Model for storing detailed breakdown of payroll items
    """
    payroll_entry = models.ForeignKey(PayrollEntry, on_delete=models.CASCADE, related_name='item_details', verbose_name=_('سجل الراتب'))
    salary_item = models.ForeignKey(SalaryItem, on_delete=models.CASCADE, verbose_name=_('بند الراتب'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('المبلغ'))

    def __str__(self):
        return f"{self.payroll_entry} - {self.salary_item}"

    class Meta:
        verbose_name = _('تفاصيل بند الراتب')
        verbose_name_plural = _('تفاصيل بنود الرواتب')
        managed = True
        db_table = 'Hr_PayrollItemDetail'
