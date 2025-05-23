from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models import Count, Q
from Hr.models import Employee


class AttendanceRule(models.Model):
    """Model for different attendance rules (e.g., Workers Rule, Management Rule)"""
    name = models.CharField(_('Rule Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    late_grace_period = models.IntegerField(
        _('Late Grace Period (minutes)'),
        default=15,
        validators=[MinValueValidator(0)]
    )
    early_leave_grace_period = models.IntegerField(
        _('Early Leave Grace Period (minutes)'),
        default=15,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Attendance Rule')
        verbose_name_plural = _('Attendance Rules')

    def __str__(self):
        return self.name


class WorkSchedule(models.Model):
    """Model for work schedules within attendance rules"""
    DAYS_OF_WEEK = [
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ]

    rule = models.ForeignKey(
        AttendanceRule,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name=_('Attendance Rule')
    )
    day_of_week = models.IntegerField(
        _('Day of Week'),
        choices=DAYS_OF_WEEK
    )
    start_time = models.TimeField(_('Start Time'))
    end_time = models.TimeField(_('End Time'))
    break_start = models.TimeField(_('Break Start Time'), null=True, blank=True)
    break_end = models.TimeField(_('Break End Time'), null=True, blank=True)

    class Meta:
        verbose_name = _('Work Schedule')
        verbose_name_plural = _('Work Schedules')
        unique_together = ['rule', 'day_of_week']

    def __str__(self):
        return f"{self.rule.name} - {self.get_day_of_week_display()}"


class WeeklyHoliday(models.Model):
    """Model for weekly holidays configuration"""
    rule = models.ForeignKey(
        AttendanceRule,
        on_delete=models.CASCADE,
        related_name='holidays',
        verbose_name=_('Attendance Rule')
    )
    day = models.IntegerField(
        _('Holiday Day'),
        choices=WorkSchedule.DAYS_OF_WEEK
    )

    class Meta:
        verbose_name = _('Weekly Holiday')
        verbose_name_plural = _('Weekly Holidays')
        unique_together = ['rule', 'day']

    def __str__(self):
        return f"{self.rule.name} - {self.get_day_display()}"


class LeaveType(models.Model):
    """Model for different types of leaves"""
    name = models.CharField(_('Leave Type'), max_length=100)
    code = models.CharField(_('Code'), max_length=20, unique=True)
    description = models.TextField(_('Description'), blank=True)
    is_paid = models.BooleanField(_('Is Paid Leave'), default=True)
    max_days_per_year = models.PositiveIntegerField(
        _('Maximum Days Per Year'),
        validators=[MinValueValidator(0)]
    )
    requires_approval = models.BooleanField(_('Requires Approval'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Leave Type')
        verbose_name_plural = _('Leave Types')

    def __str__(self):
        return self.name


class EmployeeAttendanceProfile(models.Model):
    """Model for employee-specific attendance settings"""
    SALARY_STATUS = [
        ('active', _('Active')),
        ('suspended', _('Suspended')),
    ]
    ATTENDANCE_STATUS = [
        ('active', _('Active')),
        ('suspended', _('Suspended')),
    ]

    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_profile',
        verbose_name=_('Employee')
    )
    attendance_rule = models.ForeignKey(
        AttendanceRule,
        on_delete=models.PROTECT,
        related_name='employee_profiles',
        verbose_name=_('Attendance Rule')
    )
    work_hours_per_day = models.DecimalField(
        _('Work Hours Per Day'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(24)]
    )
    salary_status = models.CharField(
        _('Salary Status'),
        max_length=20,
        choices=SALARY_STATUS,
        default='active'
    )
    attendance_status = models.CharField(
        _('Attendance Status'),
        max_length=20,
        choices=ATTENDANCE_STATUS,
        default='active'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Employee Attendance Profile')
        verbose_name_plural = _('Employee Attendance Profiles')

    def __str__(self):
        return f"{self.employee.full_name} - {self.attendance_rule.name}"


class LeaveBalance(models.Model):
    """Model for tracking employee leave balances"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balances',
        verbose_name=_('Employee')
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name='employee_balances',
        verbose_name=_('Leave Type')
    )
    year = models.PositiveIntegerField(_('Year'))
    allocated_days = models.DecimalField(
        _('Allocated Days'),
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    used_days = models.DecimalField(
        _('Used Days'),
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Leave Balance')
        verbose_name_plural = _('Leave Balances')
        unique_together = ['employee', 'leave_type', 'year']

    def __str__(self):
        return f"{self.employee.emp_full_name} - {self.leave_type.name} ({self.year})"

    @property
    def remaining_days(self):
        """Calculate remaining leave days"""
        return self.allocated_days - self.used_days


class AttendanceRecord(models.Model):
    """Model for daily attendance records"""
    RECORD_TYPE_CHOICES = [
        ('present', _('Present')),
        ('absent', _('Absent')),
        ('leave', _('Leave')),
        ('holiday', _('Holiday')),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='new_attendance_records',
        verbose_name=_('Employee')
    )
    date = models.DateField(_('Date'))
    check_in = models.DateTimeField(_('Check In Time'), null=True, blank=True)
    check_out = models.DateTimeField(_('Check Out Time'), null=True, blank=True)
    record_type = models.CharField(
        _('Record Type'),
        max_length=20,
        choices=RECORD_TYPE_CHOICES,
        default='present'
    )
    late_minutes = models.IntegerField(_('Late Minutes'), default=0)
    early_leave_minutes = models.IntegerField(_('Early Leave Minutes'), default=0)
    overtime_minutes = models.IntegerField(_('Overtime Minutes'), default=0)
    break_minutes = models.IntegerField(_('Break Minutes'), default=0)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Attendance Record')
        verbose_name_plural = _('Attendance Records')
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.emp_full_name} - {self.date}"

    def calculate_work_duration(self):
        """Calculate total work duration in minutes"""
        if self.check_in and self.check_out:
            total_minutes = (self.check_out - self.check_in).total_seconds() / 60
            return total_minutes - self.break_minutes
        return 0
