from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import LeaveType, EmployeeLeave, PublicHoliday, LeaveBalance


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('leave_type_id', 'leave_name', 'is_paid', 'max_days_per_year', 'requires_approval', 'is_active')
    search_fields = ('leave_name', 'description')
    list_filter = ('is_paid', 'requires_approval', 'can_carry_forward', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('leave_name', 'description', 'is_active')
        }),
        (_('إعدادات الإجازة'), {
            'fields': ('max_days_per_year', 'is_paid', 'requires_approval', 'can_carry_forward')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmployeeLeave)
class EmployeeLeaveAdmin(admin.ModelAdmin):
    list_display = ('leave_id', 'emp', 'leave_type', 'start_date', 'end_date', 'duration_days', 'status', 'created_at')
    search_fields = ('emp__first_name', 'emp__last_name', 'emp__emp_code', 'reason')
    list_filter = ('status', 'leave_type', 'start_date', 'created_at')
    date_hierarchy = 'start_date'
    readonly_fields = ('duration_days', 'is_current', 'is_future', 'is_past', 'created_at', 'updated_at')
    raw_id_fields = ('emp', 'approved_by')
    
    fieldsets = (
        (_('معلومات الإجازة'), {
            'fields': ('emp', 'leave_type', 'start_date', 'end_date', 'reason')
        }),
        (_('حالة الطلب'), {
            'fields': ('status', 'approved_by', 'approved_date', 'rejection_reason')
        }),
        (_('معلومات إضافية'), {
            'fields': ('duration_days', 'is_current', 'is_future', 'is_past'),
            'classes': ('collapse',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('emp', 'leave_type', 'approved_by')


@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    list_display = ('holiday_id', 'holiday_date', 'description', 'is_recurring', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_recurring', 'is_active', 'holiday_date')
    date_hierarchy = 'holiday_date'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (_('معلومات العطلة'), {
            'fields': ('holiday_date', 'description')
        }),
        (_('إعدادات العطلة'), {
            'fields': ('is_recurring', 'is_active')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('emp', 'leave_type', 'year', 'allocated_days', 'used_days', 'remaining_days', 'utilization_percentage')
    search_fields = ('emp__first_name', 'emp__last_name', 'emp__emp_code')
    list_filter = ('leave_type', 'year')
    readonly_fields = ('remaining_days', 'utilization_percentage', 'created_at', 'updated_at')
    raw_id_fields = ('emp',)
    
    fieldsets = (
        (_('معلومات الرصيد'), {
            'fields': ('emp', 'leave_type', 'year')
        }),
        (_('تفاصيل الرصيد'), {
            'fields': ('allocated_days', 'used_days', 'carried_forward')
        }),
        (_('الإحصائيات'), {
            'fields': ('remaining_days', 'utilization_percentage'),
            'classes': ('collapse',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('emp', 'leave_type')
    
    actions = ['update_used_days']
    
    def update_used_days(self, request, queryset):
        """تحديث الأيام المستخدمة من الإجازات المعتمدة"""
        updated_count = 0
        for balance in queryset:
            balance.update_used_days()
            updated_count += 1
        
        self.message_user(request, f'تم تحديث {updated_count} رصيد إجازة.')
    
    update_used_days.short_description = _('تحديث الأيام المستخدمة')
