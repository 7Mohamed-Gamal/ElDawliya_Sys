from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'user', 'priority', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'read_at')
    fieldsets = (
        ('معلومات التنبيه', {
            'fields': ('title', 'message', 'notification_type', 'priority', 'icon')
        }),
        ('الربط', {
            'fields': ('content_type', 'object_id', 'url')
        }),
        ('المستخدم والحالة', {
            'fields': ('user', 'is_read', 'read_at')
        }),
        ('التوقيت', {
            'fields': ('created_at', 'updated_at')
        }),
    )
