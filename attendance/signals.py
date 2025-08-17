from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
# Temporarily disabled - will be replaced with new employees app
# from Hr.models import Employee
from .models import EmployeeAttendanceProfile, AttendanceRule, LeaveType, LeaveBalance


# Temporarily disabled - will be replaced with new employees app
# @receiver(post_save, sender=Employee)
# def create_employee_attendance_profile(sender, instance, created, **kwargs):
#     """Create attendance profile when a new employee is created"""
#     # This will be re-enabled once the new employees app is created
