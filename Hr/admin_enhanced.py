"""
Enhanced Django Admin Configuration for HR Models
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Company, Branch, Department, JobPosition, Employee,
    EmployeeEducation, EmployeeInsurance, EmployeeVehicle,
    WorkShift, AttendanceMachine, AttendanceRecord,
    LeaveType, LeaveRequest, EmployeeLeaveBalance
)


# =============================================================================
# ENHANCED ADMIN CLASSES
# =============================================================================

@admin.register(EmployeeEducation)
class EmployeeEducationAdmin(admin.ModelAdmin):
    """إدارة المؤهلات الدراسية"""
    list_display = ['employee', 'degree_type', 'major', 'institution', 'graduation_year', 'is_verified', 'is_active']
    list_filter = ['degree_type', 'is_verified', 'is_active', 'graduation_year', 'country']
    search_fields = ['employee__full_name', 'employee__employee_number', 'major', 'institution']
    ordering = ['-graduation_year', 'employee__full_name']
    
    fieldsets = (
        ('معلومات الموظف', {
            'fields': ('employee',)
        }),
        ('تفاصيل التعليم', {
            'fields': ('degree_type', 'major', 'institution', 'graduation_year', 'grade', 'country')
        }),
        ('التحقق والملفات', {
            'fields': ('is_verified', 'certificate_file')
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee')


@admin.register(EmployeeInsurance)
class EmployeeInsuranceAdmin(admin.ModelAdmin):
    """إدارة تأمينات الموظفين"""
    list_display = ['employee', 'insurance_type', 'policy_number', 'provider', 'start_date', 'end_date', 'is_active_display']
    list_filter = ['insurance_type', 'is_active', 'provider', 'start_date']
    search_fields = ['employee__full_name', 'employee__employee_number', 'policy_number', 'provider']
    ordering = ['employee__full_name', 'insurance_type']
    
    fieldsets = (
        ('معلومات الموظف', {
            'fields': ('employee',)
        }),
        ('تفاصيل التأمين', {
            'fields': ('insurance_type', 'policy_number', 'provider')
        }),
        ('التواريخ', {
            'fields': ('start_date', 'end_date')
        }),
        ('المعلومات المالية', {
            'fields': ('premium_amount', 'coverage_amount', 'employee_contribution', 'employer_contribution')
        }),
        ('الملفات والحالة', {
            'fields': ('policy_document', 'is_active')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">نشط</span>')
        return format_html('<span style="color: red;">غير نشط</span>')
    is_active_display.short_description = 'الحالة'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee')


@admin.register(EmployeeVehicle)
class EmployeeVehicleAdmin(admin.ModelAdmin):
    """إدارة سيارات الموظفين"""
    list_display = ['employee', 'vehicle_type', 'make', 'model', 'year', 'license_plate', 'assigned_date', 'insurance_status']
    list_filter = ['vehicle_type', 'make', 'year', 'is_active', 'assigned_date']
    search_fields = ['employee__full_name', 'employee__employee_number', 'license_plate', 'make', 'model']
    ordering = ['employee__full_name', '-assigned_date']
    
    fieldsets = (
        ('معلومات الموظف', {
            'fields': ('employee',)
        }),
        ('معلومات السيارة', {
            'fields': ('vehicle_type', 'make', 'model', 'year', 'license_plate', 'color')
        }),
        ('معلومات التخصيص', {
            'fields': ('assigned_date', 'return_date', 'monthly_allowance')
        }),
        ('المعلومات القانونية', {
            'fields': ('insurance_expiry', 'registration_expiry')
        }),
        ('ملاحظات وحالة', {
            'fields': ('notes', 'is_active')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def insurance_status(self, obj):
        from django.utils import timezone
        days_remaining = (obj.insurance_expiry - timezone.now().date()).days
        
        if days_remaining < 0:
            return format_html('<span style="color: red;">منتهي الصلاحية</span>')
        elif days_remaining <= 30:
            return format_html('<span style="color: orange;">ينتهي خلال {} يوم</span>', days_remaining)
        else:
            return format_html('<span style="color: green;">ساري</span>')
    insurance_status.short_description = 'حالة التأمين'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee')


# =============================================================================
# ENHANCED EXISTING ADMIN CLASSES
# =============================================================================

class EmployeeEducationInline(admin.TabularInline):
    """إدراج المؤهلات الدراسية في صفحة الموظف"""
    model = EmployeeEducation
    extra = 0
    fields = ['degree_type', 'major', 'institution', 'graduation_year', 'is_verified']
    readonly_fields = ['created_at']


class EmployeeInsuranceInline(admin.TabularInline):
    """إدراج التأمينات في صفحة الموظف"""
    model = EmployeeInsurance
    extra = 0
    fields = ['insurance_type', 'policy_number', 'provider', 'start_date', 'end_date', 'is_active']
    readonly_fields = ['created_at']


class EmployeeVehicleInline(admin.TabularInline):
    """إدراج السيارات في صفحة الموظف"""
    model = EmployeeVehicle
    extra = 0
    fields = ['vehicle_type', 'make', 'model', 'license_plate', 'assigned_date', 'is_active']
    readonly_fields = ['created_at']


# Update existing Employee admin to include new inlines
try:
    admin.site.unregister(Employee)
except admin.sites.NotRegistered:
    pass

@admin.register(Employee)
class EmployeeEnhancedAdmin(admin.ModelAdmin):
    """إدارة الموظفين المحسنة"""
    list_display = ['employee_number', 'full_name', 'email', 'department', 'job_position', 'hire_date', 'status']
    list_filter = ['status', 'employment_type', 'company', 'department', 'hire_date']
    search_fields = ['employee_number', 'full_name', 'email', 'phone_primary']
    ordering = ['employee_number']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('employee_number', 'first_name', 'middle_name', 'last_name', 'name_english')
        }),
        ('معلومات الاتصال', {
            'fields': ('email', 'phone_primary', 'phone_secondary', 'address')
        }),
        ('المعلومات الشخصية', {
            'fields': ('national_id', 'passport_number', 'date_of_birth', 'gender', 'marital_status', 'nationality')
        }),
        ('معلومات العمل', {
            'fields': ('company', 'branch', 'department', 'job_position', 'direct_manager')
        }),
        ('تفاصيل التوظيف', {
            'fields': ('employment_type', 'hire_date', 'probation_end_date', 'contract_start_date', 'contract_end_date')
        }),
        ('الراتب والحالة', {
            'fields': ('basic_salary', 'status', 'is_active')
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    inlines = [EmployeeEducationInline, EmployeeInsuranceInline, EmployeeVehicleInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'company', 'branch', 'department', 'job_position', 'direct_manager'
        )


# =============================================================================
# ADMIN ACTIONS
# =============================================================================

def mark_as_verified(modeladmin, request, queryset):
    """وضع علامة تم التحقق"""
    queryset.update(is_verified=True)
mark_as_verified.short_description = "وضع علامة تم التحقق على العناصر المحددة"

def mark_as_active(modeladmin, request, queryset):
    """تفعيل العناصر المحددة"""
    queryset.update(is_active=True)
mark_as_active.short_description = "تفعيل العناصر المحددة"

def mark_as_inactive(modeladmin, request, queryset):
    """إلغاء تفعيل العناصر المحددة"""
    queryset.update(is_active=False)
mark_as_inactive.short_description = "إلغاء تفعيل العناصر المحددة"

# Add actions to admin classes
EmployeeEducationAdmin.actions = [mark_as_verified, mark_as_active, mark_as_inactive]
EmployeeInsuranceAdmin.actions = [mark_as_active, mark_as_inactive]
EmployeeVehicleAdmin.actions = [mark_as_active, mark_as_inactive]