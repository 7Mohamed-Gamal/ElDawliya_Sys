from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    SetupCompany, SetupDepartment, SetupJob,
    HREmployee, HREmployeeAssignment, SetupLeaveType, HREmpLeaveBalance, HREmpLeaveRequest,
    HREmpAttendance, SetupPayrollItem, HREmpSalaryComponent, HRPayrollRun, HRPayrollSlip,
    HREmpQualification, HREmpTraining, HREmpDocument, SetupAssetType, HREmpAsset,
    HRAppraisalCycle, HREmpAppraisal, HRContract, SetupViolationType, HREmpViolation,
    HRSocialInsurance, HRHealthInsurance, SetupHoliday, HRTermination
)

# Base Admin Class for Tracking Fields
class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date', 'modified_date', 'created_by', 'modified_by')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

# 1. Setup Models
@admin.register(SetupCompany)
class SetupCompanyAdmin(BaseAdmin):
    list_display = ('company_name_ar', 'company_code', 'is_active', 'created_date')
    search_fields = ('company_name_ar', 'company_code')
    list_filter = ('is_active',)

@admin.register(SetupDepartment)
class SetupDepartmentAdmin(BaseAdmin):
    list_display = ('dept_name_ar', 'company', 'parent_dept', 'manager_emp', 'is_active')
    search_fields = ('dept_name_ar', 'dept_code')
    list_filter = ('company', 'is_active')
    raw_id_fields = ('manager_emp',)

@admin.register(SetupJob)
class SetupJobAdmin(BaseAdmin):
    list_display = ('job_name_ar', 'company', 'min_salary', 'max_salary', 'is_active')
    search_fields = ('job_name_ar', 'job_code')
    list_filter = ('company', 'is_active')

@admin.register(SetupLeaveType)
class SetupLeaveTypeAdmin(BaseAdmin):
    list_display = ('leave_name_ar', 'company', 'paid_unpaid', 'max_days_year', 'carry_forward', 'is_active')
    list_filter = ('company', 'paid_unpaid', 'carry_forward', 'is_active')

@admin.register(SetupPayrollItem)
class SetupPayrollItemAdmin(BaseAdmin):
    list_display = ('item_name_ar', 'company', 'item_type', 'is_taxable', 'is_active')
    list_filter = ('company', 'item_type', 'is_taxable', 'is_active')

@admin.register(SetupAssetType)
class SetupAssetTypeAdmin(BaseAdmin):
    list_display = ('asset_name_ar', 'company', 'is_active')
    list_filter = ('company', 'is_active')

@admin.register(SetupViolationType)
class SetupViolationTypeAdmin(BaseAdmin):
    list_display = ('violation_name', 'company', 'penalty_type', 'is_active')
    list_filter = ('company', 'penalty_type', 'is_active')

@admin.register(SetupHoliday)
class SetupHolidayAdmin(BaseAdmin):
    list_display = ('holiday_name_ar', 'holiday_date', 'company', 'is_recurring')
    list_filter = ('company', 'is_recurring')
    date_hierarchy = 'holiday_date'
    readonly_fields = ('created_date', 'created_by') # Override BaseAdmin as SetupHoliday only has created fields

# 2. HR Employee Models
class HREmployeeAssignmentInline(admin.TabularInline):
    model = HREmployeeAssignment
    extra = 0
    fk_name = 'emp'
    fields = ('company', 'dept', 'job', 'direct_manager', 'employment_type', 'hiring_date', 'basic_salary', 'is_current')
    raw_id_fields = ('direct_manager',)

class HREmpQualificationInline(admin.TabularInline):
    model = HREmpQualification
    extra = 0

class HREmpDocumentInline(admin.TabularInline):
    model = HREmpDocument
    extra = 0

class HREmpAssetInline(admin.TabularInline):
    model = HREmpAsset
    extra = 0

@admin.register(HREmployee)
class HREmployeeAdmin(BaseAdmin):
    list_display = ('emp_code', 'full_name_ar', 'email_official', 'phone1', 'is_active')
    search_fields = ('emp_code', 'first_name_ar', 'last_name_ar', 'national_id', 'email_official')
    list_filter = ('is_active', 'gender', 'marital_status', 'has_special_needs')
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('emp_code', 'user', ('first_name_ar', 'second_name_ar', 'third_name_ar', 'last_name_ar'), 
                       ('first_name_en', 'second_name_en', 'third_name_en', 'last_name_en'), 'is_active')
        }),
        (_('بيانات شخصية'), {
            'fields': (('date_birth', 'gender', 'marital_status'), ('nationality', 'national_id', 'personal_id_expiry'), 'military_status', 'has_special_needs', 'notes')
        }),
        (_('التواصل'), {
            'fields': (('phone1', 'phone2'), ('email_personal', 'email_official'), 'emergency_contact', 'emergency_phone')
        }),
        (_('العنوان'), {
            'fields': (('address_country', 'address_governorate', 'address_city'), 'address_street')
        }),
        (_('تتبع النظام'), {
            'fields': BaseAdmin.readonly_fields
        }),
    )
    inlines = [HREmployeeAssignmentInline, HREmpQualificationInline, HREmpDocumentInline, HREmpAssetInline]
    raw_id_fields = ('user',)

# 3. HR Transactional Models
@admin.register(HREmployeeAssignment)
class HREmployeeAssignmentAdmin(BaseAdmin):
    list_display = ('emp', 'job', 'dept', 'company', 'hiring_date', 'basic_salary', 'is_current')
    list_filter = ('company', 'dept', 'job', 'employment_type', 'is_current')
    search_fields = ('emp__first_name_ar', 'emp__last_name_ar', 'job__job_name_ar')
    raw_id_fields = ('emp', 'company', 'dept', 'job', 'direct_manager')

@admin.register(HREmpLeaveRequest)
class HREmpLeaveRequestAdmin(BaseAdmin):
    list_display = ('emp', 'leave_type', 'start_date', 'end_date', 'days_count', 'status')
    list_filter = ('leave_type', 'status')
    search_fields = ('emp__first_name_ar', 'emp__last_name_ar', 'reason')
    raw_id_fields = ('emp', 'leave_type', 'approved_by')

@admin.register(HREmpLeaveBalance)
class HREmpLeaveBalanceAdmin(BaseAdmin):
    list_display = ('emp', 'leave_type', 'year', 'opening_balance', 'consumed_days', 'remaining_balance')
    list_filter = ('leave_type', 'year')
    search_fields = ('emp__first_name_ar', 'emp__last_name_ar')
    raw_id_fields = ('emp', 'leave_type')

@admin.register(HREmpAttendance)
class HREmpAttendanceAdmin(BaseAdmin):
    list_display = ('emp', 'attendance_datetime', 'attendance_type', 'device_id')
    list_filter = ('attendance_type',)
    search_fields = ('emp__first_name_ar', 'emp__last_name_ar', 'device_id')
    date_hierarchy = 'attendance_datetime'
    raw_id_fields = ('emp',)

@admin.register(HRPayrollRun)
class HRPayrollRunAdmin(BaseAdmin):
    list_display = ('company', 'payroll_month', 'payroll_year', 'status', 'total_net_salary')
    list_filter = ('company', 'status', 'payroll_year')

@admin.register(HRPayrollSlip)
class HRPayrollSlipAdmin(BaseAdmin):
    list_display = ('payroll_run', 'emp', 'payroll_item', 'amount')
    list_filter = ('payroll_run__company', 'payroll_item__item_type')
    search_fields = ('emp__first_name_ar', 'emp__last_name_ar', 'payroll_item__item_name_ar')
    raw_id_fields = ('payroll_run', 'emp', 'payroll_item')

@admin.register(HREmpSalaryComponent)
class HREmpSalaryComponentAdmin(BaseAdmin):
    list_display = ('emp', 'payroll_item', 'amount', 'is_fixed', 'start_date')
    list_filter = ('payroll_item__item_type', 'is_fixed')
    search_fields = ('emp__first_name_ar', 'emp__last_name_ar', 'payroll_item__item_name_ar')
    raw_id_fields = ('emp', 'payroll_item')

@admin.register(HRContract)
class HRContractAdmin(BaseAdmin):
    list_display = ('emp', 'contract_no', 'contract_type', 'start_date', 'end_date', 'status')
    list_filter = ('contract_type', 'status')
    search_fields = ('emp__first_name_ar', 'emp__last_name_ar', 'contract_no')
    raw_id_fields = ('emp',)

@admin.register(HREmpViolation)
class HREmpViolationAdmin(BaseAdmin):
    list_display = ('emp', 'violation_type', 'violation_date', 'penalty_executed')
    list_filter = ('violation_type__penalty_type', 'penalty_executed')
    search_fields = ('emp__first_name_ar', 'emp__last_name_ar', 'violation_type__violation_name')
    raw_id_fields = ('emp', 'violation_type')

@admin.register(HRSocialInsurance)
class HRSocialInsuranceAdmin(BaseAdmin):
    list_display = ('emp', 'insurance_no', 'subscription_salary', 'status')
    search_fields = ('emp__first_name_ar', 'emp__last_name_ar', 'insurance_no')
    raw_id_fields = ('emp',)

@admin.register(HRHealthInsurance)
class HRHealthInsuranceAdmin(BaseAdmin):
    list_display = ('emp', 'provider', 'policy_no', 'start_date', 'end_date')
    search_fields = ('emp__first_name_ar', 'emp__last_name_ar', 'policy_no')
    raw_id_fields = ('emp',)

@admin.register(HRTermination)
class HRTerminationAdmin(BaseAdmin):
    list_display = ('emp', 'request_date', 'last_working_date', 'reason_type', 'settlement_paid')
    list_filter = ('reason_type', 'settlement_paid')
    search_fields = ('emp__first_name_ar', 'emp__last_name_ar', 'reason_details')
    raw_id_fields = ('emp',)

@admin.register(HRAppraisalCycle)
class HRAppraisalCycleAdmin(BaseAdmin):
    list_display = ('cycle_name', 'company', 'start_date', 'end_date', 'is_active')
    list_filter = ('company', 'is_active')

@admin.register(HREmpAppraisal)
class HREmpAppraisalAdmin(BaseAdmin):
    list_display = ('emp', 'cycle', 'appraiser', 'appraisal_date', 'overall_score')
    list_filter = ('cycle',)
    search_fields = ('emp__full_name_ar', 'appraiser__full_name_ar')
    raw_id_fields = ('emp', 'cycle', 'appraiser')

# Other Inlines
@admin.register(HREmpQualification)
class HREmpQualificationAdmin(BaseAdmin):
    list_display = ('emp', 'degree', 'major', 'institution', 'graduation_year')
    search_fields = ('emp__full_name_ar', 'institution')
    raw_id_fields = ('emp',)

@admin.register(HREmpTraining)
class HREmpTrainingAdmin(BaseAdmin):
    list_display = ('emp', 'training_name', 'provider', 'start_date', 'end_date')
    search_fields = ('emp__full_name_ar', 'training_name', 'provider')
    raw_id_fields = ('emp',)

@admin.register(HREmpDocument)
class HREmpDocumentAdmin(BaseAdmin):
    list_display = ('emp', 'document_type', 'document_number', 'expiry_date')
    search_fields = ('emp__full_name_ar', 'document_type', 'document_number')
    raw_id_fields = ('emp',)

@admin.register(HREmpAsset)
class HREmpAssetAdmin(BaseAdmin):
    list_display = ('emp', 'asset_type', 'serial_number', 'assigned_date', 'return_date')
    search_fields = ('emp__full_name_ar', 'asset_type__asset_name_ar', 'serial_number')
    raw_id_fields = ('emp', 'asset_type')
