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

    fieldsets = (
        (_('معلومات التصنيف'), {
            'fields': ('name', 'description')
        }),
        (_('التنسيق'), {
            'fields': ('color', 'icon')
        }),
    )

    def has_delete_permission(self, request, obj=None):
        # منع حذف التصنيفات المستخدمة في المهام
        if obj and obj.tasks.exists():
            return False
        return super().has_delete_permission(request, obj)


class TaskStepInline(admin.TabularInline):
    """
    عرض خطوات المهمة كجدول داخل نموذج المهمة
    """
    model = TaskStep
    extra = 1
    fields = ['description', 'completed', 'completion_date', 'created_by']
    readonly_fields = ['completion_date', 'created_by']

    def has_delete_permission(self, request, obj=None):
        # السماح بحذف الخطوات فقط للمشرفين أو منشئ المهمة
        if not request.user.is_superuser and obj and obj.task.created_by != request.user:
            return False
        return super().has_delete_permission(request, obj)


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
    list_filter = ['status', 'priority', 'is_private', 'created_at', 'due_date', 'category']
    search_fields = ['title', 'description', 'created_by__username', 'assigned_to__username']
    date_hierarchy = 'due_date'
    readonly_fields = ['completion_date', 'created_at', 'updated_at', 'created_by']
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

    def save_model(self, request, obj, form, change):
        if not change:  # إذا كان إنشاء جديد
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, TaskStep) and not instance.pk:  # إذا كانت خطوة جديدة
                instance.created_by = request.user
            instance.save()
        formset.save_m2m()

    def has_change_permission(self, request, obj=None):
        # السماح للمستخدم بتعديل المهام التي أنشأها أو المهام المسندة إليه
        if obj is not None and (obj.created_by == request.user or obj.assigned_to == request.user or request.user.is_superuser):
            return True
        return super().has_change_permission(request, obj)


@admin.register(TaskStep)
class TaskStepAdmin(admin.ModelAdmin):
    """
    إدارة خطوات المهام في لوحة الإدارة
    """
    list_display = ['task', 'description', 'completed', 'completion_date', 'created_by', 'created_at']
    list_filter = ['completed', 'created_at', 'completion_date']
    search_fields = ['description', 'task__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['completion_date', 'created_by', 'created_at']

    fieldsets = [
        (_('معلومات الخطوة'), {
            'fields': ['task', 'description', 'completed', 'completion_date']
        }),
        (_('المستخدم'), {
            'fields': ['created_by', 'created_at']
        }),
    ]

    def save_model(self, request, obj, form, change):
        if not change:  # إذا كان إنشاء جديد
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        # السماح للمستخدم بتعديل خطوات المهام التي أنشأها أو المهام المسندة إليه
        if obj is not None and (obj.created_by == request.user or obj.task.created_by == request.user or obj.task.assigned_to == request.user or request.user.is_superuser):
            return True
        return super().has_change_permission(request, obj)


@admin.register(TaskReminder)
class TaskReminderAdmin(admin.ModelAdmin):
    """
    إدارة تذكيرات المهام في لوحة الإدارة
    """
    list_display = ['task', 'reminder_date', 'is_sent', 'sent_at', 'created_at']
    list_filter = ['is_sent', 'reminder_date', 'created_at']
    search_fields = ['task__title']
    date_hierarchy = 'reminder_date'
    readonly_fields = ['sent_at', 'created_at']

    fieldsets = [
        (_('معلومات التذكير'), {
            'fields': ['task', 'reminder_date']
        }),
        (_('حالة الإرسال'), {
            'fields': ['is_sent', 'sent_at', 'created_at']
        }),
    ]

    def has_change_permission(self, request, obj=None):
        # السماح للمستخدم بتعديل تذكيرات المهام التي أنشأها أو المهام المسندة إليه
        if obj is not None and (obj.task.created_by == request.user or obj.task.assigned_to == request.user or request.user.is_superuser):
            return True
        return super().has_change_permission(request, obj)
