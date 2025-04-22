from django.contrib import admin
from .models import PermissionAuditLog, DepartmentPermissionCache, ModulePermissionCache

@admin.register(PermissionAuditLog)
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

@admin.register(DepartmentPermissionCache)
class DepartmentPermissionCacheAdmin(admin.ModelAdmin):
    list_display = ('user', 'department_name', 'has_access', 'last_updated')
    list_filter = ('has_access', 'department_name')
    search_fields = ('user__username', 'department_name')
    date_hierarchy = 'last_updated'

@admin.register(ModulePermissionCache)
class ModulePermissionCacheAdmin(admin.ModelAdmin):
    list_display = ('user', 'department_name', 'module_name', 'permission_type', 'has_permission', 'last_updated')
    list_filter = ('has_permission', 'department_name', 'module_name', 'permission_type')
    search_fields = ('user__username', 'department_name', 'module_name')
    date_hierarchy = 'last_updated'
