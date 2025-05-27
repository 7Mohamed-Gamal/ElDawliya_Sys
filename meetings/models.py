from django.db import models
from accounts.models import Users_Login_New

class MeetingTask(models.Model):
    """
    نموذج مهام الاجتماع
    يستخدم لتخزين المهام المرتبطة بالاجتماعات
    """
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتملة'),
    ]
    
    meeting = models.ForeignKey('Meeting', on_delete=models.CASCADE, related_name='meeting_tasks', verbose_name="الاجتماع")
    description = models.TextField(verbose_name="وصف المهمة")
    assigned_to = models.ForeignKey(Users_Login_New, on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='meeting_tasks', verbose_name="تم تعيينها لـ")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="الحالة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء المتوقع")

    class Meta:
        verbose_name = "مهمة اجتماع"
        verbose_name_plural = "مهام الاجتماعات"

    def __str__(self):
        return f"{self.description[:50]}..." if len(self.description) > 50 else self.description

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
        permissions = [
            ("view_meetingtask", "Can view meeting tasks"),
            ("add_meetingtask", "Can add meeting tasks"),
            ("change_meetingtask", "Can change meeting tasks"),
            ("delete_meetingtask", "Can delete meeting tasks"),
            ("view_meetingreport", "Can view meeting reports"),
            ("export_meetingreport", "Can export meeting reports"),
        ]

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
