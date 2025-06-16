from django.urls import path, include

# Gradually expanding version - testing imports
from .views.employee_views import (
    dashboard, employee_list, employee_create, employee_detail,
    employee_edit, employee_delete, employee_search, employee_print,
    employee_detail_view, employee_dashboard_simple, employee_export,
    employee_list_ajax
)
from .views.department_views_updated import (
    department_list, department_create, department_edit,
    department_delete, department_performance, department_detail
)
from .views.job_views import job_list, job_create, job_detail, job_edit, job_delete, get_next_job_code
from .views.salary_views import (
    salary_item_list, salary_item_create, salary_item_edit, salary_item_delete,
    employee_salary_item_list, employee_salary_item_create, employee_salary_item_bulk_create,
    employee_salary_item_edit, employee_salary_item_delete,
    payroll_calculate, payroll_period_create,
    payroll_period_edit, payroll_period_delete,
    payroll_entry_list, payroll_entry_detail, payroll_entry_approve, payroll_entry_reject,
    payroll_period_list
)
from .views.report_views import (
    report_list, report_detail, monthly_salary_report, employee_report
)
from .views.analytics_views import (
    analytics_dashboard, analytics_chart
)
from .views.org_chart_views import (
    org_chart, org_chart_data, department_org_chart, employee_hierarchy
)
from .views.alert_views import alert_list
from .views.note_views import (
    employee_notes_dashboard, employee_notes_create, employee_search_ajax,
    employee_notes_list, employee_note_detail, employee_note_edit,
    employee_note_delete, employee_notes_reports
)
from .views import update_data

app_name = 'Hr'

# Employee patterns
employee_patterns = [
    path('', employee_list, name='list'),
    path('ajax/', employee_list_ajax, name='list_ajax'),
    path('create/', employee_create, name='create'),
    path('<int:emp_id>/', employee_detail, name='detail'),
    path('<int:emp_id>/edit/', employee_edit, name='edit'),
    path('<int:emp_id>/delete/', employee_delete, name='delete'),
    path('<int:emp_id>/print/', employee_print, name='print'),
    path('search/', employee_search, name='employee_search'),
    path('export/', employee_export, name='export'),
]

# Department patterns
department_patterns = [
    path('', department_list, name='list'),
    path('create/', department_create, name='create'),
    path('<int:dept_code>/', department_detail, name='detail'),
    path('<int:dept_code>/edit/', department_edit, name='edit'),
    path('<int:dept_code>/delete/', department_delete, name='delete'),
    path('<int:dept_code>/performance/', department_performance, name='performance'),
]

# Job patterns
job_patterns = [
    path('', job_list, name='list'),
    path('create/', job_create, name='create'),
    path('get_next_job_code/', get_next_job_code, name='get_next_job_code'),
    path('<int:jop_code>/', job_detail, name='detail'),
    path('<int:jop_code>/edit/', job_edit, name='edit'),
    path('<int:jop_code>/delete/', job_delete, name='delete'),
]

# Salary patterns
salary_patterns = [
    path('items/', salary_item_list, name='salary_item_list'),
    path('items/create/', salary_item_create, name='salary_item_create'),
    path('items/<int:pk>/edit/', salary_item_edit, name='salary_item_edit'),
    path('items/<int:pk>/delete/', salary_item_delete, name='salary_item_delete'),

    path('employee-items/', employee_salary_item_list, name='employee_salary_item_list'),
    path('employee-items/create/', employee_salary_item_create, name='employee_salary_item_create'),
    path('employee-items/bulk-create/', employee_salary_item_bulk_create, name='employee_salary_item_bulk_create'),
    path('employee-items/<int:pk>/edit/', employee_salary_item_edit, name='employee_salary_item_edit'),
    path('employee-items/<int:pk>/delete/', employee_salary_item_delete, name='employee_salary_item_delete'),

    path('calculate/', payroll_calculate, name='payroll_calculate'),
    path('periods/', payroll_period_list, name='payroll_period_list'),
    path('periods/create/', payroll_period_create, name='payroll_period_create'),
    path('periods/<int:pk>/edit/', payroll_period_edit, name='payroll_period_edit'),
    path('periods/<int:pk>/delete/', payroll_period_delete, name='payroll_period_delete'),

    path('entries/', payroll_entry_list, name='payroll_entry_list'),
    path('entries/<int:pk>/', payroll_entry_detail, name='payroll_entry_detail'),
    path('entries/<int:pk>/approve/', payroll_entry_approve, name='payroll_entry_approve'),
    path('entries/<int:pk>/reject/', payroll_entry_reject, name='payroll_entry_reject'),
]

# Note patterns
note_patterns = [
    path('', employee_notes_dashboard, name='dashboard'),
    path('create/', employee_notes_create, name='create'),
    path('search/ajax/', employee_search_ajax, name='employee_search_ajax'),
    path('employee/<str:employee_id>/', employee_notes_list, name='employee_notes'),
    path('note/<int:note_id>/', employee_note_detail, name='detail'),
    path('note/<int:note_id>/edit/', employee_note_edit, name='edit'),
    path('note/<int:note_id>/delete/', employee_note_delete, name='delete'),
    path('reports/', employee_notes_reports, name='reports'),
]

urlpatterns = [
    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard_simple/', employee_dashboard_simple, name='dashboard_simple'),

    # Include patterns for each section
    path('employees/', include((employee_patterns, 'employees'))),
    path('employees/detail_view/', employee_detail_view, name='detail_view'),
    path('departments/', include((department_patterns, 'departments'))),
    path('jobs/', include((job_patterns, 'jobs'))),
    path('salaries/', include((salary_patterns, 'salaries'))),
    path('notes/', include((note_patterns, 'notes'))),

    # Direct salary item URLs (for backward compatibility)
    path('salary_items/', salary_item_list, name='salary_item_list'),
    path('salary_items/create/', salary_item_create, name='salary_item_create'),
    path('salary_items/<int:pk>/edit/', salary_item_edit, name='salary_item_edit'),
    path('salary_items/<int:pk>/delete/', salary_item_delete, name='salary_item_delete'),

    # Employee salary items
    path('employee_salary_items/', employee_salary_item_list, name='employee_salary_item_list'),
    path('employee_salary_items/create/', employee_salary_item_create, name='employee_salary_item_create'),
    path('employee_salary_items/bulk_create/', employee_salary_item_bulk_create, name='employee_salary_item_bulk_create'),
    path('employee_salary_items/<int:pk>/edit/', employee_salary_item_edit, name='employee_salary_item_edit'),
    path('employee_salary_items/<int:pk>/delete/', employee_salary_item_delete, name='employee_salary_item_delete'),

    # Payroll periods
    path('payroll_periods/', payroll_period_list, name='payroll_period_list'),
    path('payroll_periods/create/', payroll_period_create, name='payroll_period_create'),
    path('payroll_periods/<int:pk>/edit/', payroll_period_edit, name='payroll_period_edit'),
    path('payroll_periods/<int:pk>/delete/', payroll_period_delete, name='payroll_period_delete'),

    # Payroll calculation
    path('payrolls/calculate/', payroll_calculate, name='payroll_calculate'),
    path('payrolls/entries/', payroll_entry_list, name='payroll_entry_list'),
    path('payrolls/entries/<int:pk>/', payroll_entry_detail, name='payroll_entry_detail'),
    path('payrolls/entries/<int:pk>/approve/', payroll_entry_approve, name='payroll_entry_approve'),
    path('payrolls/entries/<int:pk>/reject/', payroll_entry_reject, name='payroll_entry_reject'),

    # Reports
    path('reports/', include((
        [
            path('', report_list, name='list'),
            path('monthly_salary/', monthly_salary_report, name='monthly_salary_report'),
            path('monthly_salary/print/', monthly_salary_report, name='monthly_salary_print'),
            path('employees/', employee_report, name='employee_report'),
            path('<str:report_type>/', report_detail, name='report_detail'),
        ], 'reports'
    ))),

    # Alerts
    path('alerts/', include((
        [
            path('', alert_list, name='list'),
        ], 'alerts'
    ))),

    # Analytics
    path('analytics/', include((
        [
            path('', analytics_dashboard, name='dashboard'),
            path('<str:chart_type>/', analytics_chart, name='chart'),
        ], 'analytics'
    ))),

    # Org Chart
    path('org_chart/', include((
        [
            path('', org_chart, name='view'),
            path('data/', org_chart_data, name='data'),
            path('department/<int:dept_code>/', department_org_chart, name='department'),
            path('employee/<int:emp_id>/', employee_hierarchy, name='employee'),
        ], 'org_chart'
    ))),

    # Root redirect to employee list for backward compatibility
    path('', employee_list, name='list'),
    path('update-data/', update_data, name='update_data'),
]
