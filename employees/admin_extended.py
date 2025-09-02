"""
Extended Admin configurations for comprehensive employee management
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models_extended import (
    HealthInsuranceProvider, EmployeeHealthInsurance,
    SocialInsuranceJobTitle, EmployeeSocialInsurance,
    SalaryComponent, EmployeeSalaryComponent,
    EmployeeLeaveBalance, Vehicle, PickupPoint, EmployeeTransport,
    EvaluationCriteria, EmployeePerformanceEvaluation, EvaluationScore,
    WorkSchedule, EmployeeWorkSetup
)


@admin.register(HealthInsuranceProvider)
class HealthInsuranceProviderAdmin(admin.ModelAdmin):
    list_display = ['provider_name', 'provider_code', 'contact_person', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['provider_name', 'provider_code', 'contact_person']
    ordering = ['provider_name']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('provider_name', 'provider_code', 'is_active')
        }),
        ('معلومات الاتصال', {
            'fields': ('contact_person', 'phone', 'email', 'address')
        }),
    )


@admin.register(EmployeeHealthInsurance)
class EmployeeHealthInsuranceAdmin(admin.ModelAdmin):
    list_display = ['emp', 'provider', 'insurance_status', 'insurance_type', 'start_date', 'expiry_date', 'is_active']
    list_filter = ['insurance_status', 'insurance_type', 'provider', 'start_date']
    search_fields = ['emp__first_name', 'emp__last_name', 'insurance_number']
    ordering = ['emp__first_name', 'emp__last_name']
    
    fieldsets = (
        ('معلومات الموظف', {
            'fields': ('emp',)
        }),
        ('بيانات التأمين', {
            'fields': ('provider', 'insurance_status', 'insurance_type', 'insurance_number')
        }),
        ('التواريخ', {
            'fields': ('start_date', 'expiry_date')
        }),
        ('المعالين', {
            'fields': ('num_dependents', 'dependent_names')
        }),
        ('التكاليف', {
            'fields': ('monthly_premium', 'employee_contribution', 'company_contribution')
        }),
        ('تفاصيل إضافية', {
            'fields': ('coverage_details', 'notes')
        }),
    )
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'نشط'


@admin.register(SocialInsuranceJobTitle)
class SocialInsuranceJobTitleAdmin(admin.ModelAdmin):
    list_display = ['job_code', 'job_title', 'insurable_wage_amount', 'employee_deduction_percentage', 
                   'company_contribution_percentage', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['job_code', 'job_title']
    ordering = ['job_code']
    
    fieldsets = (
        ('معلومات الوظيفة', {
            'fields': ('job_code', 'job_title', 'is_active')
        }),
        ('بيانات التأمين', {
            'fields': ('insurable_wage_amount', 'employee_deduction_percentage', 'company_contribution_percentage')
        }),
    )


@admin.register(EmployeeSocialInsurance)
class EmployeeSocialInsuranceAdmin(admin.ModelAdmin):
    list_display = ['emp', 'insurance_status', 'job_title', 'social_insurance_number', 
                   'monthly_wage', 'employee_deduction', 'company_contribution']
    list_filter = ['insurance_status', 'subscription_confirmed', 'job_title']
    search_fields = ['emp__first_name', 'emp__last_name', 'social_insurance_number']
    ordering = ['emp__first_name', 'emp__last_name']
    
    fieldsets = (
        ('معلومات الموظف', {
            'fields': ('emp',)
        }),
        ('بيانات التأمين', {
            'fields': ('insurance_status', 'start_date', 'subscription_confirmed', 'job_title', 'social_insurance_number')
        }),
        ('البيانات المالية', {
            'fields': ('monthly_wage', 'employee_deduction', 'company_contribution')
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
    )


@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ['component_name', 'component_code', 'component_type', 'calculation_type', 
                   'default_value', 'is_taxable', 'is_active', 'sort_order']
    list_filter = ['component_type', 'calculation_type', 'is_taxable', 'is_social_insurance_applicable', 'is_active']
    search_fields = ['component_name', 'component_code']
    ordering = ['component_type', 'sort_order', 'component_name']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('component_name', 'component_code', 'component_type', 'is_active')
        }),
        ('إعدادات الحساب', {
            'fields': ('calculation_type', 'default_value')
        }),
        ('الضرائب والتأمينات', {
            'fields': ('is_taxable', 'is_social_insurance_applicable')
        }),
        ('العرض', {
            'fields': ('sort_order', 'description')
        }),
    )


class EmployeeSalaryComponentInline(admin.TabularInline):
    model = EmployeeSalaryComponent
    extra = 1
    fields = ['component', 'amount', 'percentage', 'effective_date', 'end_date', 'is_active']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number', 'vehicle_model', 'vehicle_year', 'capacity', 
                   'supervisor_name', 'driver_name', 'vehicle_status', 'is_available']
    list_filter = ['vehicle_status', 'vehicle_year']
    search_fields = ['vehicle_number', 'vehicle_model', 'supervisor_name', 'driver_name']
    ordering = ['vehicle_number']
    
    fieldsets = (
        ('معلومات المركبة', {
            'fields': ('vehicle_number', 'vehicle_model', 'vehicle_year', 'capacity', 'vehicle_status')
        }),
        ('معلومات المسار', {
            'fields': ('route_info',)
        }),
        ('بيانات المشرف', {
            'fields': ('supervisor_name', 'supervisor_phone')
        }),
        ('بيانات السائق', {
            'fields': ('driver_name', 'driver_phone', 'driver_license')
        }),
        ('التراخيص والتأمين', {
            'fields': ('insurance_expiry', 'license_expiry')
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
    )
    
    def is_available(self, obj):
        return obj.is_available
    is_available.boolean = True
    is_available.short_description = 'متاح'


@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ['point_name', 'point_code', 'address', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['point_name', 'point_code', 'address']
    ordering = ['point_code']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('point_name', 'point_code', 'is_active')
        }),
        ('الموقع', {
            'fields': ('address', 'latitude', 'longitude')
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
    )


@admin.register(EmployeeTransport)
class EmployeeTransportAdmin(admin.ModelAdmin):
    list_display = ['emp', 'vehicle', 'pickup_point', 'pickup_time', 'effective_date', 'is_active']
    list_filter = ['vehicle', 'pickup_point', 'is_active', 'effective_date']
    search_fields = ['emp__first_name', 'emp__last_name']
    ordering = ['emp__first_name', 'emp__last_name']
    
    fieldsets = (
        ('معلومات الموظف', {
            'fields': ('emp',)
        }),
        ('بيانات النقل', {
            'fields': ('vehicle', 'pickup_point', 'pickup_time')
        }),
        ('التواريخ', {
            'fields': ('effective_date', 'end_date', 'is_active')
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
    )


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ['schedule_name', 'schedule_code', 'daily_hours', 'weekly_hours', 
                   'start_time', 'end_time', 'is_flexible', 'is_active']
    list_filter = ['is_flexible', 'overtime_applicable', 'is_active']
    search_fields = ['schedule_name', 'schedule_code']
    ordering = ['schedule_name']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('schedule_name', 'schedule_code', 'is_active')
        }),
        ('ساعات العمل', {
            'fields': ('daily_hours', 'weekly_hours', 'start_time', 'end_time', 'break_duration')
        }),
        ('الإعدادات', {
            'fields': ('is_flexible', 'overtime_applicable')
        }),
        ('الوصف', {
            'fields': ('description',)
        }),
    )


@admin.register(EmployeeWorkSetup)
class EmployeeWorkSetupAdmin(admin.ModelAdmin):
    list_display = ['emp', 'work_schedule', 'effective_date', 'overtime_rate', 'is_active']
    list_filter = ['work_schedule', 'is_active', 'effective_date']
    search_fields = ['emp__first_name', 'emp__last_name']
    ordering = ['emp__first_name', 'emp__last_name']
    
    fieldsets = (
        ('معلومات الموظف', {
            'fields': ('emp',)
        }),
        ('إعدادات العمل', {
            'fields': ('work_schedule', 'overtime_rate', 'late_deduction_rate', 'absence_deduction_rate')
        }),
        ('التواريخ', {
            'fields': ('effective_date', 'end_date', 'is_active')
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
    )


@admin.register(EvaluationCriteria)
class EvaluationCriteriaAdmin(admin.ModelAdmin):
    list_display = ['criteria_name', 'criteria_code', 'max_score', 'weight', 'is_active', 'sort_order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['criteria_name', 'criteria_code']
    ordering = ['sort_order', 'criteria_name']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('criteria_name', 'criteria_code', 'is_active')
        }),
        ('إعدادات التقييم', {
            'fields': ('max_score', 'weight', 'sort_order')
        }),
        ('الوصف', {
            'fields': ('description',)
        }),
    )


class EvaluationScoreInline(admin.TabularInline):
    model = EvaluationScore
    extra = 0
    fields = ['criteria', 'score', 'comments']


@admin.register(EmployeePerformanceEvaluation)
class EmployeePerformanceEvaluationAdmin(admin.ModelAdmin):
    list_display = ['emp', 'evaluator', 'evaluation_date', 'overall_score', 'overall_rating', 'status']
    list_filter = ['status', 'evaluation_date', 'evaluator']
    search_fields = ['emp__first_name', 'emp__last_name', 'evaluator__first_name', 'evaluator__last_name']
    ordering = ['-evaluation_date']
    inlines = [EvaluationScoreInline]
    
    fieldsets = (
        ('معلومات التقييم', {
            'fields': ('emp', 'evaluator', 'evaluation_date', 'status')
        }),
        ('فترة التقييم', {
            'fields': ('evaluation_period_start', 'evaluation_period_end')
        }),
        ('النتائج', {
            'fields': ('overall_score', 'overall_rating')
        }),
        ('التعليقات', {
            'fields': ('strengths', 'areas_for_improvement', 'goals_next_period')
        }),
        ('تعليقات إضافية', {
            'fields': ('employee_comments', 'evaluator_comments')
        }),
    )


@admin.register(EmployeeLeaveBalance)
class EmployeeLeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['emp', 'leave_type', 'year', 'opening_balance', 'accrued_balance', 
                   'used_balance', 'current_balance', 'last_updated']
    list_filter = ['leave_type', 'year', 'last_updated']
    search_fields = ['emp__first_name', 'emp__last_name']
    ordering = ['emp__first_name', 'emp__last_name', 'leave_type']
    readonly_fields = ['current_balance', 'last_updated']
    
    fieldsets = (
        ('معلومات الموظف', {
            'fields': ('emp', 'leave_type', 'year')
        }),
        ('الأرصدة', {
            'fields': ('opening_balance', 'accrued_balance', 'used_balance', 'carried_forward', 'current_balance')
        }),
        ('معلومات التحديث', {
            'fields': ('last_updated',)
        }),
    )
