from django.urls import path, include

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
    path('', department_list, name='department_list'),
    path('create/', department_create, name='department_create'),
    path('<int:dept_id>/', department_detail, name='department_detail'),
    path('<int:dept_id>/edit/', department_edit, name='department_edit'),
    path('<int:dept_id>/delete/', department_delete, name='department_delete'),
    path('<int:dept_id>/performance/', department_performance, name='department_performance'),
]

# Job patterns
job_patterns = [
    path('', job_list, name='job_list'),
    path('create/', job_create, name='job_create'),
    path('<int:job_id>/', job_detail, name='job_detail'),
    path('<int:job_id>/edit/', job_edit, name='job_edit'),
    path('<int:job_id>/delete/', job_delete, name='job_delete'),
    path('next_code/', get_next_job_code, name='get_next_job_code'),
]

# Salary patterns
salary_patterns = [
    path('', salary_item_list, name='salary_item_list'),
    path('create/', salary_item_create, name='salary_item_create'),
    path('<int:item_id>/', salary_item_edit, name='salary_item_edit'),
    path('<int:item_id>/delete/', salary_item_delete, name='salary_item_delete'),
    path('employee/<int:emp_id>/', employee_salary_item_list, name='employee_salary_item_list'),
    path('employee/<int:emp_id>/create/', employee_salary_item_create, name='employee_salary_item_create'),
    path('employee/bulk_create/', employee_salary_item_bulk_create, name='employee_salary_item_bulk_create'),
    path('employee/<int:emp_id>/<int:item_id>/edit/', employee_salary_item_edit, name='employee_salary_item_edit'),
    path('employee/<int:emp_id>/<int:item_id>/delete/', employee_salary_item_delete, name='employee_salary_item_delete'),
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

# Report patterns
report_patterns = [
    path('', report_list, name='report_list'),
    path('<int:report_id>/', report_detail, name='report_detail'),
    path('monthly_salary/', monthly_salary_report, name='monthly_salary_report'),
    path('employee_report/', employee_report, name='employee_report'),
]

# Analytics patterns
analytics_patterns = [
    path('', analytics_dashboard, name='analytics_dashboard'),
    path('chart/', analytics_chart, name='analytics_chart'),
]

# Org Chart patterns
org_chart_patterns = [
    path('', org_chart, name='org_chart'),
    path('data/', org_chart_data, name='org_chart_data'),
    path('department/<int:dept_id>/', department_org_chart, name='department_org_chart'),
    path('employee/<int:emp_id>/', employee_hierarchy, name='employee_hierarchy'),
]

# Alert patterns
alert_patterns = [
    path('', alert_list, name='alert_list'),
]

# Note patterns
note_patterns = [
    path('', employee_notes_dashboard, name='employee_notes_dashboard'),
    path('create/', employee_notes_create, name='employee_notes_create'),
    path('search/ajax/', employee_search_ajax, name='employee_search_ajax'),
    path('list/', employee_notes_list, name='employee_notes_list'),
    path('<int:note_id>/', employee_note_detail, name='employee_note_detail'),
    path('<int:note_id>/edit/', employee_note_edit, name='employee_note_edit'),
    path('<int:note_id>/delete/', employee_note_delete, name='employee_note_delete'),
    path('reports/', employee_notes_reports, name='employee_notes_reports'),
]

urlpatterns = [
    path('employees/', include((employee_patterns, app_name), namespace='employees')),
    path('departments/', include((department_patterns, app_name), namespace='departments')),
    path('jobs/', include((job_patterns, app_name), namespace='jobs')),
    path('salaries/', include((salary_patterns, app_name), namespace='salaries')),
    path('reports/', include((report_patterns, app_name), namespace='reports')),
    path('analytics/', include((analytics_patterns, app_name), namespace='analytics')),
    path('org_chart/', include((org_chart_patterns, app_name), namespace='org_chart')),
    path('alerts/', include((alert_patterns, app_name), namespace='alerts')),
    path('notes/', include((note_patterns, app_name), namespace='notes')),
]
