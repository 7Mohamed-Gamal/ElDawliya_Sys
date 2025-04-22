from django.db import models
from django.utils.translation import gettext_lazy as _
from Hr.models.employee_model import Employee

class EmployeeNote(models.Model):
    """
    Modelo para notas sobre empleados
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='notes', verbose_name=_('الموظف'))
    title = models.CharField(max_length=100, verbose_name=_('العنوان'))
    content = models.TextField(verbose_name=_('المحتوى'))
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, related_name='employee_notes', verbose_name=_('تم الإنشاء بواسطة'))
    is_important = models.BooleanField(default=False, verbose_name=_('مهم'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return f"{self.title} - {self.employee}"

    class Meta:
        verbose_name = _('ملاحظة الموظف')
        verbose_name_plural = _('ملاحظات الموظفين')
        db_table = 'Hr_EmployeeNote'
        ordering = ['-created_at']
        managed = True
