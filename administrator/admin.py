from django.contrib import admin
from ElDawliya_sys.admin_site import admin_site
from .models import (
    SystemSettings,
    Department,
    Module,
    Permission,
    TemplatePermission,
    UserGroup,
    UserDepartmentPermission,
    UserModulePermission,
    GroupProfile
)

# استيراد النماذج الجديدة من RBAC
from .models_new import (
    AppModule,
    OperationPermission,
    PagePermission,
    UserOperationPermission,
    UserPagePermission
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

class PermissionAdmin(admin.ModelAdmin):
    list_display = ['module', 'permission_type', 'is_active']
    list_filter = ['permission_type', 'is_active', 'module__department']
    search_fields = ['module__name']
    list_editable = ['is_active']
    filter_horizontal = ['groups']

# إضافة إعدادات الإدارة للنموذج الجديد TemplatePermission
class TemplatePermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'app_name', 'template_path', 'is_active']
    list_filter = ['app_name', 'is_active']
    search_fields = ['name', 'app_name', 'template_path', 'description']
    list_editable = ['is_active']
    filter_horizontal = ['groups', 'users']

# إضافة إعدادات الإدارة للنموذج الجديد UserGroup
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'date_joined']
    list_filter = ['group', 'date_joined']
    search_fields = ['user__username', 'group__name', 'notes']
    readonly_fields = ['date_joined']

# إضافة إعدادات الإدارة للنموذج الجديد UserDepartmentPermission
class UserDepartmentPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'can_view']
    list_filter = ['department', 'can_view']
    search_fields = ['user__username', 'department__name']
    list_editable = ['can_view']

# إضافة إعدادات الإدارة للنموذج الجديد UserModulePermission
class UserModulePermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'can_view', 'can_add', 'can_edit', 'can_delete', 'can_print']
    list_filter = ['module__department', 'can_view', 'can_add', 'can_edit', 'can_delete', 'can_print']
    search_fields = ['user__username', 'module__name']
    list_editable = ['can_view', 'can_add', 'can_edit', 'can_delete', 'can_print']

# إضافة إعدادات الإدارة للنموذج GroupProfile
class GroupProfileAdmin(admin.ModelAdmin):
    list_display = ['group', 'description']
    search_fields = ['group__name', 'description']
    list_filter = ['group']

# ======== تسجيل نماذج RBAC الجديدة في الإدارة ========

class AppModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']
    list_editable = ['is_active', 'order']
    readonly_fields = ['code']
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'code', 'description')
        }),
        ('العرض', {
            'fields': ('icon', 'order', 'is_active')
        }),
    )

class OperationPermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'app_module', 'permission_type', 'code', 'is_active']
    list_filter = ['app_module', 'permission_type', 'is_active']
    search_fields = ['name', 'code', 'description']
    list_editable = ['is_active']
    readonly_fields = ['code']
    fieldsets = (
        ('معلومات الصلاحية', {
            'fields': ('name', 'app_module', 'permission_type')
        }),
        ('التفاصيل', {
            'fields': ('code', 'description', 'is_active')
        }),
    )

class PagePermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'app_module', 'url_pattern', 'is_active']
    list_filter = ['app_module', 'is_active']
    search_fields = ['name', 'url_pattern', 'template_path', 'description']
    list_editable = ['is_active']
    fieldsets = (
        ('معلومات الصفحة', {
            'fields': ('name', 'app_module')
        }),
        ('مسارات الوصول', {
            'fields': ('url_pattern', 'template_path')
        }),
        ('تفاصيل إضافية', {
            'fields': ('description', 'is_active')
        }),
    )

class UserOperationPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'operation']
    list_filter = ['operation__app_module', 'operation__permission_type']
    search_fields = ['user__username', 'operation__name']
    autocomplete_fields = ['user', 'operation']
    fieldsets = (
        ('تعيين الصلاحية', {
            'fields': ('user', 'operation')
        }),
    )

class UserPagePermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'page']
    list_filter = ['page__app_module']
    search_fields = ['user__username', 'page__name']
    autocomplete_fields = ['user', 'page']
    fieldsets = (
        ('تعيين صلاحية الصفحة', {
            'fields': ('user', 'page')
        }),
    )

# تسجيل النماذج في موقع الإدارة المخصص
admin_site.register(SystemSettings, SystemSettingsAdmin)
admin_site.register(Department, DepartmentAdmin)
admin_site.register(Module, ModuleAdmin)
admin_site.register(Permission, PermissionAdmin)
admin_site.register(TemplatePermission, TemplatePermissionAdmin)
admin_site.register(UserGroup, UserGroupAdmin)
admin_site.register(UserDepartmentPermission, UserDepartmentPermissionAdmin)
admin_site.register(UserModulePermission, UserModulePermissionAdmin)
admin_site.register(GroupProfile, GroupProfileAdmin)

# تسجيل نماذج RBAC الجديدة
admin_site.register(AppModule, AppModuleAdmin)
admin_site.register(OperationPermission, OperationPermissionAdmin)
admin_site.register(PagePermission, PagePermissionAdmin)
admin_site.register(UserOperationPermission, UserOperationPermissionAdmin)
admin_site.register(UserPagePermission, UserPagePermissionAdmin)
