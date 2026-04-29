from django.contrib import admin
from .models import Branch, Department, Job

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """BranchAdmin class"""
    list_display = ('branch_id', 'branch_name', 'company', 'phone', 'is_active')
    search_fields = ('branch_name', 'phone')
    list_filter = ('is_active', 'company')

# Note: Department admin is already registered in core/admin/
# The Department model is now imported from core.models.hr

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """JobAdmin class"""
    list_display = ('job_id', 'job_title', 'job_level', 'is_active')
    search_fields = ('job_title',)
    list_filter = ('is_active',)

# Register your models here.
