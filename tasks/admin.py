from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from .models import Task, TaskStep

class TaskStepInline(admin.TabularInline):
    """Enhanced inline for task steps"""
    model = TaskStep
    extra = 0
    fields = ['description', 'notes', 'completed', 'completion_date', 'created_by']
    readonly_fields = ['created_by', 'completion_date']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Task model"""

    list_display = [
        'get_title_display', 'get_priority_badge', 'assigned_to',
        'created_by', 'get_status_badge', 'get_progress',
        'start_date', 'end_date', 'get_overdue_status', 'status', 'priority'
    ]
    list_filter = [
        'status', 'priority', 'created_by', 'assigned_to',
        'meeting', 'created_at'
    ]
    search_fields = [
        'title', 'description', 'assigned_to__username',
        'created_by__username', 'meeting__title'
    ]
    date_hierarchy = 'created_at'
    list_editable = ['status', 'priority']
    inlines = [TaskStepInline]
    list_per_page = 25

    fieldsets = (
        (_('معلومات المهمة'), {
            'fields': ('title', 'description', 'priority', 'status'),
            'classes': ('wide',)
        }),
        (_('الأشخاص'), {
            'fields': ('assigned_to', 'created_by'),
            'classes': ('collapse',)
        }),
        (_('التواريخ'), {
            'fields': ('start_date', 'end_date'),
            'classes': ('wide',)
        }),
        (_('الاجتماع'), {
            'fields': ('meeting',),
            'classes': ('collapse',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_by', 'created_at', 'updated_at']

    actions = ['mark_as_completed', 'mark_as_in_progress', 'mark_as_high_priority']

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'assigned_to', 'created_by', 'meeting'
        ).prefetch_related('steps').annotate(
            steps_count=Count('steps')
        )

    def get_title_display(self, obj):
        """Display title with link to detail view"""
        title = obj.get_display_title()
        url = reverse('admin:tasks_task_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, title)
    get_title_display.short_description = _('العنوان')
    get_title_display.admin_order_field = 'title'

    def get_priority_badge(self, obj):
        """Display priority as colored badge"""
        colors = {
            'urgent': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_priority_display()
        )
    get_priority_badge.short_description = _('الأولوية')
    get_priority_badge.admin_order_field = 'priority'

    def get_status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'pending': '#6c757d',
            'in_progress': '#007bff',
            'completed': '#28a745',
            'canceled': '#dc3545',
            'deferred': '#ffc107',
            'failed': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    get_status_badge.short_description = _('الحالة')
    get_status_badge.admin_order_field = 'status'

    def get_progress(self, obj):
        """Display progress bar"""
        percentage = obj.progress_percentage
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 4px;">'
            '<div style="width: {}%; background-color: #007bff; height: 20px; '
            'border-radius: 4px; text-align: center; color: white; font-size: 11px; '
            'line-height: 20px;">{}%</div></div>',
            percentage, percentage
        )
    get_progress.short_description = _('التقدم')

    def get_overdue_status(self, obj):
        """Display overdue status"""
        if obj.is_overdue:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">متأخرة</span>'
            )
        elif obj.days_until_due <= 3 and obj.status in ['pending', 'in_progress']:
            return format_html(
                '<span style="color: #fd7e14; font-weight: bold;">قريبة الانتهاء</span>'
            )
        return format_html('<span style="color: #28a745;">في الوقت</span>')
    get_overdue_status.short_description = _('حالة الموعد')

    def save_model(self, request, obj, form, change):
        """Set created_by on new objects"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        """Enhanced permission checking"""
        if obj is not None:
            return (
                request.user.is_superuser or
                obj.created_by == request.user or
                obj.assigned_to == request.user
            )
        return super().has_change_permission(request, obj)

    def mark_as_completed(self, request, queryset):
        """Bulk action to mark tasks as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'تم تحديث {updated} مهمة إلى مكتملة')
    mark_as_completed.short_description = _('تحديد كمكتملة')

    def mark_as_in_progress(self, request, queryset):
        """Bulk action to mark tasks as in progress"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'تم تحديث {updated} مهمة إلى قيد التنفيذ')
    mark_as_in_progress.short_description = _('تحديد كقيد التنفيذ')

    def mark_as_high_priority(self, request, queryset):
        """Bulk action to mark tasks as high priority"""
        updated = queryset.update(priority='high')
        self.message_user(request, f'تم تحديث {updated} مهمة إلى أولوية عالية')
    mark_as_high_priority.short_description = _('تحديد كأولوية عالية')

@admin.register(TaskStep)
class TaskStepAdmin(admin.ModelAdmin):
    """Enhanced admin interface for TaskStep model"""

    list_display = [
        'get_task_title', 'get_description_preview', 'completed',
        'created_by', 'date', 'completion_date'
    ]
    list_filter = [
        'completed', 'task__status', 'task__priority',
        'created_by', 'date'
    ]
    search_fields = [
        'description', 'notes', 'task__title',
        'task__description', 'created_by__username'
    ]
    date_hierarchy = 'date'
    list_editable = ['completed']
    list_per_page = 30

    fieldsets = (
        (_('معلومات الخطوة'), {
            'fields': ('task', 'description', 'notes', 'completed'),
            'classes': ('wide',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_by', 'date', 'completion_date', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_by', 'date', 'completion_date', 'updated_at']

    actions = ['mark_as_completed', 'mark_as_incomplete']

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related(
            'task', 'created_by'
        )

    def get_task_title(self, obj):
        """Display task title with link"""
        title = obj.task.get_display_title()
        url = reverse('admin:tasks_task_change', args=[obj.task.pk])
        return format_html('<a href="{}">{}</a>', url, title)
    get_task_title.short_description = _('المهمة')
    get_task_title.admin_order_field = 'task__title'

    def get_description_preview(self, obj):
        """Display truncated description"""
        description = obj.description[:50]
        if len(obj.description) > 50:
            description += '...'
        return description
    get_description_preview.short_description = _('الوصف')
    get_description_preview.admin_order_field = 'description'

    def has_change_permission(self, request, obj=None):
        """Enhanced permission checking"""
        if obj is not None:
            return (
                request.user.is_superuser or
                obj.task.created_by == request.user or
                obj.task.assigned_to == request.user or
                obj.created_by == request.user
            )
        return super().has_change_permission(request, obj)

    def mark_as_completed(self, request, queryset):
        """Bulk action to mark steps as completed"""
        updated = queryset.update(
            completed=True,
            completion_date=timezone.now()
        )
        self.message_user(request, f'تم تحديث {updated} خطوة كمكتملة')
    mark_as_completed.short_description = _('تحديد كمكتملة')

    def mark_as_incomplete(self, request, queryset):
        """Bulk action to mark steps as incomplete"""
        updated = queryset.update(
            completed=False,
            completion_date=None
        )
        self.message_user(request, f'تم تحديث {updated} خطوة كغير مكتملة')
    mark_as_incomplete.short_description = _('تحديد كغير مكتملة')

# Customize admin site
admin.site.site_header = _('إدارة نظام المهام')
admin.site.site_title = _('نظام المهام')
admin.site.index_title = _('لوحة تحكم المهام')
