from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from .models import (
    AttendanceRule,
    WorkSchedule,
    WeeklyHoliday,
    LeaveType,
    EmployeeAttendanceProfile,
    LeaveBalance,
    AttendanceRecord,
    # Schema-specific models
    AttendanceRules,
    EmployeeAttendance,
    # ZK Device models
    ZKDevice,
    ZKAttendanceRaw,
    EmployeeDeviceMapping,
    AttendanceProcessingLog,
    AttendanceSummary
)


class WorkScheduleInline(admin.TabularInline):
    """WorkScheduleInline class"""
    model = WorkSchedule
    extra = 0
    min_num = 1


class WeeklyHolidayInline(admin.TabularInline):
    """WeeklyHolidayInline class"""
    model = WeeklyHoliday
    extra = 0


@admin.register(AttendanceRule)
class AttendanceRuleAdmin(admin.ModelAdmin):
    """AttendanceRuleAdmin class"""
    list_display = ['name', 'is_active', 'late_grace_period', 'early_leave_grace_period']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    inlines = [WorkScheduleInline, WeeklyHolidayInline]


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    """LeaveTypeAdmin class"""
    list_display = ['name', 'code', 'is_paid', 'max_days_per_year', 'requires_approval']
    list_filter = ['is_paid', 'requires_approval']
    search_fields = ['name', 'code', 'description']


@admin.register(EmployeeAttendanceProfile)
class EmployeeAttendanceProfileAdmin(admin.ModelAdmin):
    """EmployeeAttendanceProfileAdmin class"""
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
    """AttendanceRecordAdmin class"""
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
        """get_queryset function"""
        return super().get_queryset(request).select_related('employee')


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    """LeaveBalanceAdmin class"""
    list_display = ['employee', 'leave_type', 'year', 'allocated_days', 'used_days', 'remaining_days']
    list_filter = ['leave_type', 'year']
    search_fields = ['employee__full_name', 'employee__employee_id']
    readonly_fields = ['used_days', 'remaining_days']


# Register schema-specific attendance models
try:
    @admin.register(AttendanceRules)
    class AttendanceRulesAdmin(admin.ModelAdmin):
        """AttendanceRulesAdmin class"""
        list_display = ('rule_id', 'rule_name', 'shift_start', 'shift_end', 'is_default')
        list_filter = ('is_default', 'week_end_days')
        search_fields = ('rule_name',)
        ordering = ('-is_default', 'rule_name')

        fieldsets = (
            ('معلومات أساسية', {
                'fields': ('rule_name', 'is_default')
            }),
            ('أوقات العمل', {
                'fields': ('shift_start', 'shift_end', 'overtime_start_after')
            }),
            ('القوانين', {
                'fields': ('late_threshold', 'early_threshold', 'week_end_days')
            }),
        )

        def save_model(self, request, obj, form, change):
            """save_model function"""
            if obj.is_default:
                # إزالة الافتراضية من جميع القواعد الأخرى
                AttendanceRules.objects.exclude(pk=obj.pk).update(is_default=False)
            super().save_model(request, obj, form, change)

    @admin.register(EmployeeAttendance)
    class EmployeeAttendanceAdmin(admin.ModelAdmin):
        """EmployeeAttendanceAdmin class"""
        list_display = ('att_id', 'emp', 'att_date', 'check_in', 'check_out',
                       'work_duration_display', 'status', 'rule')
        list_filter = ('status', 'att_date', 'rule')
        date_hierarchy = 'att_date'
        search_fields = ('emp__emp_code', 'emp__first_name', 'emp__last_name')
        ordering = ('-att_date', 'emp__emp_code')

        readonly_fields = ('work_duration_display', 'late_minutes_display',
                          'early_leave_minutes_display', 'overtime_minutes_display')

        fieldsets = (
            ('معلومات الموظف', {
                'fields': ('emp', 'att_date', 'rule')
            }),
            ('أوقات الحضور', {
                'fields': ('check_in', 'check_out')
            }),
            ('الحالة والإحصائيات', {
                'fields': ('status', 'work_duration_display', 'late_minutes_display',
                          'early_leave_minutes_display', 'overtime_minutes_display')
            }),
        )

        def work_duration_display(self, obj):
            """work_duration_display function"""
            if obj.check_in and obj.check_out:
                minutes = obj.calculate_work_minutes()
                hours = minutes // 60
                mins = minutes % 60
                return f"{hours}:{mins:02d}"
            return "-"
        work_duration_display.short_description = "مدة العمل"

        def late_minutes_display(self, obj):
            """late_minutes_display function"""
            return f"{obj.calculate_late_minutes()} دقيقة"
        late_minutes_display.short_description = "دقائق التأخير"

        def early_leave_minutes_display(self, obj):
            """early_leave_minutes_display function"""
            return f"{obj.calculate_early_leave_minutes()} دقيقة"
        early_leave_minutes_display.short_description = "دقائق المغادرة المبكرة"

        def overtime_minutes_display(self, obj):
            """overtime_minutes_display function"""
            return f"{obj.calculate_overtime_minutes()} دقيقة"
        overtime_minutes_display.short_description = "دقائق الوقت الإضافي"

        def get_queryset(self, request):
            """get_queryset function"""
            return super().get_queryset(request).select_related('emp', 'rule')

        actions = ['mark_as_present', 'mark_as_absent', 'recalculate_status']

        def mark_as_present(self, request, queryset):
            """mark_as_present function"""
            updated = queryset.update(status='Present')
            self.message_user(request, f'تم تحديث {updated} سجل إلى حاضر')
        mark_as_present.short_description = "تحديد كحاضر"

        def mark_as_absent(self, request, queryset):
            """mark_as_absent function"""
            updated = queryset.update(status='Absent')
            self.message_user(request, f'تم تحديث {updated} سجل إلى غائب')
        mark_as_absent.short_description = "تحديد كغائب"

        def recalculate_status(self, request, queryset):
            """recalculate_status function"""
            updated_count = 0
            for record in queryset:
                old_status = record.status
                # إعادة حساب الحالة بناءً على المنطق
                if record.check_in and record.check_out:
                    if record.calculate_late_minutes() > 0:
                        record.status = 'Late'
                    elif record.calculate_early_leave_minutes() > 0:
                        record.status = 'EarlyLeave'
                    else:
                        record.status = 'Present'
                elif record.check_in:
                    record.status = 'Present'
                else:
                    record.status = 'Absent'

                if old_status != record.status:
                    record.save()
                    updated_count += 1

            self.message_user(request, f'تم إعادة حساب {updated_count} سجل')
        recalculate_status.short_description = "إعادة حساب الحالة"

except Exception:
    # If models are not present for any reason, skip admin registration
    pass


# ============================================================================
# ZK DEVICE MANAGEMENT ADMIN
# ============================================================================

@admin.register(ZKDevice)
class ZKDeviceAdmin(admin.ModelAdmin):
    """ZKDeviceAdmin class"""
    list_display = ('device_name', 'ip_address', 'port', 'location',
                   'status', 'connection_status', 'last_sync', 'unprocessed_count')
    list_filter = ('status', 'timezone')
    search_fields = ('device_name', 'device_serial', 'ip_address', 'location')
    ordering = ('device_name',)

    fieldsets = (
        ('معلومات الجهاز', {
            'fields': ('device_name', 'device_serial', 'status')
        }),
        ('إعدادات الشبكة', {
            'fields': ('ip_address', 'port', 'timezone')
        }),
        ('معلومات إضافية', {
            'fields': ('location',)
        }),
        ('معلومات المزامنة', {
            'fields': ('last_sync',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('last_sync',)

    def connection_status(self, obj):
        """connection_status function"""
        if obj.is_online():
            return format_html('<span style="color: green;">●</span> متصل')
        else:
            return format_html('<span style="color: red;">●</span> غير متصل')
    connection_status.short_description = "حالة الاتصال"

    def unprocessed_count(self, obj):
        """unprocessed_count function"""
        count = ZKAttendanceRaw.objects.filter(
            device=obj, is_processed=False
        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
        if count > 0:
            return format_html('<span style="color: orange;">{}</span>', count)
        return count
    unprocessed_count.short_description = "السجلات غير المعالجة"

    actions = ['test_connection', 'sync_device_data', 'activate_devices', 'deactivate_devices']

    def test_connection(self, request, queryset):
        """test_connection function"""
        from .zk_service import test_device_connection

        success_count = 0
        for device in queryset:
            result = test_device_connection(device.device_id)
            if result['connection_status']:
                success_count += 1

        self.message_user(
            request,
            f'تم اختبار {queryset.count()} جهاز. {success_count} متصل بنجاح.'
        )
    test_connection.short_description = "اختبار الاتصال"

    def sync_device_data(self, request, queryset):
        """sync_device_data function"""
        from .tasks import sync_single_device

        for device in queryset:
            sync_single_device.delay(device.device_id)

        self.message_user(
            request,
            f'تم بدء مزامنة {queryset.count()} جهاز في الخلفية.'
        )
    sync_device_data.short_description = "مزامنة البيانات"

    def activate_devices(self, request, queryset):
        """activate_devices function"""
        updated = queryset.update(status='active')
        self.message_user(request, f'تم تفعيل {updated} جهاز')
    activate_devices.short_description = "تفعيل الأجهزة"

    def deactivate_devices(self, request, queryset):
        """deactivate_devices function"""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'تم إلغاء تفعيل {updated} جهاز')
    deactivate_devices.short_description = "إلغاء تفعيل الأجهزة"


@admin.register(ZKAttendanceRaw)
class ZKAttendanceRawAdmin(admin.ModelAdmin):
    """ZKAttendanceRawAdmin class"""
    list_display = ('raw_id', 'device', 'user_id', 'employee_name',
                   'timestamp', 'punch_type_arabic', 'is_processed')
    list_filter = ('device', 'punch_type', 'is_processed', 'timestamp')
    search_fields = ('user_id', 'employee__emp_code', 'employee__first_name')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

    readonly_fields = ('created_at',)

    def employee_name(self, obj):
        """employee_name function"""
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return "-"
    employee_name.short_description = "اسم الموظف"

    def punch_type_arabic(self, obj):
        """punch_type_arabic function"""
        return obj.get_punch_type_display_arabic()
    punch_type_arabic.short_description = "نوع البصمة"

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('device', 'employee')

    actions = ['mark_as_processed', 'reprocess_records']

    def mark_as_processed(self, request, queryset):
        """mark_as_processed function"""
        updated = queryset.update(is_processed=True)
        self.message_user(request, f'تم تحديد {updated} سجل كمعالج')
    mark_as_processed.short_description = "تحديد كمعالج"

    def reprocess_records(self, request, queryset):
        """reprocess_records function"""
        from .zk_service import ZKDataProcessor

        processed_count = 0
        for record in queryset:
            if record.employee:
                try:
                    ZKDataProcessor._create_attendance_record(record)
                    processed_count += 1
                except Exception as e:
                    messages.error(request, f'خطأ في معالجة السجل {record.raw_id}: {str(e)}')

        self.message_user(request, f'تم إعادة معالجة {processed_count} سجل')
    reprocess_records.short_description = "إعادة معالجة السجلات"


@admin.register(EmployeeDeviceMapping)
class EmployeeDeviceMappingAdmin(admin.ModelAdmin):
    """EmployeeDeviceMappingAdmin class"""
    list_display = ('mapping_id', 'employee_code', 'employee_name',
                   'device', 'device_user_id', 'is_active', 'last_used')
    list_filter = ('device', 'is_active')
    search_fields = ('employee__emp_code', 'employee__first_name',
                    'device_user_id', 'device__device_name')
    ordering = ('device__device_name', 'employee__emp_code')

    readonly_fields = ('enrollment_date', 'last_used')

    def employee_code(self, obj):
        """employee_code function"""
        return obj.employee.emp_code
    employee_code.short_description = "كود الموظف"

    def employee_name(self, obj):
        """employee_name function"""
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    employee_name.short_description = "اسم الموظف"

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('employee', 'device')

    actions = ['activate_mappings', 'deactivate_mappings']

    def activate_mappings(self, request, queryset):
        """activate_mappings function"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'تم تفعيل {updated} ربط')
    activate_mappings.short_description = "تفعيل الربط"

    def deactivate_mappings(self, request, queryset):
        """deactivate_mappings function"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'تم إلغاء تفعيل {updated} ربط')
    deactivate_mappings.short_description = "إلغاء تفعيل الربط"


@admin.register(AttendanceProcessingLog)
class AttendanceProcessingLogAdmin(admin.ModelAdmin):
    """AttendanceProcessingLogAdmin class"""
    list_display = ('log_id', 'device', 'process_date', 'records_fetched',
                   'records_processed', 'records_failed', 'status',
                   'success_rate_display', 'processing_time')
    list_filter = ('device', 'status', 'process_date')
    search_fields = ('device__device_name',)
    date_hierarchy = 'process_date'
    ordering = ('-created_at',)

    readonly_fields = ('created_at', 'success_rate_display')

    def success_rate_display(self, obj):
        """success_rate_display function"""
        rate = obj.success_rate
        if rate >= 90:
            color = 'green'
        elif rate >= 70:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}">{:.1f}%</span>',
            color, rate
        )
    success_rate_display.short_description = "نسبة النجاح"

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('device')


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    """AttendanceSummaryAdmin class"""
    list_display = ('employee_code', 'employee_name', 'year', 'month',
                   'present_days', 'absent_days', 'late_days',
                   'attendance_rate_display', 'punctuality_rate_display',
                   'total_work_hours')
    list_filter = ('year', 'month')
    search_fields = ('employee__emp_code', 'employee__first_name')
    ordering = ('-year', '-month', 'employee__emp_code')

    readonly_fields = ('created_at', 'updated_at', 'attendance_rate_display',
                      'punctuality_rate_display')

    def employee_code(self, obj):
        """employee_code function"""
        return obj.employee.emp_code
    employee_code.short_description = "كود الموظف"

    def employee_name(self, obj):
        """employee_name function"""
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    employee_name.short_description = "اسم الموظف"

    def attendance_rate_display(self, obj):
        """attendance_rate_display function"""
        rate = obj.attendance_rate
        if rate >= 95:
            color = 'green'
        elif rate >= 85:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}">{:.1f}%</span>',
            color, rate
        )
    attendance_rate_display.short_description = "نسبة الحضور"

    def punctuality_rate_display(self, obj):
        """punctuality_rate_display function"""
        rate = obj.punctuality_rate
        if rate >= 95:
            color = 'green'
        elif rate >= 85:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}">{:.1f}%</span>',
            color, rate
        )
    punctuality_rate_display.short_description = "نسبة الالتزام بالوقت"

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('employee')

    actions = ['regenerate_summaries']

    def regenerate_summaries(self, request, queryset):
        """regenerate_summaries function"""
        from .tasks import generate_daily_attendance_summary

        # تشغيل مهمة إعادة إنشاء الملخصات
        generate_daily_attendance_summary.delay()

        self.message_user(
            request,
            'تم بدء إعادة إنشاء ملخصات الحضور في الخلفية.'
        )
    regenerate_summaries.short_description = "إعادة إنشاء الملخصات"
