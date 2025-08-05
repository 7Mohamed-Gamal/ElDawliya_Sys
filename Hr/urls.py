from django.urls import path, include

# Legacy views (existing)
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
# Import salary views from main views module (temporarily using placeholders)
from .views import (
    salary_item_list, salary_item_create, salary_item_edit, salary_item_delete,
    employee_salary_item_list, employee_salary_item_create, employee_salary_item_bulk_create,
    employee_salary_item_edit, employee_salary_item_delete,
    payroll_calculate, payroll_period_create,
    payroll_period_edit, payroll_period_delete,
    payroll_entry_list, payroll_entry_detail, payroll_entry_approve, payroll_entry_reject,
    payroll_period_list
)
# Temporarily disabled due to model conflicts
# from .views.report_views import (
#     report_list, report_detail, monthly_salary_report, employee_report
# )
# Import placeholder functions instead
from .views import (
    report_list, report_detail, monthly_salary_report, employee_report
)
# Temporarily disabled due to attendance model conflicts
# from .views.analytics_views import (
#     analytics_dashboard, analytics_chart
# )
# Import placeholder functions instead
from .views import (
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
from .views.attendance_views import (
    attendance_rule_list, attendance_rule_create, attendance_rule_edit, attendance_rule_delete,
    employee_attendance_rule_list, employee_attendance_rule_create, employee_attendance_rule_edit,
    employee_attendance_rule_delete, employee_attendance_rule_bulk_create,
    official_holiday_list, official_holiday_create, official_holiday_edit, official_holiday_delete,
    attendance_machine_list, attendance_machine_create, attendance_machine_edit, attendance_machine_delete,
    attendance_record_list, attendance_record_create, attendance_record_edit, attendance_record_delete,
    fetch_attendance_data, attendance_summary_list, zk_device_connection,
    test_zk_connection, fetch_zk_records_ajax, save_zk_records_to_db
)

from .views import update_data

app_name = 'Hr'

urlpatterns = [
    # Main dashboard
    path('', dashboard, name='dashboard'),
    path('dashboard/', dashboard, name='dashboard_alt'),

    # Employee patterns with namespace
    path('employees/', include('Hr.url_modules.employee_urls', namespace='employees')),

    # Department patterns with namespace
    path('departments/', include('Hr.url_modules.department_urls', namespace='departments')),
    
    # Department patterns with new namespace (alias)
    path('departments_new/', include('Hr.url_modules.departments_new_urls', namespace='departments_new')),

    # Job patterns with namespace
    path('jobs/', include('Hr.url_modules.job_urls', namespace='jobs')),

    # Salary patterns with namespace
    path('salaries/', include('Hr.url_modules.salary_urls', namespace='salaries')),
    
    # Salary components patterns with namespace
    path('salary-components/', include('Hr.url_modules.salary_component_urls', namespace='salary_components')),

    # Search patterns with namespace
    path('search/', include('Hr.url_modules.search_urls', namespace='search')),
    
    # Reports patterns with namespace
    path('reports/', include('Hr.url_modules.reports_urls', namespace='reports')),
    
    # Notifications patterns with namespace
    path('notifications/', include('Hr.url_modules.notification_urls', namespace='notifications')),
    
    # Integrations patterns with namespace
    path('integrations/', include('Hr.url_modules.integration_urls', namespace='integrations')),

    # Analytics patterns with namespace
    path('analytics/', include('Hr.url_modules.analytics_urls', namespace='analytics')),

    # Org Chart patterns with namespace
    path('org_chart/', include('Hr.url_modules.org_chart_urls', namespace='org_chart')),

    # Alert patterns with namespace
    path('alerts/', include('Hr.url_modules.alerts_urls', namespace='alerts')),

    # Note patterns with namespace
    path('notes/', include('Hr.url_modules.notes_urls', namespace='notes')),

    # Attendance patterns with namespace
    path('attendance/', include('Hr.url_modules.attendance_urls', namespace='attendance')),

    # Leave Requests patterns with namespace
    path('leave_requests/', include('Hr.url_modules.leave_requests_urls', namespace='leave_requests')),
    
    # Leave Balances patterns with namespace
    path('leave_balances/', include('Hr.url_modules.leave_balances_urls', namespace='leave_balances')),
    
    # Employee Training patterns with namespace
    path('employee_training/', include('Hr.url_modules.employee_training_urls', namespace='employee_training')),

    # Update data
    path('update_data/', update_data, name='update_data'),
    
    # نظام مراقبة النظام
    path('monitoring/', include('Hr.url_modules.monitoring_urls', namespace='monitoring')),
]