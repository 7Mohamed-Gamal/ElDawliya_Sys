from django.contrib import admin
from .models import (
    SystemSettings,
    Department,
    Module,
    Permission,
    TemplatePermission,  # تمت إضافته
    UserGroup,  # تمت إضافته
    UserDepartmentPermission,
    UserModulePermission,
    GroupProfile
)

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

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'url_name', 'is_active', 'require_admin', 'order']
    list_filter = ['is_active', 'require_admin']
    search_fields = ['name', 'url_name', 'description']
    list_editable = ['is_active', 'order']
    filter_horizontal = ['groups']

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'url', 'is_active', 'require_admin', 'order']
    list_filter = ['department', 'is_active', 'require_admin']
    search_fields = ['name', 'url', 'description']
    list_editable = ['is_active', 'order']
    filter_horizontal = ['groups']

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['module', 'permission_type', 'is_active']
    list_filter = ['permission_type', 'is_active', 'module__department']
    search_fields = ['module__name']
    list_editable = ['is_active']
    filter_horizontal = ['groups']

# إضافة إعدادات الإدارة للنموذج الجديد TemplatePermission
@admin.register(TemplatePermission)
class TemplatePermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'app_name', 'template_path', 'is_active']
    list_filter = ['app_name', 'is_active']
    search_fields = ['name', 'app_name', 'template_path', 'description']
    list_editable = ['is_active']
    filter_horizontal = ['groups', 'users']

# إضافة إعدادات الإدارة للنموذج الجديد UserGroup
@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'date_joined']
    list_filter = ['group', 'date_joined']
    search_fields = ['user__username', 'group__name', 'notes']
    readonly_fields = ['date_joined']

# إضافة إعدادات الإدارة للنموذج الجديد UserDepartmentPermission
@admin.register(UserDepartmentPermission)
class UserDepartmentPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'can_view']
    list_filter = ['department', 'can_view']
    search_fields = ['user__username', 'department__name']
    list_editable = ['can_view']

# إضافة إعدادات الإدارة للنموذج الجديد UserModulePermission
@admin.register(UserModulePermission)
class UserModulePermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'can_view', 'can_add', 'can_edit', 'can_delete', 'can_print']
    list_filter = ['module__department', 'can_view', 'can_add', 'can_edit', 'can_delete', 'can_print']
    search_fields = ['user__username', 'module__name']
    list_editable = ['can_view', 'can_add', 'can_edit', 'can_delete', 'can_print']

# إضافة إعدادات الإدارة للنموذج GroupProfile
@admin.register(GroupProfile)
class GroupProfileAdmin(admin.ModelAdmin):
    list_display = ['group', 'description']
    search_fields = ['group__name', 'description']
    list_filter = ['group']