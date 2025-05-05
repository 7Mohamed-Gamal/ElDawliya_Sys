from django.db import models
from django.utils.translation import gettext_lazy as _
from Hr.models.employee_model import Employee

class EmployeeFile(models.Model):
    """
    Modelo para archivos/documentos de empleados
    """
    FILE_TYPE_CHOICES = [
        ('id_card', _('بطاقة الهوية')),
        ('contract', _('عقد العمل')),
        ('cv', _('السيرة الذاتية')),
        ('certificate', _('شهادة')),
        ('medical', _('تقرير طبي')),
        ('other', _('أخرى')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='files', verbose_name=_('الموظف'))
    title = models.CharField(max_length=100, verbose_name=_('العنوان'))
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='other', verbose_name=_('نوع الملف'))
    file = models.FileField(upload_to='employee_files/%Y/%m/', verbose_name=_('الملف'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف'))
    uploaded_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, related_name='uploaded_files', verbose_name=_('تم الرفع بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return f"{self.title} - {self.employee}"

    class Meta:
        verbose_name = _('ملف الموظف')
        verbose_name_plural = _('ملفات الموظفين')
        # Using the default table name (hr_employeefile) instead of a custom one
        # db_table = 'Hr_EmployeeFile'
        ordering = ['-created_at']
        managed = True
