from django.contrib import admin
from .models import EmployeeSalary, PayrollRun, PayrollDetail

@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    """EmployeeSalaryAdmin class"""
    list_display = ('salary_id', 'emp', 'basic_salary', 'currency', 'is_current')
    search_fields = ('emp__emp_code',)
    list_filter = ('is_current', 'currency')

@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    """PayrollRunAdmin class"""
    list_display = ('run_id', 'run_date', 'month_year', 'status', 'confirmed_by')
    list_filter = ('status',)

@admin.register(PayrollDetail)
class PayrollDetailAdmin(admin.ModelAdmin):
    """PayrollDetailAdmin class"""
    list_display = ('payroll_detail_id', 'run', 'emp', 'net_salary', 'paid_date')
    search_fields = ('emp__emp_code',)
    date_hierarchy = 'paid_date'
