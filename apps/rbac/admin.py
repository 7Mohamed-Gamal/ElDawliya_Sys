from django.contrib import admin
from .models import Role, Permission, RolePermission, UserRole

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """RoleAdmin class"""
    list_display = ('role_id', 'role_name')
    search_fields = ('role_name',)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """PermissionAdmin class"""
    list_display = ('permission_id', 'permission_key')
    search_fields = ('permission_key',)

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """RolePermissionAdmin class"""
    list_display = ('role', 'permission')
    list_filter = ('role',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """UserRoleAdmin class"""
    list_display = ('user_id', 'role')
    list_filter = ('role',)
