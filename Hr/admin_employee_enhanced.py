"""
إعدادات Django Admin للنماذج المحسنة للموظفين
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models.employee import (
    EmployeeEnhanced,
    EmployeeEducationEnhanced,
    EmployeeInsuranceEnhanced,
    EmployeeVehicleEnhanced
)


class EmployeeEducationEnhancedInline(admin.TabularInline):
    """إدراج المؤهلات الدراسية في صفحة الموظف"""
    model = EmployeeEducationEnhanced
    extra = 0
    fields = [
        'degree_type', 'major', 'institution', 'graduation_year', 
        'grade', 'country', 'is_verified'
    ]
    readonly_fields = ['created_at', 'updated_at']


class EmployeeInsuranceEnhancedInline(admin.TabularInline):
    """إدراج التأمينات في صفحة الموظف"""
    model = EmployeeInsuranceEnhanced
    extra = 0
    fields = [
        'insurance_type', 'policy_number', 'provider', 
        'start_date', 'end_date', 'status'
    ]
    readonly_fields = ['created_at', 'updated_at']


class EmployeeVehicleEnhancedInline(admin.TabularInline):
    """إدراج السيارات في صفحة الموظف"""
    model = EmployeeVehicleEnhanced
    extra = 0
    fields = [
        'vehicle_type', 'make', 'model', 'license_plate',
        'assigned_date', 'status'
    ]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmployeeEnhanced)
class EmployeeEnhancedAdmin(admin.ModelAdmin):
    """إدارة الموظفين المحسنة"""
    
    list_display = [
        'employee_id', 'full_name', 'department', 'position', 
        'employment_type', 'status', 'join_date', 'age_display'
    ]
    
    list_filter = [
        'status', 'employment_type', 'company', 'department', 
        'gender', 'marital_status', 'join_date'
    ]
    
    search_fields = [
        'employee_id', 'first_name', 'middle_name', 'last_name',
        'first_name_en', 'middle_name_en', 'last_name_en',
        'work_email'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'age', 'years_of_service',
        'months_of_service', 'full_name', 'full_name_en'
    ]
    
    fieldsets = (
        (_('المعلومات الأساسية'), {
            'fields': (
                'employee_id', 'employee_number', 'status',
                ('first_name', 'middle_name', 'last_name'),
                ('first_name_en', 'middle_name_en', 'last_name_en'),
                'profile_picture'
            )
        }),
        (_('المعلومات الشخصية'), {
            'fields': (
                ('gender', 'date_of_birth', 'place_of_birth'),
                ('marital_status', 'number_of_children'),
                ('nationality', 'religion', 'blood_type'),
                'mother_name',
                ('height', 'weight'),
                'languages_spoken'
            )
        }),
        (_('معلومات الاتصال'), {
            'fields': (
                ('work_email', 'private_email'),
                ('mobile_phone', 'home_phone'),
                'address',
                ('city', 'state_province'),
                ('country', 'postal_code')
            )
        }),
        (_('معلومات التوظيف'), {
            'fields': (
                ('company', 'branch'),
                ('department', 'position'),
                'direct_manager',
                ('join_date', 'employment_type'),
                ('probation_end_date', 'contract_start_date', 'contract_end_date'),
                ('base_salary', 'salary_currency'),
                'work_schedule'
            )
        }),
        (_('المعلومات المالية'), {
            'fields': (
                'bank_name',
                ('bank_account_number', 'iban')
            ),
            'classes': ('collapse',)
        }),
        (_('الوثائق الحكومية'), {
            'fields': (
                'national_id',
                ('passport_number', 'passport_issue_date', 'passport_expiry_date'),
                'passport_issue_place',
                ('visa_number', 'visa_expiry_date')
            ),
            'classes': ('collapse',)
        }),
        (_('معلومات التأمين'), {
            'fields': (
                ('social_insurance_number', 'health_insurance_number'),
                'insurance_start_date'
            ),
            'classes': ('collapse',)
        }),
        (_('جهة الاتصال للطوارئ'), {
            'fields': (
                'emergency_contact_name',
                'emergency_contact_relationship',
                'emergency_contact_phone',
                'emergency_contact_address'
            ),
            'classes': ('collapse',)
        }),
        (_('الخدمة العسكرية'), {
            'fields': (
                'military_service_status',
                'military_service_end_date'
            ),
            'classes': ('collapse',)
        }),
        (_('التقييم والأداء'), {
            'fields': (
                'performance_rating',
                ('last_evaluation_date', 'next_evaluation_date')
            ),
            'classes': ('collapse',)
        }),
        (_('إنهاء الخدمة'), {
            'fields': (
                'termination_date',
                'termination_reason'
            ),
            'classes': ('collapse',)
        }),
        (_('ملاحظات إضافية'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('معلومات النظام'), {
            'fields': (
                'id', 'created_at', 'updated_at',
                'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [
        EmployeeEducationEnhancedInline,
        EmployeeInsuranceEnhancedInline,
        EmployeeVehicleEnhancedInline
    ]
    
    actions = ['activate_employees', 'deactivate_employees', 'export_to_excel']
    
    def age_display(self, obj):
        """عرض العمر"""
        return f"{obj.age} سنة"
    age_display.short_description = _('العمر')
    
    def activate_employees(self, request, queryset):
        """تفعيل الموظفين المحددين"""
        updated = queryset.update(status='active')
        self.message_user(request, f'تم تفعيل {updated} موظف')
    activate_employees.short_description = _('تفعيل الموظفين المحددين')
    
    def deactivate_employees(self, request, queryset):
        """إلغاء تفعيل الموظفين المحددين"""
        updated = queryset.update(status='suspended')
        self.message_user(request, f'تم إيقاف {updated} موظف')
    deactivate_employees.short_description = _('إيقاف الموظفين المحددين')
    
    def export_to_excel(self, request, queryset):
        """تصدير إلى Excel"""
        # يمكن تنفيذ تصدير Excel هنا
        self.message_user(request, 'سيتم تنفيذ التصدير قريباً')
    export_to_excel.short_description = _('تصدير إلى Excel')


@admin.register(EmployeeEducationEnhanced)
class EmployeeEducationEnhancedAdmin(admin.ModelAdmin):
    """إدارة المؤهلات الدراسية المحسنة"""
    
    list_display = [
        'employee', 'degree_type', 'major', 'institution',
        'graduation_year', 'grade', 'is_verified'
    ]
    
    list_filter = [
        'degree_type', 'graduation_year', 'country', 
        'is_verified', 'is_relevant_to_job'
    ]
    
    search_fields = [
        'employee__first_name', 'employee__last_name',
        'major', 'institution', 'thesis_title'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'years_since_graduation',
        'is_recent_graduate', 'study_duration_calculated'
    ]
    
    fieldsets = (
        (_('معلومات الموظف'), {
            'fields': ('employee',)
        }),
        (_('تفاصيل الشهادة'), {
            'fields': (
                ('degree_type', 'major', 'minor'),
                ('institution', 'institution_english'),
                ('country', 'city')
            )
        }),
        (_('المعلومات الأكاديمية'), {
            'fields': (
                ('start_year', 'graduation_year', 'study_duration_years'),
                ('study_mode', 'grade_system', 'grade'),
                ('honors', 'class_rank', 'class_size'),
                'awards'
            )
        }),
        (_('الرسالة/المشروع'), {
            'fields': (
                'thesis_title', 'thesis_title_en', 'supervisor_name'
            ),
            'classes': ('collapse',)
        }),
        (_('التحقق'), {
            'fields': (
                'is_verified', 'verification_date', 
                'verified_by', 'verification_notes'
            )
        }),
        (_('الملفات'), {
            'fields': ('certificate_file', 'transcript_file')
        }),
        (_('الصلة بالوظيفة'), {
            'fields': ('is_relevant_to_job', 'relevance_notes'),
            'classes': ('collapse',)
        }),
        (_('معلومات النظام'), {
            'fields': (
                'id', 'is_active', 'created_at', 'updated_at', 'created_by'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['verify_education', 'mark_as_relevant']
    
    def verify_education(self, request, queryset):
        """التحقق من المؤهلات المحددة"""
        updated = queryset.update(is_verified=True, verified_by=request.user)
        self.message_user(request, f'تم التحقق من {updated} مؤهل')
    verify_education.short_description = _('التحقق من المؤهلات المحددة')
    
    def mark_as_relevant(self, request, queryset):
        """تحديد كمرتبط بالوظيفة"""
        updated = queryset.update(is_relevant_to_job=True)
        self.message_user(request, f'تم تحديد {updated} مؤهل كمرتبط بالوظيفة')
    mark_as_relevant.short_description = _('تحديد كمرتبط بالوظيفة')


@admin.register(EmployeeInsuranceEnhanced)
class EmployeeInsuranceEnhancedAdmin(admin.ModelAdmin):
    """إدارة تأمينات الموظفين المحسنة"""
    
    list_display = [
        'employee', 'insurance_type', 'policy_number', 'provider',
        'start_date', 'end_date', 'status', 'expiry_warning'
    ]
    
    list_filter = [
        'insurance_type', 'status', 'provider', 'coverage_type',
        'start_date', 'end_date'
    ]
    
    search_fields = [
        'employee__first_name', 'employee__last_name',
        'policy_number', 'provider'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'days_until_expiry',
        'is_active_insurance', 'monthly_premium', 'annual_premium',
        'total_family_members_covered'
    ]
    
    fieldsets = (
        (_('معلومات الموظف'), {
            'fields': ('employee',)
        }),
        (_('تفاصيل التأمين'), {
            'fields': (
                ('insurance_type', 'coverage_type'),
                ('policy_number', 'provider'),
                ('provider_contact', 'provider_phone', 'provider_email'),
                'coverage_description'
            )
        }),
        (_('التواريخ'), {
            'fields': (
                ('start_date', 'end_date'),
                ('renewal_date', 'last_renewal_date')
            )
        }),
        (_('المعلومات المالية'), {
            'fields': (
                ('premium_amount', 'coverage_amount', 'currency'),
                ('employee_contribution', 'employer_contribution'),
                ('deductible', 'payment_frequency')
            )
        }),
        (_('التغطية العائلية'), {
            'fields': (
                'spouse_covered', 'children_covered', 'parents_covered',
                'beneficiaries'
            ),
            'classes': ('collapse',)
        }),
        (_('المطالبات'), {
            'fields': (
                'total_claims_amount', 'claims_count', 'last_claim_date'
            ),
            'classes': ('collapse',)
        }),
        (_('الوثائق'), {
            'fields': ('policy_document', 'terms_document')
        }),
        (_('معلومات إضافية'), {
            'fields': ('notes', 'special_conditions'),
            'classes': ('collapse',)
        }),
        (_('الاعتماد'), {
            'fields': ('approved_by', 'approval_date'),
            'classes': ('collapse',)
        }),
        (_('معلومات النظام'), {
            'fields': (
                'id', 'status', 'created_at', 'updated_at', 'created_by'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_insurance', 'renew_insurance', 'check_expiry']
    
    def expiry_warning(self, obj):
        """تحذير انتهاء الصلاحية"""
        if obj.is_expiring_soon():
            return format_html(
                '<span style="color: red;">ينتهي خلال {} يوم</span>',
                obj.days_until_expiry
            )
        return _('طبيعي')
    expiry_warning.short_description = _('تحذير الانتهاء')
    
    def activate_insurance(self, request, queryset):
        """تفعيل التأمينات المحددة"""
        updated = queryset.update(status='active')
        self.message_user(request, f'تم تفعيل {updated} تأمين')
    activate_insurance.short_description = _('تفعيل التأمينات المحددة')


@admin.register(EmployeeVehicleEnhanced)
class EmployeeVehicleEnhancedAdmin(admin.ModelAdmin):
    """إدارة سيارات الموظفين المحسنة"""
    
    list_display = [
        'employee', 'make', 'model', 'license_plate',
        'vehicle_type', 'assigned_date', 'status', 'insurance_warning'
    ]
    
    list_filter = [
        'vehicle_type', 'status', 'make', 'fuel_type',
        'assigned_date', 'condition'
    ]
    
    search_fields = [
        'employee__first_name', 'employee__last_name',
        'license_plate', 'make', 'model', 'vin_number'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'vehicle_age_years',
        'assignment_duration_days', 'estimated_current_value',
        'monthly_cost', 'fuel_efficiency_rating'
    ]
    
    fieldsets = (
        (_('معلومات الموظف'), {
            'fields': ('employee',)
        }),
        (_('معلومات السيارة'), {
            'fields': (
                ('vehicle_type', 'make', 'model', 'year'),
                ('license_plate', 'vin_number'),
                ('color', 'fuel_type', 'engine_size'),
                ('transmission', 'doors_count', 'seats_count'),
                'condition'
            )
        }),
        (_('التخصيص'), {
            'fields': (
                ('assigned_date', 'return_date'),
                'assignment_reason'
            )
        }),
        (_('المعلومات المالية'), {
            'fields': (
                ('monthly_allowance', 'purchase_price', 'current_value'),
                'depreciation_rate'
            )
        }),
        (_('المعلومات القانونية'), {
            'fields': (
                ('insurance_company', 'insurance_policy_number'),
                ('insurance_expiry', 'insurance_amount'),
                ('registration_expiry', 'license_expiry')
            )
        }),
        (_('الصيانة'), {
            'fields': (
                ('last_maintenance_date', 'next_maintenance_date'),
                ('maintenance_interval_km', 'mileage'),
                ('last_mileage_update', 'fuel_consumption_per_100km')
            )
        }),
        (_('GPS والتتبع'), {
            'fields': ('has_gps', 'gps_device_id'),
            'classes': ('collapse',)
        }),
        (_('المميزات والملاحظات'), {
            'fields': ('features', 'notes'),
            'classes': ('collapse',)
        }),
        (_('الوثائق'), {
            'fields': (
                'registration_document', 'insurance_document', 'vehicle_photos'
            )
        }),
        (_('الاعتماد'), {
            'fields': ('approved_by', 'approval_date'),
            'classes': ('collapse',)
        }),
        (_('معلومات النظام'), {
            'fields': (
                'id', 'status', 'is_active', 'created_at', 'updated_at', 'created_by'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['perform_maintenance', 'return_vehicles', 'check_documents']
    
    def insurance_warning(self, obj):
        """تحذير انتهاء التأمين"""
        if obj.is_insurance_expiring_soon():
            return format_html(
                '<span style="color: red;">التأمين ينتهي خلال {} يوم</span>',
                obj.insurance_days_remaining
            )
        elif obj.is_registration_expiring_soon():
            return format_html(
                '<span style="color: orange;">الاستمارة تنتهي خلال {} يوم</span>',
                obj.registration_days_remaining
            )
        return _('طبيعي')
    insurance_warning.short_description = _('تحذير الوثائق')
    
    def perform_maintenance(self, request, queryset):
        """تسجيل صيانة للسيارات المحددة"""
        updated = queryset.update(status='maintenance')
        self.message_user(request, f'تم تحديد {updated} سيارة للصيانة')
    perform_maintenance.short_description = _('تسجيل صيانة')
    
    def return_vehicles(self, request, queryset):
        """إرجاع السيارات المحددة"""
        from django.utils import timezone
        updated = queryset.update(return_date=timezone.now().date(), status='available')
        self.message_user(request, f'تم إرجاع {updated} سيارة')
    return_vehicles.short_description = _('إرجاع السيارات')
    
    def check_documents(self, request, queryset):
        """فحص وثائق السيارات"""
        expiring_count = 0
        for vehicle in queryset:
            if vehicle.get_upcoming_expirations():
                expiring_count += 1
        
        self.message_user(
            request, 
            f'تم فحص {queryset.count()} سيارة، {expiring_count} تحتاج تجديد وثائق'
        )
    check_documents.short_description = _('فحص الوثائق')