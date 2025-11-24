from django.contrib import admin
from .models import HRSystemConfig, HRSystemLog


@admin.register(HRSystemConfig)
class HRSystemConfigAdmin(admin.ModelAdmin):
    """إدارة إعدادات النظام"""

    list_display = ['key', 'value', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['key', 'value', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('key', 'value', 'description', 'is_active')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HRSystemLog)
class HRSystemLogAdmin(admin.ModelAdmin):
    """إدارة سجلات النظام"""

    list_display = ['user', 'action', 'module', 'object_id', 'ip_address', 'created_at']
    list_filter = ['action', 'module', 'created_at']
    search_fields = ['user__username', 'module', 'description', 'object_id']
    readonly_fields = ['user', 'action', 'module', 'object_id', 'description', 'ip_address', 'created_at']

    def has_add_permission(self, request):
        """منع إضافة سجلات جديدة يدوياً"""
        return False

    def has_change_permission(self, request, obj=None):
        """منع تعديل السجلات"""
        return False

    def has_delete_permission(self, request, obj=None):
        """السماح بالحذف للمديرين فقط"""
        return request.user.is_superuser
