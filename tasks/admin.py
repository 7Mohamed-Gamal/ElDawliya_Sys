from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Task, TaskStep

class TaskStepInline(admin.TabularInline):
    model = TaskStep
    extra = 1
    fields = ['description', 'date']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['description', 'meeting', 'assigned_to', 'created_by', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'created_by', 'assigned_to', 'meeting']
    search_fields = ['description', 'assigned_to__username', 'created_by__username']
    date_hierarchy = 'start_date'
    list_editable = ['status']
    inlines = [TaskStepInline]
    fieldsets = (
        (_('معلومات المهمة'), {
            'fields': ('description', 'status')
        }),
        (_('الأشخاص'), {
            'fields': ('assigned_to', 'created_by')
        }),
        (_('التواريخ'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('الاجتماع'), {
            'fields': ('meeting',)
        }),
    )
    readonly_fields = ['created_by']

    def save_model(self, request, obj, form, change):
        if not change:  # إذا كان إنشاء جديد
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        # السماح للمستخدم بتعديل المهام التي أنشأها أو المهام المسندة إليه
        if obj is not None and (obj.created_by == request.user or obj.assigned_to == request.user or request.user.is_superuser):
            return True
        return super().has_change_permission(request, obj)

@admin.register(TaskStep)
class TaskStepAdmin(admin.ModelAdmin):
    list_display = ['task', 'description', 'date']
    list_filter = ['task__status', 'date']
    search_fields = ['description', 'task__description']
    date_hierarchy = 'date'

    def has_change_permission(self, request, obj=None):
        # السماح للمستخدم بتعديل خطوات المهام التي أنشأها أو المهام المسندة إليه
        if obj is not None and (obj.task.created_by == request.user or obj.task.assigned_to == request.user or request.user.is_superuser):
            return True
        return super().has_change_permission(request, obj)
