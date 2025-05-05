from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import TaskCategory, EmployeeTask, TaskStep, TaskReminder

@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    """
    إدارة تصنيفات المهام في لوحة الإدارة
    """
    list_display = ['name', 'description', 'color', 'icon', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']


class TaskStepInline(admin.TabularInline):
    """
    عرض خطوات المهمة كجدول داخل نموذج المهمة
    """
    model = TaskStep
    extra = 1
    fields = ['description', 'completed', 'completion_date', 'created_by']
    readonly_fields = ['completion_date']


class TaskReminderInline(admin.TabularInline):
    """
    عرض تذكيرات المهمة كجدول داخل نموذج المهمة
    """
    model = TaskReminder
    extra = 1
    fields = ['reminder_date', 'is_sent', 'sent_at']
    readonly_fields = ['sent_at']


@admin.register(EmployeeTask)
class EmployeeTaskAdmin(admin.ModelAdmin):
    """
    إدارة مهام الموظفين في لوحة الإدارة
    """
    list_display = ['title', 'created_by', 'assigned_to', 'status', 'priority',
                   'start_date', 'due_date', 'progress', 'is_private']
    list_filter = ['status', 'priority', 'is_private', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'created_by__username', 'assigned_to__username']
    date_hierarchy = 'due_date'
    readonly_fields = ['completion_date', 'created_at', 'updated_at']
    fieldsets = [
        (_('معلومات المهمة'), {
            'fields': ['title', 'description', 'category', 'status', 'priority', 'progress', 'is_private']
        }),
        (_('المستخدمين'), {
            'fields': ['created_by', 'assigned_to']
        }),
        (_('التواريخ'), {
            'fields': ['start_date', 'due_date', 'completion_date', 'created_at', 'updated_at']
        }),
    ]
    inlines = [TaskStepInline, TaskReminderInline]


@admin.register(TaskStep)
class TaskStepAdmin(admin.ModelAdmin):
    """
    إدارة خطوات المهام في لوحة الإدارة
    """
    list_display = ['task', 'description', 'completed', 'completion_date', 'created_by', 'created_at']
    list_filter = ['completed', 'created_at', 'completion_date']
    search_fields = ['description', 'task__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['completion_date']


@admin.register(TaskReminder)
class TaskReminderAdmin(admin.ModelAdmin):
    """
    إدارة تذكيرات المهام في لوحة الإدارة
    """
    list_display = ['task', 'reminder_date', 'is_sent', 'sent_at', 'created_at']
    list_filter = ['is_sent', 'reminder_date', 'created_at']
    search_fields = ['task__title']
    date_hierarchy = 'reminder_date'
    readonly_fields = ['sent_at']
