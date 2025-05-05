from django.db import models
from django.utils.translation import gettext_lazy as _

class HrTask(models.Model):
    """
    Modelo para tareas del departamento de RRHH
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

    TASK_TYPE_CHOICES = [
        ('insurance', _('متابعة التأمينات')),
        ('transportation', _('متابعة بدل المواصلات')),
        ('car_issues', _('مشاكل سيارات النقل')),
        ('contract_renewal', _('تجديد العقود')),
        ('other', _('أخرى')),
    ]

    title = models.CharField(max_length=200, verbose_name=_('عنوان المهمة'))
    description = models.TextField(verbose_name=_('وصف المهمة'))
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='other', verbose_name=_('نوع المهمة'))
    assigned_to = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, related_name='hr_tasks', verbose_name=_('تم التكليف إلى'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name=_('الأولوية'))
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    due_date = models.DateField(verbose_name=_('تاريخ الاستحقاق'))
    completion_date = models.DateField(null=True, blank=True, verbose_name=_('تاريخ الإنجاز'))
    progress = models.PositiveIntegerField(default=0, verbose_name=_('نسبة الإنجاز (%)'), help_text=_('من 0 إلى 100'))
    steps_taken = models.TextField(blank=True, null=True, verbose_name=_('الخطوات المتخذة'))
    reminder_days = models.PositiveIntegerField(default=3, verbose_name=_('أيام التذكير قبل الموعد'))
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, related_name='created_hr_tasks', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('مهمة الموارد البشرية')
        verbose_name_plural = _('مهام الموارد البشرية')
        # Using the default table name (hr_hrtask) instead of a custom one
        # db_table = 'Hr_HrTask'
        ordering = ['-due_date', 'priority']
        managed = True
