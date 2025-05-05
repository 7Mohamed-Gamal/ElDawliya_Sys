from django.contrib import admin
from ElDawliya_sys.admin_site import admin_site
from .models import PermissionAuditLog, DepartmentPermissionCache, ModulePermissionCache

# Register with custom admin site instead of default admin site
class PermissionAuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'department', 'module', 'permission_type', 'timestamp')
    list_filter = ('action_type', 'department', 'module', 'permission_type', 'timestamp')
    search_fields = ('user__username', 'department', 'module', 'description')
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'action_type', 'department', 'module', 'permission_type',
                      'description', 'timestamp', 'ip_address', 'additional_data')
    filter_horizontal = ('affected_groups', 'affected_users')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

class DepartmentPermissionCacheAdmin(admin.ModelAdmin):
    list_display = ('user', 'department_name', 'has_access', 'last_updated')
    list_filter = ('has_access', 'department_name')
    search_fields = ('user__username', 'department_name')
    date_hierarchy = 'last_updated'

class ModulePermissionCacheAdmin(admin.ModelAdmin):
    list_display = ('user', 'department_name', 'module_name', 'permission_type', 'has_permission', 'last_updated')
    list_filter = ('has_permission', 'department_name', 'module_name', 'permission_type')
    search_fields = ('user__username', 'department_name', 'module_name')
    date_hierarchy = 'last_updated'

# تسجيل النماذج في موقع الإدارة المخصص
admin_site.register(PermissionAuditLog, PermissionAuditLogAdmin)
admin_site.register(DepartmentPermissionCache, DepartmentPermissionCacheAdmin)
admin_site.register(ModulePermissionCache, ModulePermissionCacheAdmin)
