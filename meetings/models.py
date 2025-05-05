from django.db import models
from accounts.models import Users_Login_New

class Meeting(models.Model):
    """
    نموذج الاجتماعات
    يستخدم لتخزين معلومات الاجتماعات في النظام
    """
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان الاجتماع")
    date = models.DateTimeField(verbose_name="تاريخ ووقت الاجتماع")
    topic = models.TextField(verbose_name="موضوع الاجتماع")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="حالة الاجتماع")
    created_by = models.ForeignKey(Users_Login_New, on_delete=models.CASCADE, related_name='meetings', verbose_name="منشئ الاجتماع")

    class Meta:
        verbose_name = "اجتماع"
        verbose_name_plural = "الاجتماعات"

    def __str__(self):
        return self.title

class Attendee(models.Model):
    """
    نموذج الحضور
    يستخدم لتخزين معلومات حضور المستخدمين للاجتماعات
    """
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendees', verbose_name="الاجتماع")
    user = models.ForeignKey(Users_Login_New, on_delete=models.CASCADE, related_name='attendees', verbose_name="المستخدم")

    class Meta:
        unique_together = ('meeting', 'user')
        verbose_name = "حضور"
        verbose_name_plural = "الحضور"

    def __str__(self):
        return f"{self.user.username} - {self.meeting.title}"