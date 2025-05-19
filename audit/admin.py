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
        (_('معلومات الحدث'), {
            'fields': ('timestamp', 'user', 'action', 'app_name', 'model_name', 'object_id', 'object_repr')
        }),
        (_('تفاصيل الإجراء'), {
            'fields': ('action_details',)
        }),
        (_('معلومات الاتصال'), {
            'fields': ('ip_address', 'user_agent')
        }),
    )

    def user_display(self, obj):
        """Display user with link to admin page."""
        if obj.user:
            try:
                url = reverse('admin:accounts_users_login_new_change', args=[obj.user.id])
                return format_html('<a href="{}">{}</a>', url, obj.user.username)
            except:
                return obj.user.username
        return _('مستخدم غير معروف')
    user_display.short_description = _('المستخدم')

    def action_display(self, obj):
        """Display action with appropriate color."""
        colors = {
            'create': 'success',
            'update': 'primary',
            'delete': 'danger',
            'login': 'info',
            'logout': 'secondary',
            'view': 'light',
        }
        color = colors.get(obj.action, 'dark')
        return format_html('<span class="badge bg-{}">{}</span>', color, obj.get_action_display())
    action_display.short_description = _('الإجراء')

    def object_display(self, obj):
        """Display object with link if possible."""
        if obj.object_id and obj.app_name and obj.model_name:
            try:
                url = reverse(f'admin:{obj.app_name}_{obj.model_name}_change', args=[obj.object_id])
                return format_html('<a href="{}">{}</a>', url, obj.object_repr)
            except:
                pass
        return obj.object_repr
    object_display.short_description = _('الكائن')

    def has_add_permission(self, request):
        """Disable adding audit logs manually."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing audit logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete audit logs."""
        return request.user.is_superuser
