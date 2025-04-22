from django.db import models
from django.utils.translation import gettext_lazy as _
from Hr.models.employee_model import Employee

class LeaveType(models.Model):
    """
    Modelo para tipos de permisos/licencias
    """
    name = models.CharField(max_length=100, verbose_name=_('الاسم'))
    affects_salary = models.BooleanField(default=False, verbose_name=_('يؤثر على الراتب'))
    is_paid = models.BooleanField(default=True, verbose_name=_('مدفوع الأجر'))
    max_days_per_year = models.PositiveIntegerField(default=0, verbose_name=_('الحد الأقصى للأيام في السنة'), help_text=_('0 يعني غير محدود'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('نوع الإجازة')
        verbose_name_plural = _('أنواع الإجازات')
        db_table = 'Hr_LeaveType'
        managed = True

class EmployeeLeave(models.Model):
    """
    Modelo para permisos/licencias de empleados
    """
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('approved', _('موافق عليه')),
        ('rejected', _('مرفوض')),
        ('cancelled', _('ملغى')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves', verbose_name=_('الموظف'))
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='employee_leaves', verbose_name=_('نوع الإجازة'))
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
    days_count = models.PositiveIntegerField(verbose_name=_('عدد الأيام'))
    reason = models.TextField(verbose_name=_('السبب'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))
    approved_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves', verbose_name=_('تمت الموافقة بواسطة'))
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الموافقة'))
    rejection_reason = models.TextField(blank=True, null=True, verbose_name=_('سبب الرفض'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"

    class Meta:
        verbose_name = _('إجازة الموظف')
        verbose_name_plural = _('إجازات الموظفين')
        db_table = 'Hr_EmployeeLeave'
        ordering = ['-start_date']
        managed = True
