from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    AttendanceRule,
    WorkSchedule,
    WeeklyHoliday,
    LeaveType,
    EmployeeAttendanceProfile,
    LeaveBalance,
    AttendanceRecord
)


class WorkScheduleInline(admin.TabularInline):
    model = WorkSchedule
    extra = 0
    min_num = 1


class WeeklyHolidayInline(admin.TabularInline):
    model = WeeklyHoliday
    extra = 0


@admin.register(AttendanceRule)
class AttendanceRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'late_grace_period', 'early_leave_grace_period']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    inlines = [WorkScheduleInline, WeeklyHolidayInline]


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_paid', 'max_days_per_year', 'requires_approval']
    list_filter = ['is_paid', 'requires_approval']
    search_fields = ['name', 'code', 'description']


@admin.register(EmployeeAttendanceProfile)
class EmployeeAttendanceProfileAdmin(admin.ModelAdmin):
    list_display = [
        'employee',
        'attendance_rule',
        'work_hours_per_day',
        'salary_status',
        'attendance_status'
    ]
    list_filter = ['salary_status', 'attendance_status', 'attendance_rule']
    search_fields = ['employee__full_name', 'employee__employee_id']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'employee',
        'date',
        'record_type',
        'check_in',
        'check_out',
        'late_minutes',
        'early_leave_minutes',
        'overtime_minutes'
    ]
    list_filter = ['record_type', 'date', 'employee']
    search_fields = ['employee__full_name', 'employee__employee_id', 'notes']
    date_hierarchy = 'date'
    readonly_fields = ['late_minutes', 'early_leave_minutes', 'overtime_minutes', 'break_minutes']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee')


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'year', 'allocated_days', 'used_days', 'remaining_days']
    list_filter = ['leave_type', 'year']
    search_fields = ['employee__full_name', 'employee__employee_id']
    readonly_fields = ['used_days', 'remaining_days']
