from django.contrib import admin
from .models import WorkflowStep, WorkflowInstance

@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    """WorkflowStepAdmin class"""
    list_display = ('step_id', 'step_name', 'sequence_no', 'role_id')
    search_fields = ('step_name',)

@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    """WorkflowInstanceAdmin class"""
    list_display = ('instance_id', 'step', 'emp', 'status', 'action_date')
    list_filter = ('status',)
    date_hierarchy = 'action_date'
