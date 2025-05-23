from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from Hr.models import Employee
from .models import EmployeeAttendanceProfile, AttendanceRule, LeaveType, LeaveBalance


@receiver(post_save, sender=Employee)
def create_employee_attendance_profile(sender, instance, created, **kwargs):
    """Create attendance profile when a new employee is created"""
    if created:
        # Get or create a default attendance rule
        default_rule, _ = AttendanceRule.objects.get_or_create(
            name="Default Rule",
            defaults={
                'description': "Default attendance rule for new employees",
                'late_grace_period': 15,
                'early_leave_grace_period': 15,
                'is_active': True
            }
        )

        # Create attendance profile
        profile = EmployeeAttendanceProfile.objects.create(
            employee=instance,
            attendance_rule=default_rule,
            work_hours_per_day=8.00  # Default to 8 hours
        )

        # Create leave balances for all active leave types
        current_year = now().year
        for leave_type in LeaveType.objects.filter(is_active=True):
            LeaveBalance.objects.create(
                employee=instance,
                leave_type=leave_type,
                year=current_year,
                allocated_days=leave_type.max_days_per_year
            )
