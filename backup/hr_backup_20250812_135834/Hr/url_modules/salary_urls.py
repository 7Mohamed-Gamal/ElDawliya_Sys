"""
URLs for Salary, Payroll, and Salary Components.
"""

from django.urls import path
from ..views import salary_views

app_name = 'salary'

# Refactored and simplified URL structure for salaries and payroll.

urlpatterns = [
    # Salary Items (e.g., Basic, Housing Allowance)
    path('items/', salary_views.salary_item_list, name='item_list'),
    path('items/create/', salary_views.salary_item_create, name='item_create'),
    path('items/<int:pk>/edit/', salary_views.salary_item_edit, name='item_edit'),
    # The delete view for salary items was missing, let's add it.
    # path('items/<int:pk>/delete/', salary_views.salary_item_delete, name='item_delete'),

    # Employee Salary Assignments (linking items to employees)
    path('employee-salaries/', salary_views.employee_salary_item_list, name='employee_salary_list'),
    path('employee-salaries/assign/', salary_views.employee_salary_item_create, name='employee_salary_assign'),
    path('employee-salaries/assign-bulk/', salary_views.employee_salary_item_bulk_create, name='employee_salary_assign_bulk'),
    # path('employee-salaries/<int:pk>/edit/', salary_views.employee_salary_item_edit, name='employee_salary_edit'),
    # path('employee-salaries/<int:pk>/delete/', salary_views.employee_salary_item_delete, name='employee_salary_delete'),

    # Payroll Periods (e.g., January 2024)
    path('periods/', salary_views.payroll_period_list, name='period_list'),
    path('periods/create/', salary_views.payroll_period_create, name='period_create'),
    # path('periods/<int:pk>/edit/', salary_views.payroll_period_edit, name='period_edit'),
    # path('periods/<int:pk>/delete/', salary_views.payroll_period_delete, name='period_delete'),

    # Payroll Processing and Entries
    path('run-payroll/', salary_views.payroll_calculate, name='run_payroll'),
    path('entries/', salary_views.payroll_entry_list, name='entry_list'),
    path('entries/<int:pk>/', salary_views.payroll_entry_detail, name='entry_detail'),
]
