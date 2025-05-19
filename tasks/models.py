from django.db import models
from meetings.models import Meeting
from accounts.models import Users_Login_New

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('in_progress', 'يجرى العمل عليها'),
        ('completed', 'مكتملة'),
        ('canceled', 'ملغاة'),
        # ('deferred', 'مؤجلة'),
        # ('failed', 'فشلت'),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    assigned_to = models.ForeignKey(Users_Login_New, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(Users_Login_New, on_delete=models.CASCADE, related_name='created_tasks', null=True, blank=True)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        permissions = [
            ("view_dashboard", "Can view tasks dashboard"),
            ("view_mytask", "Can view my tasks"),
            ("view_report", "Can view task reports"),
            ("export_report", "Can export task reports"),
        ]

    def __str__(self):
        return f"{self.description[:50]} - {self.assigned_to.username}"


class TaskStep(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='steps')
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Step for {self.task.description[:20]}"


