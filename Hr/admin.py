from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# تخصيص موقع الإدارة
admin.site.site_header = _('نظام الدولية للموارد البشرية')
admin.site.site_title = _('إدارة الموارد البشرية')
admin.site.index_title = _('لوحة تحكم الموارد البشرية')

# استيراد النماذج المتاحة فقط
from Hr.models import (
    # Core Organizational Models
    Company, Branch, Department, JobPosition,

    # Employee Management Models
    Employee, EmployeeDocument, EmployeeEmergencyContact, EmployeeTraining,

    # Attendance & Time Management Models
    WorkShift, AttendanceMachine, AttendanceRecord, AttendanceSummary,
    EmployeeShiftAssignment,

    # Leave Management Models
    LeaveType, LeavePolicy, LeaveRequest, LeaveBalance,

    # Payroll Management Models
    SalaryComponent,

    # TODO: Import legacy models when they are created
    # Department, Job, JobInsurance, Car, Employee,
    # SalaryItem, EmployeeSalaryItem, PayrollPeriod, PayrollEntry, PayrollItemDetail,
    # AttendanceRule, EmployeeAttendanceRule, OfficialHoliday, AttendanceMachine,
    # AttendanceRecord, AttendanceSummary, PickupPoint, EmployeeTask, EmployeeNote,
    # EmployeeFile, HrTask, LeaveType, EmployeeLeave, EmployeeEvaluation
)

# ==================== CORE ORGANIZATIONAL MODELS ====================

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'tax_id', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'tax_id', 'legal_name']
    ordering = ['name']

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'company', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['company', 'name']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'branch', 'manager', 'is_active']
    list_filter = ['branch', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['branch', 'name']

@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'department', 'level', 'is_active']
    list_filter = ['department', 'level', 'is_active']
    search_fields = ['title', 'code']
    ordering = ['department', 'title']

# ==================== EMPLOYEE MANAGEMENT MODELS ====================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_number', 'full_name', 'department', 'job_position', 'status', 'hire_date']
    list_filter = ['status', 'department', 'job_position', 'employment_type']
    search_fields = ['employee_number', 'full_name', 'first_name', 'last_name', 'national_id', 'email']
    date_hierarchy = 'hire_date'
    # TODO: Re-enable autocomplete_fields when all models are properly registered
    # autocomplete_fields = ['company', 'branch', 'department', 'job_position', 'manager']
    fieldsets = (
        (_('البيانات الأساسية'), {
            'fields': ('employee_number', 'first_name', 'middle_name', 'last_name', 'full_name', 'full_name_english')
        }),
        (_('المعلومات التنظيمية'), {
            'fields': ('company', 'branch', 'department', 'job_position', 'manager')
        }),
        (_('بيانات الاتصال'), {
            'fields': ('email', 'personal_email', 'phone', 'mobile', 'address')
        }),
        (_('البيانات الشخصية'), {
            'fields': ('national_id', 'passport_number', 'date_of_birth', 'place_of_birth', 'gender', 'marital_status', 'nationality')
        }),
        (_('بيانات التوظيف'), {
            'fields': ('hire_date', 'employment_type', 'employment_status', 'probation_end_date', 'contract_end_date')
        }),
        (_('معلومات الراتب'), {
            'fields': ('basic_salary', 'currency')
        }),
    )

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'document_type', 'title', 'status', 'expiry_date']
    list_filter = ['document_type', 'status']
    search_fields = ['employee__full_name', 'title']
    # autocomplete_fields = ['employee']

@admin.register(EmployeeEmergencyContact)
class EmployeeEmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['employee', 'full_name', 'relationship', 'primary_phone', 'is_primary']
    list_filter = ['relationship', 'is_primary']
    search_fields = ['employee__full_name', 'full_name', 'primary_phone']
    # autocomplete_fields = ['employee']

@admin.register(EmployeeTraining)
class EmployeeTrainingAdmin(admin.ModelAdmin):
    list_display = ['employee', 'title', 'training_type', 'start_date', 'end_date', 'status']
    list_filter = ['training_type', 'status']
    search_fields = ['employee__full_name', 'title']
    # autocomplete_fields = ['employee']
    date_hierarchy = 'start_date'

# ==================== PAYROLL MANAGEMENT MODELS ====================

@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'component_type', 'category', 'calculation_method', 'is_active']
    list_filter = ['component_type', 'category', 'calculation_method', 'is_active', 'frequency']
    search_fields = ['name', 'code', 'description']
    ordering = ['display_order', 'name']
    fieldsets = (
        (_('المعلومات الأساسية'), {
            'fields': ('name', 'code', 'description', 'component_type', 'category')
        }),
        (_('طريقة الحساب'), {
            'fields': ('calculation_method', 'fixed_amount', 'percentage_value', 'percentage_basis', 'basis_component', 'calculation_formula')
        }),
        (_('الحدود والقيود'), {
            'fields': ('minimum_amount', 'maximum_amount')
        }),
        (_('الإعدادات'), {
            'fields': ('is_taxable', 'is_insurance_applicable', 'affects_overtime', 'frequency')
        }),
        (_('العرض والتقارير'), {
            'fields': ('display_order', 'show_in_payslip', 'show_in_summary')
        }),
        (_('الحالة'), {
            'fields': ('is_active', 'is_system_component')
        }),
    )

# TODO: Add admin registrations for other payroll models when they are created
# @admin.register(EmployeeSalaryStructure)
# @admin.register(PayrollPeriod)
# @admin.register(PayrollEntry)
# @admin.register(TaxConfiguration)

# ==================== ATTENDANCE & TIME MANAGEMENT MODELS ====================

@admin.register(WorkShift)
class WorkShiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'break_duration_minutes', 'is_active']
    list_filter = ['is_active', 'shift_type']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(AttendanceMachine)
class AttendanceMachineAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_id', 'location_description', 'ip_address', 'is_active']
    list_filter = ['is_active', 'status']
    search_fields = ['name', 'device_id', 'location_description']
    ordering = ['name']

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'machine', 'record_datetime', 'record_type']
    list_filter = ['record_type', 'machine', 'record_datetime']
    search_fields = ['employee__full_name', 'employee__employee_number']
    date_hierarchy = 'record_datetime'
    # autocomplete_fields = ['employee', 'machine']

@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'first_in_time', 'last_out_time', 'total_work_hours', 'status']
    list_filter = ['status', 'date']
    search_fields = ['employee__full_name', 'employee__employee_number']
    date_hierarchy = 'date'
    # autocomplete_fields = ['employee', 'work_shift']

@admin.register(EmployeeShiftAssignment)
class EmployeeShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'work_shift', 'start_date', 'end_date', 'status']
    list_filter = ['work_shift', 'status']
    search_fields = ['employee__full_name', 'employee__employee_number']
    date_hierarchy = 'start_date'
    # autocomplete_fields = ['employee', 'work_shift']

# ==================== LEAVE MANAGEMENT MODELS ====================

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'max_days_per_year', 'is_paid', 'is_active']
    list_filter = ['is_paid', 'is_active', 'requires_approval']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']

@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'employment_types', 'calendar_year_type', 'is_active']
    list_filter = ['employment_types', 'is_active']
    search_fields = ['name', 'description']
    # autocomplete_fields = ['company', 'branches', 'departments']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'duration_days', 'status']
    list_filter = ['leave_type', 'status', 'start_date']
    search_fields = ['employee__full_name', 'employee__employee_number', 'reason']
    date_hierarchy = 'start_date'
    # autocomplete_fields = ['employee', 'leave_type', 'approved_by']
    readonly_fields = ['duration_days', 'created_at', 'updated_at']

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'balance_year', 'accrued_balance', 'used_balance', 'calculate_available_balance']
    list_filter = ['leave_type', 'balance_year']
    search_fields = ['employee__full_name', 'employee__employee_number']
    # autocomplete_fields = ['employee', 'leave_type']
    readonly_fields = ['calculate_available_balance']

# TODO: Add admin registrations for other models when they are created
# Legacy models, performance models, document models, notification models, etc.
