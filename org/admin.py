from django.contrib import admin
from .models import Branch, Department, Job

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """BranchAdmin class"""
    list_display = ('branch_id', 'branch_name', 'company', 'phone', 'is_active')
    search_fields = ('branch_name', 'phone')
    list_filter = ('is_active', 'company')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """DepartmentAdmin class"""
    list_display = ('dept_id', 'dept_name', 'branch', 'is_active')
    search_fields = ('dept_name',)
    list_filter = ('is_active', 'branch')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """JobAdmin class"""
    list_display = ('job_id', 'job_title', 'job_level', 'is_active')
    search_fields = ('job_title',)
    list_filter = ('is_active',)

# Register your models here.
