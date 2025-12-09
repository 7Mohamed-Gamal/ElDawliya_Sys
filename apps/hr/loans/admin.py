from django.contrib import admin
from .models import LoanType, EmployeeLoan, LoanInstallment

@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    """LoanTypeAdmin class"""
    list_display = ('loan_type_id', 'type_name', 'max_amount', 'max_installments', 'interest_rate')
    search_fields = ('type_name',)

@admin.register(EmployeeLoan)
class EmployeeLoanAdmin(admin.ModelAdmin):
    """EmployeeLoanAdmin class"""
    list_display = ('loan_id', 'emp', 'loan_type', 'request_amount', 'approved_amount', 'status')
    list_filter = ('status', 'loan_type')
    search_fields = ('emp__emp_code',)

@admin.register(LoanInstallment)
class LoanInstallmentAdmin(admin.ModelAdmin):
    """LoanInstallmentAdmin class"""
    list_display = ('installment_id', 'loan', 'due_date', 'paid_date', 'amount', 'status')
    list_filter = ('status',)
    date_hierarchy = 'due_date'
