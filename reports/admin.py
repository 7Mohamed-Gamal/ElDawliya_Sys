from django.contrib import admin
from .models import (
    ReportCategory, ReportTemplate, ReportSchedule, 
    GeneratedReport, ReportAccessLog, ReportDashboard
)


@admin.register(ReportCategory)
class ReportCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category_type', 'is_active', 'sort_order']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['sort_order', 'name']


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'is_active', 'is_featured', 'created_at']
    list_filter = ['category', 'is_active', 'is_featured', 'default_format']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['allowed_users']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('category', 'name', 'code', 'description')
        }),
        ('إعدادات التقرير', {
            'fields': ('query_sql', 'python_code', 'template_file', 'parameters', 'default_filters')
        }),
        ('إعدادات الإخراج', {
            'fields': ('supported_formats', 'default_format')
        }),
        ('التحكم في الوصول', {
            'fields': ('is_public', 'allowed_roles', 'allowed_users')
        }),
        ('البيانات الوصفية', {
            'fields': ('is_active', 'is_featured', 'estimated_time', 'created_by')
        }),
        ('الطوابع الزمنية', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'frequency', 'status', 'next_run', 'run_count']
    list_filter = ['frequency', 'status', 'template__category']
    search_fields = ['name', 'template__name']
    readonly_fields = ['last_run', 'run_count', 'error_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('template', 'name')
        }),
        ('إعدادات الجدولة', {
            'fields': ('frequency', 'start_date', 'end_date', 'next_run')
        }),
        ('معاملات التقرير', {
            'fields': ('parameters', 'output_format')
        }),
        ('إعدادات البريد الإلكتروني', {
            'fields': ('email_recipients', 'email_subject', 'email_body')
        }),
        ('الحالة والإحصائيات', {
            'fields': ('status', 'last_run', 'run_count', 'error_count', 'last_error')
        }),
        ('البيانات الوصفية', {
            'fields': ('created_by', 'created_at', 'updated_at')
        })
    )


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'status', 'output_format', 'file_size', 'download_count', 'generated_at']
    list_filter = ['status', 'output_format', 'template__category', 'generated_at']
    search_fields = ['name', 'template__name']
    readonly_fields = ['file_size', 'download_count', 'execution_time', 'generated_at']
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('معلومات التقرير', {
            'fields': ('template', 'schedule', 'name', 'parameters', 'output_format')
        }),
        ('معلومات الملف', {
            'fields': ('file_path', 'file_size', 'download_count')
        }),
        ('الحالة والتوقيت', {
            'fields': ('status', 'started_at', 'completed_at', 'execution_time', 'expires_at')
        }),
        ('معالجة الأخطاء', {
            'fields': ('error_message', 'error_details')
        }),
        ('البيانات الوصفية', {
            'fields': ('generated_by', 'generated_at')
        })
    )


@admin.register(ReportAccessLog)
class ReportAccessLogAdmin(admin.ModelAdmin):
    list_display = ['report', 'user', 'access_type', 'success', 'accessed_at']
    list_filter = ['access_type', 'success', 'accessed_at']
    search_fields = ['report__name', 'user__username']
    readonly_fields = ['accessed_at']
    date_hierarchy = 'accessed_at'


@admin.register(ReportDashboard)
class ReportDashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_public', 'is_active', 'is_default', 'created_at']
    list_filter = ['is_public', 'is_active', 'is_default']
    search_fields = ['name', 'description', 'owner__first_name', 'owner__last_name']
    filter_horizontal = ['shared_with']
    readonly_fields = ['created_at', 'updated_at']