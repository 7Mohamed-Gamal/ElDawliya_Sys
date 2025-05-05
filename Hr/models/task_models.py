from django.db import models
from django.utils.translation import gettext_lazy as _
from Hr.models.employee_model import Employee

class EmployeeTask(models.Model):
    """
    Modelo para tareas asignadas a empleados
    """
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتملة')),
        ('cancelled', _('ملغاة')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('منخفضة')),
        ('medium', _('متوسطة')),
        ('high', _('عالية')),
        ('urgent', _('عاجلة')),
    ]

    title = models.CharField(max_length=200, verbose_name=_('عنوان المهمة'))
    description = models.TextField(verbose_name=_('وصف المهمة'))
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='tasks', verbose_name=_('الموظف'))
    assigned_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, related_name='hr_assigned_tasks', verbose_name=_('تم التكليف بواسطة'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name=_('الأولوية'))
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    due_date = models.DateField(verbose_name=_('تاريخ الاستحقاق'))
    completion_date = models.DateField(null=True, blank=True, verbose_name=_('تاريخ الإنجاز'))
    progress = models.PositiveIntegerField(default=0, verbose_name=_('نسبة الإنجاز (%)'), help_text=_('من 0 إلى 100'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return f"{self.title} - {self.employee}"

    class Meta:
        verbose_name = _('مهمة الموظف')
        verbose_name_plural = _('مهام الموظفين')
        # Using the default table name (hr_employeetask) instead of a custom one
        # db_table = 'Hr_EmployeeTask'
        ordering = ['-due_date', 'priority']
        managed = True


class TaskStep(models.Model):
    """
    نموذج لخطوات المهمة
    """
    task_id = models.IntegerField(verbose_name=_('رقم المهمة'))  # استخدام حقل عددي بدلاً من ForeignKey
    description = models.TextField(verbose_name=_('وصف الخطوة'))
    completed = models.BooleanField(default=False, verbose_name=_('مكتملة'))
    completion_date = models.DateField(null=True, blank=True, verbose_name=_('تاريخ الإنجاز'))
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, related_name='created_task_steps', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return f"خطوة للمهمة رقم: {self.task_id}"

    @property
    def task(self):
        """الحصول على المهمة المرتبطة"""
        return EmployeeTask.objects.get(pk=self.task_id)

    class Meta:
        verbose_name = _('خطوة المهمة')
        verbose_name_plural = _('خطوات المهام')
        ordering = ['-created_at']
        managed = True
