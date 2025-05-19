from django.contrib import admin
from .models import SystemSettings

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('قاعدة البيانات', {
            'fields': ('db_host', 'db_name', 'db_user', 'db_password', 'db_port'),
        }),
        ('معلومات الشركة', {
            'fields': ('company_name', 'company_address', 'company_phone', 'company_email', 'company_website', 'company_logo'),
        }),
        ('إعدادات النظام', {
            'fields': ('system_name', 'enable_debugging', 'maintenance_mode', 'timezone', 'date_format'),
        }),
        ('اللغة والواجهة', {
            'fields': ('language', 'font_family', 'text_direction'),
        }),
    )
    readonly_fields = ['last_modified']
    list_display = ['company_name', 'system_name', 'last_modified']

    def has_add_permission(self, request):
        return not SystemSettings.objects.exists() and super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False # Prevent deletion of settings
