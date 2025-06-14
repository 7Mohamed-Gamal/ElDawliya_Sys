from django.db import models
from meetings.models import Meeting
from accounts.models import Users_Login_New

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('in_progress', 'يجرى العمل عليها'),
        ('completed', 'مكتملة'),
        ('canceled', 'ملغاة'),
        ('deferred', 'مؤجلة'),
        ('failed', 'فشلت'),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان المهمة", blank=True, null=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    assigned_to = models.ForeignKey(Users_Login_New, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(Users_Login_New, on_delete=models.CASCADE, related_name='created_tasks', null=True, blank=True)
    description = models.TextField(verbose_name="وصف المهمة")
    start_date = models.DateTimeField(verbose_name="تاريخ البدء")
    end_date = models.DateTimeField(verbose_name="تاريخ الانتهاء")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="الحالة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        permissions = [
            ("view_dashboard", "Can view tasks dashboard"),
            ("view_mytask", "Can view my tasks"),
            ("view_report", "Can view task reports"),
            ("export_report", "Can export task reports"),
        ]

    def __str__(self):
        title = self.title or self.description[:50]
        return f"{title} - {self.assigned_to.username}"

    def get_display_title(self):
        """Get the display title for the task"""
        return self.title if self.title else self.description[:50] + "..."

    def get_status_display(self):
        """Get the display text for status"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class TaskStep(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='steps')
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Step for {self.task.description[:20]}"


