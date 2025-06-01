from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# تخصيص موقع الإدارة
admin.site.site_header = _('نظام الدولية للموارد البشرية')
admin.site.site_title = _('إدارة الموارد البشرية')
admin.site.index_title = _('لوحة تحكم الموارد البشرية')

# استيراد النماذج
from Hr.models import (
    Department, Job, JobInsurance, Car, Employee,
    SalaryItem, EmployeeSalaryItem, PayrollPeriod, PayrollEntry, PayrollItemDetail,
    AttendanceRule, EmployeeAttendanceRule, OfficialHoliday, AttendanceMachine,
    AttendanceRecord, AttendanceSummary, PickupPoint, EmployeeTask, EmployeeNote,
    EmployeeFile, HrTask, LeaveType, EmployeeLeave, EmployeeEvaluation
)

# النماذج الأساسية
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['dept_code', 'dept_name']
    search_fields = ['dept_name']
    ordering = ['dept_code']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['jop_code', 'jop_name']
    search_fields = ['jop_name']
    ordering = ['jop_code']

@admin.register(JobInsurance)
class JobInsuranceAdmin(admin.ModelAdmin):
    list_display = ['job_code_insurance', 'job_name_insurance']
    search_fields = ['job_name_insurance']
    ordering = ['job_code_insurance']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['car_id', 'car_name', 'car_type', 'supplier', 'is_active']
    list_filter = ['car_type', 'is_active']
    search_fields = ['car_name', 'car_id']
    ordering = ['car_id']

# نماذج الموظفين
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['emp_id', 'emp_full_name', 'department', 'jop_name', 'working_condition', 'emp_date_hiring']
    list_filter = ['working_condition', 'department', 'insurance_status', 'emp_type']
    search_fields = ['emp_id', 'emp_full_name', 'emp_phone1', 'national_id']
    date_hierarchy = 'emp_date_hiring'
    fieldsets = (
        (_('البيانات الأساسية'), {
            'fields': ('emp_id', 'emp_first_name', 'emp_second_name', 'emp_full_name', 'emp_name_english', 'emp_type')
        }),
        (_('بيانات الاتصال'), {
            'fields': ('emp_phone1', 'emp_phone2', 'emp_address', 'governorate')
        }),
        (_('البيانات الشخصية'), {
            'fields': ('emp_marital_status', 'emp_nationality', 'people_with_special_needs', 'national_id', 'date_birth', 'place_birth', 'emp_image')
        }),
        (_('بيانات العمل'), {
            'fields': ('working_condition', 'department', 'jop_code', 'jop_name', 'emp_date_hiring', 'shift_type')
        }),
        (_('بيانات التأمين'), {
            'fields': ('insurance_status', 'job_insurance', 'number_insurance')
        }),
    )

# نماذج الرواتب
@admin.register(SalaryItem)
class SalaryItemAdmin(admin.ModelAdmin):
    list_display = ['item_code', 'name', 'type', 'default_value', 'is_auto_applied', 'is_active']
    list_filter = ['type', 'is_auto_applied', 'is_active']
    search_fields = ['item_code', 'name']
    ordering = ['item_code']

@admin.register(EmployeeSalaryItem)
class EmployeeSalaryItemAdmin(admin.ModelAdmin):
    list_display = ['employee', 'salary_item', 'amount', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'salary_item__type']
    search_fields = ['employee__emp_full_name', 'salary_item__name']
    autocomplete_fields = ['employee', 'salary_item']
    date_hierarchy = 'start_date'

@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ['period', 'status', 'total_amount', 'created_by', 'approved_by']
    list_filter = ['status']
    search_fields = ['period']
    date_hierarchy = 'period'
    readonly_fields = ['created_by', 'approved_by', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(PayrollEntry)
class PayrollEntryAdmin(admin.ModelAdmin):
    list_display = ['period', 'employee', 'total_amount', 'status']
    list_filter = ['status', 'period']
    search_fields = ['employee__emp_full_name']
    autocomplete_fields = ['employee']
    date_hierarchy = 'created_at'

@admin.register(PayrollItemDetail)
class PayrollItemDetailAdmin(admin.ModelAdmin):
    list_display = ['payroll_entry', 'salary_item', 'amount']
    list_filter = ['salary_item__type']
    search_fields = ['payroll_entry__employee__emp_full_name', 'salary_item__name']
    autocomplete_fields = ['payroll_entry', 'salary_item']

# نماذج الحضور
@admin.register(AttendanceRule)
class AttendanceRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(EmployeeAttendanceRule)
class EmployeeAttendanceRuleAdmin(admin.ModelAdmin):
    list_display = ['employee', 'attendance_rule', 'effective_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['employee__emp_full_name']
    date_hierarchy = 'effective_date'

@admin.register(OfficialHoliday)
class OfficialHolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'description']
    list_filter = ['date']
    search_fields = ['name', 'description']
    date_hierarchy = 'date'

@admin.register(AttendanceMachine)
class AttendanceMachineAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'location', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'location']

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'machine']
    list_filter = ['machine']
    search_fields = ['employee__emp_full_name']

@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status']
    list_filter = ['status', 'date']
    search_fields = ['employee__emp_full_name']
    date_hierarchy = 'date'

# نماذج نقاط الالتقاط
@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ['car']
    search_fields = ['car__car_name']

# نماذج المهام
@admin.register(EmployeeTask)
class EmployeeTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'assigned_by', 'due_date', 'status']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'employee__emp_full_name']
    date_hierarchy = 'due_date'

# نماذج الملاحظات
@admin.register(EmployeeNote)
class EmployeeNoteAdmin(admin.ModelAdmin):
    list_display = ['employee', 'title', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'employee__emp_full_name']
    date_hierarchy = 'created_at'

# نماذج الملفات
@admin.register(EmployeeFile)
class EmployeeFileAdmin(admin.ModelAdmin):
    list_display = ['employee', 'title', 'file_type', 'uploaded_by', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['title', 'employee__emp_full_name']
    date_hierarchy = 'created_at'

# نماذج مهام الموارد البشرية
@admin.register(HrTask)
class HrTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'due_date', 'status']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'assigned_to__username']
    date_hierarchy = 'due_date'

# نماذج الإجازات
@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']

@admin.register(EmployeeLeave)
class EmployeeLeaveAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['leave_type', 'status']
    search_fields = ['employee__emp_full_name', 'reason']
    date_hierarchy = 'start_date'

# نماذج التقييمات
@admin.register(EmployeeEvaluation)
class EmployeeEvaluationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'evaluation_date', 'evaluator', 'overall_rating']
    list_filter = ['evaluation_date']
    search_fields = ['employee__emp_full_name', 'evaluator__username']
    date_hierarchy = 'evaluation_date'
