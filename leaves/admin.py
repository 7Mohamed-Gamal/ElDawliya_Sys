from django.contrib import admin
from .models import LeaveType, EmployeeLeave, PublicHoliday

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('leave_type_id', 'leave_name', 'is_paid', 'max_days_per_year')
    search_fields = ('leave_name',)
    list_filter = ('is_paid',)

@admin.register(EmployeeLeave)
class EmployeeLeaveAdmin(admin.ModelAdmin):
    list_display = ('leave_id', 'emp', 'leave_type', 'start_date', 'end_date', 'status')
    search_fields = ('emp__emp_code', 'reason')
    list_filter = ('status', 'leave_type')
    date_hierarchy = 'start_date'

@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    list_display = ('holiday_id', 'holiday_date', 'description')
    date_hierarchy = 'holiday_date'
