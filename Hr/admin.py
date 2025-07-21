from django.contrib import admin
from django.utils.translation import gettext_lazy as _

admin.site.site_header = _('نظام الدولية للموارد البشرية')
admin.site.site_title = _('إدارة الموارد البشرية')
admin.site.index_title = _('لوحة تحكم الموارد البشرية')

from Hr.models.core import Company, Branch, Department, JobPosition
from Hr.models.employee import Employee
from Hr.models.leave import LeaveType, LeaveRequest
from Hr.models.payroll import SalaryComponent

# Core Models
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'tax_id', 'registration_number', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'tax_id', 'registration_number']

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'company', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'code']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'company', 'manager', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'code']

@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'department', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['title', 'code']

# Employee Models
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'department', 'position', 'status']
    list_filter = ['status', 'department', 'position']
    search_fields = ['employee_id', 'first_name', 'last_name', 'national_id']
    date_hierarchy = 'join_date'

# Payroll Models
@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'component_type', 'is_active']
    list_filter = ['component_type', 'is_active']
    search_fields = ['name', 'code']

# Leave Models
@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_paid', 'is_active']
    list_filter = ['is_paid', 'is_active']
    search_fields = ['name', 'code']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['leave_type', 'status']
    search_fields = ['employee__full_name']
    date_hierarchy = 'start_date'
