from django.contrib import admin
from ElDawliya_sys.admin_site import admin_site
from .models import (
    SystemSettings,
    Department,
    Module,
    GroupProfile
)

# Register with custom admin site instead of default admin site
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

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'url_name', 'is_active', 'require_admin', 'order']
    list_filter = ['is_active', 'require_admin']
    search_fields = ['name', 'url_name', 'description']
    list_editable = ['is_active', 'order']
    filter_horizontal = ['groups']

class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'url', 'is_active', 'require_admin', 'order']
    list_filter = ['department', 'is_active', 'require_admin']
    search_fields = ['name', 'url', 'description']
    list_editable = ['is_active', 'order']
    filter_horizontal = ['groups']

# إضافة إعدادات الإدارة للنموذج GroupProfile
class GroupProfileAdmin(admin.ModelAdmin):
    list_display = ['group', 'description']
    search_fields = ['group__name', 'description']
    list_filter = ['group']


# تسجيل النماذج في موقع الإدارة المخصص
admin_site.register(SystemSettings, SystemSettingsAdmin)
admin_site.register(Department, DepartmentAdmin)
admin_site.register(Module, ModuleAdmin)
admin_site.register(GroupProfile, GroupProfileAdmin)
