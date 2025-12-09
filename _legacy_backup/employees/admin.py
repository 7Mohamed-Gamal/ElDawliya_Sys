from django.contrib import admin
from .models import Employee, EmployeeBankAccount, EmployeeDocument

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """EmployeeAdmin class"""
    list_display = ('emp_id', 'emp_code', 'first_name', 'last_name', 'job', 'dept', 'branch', 'emp_status')
    search_fields = ('emp_code', 'first_name', 'last_name', 'email', 'mobile')
    list_filter = ('emp_status', 'dept', 'branch')

@admin.register(EmployeeBankAccount)
class EmployeeBankAccountAdmin(admin.ModelAdmin):
    """EmployeeBankAccountAdmin class"""
    list_display = ('acc_id', 'emp', 'bank', 'account_no', 'iban')
    search_fields = ('account_no', 'iban')

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    """EmployeeDocumentAdmin class"""
    list_display = ('doc_id', 'emp', 'doc_type', 'doc_name', 'upload_date')
    search_fields = ('doc_type', 'doc_name')

# Register your models here.
