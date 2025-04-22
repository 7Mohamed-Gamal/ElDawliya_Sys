from django.contrib import admin
from .models import Task, TaskStep

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['description', 'meeting', 'assigned_to', 'created_by', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'created_by', 'assigned_to', 'meeting']
    search_fields = ['description']
    date_hierarchy = 'start_date'
    list_editable = ['status']

@admin.register(TaskStep)
class TaskStepAdmin(admin.ModelAdmin):
    list_display = ['task', 'description', 'date']
    list_filter = ['task', 'date']
    search_fields = ['description']
