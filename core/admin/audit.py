"""
Admin interface for audit and monitoring system
واجهة الإدارة لنظام التدقيق والمراقبة
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.forms import widgets
from django.utils import timezone
from datetime import timedelta

from ..models.audit import (
    AuditLog, SecurityEvent, SystemMetric, AlertRule, Alert
)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin interface for audit logs
    واجهة إدارة سجلات التدقيق
    """
    list_display = [
        'timestamp', 'user', 'action_type', 'action_description_short',
        'ip_address', 'response_status', 'severity', 'is_suspicious', 'module'
    ]
    list_filter = [
        'action_type', 'severity', 'is_suspicious', 'is_security_relevant',
        'module', 'response_status', 'timestamp'
    ]
    search_fields = [
        'user__username', 'action_description', 'ip_address',
        'request_path', 'object_repr'
    ]
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('timestamp', 'user', 'session_key', 'action_type', 'action_description')
        }),
        ('تفاصيل الكائن المستهدف', {
            'fields': ('content_type', 'object_id', 'object_repr'),
            'classes': ('collapse',)
        }),
        ('تتبع التغييرات', {
            'fields': ('old_values', 'new_values'),
            'classes': ('collapse',)
        }),
        ('معلومات الطلب', {
            'fields': ('ip_address', 'user_agent', 'request_method', 'request_path', 'request_data'),
            'classes': ('collapse',)
        }),
        ('معلومات الاستجابة', {
            'fields': ('response_status', 'response_time'),
            'classes': ('collapse',)
        }),
        ('التصنيف والأمان', {
            'fields': ('severity', 'is_suspicious', 'is_security_relevant', 'module', 'tags')
        }),
        ('بيانات إضافية', {
            'fields': ('additional_data',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['timestamp']

    def action_description_short(self, obj):
        """Display shortened action description"""
        return obj.action_description[:50] + '...' if len(obj.action_description) > 50 else obj.action_description
    action_description_short.short_description = 'وصف الإجراء'

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('user', 'content_type')

    def has_add_permission(self, request):
        """has_add_permission function"""
        return False  # Audit logs should not be manually created

    def has_change_permission(self, request, obj=None):
        """has_change_permission function"""
        return False  # Audit logs should not be modified

    def has_delete_permission(self, request, obj=None):
        """has_delete_permission function"""
        return request.user.is_superuser  # Only superusers can delete audit logs

    actions = ['mark_as_reviewed', 'export_selected_logs']

    def mark_as_reviewed(self, request, queryset):
        """Mark selected logs as reviewed"""
        # This would add a reviewed flag if we had one
        self.message_user(request, f'تم وضع علامة مراجعة على {queryset.count()} سجل')
    mark_as_reviewed.short_description = 'وضع علامة مراجعة'

    def export_selected_logs(self, request, queryset):
        """Export selected logs"""
        # This would implement export functionality
        self.message_user(request, f'تم تصدير {queryset.count()} سجل')
    export_selected_logs.short_description = 'تصدير السجلات المحددة'


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    """
    Admin interface for security events
    واجهة إدارة الأحداث الأمنية
    """
    list_display = [
        'detected_at', 'title', 'event_type', 'threat_level', 'status',
        'source_ip', 'target_user', 'assigned_to', 'confidence_score'
    ]
    list_filter = [
        'event_type', 'threat_level', 'status', 'detected_at',
        'assigned_to', 'source_country'
    ]
    search_fields = [
        'title', 'description', 'source_ip', 'target_user__username',
        'target_endpoint', 'target_resource'
    ]
    ordering = ['-detected_at']
    date_hierarchy = 'detected_at'

    fieldsets = (
        ('تصنيف الحدث', {
            'fields': ('event_type', 'threat_level', 'status', 'title', 'description')
        }),
        ('معلومات المصدر', {
            'fields': ('source_ip', 'source_user_agent', 'source_country')
        }),
        ('معلومات الهدف', {
            'fields': ('target_user', 'target_endpoint', 'target_resource')
        }),
        ('معلومات الاكتشاف', {
            'fields': ('detected_by', 'detection_method', 'confidence_score')
        }),
        ('معلومات الاستجابة', {
            'fields': ('assigned_to', 'response_actions', 'mitigation_steps'),
            'classes': ('collapse',)
        }),
        ('الأدلة والقطع الأثرية', {
            'fields': ('evidence', 'artifacts', 'related_logs'),
            'classes': ('collapse',)
        }),
        ('الطوابع الزمنية', {
            'fields': ('detected_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['detected_at', 'updated_at']
    filter_horizontal = ['related_logs']

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related(
            'target_user', 'assigned_to'
        ).prefetch_related('related_logs')

    actions = ['assign_to_me', 'mark_as_resolved', 'mark_as_false_positive']

    def assign_to_me(self, request, queryset):
        """Assign selected events to current user"""
        updated = queryset.update(assigned_to=request.user)
        self.message_user(request, f'تم تعيين {updated} حدث لك')
    assign_to_me.short_description = 'تعيين لي'

    def mark_as_resolved(self, request, queryset):
        """Mark selected events as resolved"""
        updated = queryset.update(
            status='resolved',
            resolved_at=timezone.now()
        )
        self.message_user(request, f'تم وضع علامة حل على {updated} حدث')
    mark_as_resolved.short_description = 'وضع علامة حل'

    def mark_as_false_positive(self, request, queryset):
        """Mark selected events as false positive"""
        updated = queryset.update(status='false_positive')
        self.message_user(request, f'تم وضع علامة إيجابي خاطئ على {updated} حدث')
    mark_as_false_positive.short_description = 'وضع علامة إيجابي خاطئ'


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    """
    Admin interface for system metrics
    واجهة إدارة مقاييس النظام
    """
    list_display = [
        'timestamp', 'metric_name', 'value', 'unit', 'status_indicator',
        'host', 'service'
    ]
    list_filter = [
        'metric_type', 'host', 'service', 'timestamp'
    ]
    search_fields = ['metric_name', 'host', 'service']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('تحديد المقياس', {
            'fields': ('metric_type', 'metric_name', 'value', 'unit')
        }),
        ('العتبات', {
            'fields': ('warning_threshold', 'critical_threshold')
        }),
        ('معلومات السياق', {
            'fields': ('host', 'service', 'tags')
        }),
        ('الطابع الزمني', {
            'fields': ('timestamp',)
        }),
    )

    readonly_fields = ['timestamp']

    def status_indicator(self, obj):
        """Display status indicator based on thresholds"""
        status = obj.get_status()
        colors = {
            'normal': 'green',
            'warning': 'orange',
            'critical': 'red'
        }
        color = colors.get(status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status.upper()
        )
    status_indicator.short_description = 'الحالة'

    def has_add_permission(self, request):
        """has_add_permission function"""
        return False  # Metrics should be automatically collected

    def has_change_permission(self, request, obj=None):
        """has_change_permission function"""
        return False  # Metrics should not be modified

    actions = ['delete_old_metrics']

    def delete_old_metrics(self, request, queryset):
        """Delete metrics older than 90 days"""
        cutoff_date = timezone.now() - timedelta(days=90)
        old_metrics = SystemMetric.objects.filter(timestamp__lt=cutoff_date)
        count = old_metrics.count()
        old_metrics.delete()
        self.message_user(request, f'تم حذف {count} مقياس قديم')
    delete_old_metrics.short_description = 'حذف المقاييس القديمة'


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    """
    Admin interface for alert rules
    واجهة إدارة قواعد التنبيه
    """
    list_display = [
        'name', 'rule_type', 'severity', 'is_active',
        'last_triggered', 'trigger_count'
    ]
    list_filter = ['rule_type', 'severity', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']

    fieldsets = (
        ('تحديد القاعدة', {
            'fields': ('name', 'description', 'rule_type')
        }),
        ('تكوين القاعدة', {
            'fields': ('conditions', 'severity')
        }),
        ('إعدادات الإشعار', {
            'fields': ('notification_channels', 'notification_template')
        }),
        ('حالة القاعدة', {
            'fields': ('is_active', 'last_triggered', 'trigger_count')
        }),
        ('الطوابع الزمنية', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['last_triggered', 'trigger_count', 'created_at', 'updated_at']

    actions = ['activate_rules', 'deactivate_rules', 'test_rules']

    def activate_rules(self, request, queryset):
        """Activate selected rules"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'تم تفعيل {updated} قاعدة')
    activate_rules.short_description = 'تفعيل القواعد'

    def deactivate_rules(self, request, queryset):
        """Deactivate selected rules"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'تم إلغاء تفعيل {updated} قاعدة')
    deactivate_rules.short_description = 'إلغاء تفعيل القواعد'

    def test_rules(self, request, queryset):
        """Test selected rules"""
        # This would implement rule testing functionality
        self.message_user(request, f'تم اختبار {queryset.count()} قاعدة')
    test_rules.short_description = 'اختبار القواعد'


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """
    Admin interface for alerts
    واجهة إدارة التنبيهات
    """
    list_display = [
        'created_at', 'title', 'severity', 'status', 'rule',
        'acknowledged_by', 'resolved_by'
    ]
    list_filter = [
        'severity', 'status', 'rule', 'created_at',
        'acknowledged_by', 'resolved_by'
    ]
    search_fields = ['title', 'message', 'rule__name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('مصدر التنبيه', {
            'fields': ('rule',)
        }),
        ('تفاصيل التنبيه', {
            'fields': ('title', 'message', 'severity', 'status')
        }),
        ('معلومات الاستجابة', {
            'fields': (
                'acknowledged_by', 'acknowledged_at',
                'resolved_by', 'resolved_at'
            )
        }),
        ('بيانات السياق', {
            'fields': ('context_data',),
            'classes': ('collapse',)
        }),
        ('الطوابع الزمنية', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = [
        'created_at', 'updated_at', 'acknowledged_at', 'resolved_at'
    ]

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related(
            'rule', 'acknowledged_by', 'resolved_by'
        )

    actions = ['acknowledge_alerts', 'resolve_alerts', 'suppress_alerts']

    def acknowledge_alerts(self, request, queryset):
        """Acknowledge selected alerts"""
        updated = queryset.filter(status='open').update(
            status='acknowledged',
            acknowledged_by=request.user,
            acknowledged_at=timezone.now()
        )
        self.message_user(request, f'تم تأكيد {updated} تنبيه')
    acknowledge_alerts.short_description = 'تأكيد التنبيهات'

    def resolve_alerts(self, request, queryset):
        """Resolve selected alerts"""
        updated = queryset.filter(status__in=['open', 'acknowledged']).update(
            status='resolved',
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'تم حل {updated} تنبيه')
    resolve_alerts.short_description = 'حل التنبيهات'

    def suppress_alerts(self, request, queryset):
        """Suppress selected alerts"""
        updated = queryset.update(status='suppressed')
        self.message_user(request, f'تم كبت {updated} تنبيه')
    suppress_alerts.short_description = 'كبت التنبيهات'


# Custom admin site for security monitoring
class SecurityAdminSite(admin.AdminSite):
    """
    Custom admin site for security monitoring
    موقع إدارة مخصص لمراقبة الأمان
    """
    site_header = 'مراقبة الأمان والتدقيق'
    site_title = 'نظام الأمان'
    index_title = 'لوحة تحكم الأمان'

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request)

        # Custom ordering for security app
        for app in app_list:
            if app['name'] == 'Core':
                # Custom model ordering
                model_order = [
                    'SecurityEvent', 'AuditLog', 'Alert', 'AlertRule', 'SystemMetric'
                ]

                app['models'].sort(key=lambda x: (
                    model_order.index(x['object_name'])
                    if x['object_name'] in model_order
                    else len(model_order)
                ))

        return app_list


# Create custom admin site instance
security_admin_site = SecurityAdminSite(name='security_admin')

# Register models with custom admin site
security_admin_site.register(AuditLog, AuditLogAdmin)
security_admin_site.register(SecurityEvent, SecurityEventAdmin)
security_admin_site.register(SystemMetric, SystemMetricAdmin)
security_admin_site.register(AlertRule, AlertRuleAdmin)
security_admin_site.register(Alert, AlertAdmin)
