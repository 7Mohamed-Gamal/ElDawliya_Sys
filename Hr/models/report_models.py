from django.db import models

class Report(models.Model):
    # ...existing fields...

    class Meta:
        # ...existing options...
        permissions = [
            ("view_reports", "Can view all reports"),
            ("view_report", "Can view individual report"),
            ("view_salary_report", "Can view salary reports"),
            ("view_attendance_report", "Can view attendance reports"), 
            ("view_leave_report", "Can view leave reports"),
            ("view_task_report", "Can view task reports"),
            ("export_salary_report", "Can export salary reports"),
            ("export_attendance_report", "Can export attendance reports"),
            ("export_leave_report", "Can export leave reports"),
            ("export_task_report", "Can export task reports"),
        ]