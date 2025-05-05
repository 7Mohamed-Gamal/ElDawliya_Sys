from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for AuditLog model."""
    
    list_display = ['timestamp', 'user_display', 'action_display', 'app_name', 'object_display', 'ip_address']
    list_filter = ['action', 'app_name', 'timestamp', 'user']
    search_fields = ['user__username', 'object_repr', 'action_details', 'ip_address']
    readonly_fields = [field.name for field in AuditLog._meta.fields]
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        (_('Action Information'), {
            'fields': ('action', 'timestamp', 'app_name', 'action_details')
        }),
        (_('Object Information'), {
            'fields': ('content_type', 'object_id', 'object_repr')
        }),
        (_('Additional Details'), {
            'fields': ('change_data',),
            'classes': ('collapse',)
        }),
    )
    
    def user_display(self, obj):
        """Display user with link to admin."""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return _('مستخدم غير معروف')
    user_display.short_description = _('المستخدم')
    user_display.admin_order_field = 'user__username'
    
    def action_display(self, obj):
        """Display action with color coding."""
        action_colors = {
            AuditLog.CREATE: 'green',
            AuditLog.UPDATE: 'orange',
            AuditLog.DELETE: 'red',
            AuditLog.VIEW: 'blue',
            AuditLog.LOGIN: 'purple',
            AuditLog.LOGOUT: 'purple',
        }
        color = action_colors.get(obj.action, 'gray')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_action_display())
    action_display.short_description = _('الإجراء')
    action_display.admin_order_field = 'action'
    
    def object_display(self, obj):
        """Display object with link if available."""
        if obj.content_type and obj.object_id:
            model_admin_url = f'admin:{obj.content_type.app_label}_{obj.content_type.model}_change'
            try:
                url = reverse(model_admin_url, args=[obj.object_id])
                return format_html('<a href="{}">{}</a>', url, obj.object_repr or obj.object_id)
            except Exception:
                # If we can't reverse the URL, just display the object_repr
                pass
        return obj.object_repr or '-'
    object_display.short_description = _('الكائن')
    
    def has_add_permission(self, request):
        """Prevent adding audit logs manually."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting audit logs to maintain integrity."""
        # Only superusers can delete audit logs, and consider making this False
        # for production to ensure auditlog integrity
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing audit logs to maintain integrity."""
        return False
