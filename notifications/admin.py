from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type_display', 'user', 'priority_display', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'read_at')

    fieldsets = (
        (_('معلومات التنبيه'), {
            'fields': ('title', 'message', 'notification_type', 'priority', 'icon')
        }),
        (_('الربط'), {
            'fields': ('content_type', 'object_id', 'url')
        }),
        (_('المستخدم والحالة'), {
            'fields': ('user', 'is_read', 'read_at')
        }),
        (_('التوقيت'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def notification_type_display(self, obj):
        """عرض نوع التنبيه بألوان مختلفة"""
        colors = {
            'info': 'primary',
            'success': 'success',
            'warning': 'warning',
            'error': 'danger',
            'system': 'secondary',
        }
        color = colors.get(obj.notification_type, 'info')
        return format_html('<span class="badge bg-{}">{}</span>', color, obj.get_notification_type_display())
    notification_type_display.short_description = _('نوع التنبيه')

    def priority_display(self, obj):
        """عرض أولوية التنبيه بألوان مختلفة"""
        colors = {
            'low': 'info',
            'normal': 'primary',
            'high': 'warning',
            'urgent': 'danger',
        }
        color = colors.get(obj.priority, 'primary')
        return format_html('<span class="badge bg-{}">{}</span>', color, obj.get_priority_display())
    priority_display.short_description = _('الأولوية')

    def has_add_permission(self, request):
        """منع إضافة التنبيهات يدويًا - يجب أن تتم إضافتها من خلال النظام"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """السماح بتعديل التنبيهات فقط للمشرفين أو المستخدم المرسل إليه التنبيه"""
        if obj is not None and (obj.user == request.user or request.user.is_superuser):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """السماح بحذف التنبيهات فقط للمشرفين أو المستخدم المرسل إليه التنبيه"""
        if obj is not None and (obj.user == request.user or request.user.is_superuser):
            return True
        return super().has_delete_permission(request, obj)
