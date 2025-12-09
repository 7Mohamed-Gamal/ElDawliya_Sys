from django.contrib import admin
from .models import DisciplinaryAction

@admin.register(DisciplinaryAction)
class DisciplinaryActionAdmin(admin.ModelAdmin):
    """DisciplinaryActionAdmin class"""
    list_display = ('action_id', 'emp', 'action_type', 'action_date', 'severity_level')
    search_fields = ('emp__emp_code', 'action_type', 'reason')
    list_filter = ('action_type', 'severity_level')
    date_hierarchy = 'action_date'
