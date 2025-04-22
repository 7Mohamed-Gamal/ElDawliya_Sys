from django.db import models
from accounts.models import Users_Login_New

class Meeting(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    topic = models.TextField()
    created_by = models.ForeignKey(Users_Login_New, on_delete=models.CASCADE, related_name='meetings')

    def __str__(self):
        return self.title

class Attendee(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(Users_Login_New, on_delete=models.CASCADE, related_name='attendees')

    class Meta:
        unique_together = ('meeting', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.meeting.title}"