"""
URLs خاصة بالرواتب
"""

from django.urls import path
from ..views import (
    salary_item_list, salary_item_create, salary_item_edit, salary_item_delete,
    employee_salary_item_list, employee_salary_item_create, employee_salary_item_bulk_create,
    employee_salary_item_edit, employee_salary_item_delete,
    payroll_calculate, payroll_period_create,
    payroll_period_edit, payroll_period_delete,
    payroll_entry_list, payroll_entry_detail, payroll_entry_approve, payroll_entry_reject,
    payroll_period_list
)

app_name = 'salaries'

urlpatterns = [
    # Salary items
    path('', salary_item_list, name='salary_item_list'),
    path('create/', salary_item_create, name='salary_item_create'),
    path('<int:pk>/', salary_item_edit, name='salary_item_edit'),
    path('<int:pk>/delete/', salary_item_delete, name='salary_item_delete'),
    
    # Employee salary items
    path('employee/<int:emp_id>/', employee_salary_item_list, name='employee_salary_item_list'),
    path('employee/<int:emp_id>/create/', employee_salary_item_create, name='employee_salary_item_create'),
    path('employee/bulk_create/', employee_salary_item_bulk_create, name='employee_salary_item_bulk_create'),
    path('employee/item/<int:pk>/edit/', employee_salary_item_edit, name='employee_salary_item_edit'),
    path('employee/item/<int:pk>/delete/', employee_salary_item_delete, name='employee_salary_item_delete'),
    
    # Payroll
    path('payroll/calculate/', payroll_calculate, name='payroll_calculate'),
    path('payroll/period/create/', payroll_period_create, name='payroll_period_create'),
    path('payroll/period/<int:period_id>/edit/', payroll_period_edit, name='payroll_period_edit'),
    path('payroll/period/<int:period_id>/delete/', payroll_period_delete, name='payroll_period_delete'),
    path('payroll/entry/list/', payroll_entry_list, name='payroll_entry_list'),
    path('payroll/entry/<int:entry_id>/detail/', payroll_entry_detail, name='payroll_entry_detail'),
    path('payroll/entry/<int:entry_id>/approve/', payroll_entry_approve, name='payroll_entry_approve'),
    path('payroll/entry/<int:entry_id>/reject/', payroll_entry_reject, name='payroll_entry_reject'),
    path('payroll/period/list/', payroll_period_list, name='payroll_period_list'),
]