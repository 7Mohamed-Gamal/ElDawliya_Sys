"""
Django Admin configuration for Enhanced Employee Extended Models
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.contrib.admin import SimpleListFilter
from datetime import date, timedelta

from .models.employee import (
    EmployeeFileEnhanced, EmployeeFileCategory, EmployeeFileAccessLog,
    EmployeeTrainingEnhanced, TrainingCategory, TrainingProvider,
    EmployeeEmergencyContactEnhanced
)


# Custom Filters
class FileStatusFilter(SimpleListFilter):
    title = _('حالة الملف')
    parameter_name = 'file_status'

    def lookups(self, request, model_admin):
        return (
            ('pending', _('في انتظار المراجعة')),
            ('approved', _('معتمد')),
            ('expired', _('منتهي الصلاحية')),
            ('confidential', _('سري')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'pending':
            return queryset.filter(status='pending_review')
        elif self.value() == 'approved':
            return queryset.filter(status='approved')
        elif self.value() == 'expired':
            return queryset.filter(expiry_date__lt=date.today())
        elif self.value() == 'confidential':
            return queryset.filter(is_confidential=True)


class TrainingStatusFilter(SimpleListFilter):
    title = _('حالة التدريب')
    parameter_name = 'training_status'

    def lookups(self, request, model_admin):
        return (
            ('upcoming', _('قادم')),
            ('current', _('جاري')),
            ('completed', _('مكتمل')),
            ('overdue', _('متأخر')),
        )

    def queryset(self, request, queryset):
        today = date.today()
        if self.value() == 'upcoming':
            return queryset.filter(start_date__gt=today, status__in=['approved', 'registered'])
        elif self.value() == 'current':
            return queryset.filter(start_date__lte=today, end_date__gte=today, status='in_progress')
        elif self.value() == 'completed':
            return queryset.filter(status='completed')
        elif self.value() == 'overdue':
            return queryset.filter(end_date__lt=today, status__in=['in_progress', 'registered'])


# File Category Admin
@admin.register(EmployeeFileCategory)
class EmployeeFileCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'icon_display', 'color_display', 'is_active', 'sort_order', 'files_count']
    list_filter = ['is_active']
    search_fields = ['name', 'name_en', 'description']
    ordering = ['sort_order', 'name']
    list_editable = ['is_active', 'sort_order']
    
    def icon_display(self, obj):
        return format_html('<span style="font-size: 20px;">{}</span>', obj.icon)
    icon_display.short_description = _('الأيقونة')
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = _('اللون')
    
    def files_count(self, obj):
        count = obj.files.count()
        if count > 0:
            url = reverse('admin:Hr_employeefileenhanced_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} ملف</a>', url, count)
        return '0 ملف'
    files_count.short_description = _('عدد الملفات')


# File Enhanced Admin
@admin.register(EmployeeFileEnhanced)
class EmployeeFileEnhancedAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'employee', 'category', 'file_type_icon', 'file_size_display', 
        'status_display', 'access_level_display', 'expiry_status', 'created_at'
    ]
    list_filter = [
        FileStatusFilter, 'category', 'access_level', 'is_confidential', 
        'status', 'created_at', 'expiry_date'
    ]
    search_fields = ['title', 'description', 'employee__full_name', 'keywords', 'tags']
    readonly_fields = [
        'file_hash', 'file_size', 'mime_type', 'original_filename', 
        'download_count', 'last_accessed', 'created_at', 'updated_at'
    ]
    raw_id_fields = ['employee', 'parent_file', 'uploaded_by', 'approved_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('employee', 'title', 'description', 'category', 'tags')
        }),
        (_('الملف'), {
            'fields': ('file', 'original_filename', 'file_size', 'mime_type', 'file_hash')
        }),
        (_('التحكم في الوصول'), {
            'fields': ('access_level', 'is_confidential', 'is_encrypted', 'encryption_key_id')
        }),
        (_('الحالة والإصدار'), {
            'fields': ('status', 'version', 'parent_file')
        }),
        (_('انتهاء الصلاحية'), {
            'fields': ('expiry_date', 'renewal_required', 'reminder_days')
        }),
        (_('الاعتماد'), {
            'fields': ('approved_by', 'approved_at', 'rejection_reason')
        }),
        (_('معلومات إضافية'), {
            'fields': ('keywords', 'notes', 'download_count', 'last_accessed')
        }),
        (_('معلومات النظام'), {
            'fields': ('uploaded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_files', 'archive_files', 'mark_confidential']
    
    def file_type_icon(self, obj):
        return format_html('<span style="font-size: 18px;">{}</span>', obj.get_file_type_icon())
    file_type_icon.short_description = _('نوع الملف')
    
    def file_size_display(self, obj):
        if obj.file_size_mb:
            return f"{obj.file_size_mb} MB"
        return "-"
    file_size_display.short_description = _('الحجم')
    
    def status_display(self, obj):
        return format_html('<span>{}</span>', obj.get_status_display_with_icon())
    status_display.short_description = _('الحالة')
    
    def access_level_display(self, obj):
        return format_html('<span>{}</span>', obj.get_access_level_display_with_icon())
    access_level_display.short_description = _('مستوى الوصول')
    
    def expiry_status(self, obj):
        if not obj.expiry_date:
            return format_html('<span style="color: green;">✓ لا ينتهي</span>')
        
        status = obj.get_expiry_status()
        color_map = {
            'expired': 'red',
            'critical': 'red',
            'warning': 'orange',
            'valid': 'green'
        }
        color = color_map.get(status['status'], 'black')
        return format_html('<span style="color: {};">{}</span>', color, status['message'])
    expiry_status.short_description = _('حالة الصلاحية')
    
    def approve_files(self, request, queryset):
        updated = queryset.filter(status='pending_review').update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'تم اعتماد {updated} ملف.')
    approve_files.short_description = _('اعتماد الملفات المحددة')
    
    def archive_files(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'تم أرشفة {updated} ملف.')
    archive_files.short_description = _('أرشفة الملفات المحددة')
    
    def mark_confidential(self, request, queryset):
        updated = queryset.update(is_confidential=True, access_level='confidential')
        self.message_user(request, f'تم تمييز {updated} ملف كسري.')
    mark_confidential.short_description = _('تمييز كملفات سرية')


# File Access Log Admin
@admin.register(EmployeeFileAccessLog)
class EmployeeFileAccessLogAdmin(admin.ModelAdmin):
    list_display = ['file', 'user', 'action', 'ip_address', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['file__title', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['file', 'user', 'action', 'ip_address', 'user_agent', 'timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# Training Category Admin
@admin.register(TrainingCategory)
class TrainingCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'icon_display', 'color_display', 'is_mandatory', 'is_active', 'trainings_count']
    list_filter = ['is_mandatory', 'is_active']
    search_fields = ['name', 'name_en', 'description']
    ordering = ['sort_order', 'name']
    list_editable = ['is_mandatory', 'is_active']
    
    def icon_display(self, obj):
        return format_html('<span style="font-size: 20px;">{}</span>', obj.icon)
    icon_display.short_description = _('الأيقونة')
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = _('اللون')
    
    def trainings_count(self, obj):
        count = obj.trainings.count()
        if count > 0:
            url = reverse('admin:Hr_employeetrainingenhanced_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} تدريب</a>', url, count)
        return '0 تدريب'
    trainings_count.short_description = _('عدد التدريبات')


# Training Provider Admin
@admin.register(TrainingProvider)
class TrainingProviderAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'provider_type', 'rating_display', 'is_preferred', 
        'is_active', 'trainings_count', 'created_at'
    ]
    list_filter = ['provider_type', 'is_preferred', 'is_active', 'rating']
    search_fields = ['name', 'name_en', 'description', 'contact_person']
    ordering = ['-is_preferred', 'name']
    list_editable = ['is_preferred', 'is_active']
    
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('name', 'name_en', 'provider_type', 'description')
        }),
        (_('معلومات الاتصال'), {
            'fields': ('contact_person', 'phone', 'email', 'website', 'address')
        }),
        (_('الاعتماد والتقييم'), {
            'fields': ('accreditation_body', 'accreditation_number', 'rating')
        }),
        (_('الحالة'), {
            'fields': ('is_preferred', 'is_active', 'notes')
        }),
    )
    
    def rating_display(self, obj):
        if obj.rating:
            stars = '⭐' * int(obj.rating)
            return format_html('<span title="{}/5">{}</span>', obj.rating, stars)
        return '-'
    rating_display.short_description = _('التقييم')
    
    def trainings_count(self, obj):
        count = obj.trainings.count()
        if count > 0:
            url = reverse('admin:Hr_employeetrainingenhanced_changelist') + f'?provider__id__exact={obj.id}'
            return format_html('<a href="{}">{} تدريب</a>', url, count)
        return '0 تدريب'
    trainings_count.short_description = _('عدد التدريبات')


# Training Enhanced Admin
@admin.register(EmployeeTrainingEnhanced)
class EmployeeTrainingEnhancedAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'employee', 'category', 'provider', 'training_type',
        'status_display', 'priority_display', 'start_date', 'progress_bar', 'cost'
    ]
    list_filter = [
        TrainingStatusFilter, 'category', 'provider', 'training_type', 
        'status', 'priority', 'is_mandatory', 'start_date'
    ]
    search_fields = [
        'title', 'title_en', 'description', 'employee__full_name',
        'provider__name', 'category__name'
    ]
    raw_id_fields = ['employee', 'category', 'provider', 'requested_by', 'approved_by', 'created_by']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
    
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('employee', 'title', 'title_en', 'description', 'category', 'provider')
        }),
        (_('تفاصيل التدريب'), {
            'fields': ('training_type', 'delivery_method', 'start_date', 'end_date', 'duration_hours')
        }),
        (_('المكان والموقع'), {
            'fields': ('location', 'city', 'country')
        }),
        (_('التكلفة والميزانية'), {
            'fields': ('cost', 'currency', 'budget_code')
        }),
        (_('الحالة والتقدم'), {
            'fields': ('status', 'progress_percentage', 'priority', 'is_mandatory')
        }),
        (_('التقييم والنتائج'), {
            'fields': (
                'has_assessment', 'assessment_score', 'max_score', 'pass_score', 'is_passed'
            )
        }),
        (_('الشهادة'), {
            'fields': (
                'has_certificate', 'certificate_number', 'certificate_date', 
                'certificate_expiry_date', 'certificate_file'
            )
        }),
        (_('سير العمل'), {
            'fields': ('requested_by', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        (_('المهارات والكفاءات'), {
            'fields': ('skills_gained', 'competencies_improved')
        }),
        (_('التقييم والملاحظات'), {
            'fields': (
                'employee_feedback', 'employee_rating', 'trainer_feedback', 'trainer_rating'
            )
        }),
        (_('المتابعة'), {
            'fields': ('follow_up_required', 'follow_up_date', 'application_plan')
        }),
        (_('معلومات إضافية'), {
            'fields': ('prerequisites', 'learning_objectives', 'materials_provided', 'notes')
        }),
    )
    
    actions = ['approve_trainings', 'complete_trainings', 'cancel_trainings']
    
    def status_display(self, obj):
        return format_html('<span>{}</span>', obj.get_status_display_with_icon())
    status_display.short_description = _('الحالة')
    
    def priority_display(self, obj):
        return format_html('<span>{}</span>', obj.get_priority_display_with_icon())
    priority_display.short_description = _('الأولوية')
    
    def progress_bar(self, obj):
        percentage = obj.progress_percentage
        color = 'green' if percentage == 100 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{}%</div></div>',
            percentage, color, percentage
        )
    progress_bar.short_description = _('التقدم')
    
    def approve_trainings(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='planned').update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'تم اعتماد {updated} تدريب.')
    approve_trainings.short_description = _('اعتماد التدريبات المحددة')
    
    def complete_trainings(self, request, queryset):
        updated = queryset.filter(status='in_progress').update(
            status='completed',
            progress_percentage=100
        )
        self.message_user(request, f'تم إكمال {updated} تدريب.')
    complete_trainings.short_description = _('إكمال التدريبات المحددة')
    
    def cancel_trainings(self, request, queryset):
        updated = queryset.exclude(status__in=['completed', 'cancelled']).update(
            status='cancelled'
        )
        self.message_user(request, f'تم إلغاء {updated} تدريب.')
    cancel_trainings.short_description = _('إلغاء التدريبات المحددة')


# Emergency Contact Enhanced Admin
@admin.register(EmployeeEmergencyContactEnhanced)
class EmployeeEmergencyContactEnhancedAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'employee', 'relationship_display', 'primary_phone', 
        'priority_display', 'is_primary', 'is_verified', 'is_active'
    ]
    list_filter = [
        'relationship', 'priority', 'is_primary', 'is_verified', 
        'is_active', 'preferred_language'
    ]
    search_fields = [
        'full_name', 'employee__full_name', 'primary_phone', 
        'secondary_phone', 'email'
    ]
    raw_id_fields = ['employee', 'created_by']
    ordering = ['employee', 'priority']
    list_editable = ['is_active']
    
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('employee', 'full_name', 'relationship', 'relationship_other')
        }),
        (_('معلومات الاتصال'), {
            'fields': ('primary_phone', 'secondary_phone', 'email')
        }),
        (_('العنوان'), {
            'fields': ('address', 'city', 'country')
        }),
        (_('معلومات إضافية'), {
            'fields': ('occupation', 'workplace')
        }),
        (_('الأولوية والتوفر'), {
            'fields': (
                'priority', 'is_primary', 'best_time_to_call', 
                'availability_notes', 'preferred_language'
            )
        }),
        (_('التفويضات'), {
            'fields': (
                'can_make_medical_decisions', 'can_receive_salary', 'has_power_of_attorney'
            )
        }),
        (_('الحالة والتحقق'), {
            'fields': ('is_verified', 'verified_date', 'is_active')
        }),
        (_('ملاحظات'), {
            'fields': ('notes',)
        }),
    )
    
    actions = ['verify_contacts', 'set_as_primary', 'send_test_notification']
    
    def relationship_display(self, obj):
        return obj.relationship_display
    relationship_display.short_description = _('صلة القرابة')
    
    def priority_display(self, obj):
        return format_html('<span>{}</span>', obj.get_priority_display_with_icon())
    priority_display.short_description = _('الأولوية')
    
    def verify_contacts(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_verified=True, verified_date=timezone.now())
        self.message_user(request, f'تم التحقق من {updated} جهة اتصال.')
    verify_contacts.short_description = _('التحقق من جهات الاتصال المحددة')
    
    def set_as_primary(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, 'يرجى اختيار جهة اتصال واحدة فقط.', level='error')
            return
        
        contact = queryset.first()
        # Unset other primary contacts for the same employee
        EmployeeEmergencyContactEnhanced.objects.filter(
            employee=contact.employee, is_primary=True
        ).update(is_primary=False)
        
        contact.is_primary = True
        contact.save()
        self.message_user(request, f'تم تعيين {contact.full_name} كجهة اتصال أساسية.')
    set_as_primary.short_description = _('تعيين كجهة اتصال أساسية')
    
    def send_test_notification(self, request, queryset):
        count = 0
        for contact in queryset:
            if contact.is_active:
                # Here you would integrate with your notification system
                count += 1
        self.message_user(request, f'تم إرسال إشعار تجريبي لـ {count} جهة اتصال.')
    send_test_notification.short_description = _('إرسال إشعار تجريبي')


# Inline Admin Classes for use in Employee Admin
class EmployeeFileInline(admin.TabularInline):
    model = EmployeeFileEnhanced
    extra = 0
    fields = ['title', 'category', 'file', 'status', 'access_level', 'expiry_date']
    readonly_fields = ['file_size', 'created_at']
    show_change_link = True


class EmployeeTrainingInline(admin.TabularInline):
    model = EmployeeTrainingEnhanced
    extra = 0
    fields = ['title', 'category', 'start_date', 'end_date', 'status', 'progress_percentage']
    readonly_fields = ['created_at']
    show_change_link = True


class EmployeeEmergencyContactInline(admin.TabularInline):
    model = EmployeeEmergencyContactEnhanced
    extra = 0
    fields = ['full_name', 'relationship', 'primary_phone', 'priority', 'is_primary', 'is_active']
    show_change_link = True