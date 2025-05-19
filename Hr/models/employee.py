from django.db import models

class Employee(models.Model):
    # ...existing fields...
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    hire_date = models.DateField()

    class Meta:
        permissions = [
            ("view_salary_report", "Can view salary reports"),
            ("view_attendance_report", "Can view attendance reports"),
            ("view_leave_report", "Can view leave reports"),
            ("view_task_report", "Can view task reports"),
            ("export_salary_report", "Can export salary reports"),
            ("export_attendance_report", "Can export attendance reports"),
            ("export_leave_report", "Can export leave reports"),
            ("export_task_report", "Can export task reports"),
        ]

    def __str__(self):
        return self.name