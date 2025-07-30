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

    # Job patterns
    path('jobs/', job_list, name='job_list'),
    path('jobs/create/', job_create, name='job_create'),
    path('jobs/<int:jop_code>/', job_detail, name='job_detail'),
    path('jobs/<int:jop_code>/edit/', job_edit, name='job_edit'),
    path('jobs/<int:jop_code>/delete/', job_delete, name='job_delete'),
    path('jobs/next_code/', get_next_job_code, name='get_next_job_code'),

    # Salary patterns with namespace
    path('salaries/', include('Hr.url_modules.salary_urls', namespace='salaries')),

    # Legacy Report patterns (temporarily disabled)
    # path('reports/', report_list, name='report_list'),
    # path('reports/<str:report_type>/', report_detail, name='report_detail'),
    # path('reports/monthly_salary/', monthly_salary_report, name='monthly_salary_report'),
    # path('reports/employee_report/', employee_report, name='employee_report'),

    # Analytics patterns
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('analytics/chart/', analytics_chart, name='analytics_chart'),

    # Org Chart patterns
    path('org_chart/', org_chart, name='org_chart'),
    path('org_chart/data/', org_chart_data, name='org_chart_data'),
    path('org_chart/department/<int:dept_id>/', department_org_chart, name='department_org_chart'),
    path('org_chart/employee/<int:emp_id>/', employee_hierarchy, name='employee_hierarchy'),

    # Alert patterns
    path('alerts/', alert_list, name='alert_list'),

    # Note patterns
    path('notes/', employee_notes_dashboard, name='employee_notes_dashboard'),
    path('notes/create/', employee_notes_create, name='employee_notes_create'),
    path('notes/search/ajax/', employee_search_ajax, name='employee_search_ajax'),
    path('notes/list/', employee_notes_list, name='employee_notes_list'),
    path('notes/<int:note_id>/', employee_note_detail, name='employee_note_detail'),
    path('notes/<int:note_id>/edit/', employee_note_edit, name='employee_note_edit'),
    path('notes/<int:note_id>/delete/', employee_note_delete, name='employee_note_delete'),
    path('notes/reports/', employee_notes_reports, name='employee_notes_reports'),

    # Attendance patterns
    path('attendance/rules/', attendance_rule_list, name='attendance_rule_list'),
    path('attendance/rules/create/', attendance_rule_create, name='attendance_rule_create'),
    path('attendance/rules/<int:rule_id>/edit/', attendance_rule_edit, name='attendance_rule_edit'),
    path('attendance/rules/<int:rule_id>/delete/', attendance_rule_delete, name='attendance_rule_delete'),
    path('attendance/employee-rules/', employee_attendance_rule_list, name='employee_attendance_rule_list'),
    path('attendance/employee-rules/create/', employee_attendance_rule_create, name='employee_attendance_rule_create'),
    path('attendance/employee-rules/<int:rule_id>/edit/', employee_attendance_rule_edit, name='employee_attendance_rule_edit'),
    path('attendance/employee-rules/<int:rule_id>/delete/', employee_attendance_rule_delete, name='employee_attendance_rule_delete'),
    path('attendance/employee-rules/bulk-create/', employee_attendance_rule_bulk_create, name='employee_attendance_rule_bulk_create'),
    path('attendance/holidays/', official_holiday_list, name='official_holiday_list'),
    path('attendance/holidays/create/', official_holiday_create, name='official_holiday_create'),
    path('attendance/holidays/<int:holiday_id>/edit/', official_holiday_edit, name='official_holiday_edit'),
    path('attendance/holidays/<int:holiday_id>/delete/', official_holiday_delete, name='official_holiday_delete'),
    path('attendance/machines/', attendance_machine_list, name='attendance_machine_list'),
    path('attendance/machines/create/', attendance_machine_create, name='attendance_machine_create'),
    path('attendance/machines/<int:machine_id>/edit/', attendance_machine_edit, name='attendance_machine_edit'),
    path('attendance/machines/<int:machine_id>/delete/', attendance_machine_delete, name='attendance_machine_delete'),
    path('attendance/records/', attendance_record_list, name='attendance_record_list'),
    path('attendance/records/create/', attendance_record_create, name='attendance_record_create'),
    path('attendance/records/<int:record_id>/edit/', attendance_record_edit, name='attendance_record_edit'),
    path('attendance/records/<int:record_id>/delete/', attendance_record_delete, name='attendance_record_delete'),
    path('attendance/summary/', attendance_summary_list, name='attendance_summary_list'),
    path('attendance/zk-device/', zk_device_connection, name='zk_device_connection'),
    path('attendance/fetch-data/', fetch_attendance_data, name='fetch_attendance_data'),
    path('attendance/ajax/test-zk-connection/', test_zk_connection, name='test_zk_connection'),
    path('attendance/ajax/fetch-zk-records/', fetch_zk_records_ajax, name='fetch_zk_records_ajax'),
    path('attendance/ajax/save-zk-records/', save_zk_records_to_db, name='save_zk_records_to_db'),

    # Update data
    path('update_data/', update_data, name='update_data'),
    
    # نظام التقارير الشامل
    path('reports/', include('Hr.report_urls')),
    
    # نظام مراقبة النظام
    path('monitoring/', include('Hr.url_modules.monitoring_urls', namespace='monitoring')),
]