from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from accounts.models import Users_Login_New

class TaskCategory(models.Model):
    """
    نموذج لتصنيفات المهام
    """
    name = models.CharField(max_length=100, verbose_name=_('اسم التصنيف'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف التصنيف'))
    color = models.CharField(max_length=20, default='#3498db', verbose_name=_('اللون'))
    icon = models.CharField(max_length=50, default='fas fa-tasks', verbose_name=_('الأيقونة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('تصنيف المهام')
        verbose_name_plural = _('تصنيفات المهام')
        ordering = ['name']


class EmployeeTask(models.Model):
    """
    نموذج لمهام الموظفين
    """
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتملة')),
        ('cancelled', _('ملغاة')),
        ('deferred', _('مؤجلة')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('منخفضة')),
        ('medium', _('متوسطة')),
        ('high', _('عالية')),
        ('urgent', _('عاجلة')),
    ]

    title = models.CharField(max_length=200, verbose_name=_('عنوان المهمة'))
    description = models.TextField(verbose_name=_('وصف المهمة'))
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='tasks', verbose_name=_('التصنيف'))
    created_by = models.ForeignKey(Users_Login_New, on_delete=models.CASCADE,
                                  related_name='created_employee_tasks', verbose_name=_('تم الإنشاء بواسطة'))
    assigned_to = models.ForeignKey(Users_Login_New, on_delete=models.CASCADE,
                                   related_name='assigned_employee_tasks', verbose_name=_('تم التكليف إلى'),
                                   null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name=_('الأولوية'))
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    due_date = models.DateField(verbose_name=_('تاريخ الاستحقاق'))
    completion_date = models.DateField(null=True, blank=True, verbose_name=_('تاريخ الإنجاز'))
    progress = models.PositiveIntegerField(default=0, verbose_name=_('نسبة الإنجاز (%)'),
                                         help_text=_('من 0 إلى 100'))
    is_private = models.BooleanField(default=True, verbose_name=_('خاص'),
                                   help_text=_('إذا كان خاصًا، فلن يراه إلا المنشئ والمشرف'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # إذا تم تغيير الحالة إلى مكتملة، قم بتعيين تاريخ الإنجاز
        if self.status == 'completed' and not self.completion_date:
            self.completion_date = timezone.now().date()
        # إذا تم تغيير الحالة من مكتملة، قم بإزالة تاريخ الإنجاز
        elif self.status != 'completed':
            self.completion_date = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('مهمة الموظف')
        verbose_name_plural = _('مهام الموظفين')
        ordering = ['-created_at', 'priority']
        permissions = [
            ("view_dashboard", "Can view employee tasks dashboard"),
            ("view_mytask", "Can view my employee tasks"),
            ("view_calendar", "Can view employee tasks calendar"),
            ("view_analytics", "Can view employee tasks analytics"),
            ("view_notification", "Can view employee tasks notifications"),
            ("export_report", "Can export employee tasks reports"),
        ]


class TaskStep(models.Model):
    """
    نموذج لخطوات المهمة
    """
    task = models.ForeignKey(EmployeeTask, on_delete=models.CASCADE, related_name='steps',
                           verbose_name=_('المهمة'))
    description = models.TextField(verbose_name=_('وصف الخطوة'))
    completed = models.BooleanField(default=False, verbose_name=_('مكتملة'))
    completion_date = models.DateField(null=True, blank=True, verbose_name=_('تاريخ الإنجاز'))
    created_by = models.ForeignKey(Users_Login_New, on_delete=models.SET_NULL, null=True,
                                  related_name='created_employee_task_steps', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return f"{self.description[:50]}..."

    def save(self, *args, **kwargs):
        # إذا تم تعيين الخطوة كمكتملة، قم بتعيين تاريخ الإنجاز
        if self.completed and not self.completion_date:
            self.completion_date = timezone.now().date()
        # إذا تم تغيير الحالة من مكتملة، قم بإزالة تاريخ الإنجاز
        elif not self.completed:
            self.completion_date = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('خطوة المهمة')
        verbose_name_plural = _('خطوات المهام')
        ordering = ['created_at']


class TaskReminder(models.Model):
    """
    نموذج لتذكيرات المهام
    """
    task = models.ForeignKey(EmployeeTask, on_delete=models.CASCADE, related_name='reminders',
                           verbose_name=_('المهمة'))
    reminder_date = models.DateTimeField(verbose_name=_('تاريخ التذكير'))
    is_sent = models.BooleanField(default=False, verbose_name=_('تم الإرسال'))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الإرسال'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))

    def __str__(self):
        return f"تذكير لـ {self.task.title} في {self.reminder_date}"

    class Meta:
        verbose_name = _('تذكير المهمة')
        verbose_name_plural = _('تذكيرات المهام')
        ordering = ['reminder_date']
