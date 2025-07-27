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

# New HRMS views - temporarily disabled due to form conflicts
# TODO: Fix form imports and re-enable
COMPANY_VIEWS_AVAILABLE = False

# Import placeholder views for features not yet implemented
from .views.core.placeholder_views import (
    # Department views (still using placeholders)
    department_list as department_list_new, department_create as department_create_new,
    department_detail as department_detail_new, department_edit as department_edit_new,
    department_delete as department_delete_new, department_hierarchy, departments_by_branch,
    department_search_ajax,
    # Job position views (still using placeholders)
    job_position_list, job_position_create, job_position_detail, job_position_edit, job_position_delete,
    positions_by_department, job_position_search_ajax
)

# If company views are not available, use placeholders
if not COMPANY_VIEWS_AVAILABLE:
    from .views.core.placeholder_views import (
        company_list, company_create, company_detail, company_edit, company_delete,
        company_toggle_status, company_dashboard, company_export, company_search_ajax, company_stats_ajax,
        branch_list, branch_create, branch_detail, branch_edit, branch_delete,
        branch_toggle_status, branches_by_company, branch_search_ajax,
    )

# Create a simple placeholder function
def placeholder_view(request, *args, **kwargs):
    from django.shortcuts import render
    return render(request, 'Hr/under_construction.html', {'title': 'تحت الإنشاء'})

# Create placeholder modules for URL patterns
class PlaceholderModule:
    def __getattr__(self, name):
        # Return the placeholder function for any attribute
        return placeholder_view

# Placeholder modules for features still under development
job_position_views = PlaceholderModule()
leave_type_views = PlaceholderModule()

try:
    from .views.employee import (
        employee_views_new, employee_document_views, employee_emergency_contact_views,
        employee_training_views
    )
except ImportError:
    # Keep the placeholder modules if import fails
    if 'employee_views_new' not in globals():
        employee_views_new = PlaceholderModule()
    if 'employee_document_views' not in globals():
        employee_document_views = PlaceholderModule()
    if 'employee_emergency_contact_views' not in globals():
        employee_emergency_contact_views = PlaceholderModule()
    if 'employee_training_views' not in globals():
        employee_training_views = PlaceholderModule()

try:
    from .views.leave import (
        leave_type_views, leave_policy_views, leave_request_views, leave_balance_views
    )
except ImportError:
    # Keep the placeholder modules if import fails
    if 'leave_type_views' not in globals():
        leave_type_views = PlaceholderModule()
    if 'leave_policy_views' not in globals():
        leave_policy_views = PlaceholderModule()
    if 'leave_request_views' not in globals():
        leave_request_views = PlaceholderModule()
    if 'leave_balance_views' not in globals():
        leave_balance_views = PlaceholderModule()

try:
    from .views.attendance import (
        work_shift_views, attendance_machine_views_new, attendance_record_views_new,
        attendance_summary_views_new, employee_shift_assignment_views
    )
except ImportError:
    # Keep the placeholder modules if import fails
    if 'work_shift_views' not in globals():
        work_shift_views = PlaceholderModule()
    if 'attendance_machine_views_new' not in globals():
        attendance_machine_views_new = PlaceholderModule()
    if 'attendance_record_views_new' not in globals():
        attendance_record_views_new = PlaceholderModule()
    if 'attendance_summary_views_new' not in globals():
        attendance_summary_views_new = PlaceholderModule()
    if 'employee_shift_assignment_views' not in globals():
        employee_shift_assignment_views = PlaceholderModule()

try:
    from .views.payroll import (
        salary_component_views, employee_salary_structure_views, payroll_period_views_new,
        payroll_entry_views_new, payroll_calculation_views, tax_configuration_views
    )
except ImportError:
    # Keep the placeholder modules if import fails
    if 'salary_component_views' not in globals():
        salary_component_views = PlaceholderModule()
    if 'employee_salary_structure_views' not in globals():
        employee_salary_structure_views = PlaceholderModule()
    if 'payroll_period_views_new' not in globals():
        payroll_period_views_new = PlaceholderModule()
    if 'payroll_entry_views_new' not in globals():
        payroll_entry_views_new = PlaceholderModule()
    if 'payroll_calculation_views' not in globals():
        payroll_calculation_views = PlaceholderModule()
    if 'tax_configuration_views' not in globals():
        tax_configuration_views = PlaceholderModule()

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
    path('<int:dept_code>/', department_detail, name='department_detail'),
    path('<int:dept_code>/edit/', department_edit, name='department_edit'),
    path('<int:dept_code>/delete/', department_delete, name='department_delete'),
    path('<int:dept_code>/performance/', department_performance, name='department_performance'),
]

# Job patterns
job_patterns = [
    path('', job_list, name='job_list'),
    path('create/', job_create, name='job_create'),
    path('<int:jop_code>/', job_detail, name='job_detail'),
    path('<int:jop_code>/edit/', job_edit, name='job_edit'),
    path('<int:jop_code>/delete/', job_delete, name='job_delete'),
    path('next_code/', get_next_job_code, name='get_next_job_code'),
]

# Salary patterns
salary_patterns = [
    path('', salary_item_list, name='salary_item_list'),
    path('create/', salary_item_create, name='salary_item_create'),
    path('<int:pk>/', salary_item_edit, name='salary_item_edit'),
    path('<int:pk>/delete/', salary_item_delete, name='salary_item_delete'),
    path('employee/<int:emp_id>/', employee_salary_item_list, name='employee_salary_item_list'),
    path('employee/<int:emp_id>/create/', employee_salary_item_create, name='employee_salary_item_create'),
    path('employee/bulk_create/', employee_salary_item_bulk_create, name='employee_salary_item_bulk_create'),
    path('employee/item/<int:pk>/edit/', employee_salary_item_edit, name='employee_salary_item_edit'),
    path('employee/item/<int:pk>/delete/', employee_salary_item_delete, name='employee_salary_item_delete'),
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
    path('<str:report_type>/', report_detail, name='report_detail'),
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

# Attendance patterns
attendance_patterns = [
    # Attendance Rules
    path('rules/', attendance_rule_list, name='attendance_rule_list'),
    path('rules/create/', attendance_rule_create, name='attendance_rule_create'),
    path('rules/<int:rule_id>/edit/', attendance_rule_edit, name='attendance_rule_edit'),
    path('rules/<int:rule_id>/delete/', attendance_rule_delete, name='attendance_rule_delete'),

    # Employee Attendance Rules
    path('employee-rules/', employee_attendance_rule_list, name='employee_attendance_rule_list'),
    path('employee-rules/create/', employee_attendance_rule_create, name='employee_attendance_rule_create'),
    path('employee-rules/<int:rule_id>/edit/', employee_attendance_rule_edit, name='employee_attendance_rule_edit'),
    path('employee-rules/<int:rule_id>/delete/', employee_attendance_rule_delete, name='employee_attendance_rule_delete'),
    path('employee-rules/bulk-create/', employee_attendance_rule_bulk_create, name='employee_attendance_rule_bulk_create'),

    # Official Holidays
    path('holidays/', official_holiday_list, name='official_holiday_list'),
    path('holidays/create/', official_holiday_create, name='official_holiday_create'),
    path('holidays/<int:holiday_id>/edit/', official_holiday_edit, name='official_holiday_edit'),
    path('holidays/<int:holiday_id>/delete/', official_holiday_delete, name='official_holiday_delete'),

    # Attendance Machines
    path('machines/', attendance_machine_list, name='attendance_machine_list'),
    path('machines/create/', attendance_machine_create, name='attendance_machine_create'),
    path('machines/<int:machine_id>/edit/', attendance_machine_edit, name='attendance_machine_edit'),
    path('machines/<int:machine_id>/delete/', attendance_machine_delete, name='attendance_machine_delete'),

    # Attendance Records
    path('records/', attendance_record_list, name='attendance_record_list'),
    path('records/create/', attendance_record_create, name='attendance_record_create'),
    path('records/<int:record_id>/edit/', attendance_record_edit, name='attendance_record_edit'),
    path('records/<int:record_id>/delete/', attendance_record_delete, name='attendance_record_delete'),

    # Attendance Summary
    path('summary/', attendance_summary_list, name='attendance_summary_list'),

    # ZK Device Integration
    path('zk-device/', zk_device_connection, name='zk_device_connection'),
    path('fetch-data/', fetch_attendance_data, name='fetch_attendance_data'),

    # AJAX endpoints for ZK device
    path('ajax/test-zk-connection/', test_zk_connection, name='test_zk_connection'),
    path('ajax/fetch-zk-records/', fetch_zk_records_ajax, name='fetch_zk_records_ajax'),
    path('ajax/save-zk-records/', save_zk_records_to_db, name='save_zk_records_to_db'),
]

# ==================== NEW HRMS MODULE PATTERNS ====================

# Company patterns
company_patterns = [
    path('', company_list, name='list'),
    path('create/', company_create, name='create'),
    path('<int:company_id>/', company_detail, name='detail'),
    path('<int:company_id>/edit/', company_edit, name='edit'),
    path('<int:company_id>/delete/', company_delete, name='delete'),
    path('<int:company_id>/toggle-status/', company_toggle_status, name='toggle_status'),
    path('<int:company_id>/dashboard/', company_dashboard, name='dashboard'),
    path('export/', company_export, name='export'),
    path('ajax/search/', company_search_ajax, name='search_ajax'),
    path('<int:company_id>/ajax/stats/', company_stats_ajax, name='stats_ajax'),
]

# Branch patterns
branch_patterns = [
    path('', branch_list, name='list'),
    path('create/', branch_create, name='create'),
    path('<int:branch_id>/', branch_detail, name='detail'),
    path('<int:branch_id>/edit/', branch_edit, name='edit'),
    path('<int:branch_id>/delete/', branch_delete, name='delete'),
    path('<int:branch_id>/toggle-status/', branch_toggle_status, name='toggle_status'),
    path('by-company/<int:company_id>/', branches_by_company, name='by_company'),
    path('ajax/search/', branch_search_ajax, name='search_ajax'),
]

# Enhanced Department patterns
department_new_patterns = [
    path('', department_list_new, name='list'),
    path('create/', department_create_new, name='create'),
    path('<int:department_id>/', department_detail_new, name='detail'),
    path('<int:department_id>/edit/', department_edit_new, name='edit'),
    path('<int:department_id>/delete/', department_delete_new, name='delete'),
    path('<int:department_id>/hierarchy/', department_hierarchy, name='hierarchy'),
    path('by-branch/<int:branch_id>/', departments_by_branch, name='by_branch'),
    path('ajax/search/', department_search_ajax, name='search_ajax'),
]

# Job Position patterns
job_position_patterns = [
    path('', job_position_views.job_position_list, name='list'),
    path('create/', job_position_views.job_position_create, name='create'),
    path('<int:position_id>/', job_position_views.job_position_detail, name='detail'),
    path('<int:position_id>/edit/', job_position_views.job_position_edit, name='edit'),
    path('<int:position_id>/delete/', job_position_views.job_position_delete, name='delete'),
    path('by-department/<int:department_id>/', job_position_views.positions_by_department, name='by_department'),
    path('ajax/search/', job_position_views.job_position_search_ajax, name='search_ajax'),
]

# Leave Type patterns
leave_type_patterns = [
    path('', leave_type_views.leave_type_list, name='list'),
    path('create/', leave_type_views.leave_type_create, name='create'),
    path('<int:leave_type_id>/', leave_type_views.leave_type_detail, name='detail'),
    path('<int:leave_type_id>/edit/', leave_type_views.leave_type_edit, name='edit'),
    path('<int:leave_type_id>/delete/', leave_type_views.leave_type_delete, name='delete'),
    path('<int:leave_type_id>/toggle-status/', leave_type_views.leave_type_toggle_status, name='toggle_status'),
]

# Leave Policy patterns
leave_policy_patterns = [
    path('', leave_policy_views.leave_policy_list, name='list'),
    path('create/', leave_policy_views.leave_policy_create, name='create'),
    path('<int:policy_id>/', leave_policy_views.leave_policy_detail, name='detail'),
    path('<int:policy_id>/edit/', leave_policy_views.leave_policy_edit, name='edit'),
    path('<int:policy_id>/delete/', leave_policy_views.leave_policy_delete, name='delete'),
    path('<int:policy_id>/employees/', leave_policy_views.policy_applicable_employees, name='applicable_employees'),
]

# Leave Request patterns
leave_request_patterns = [
    path('', leave_request_views.leave_request_list, name='list'),
    path('create/', leave_request_views.leave_request_create, name='create'),
    path('<int:request_id>/', leave_request_views.leave_request_detail, name='detail'),
    path('<int:request_id>/edit/', leave_request_views.leave_request_edit, name='edit'),
    path('<int:request_id>/delete/', leave_request_views.leave_request_delete, name='delete'),
    path('<int:request_id>/approve/', leave_request_views.leave_request_approve, name='approve'),
    path('<int:request_id>/reject/', leave_request_views.leave_request_reject, name='reject'),
    path('<int:request_id>/cancel/', leave_request_views.leave_request_cancel, name='cancel'),
    path('pending/', leave_request_views.pending_leave_requests, name='pending'),
    path('calendar/', leave_request_views.leave_calendar, name='calendar'),
]

# Leave Balance patterns
leave_balance_patterns = [
    path('', leave_balance_views.leave_balance_list, name='list'),
    path('employee/<int:employee_id>/', leave_balance_views.employee_leave_balance, name='employee_balance'),
    path('<int:balance_id>/adjust/', leave_balance_views.adjust_leave_balance, name='adjust'),
    path('<int:balance_id>/encash/', leave_balance_views.encash_leave_balance, name='encash'),
    path('bulk-update/', leave_balance_views.bulk_update_balances, name='bulk_update'),
    path('report/', leave_balance_views.leave_balance_report, name='report'),
]

# Work Shift patterns
work_shift_patterns = [
    path('', work_shift_views.work_shift_list, name='list'),
    path('create/', work_shift_views.work_shift_create, name='create'),
    path('<int:shift_id>/', work_shift_views.work_shift_detail, name='detail'),
    path('<int:shift_id>/edit/', work_shift_views.work_shift_edit, name='edit'),
    path('<int:shift_id>/delete/', work_shift_views.work_shift_delete, name='delete'),
    path('<int:shift_id>/employees/', work_shift_views.shift_employees, name='employees'),
]

# Attendance Machine (New) patterns
attendance_machine_new_patterns = [
    path('', attendance_machine_views_new.machine_list, name='list'),
    path('create/', attendance_machine_views_new.machine_create, name='create'),
    path('<int:machine_id>/', attendance_machine_views_new.machine_detail, name='detail'),
    path('<int:machine_id>/edit/', attendance_machine_views_new.machine_edit, name='edit'),
    path('<int:machine_id>/delete/', attendance_machine_views_new.machine_delete, name='delete'),
    path('<int:machine_id>/test-connection/', attendance_machine_views_new.test_machine_connection, name='test_connection'),
    path('<int:machine_id>/sync-users/', attendance_machine_views_new.sync_machine_users, name='sync_users'),
    path('<int:machine_id>/fetch-records/', attendance_machine_views_new.fetch_machine_records, name='fetch_records'),
]

# Salary Component patterns
salary_component_patterns = [
    path('', salary_component_views.component_list, name='list'),
    path('create/', salary_component_views.component_create, name='create'),
    path('<int:component_id>/', salary_component_views.component_detail, name='detail'),
    path('<int:component_id>/edit/', salary_component_views.component_edit, name='edit'),
    path('<int:component_id>/delete/', salary_component_views.component_delete, name='delete'),
    path('<int:component_id>/toggle-status/', salary_component_views.component_toggle_status, name='toggle_status'),
]

# Employee Salary Structure patterns
employee_salary_structure_patterns = [
    path('', employee_salary_structure_views.structure_list, name='list'),
    path('create/', employee_salary_structure_views.structure_create, name='create'),
    path('<int:structure_id>/', employee_salary_structure_views.structure_detail, name='detail'),
    path('<int:structure_id>/edit/', employee_salary_structure_views.structure_edit, name='edit'),
    path('<int:structure_id>/delete/', employee_salary_structure_views.structure_delete, name='delete'),
    path('<int:structure_id>/activate/', employee_salary_structure_views.structure_activate, name='activate'),
    path('<int:structure_id>/copy/', employee_salary_structure_views.structure_copy, name='copy'),
]

# Payroll Period patterns (New)
payroll_period_new_patterns = [
    path('', payroll_period_views_new.period_list, name='list'),
    path('create/', payroll_period_views_new.period_create, name='create'),
    path('<int:period_id>/', payroll_period_views_new.period_detail, name='detail'),
    path('<int:period_id>/edit/', payroll_period_views_new.period_edit, name='edit'),
    path('<int:period_id>/delete/', payroll_period_views_new.period_delete, name='delete'),
    path('<int:period_id>/close/', payroll_period_views_new.period_close, name='close'),
    path('<int:period_id>/reopen/', payroll_period_views_new.period_reopen, name='reopen'),
    path('<int:period_id>/summary/', payroll_period_views_new.period_summary_ajax, name='summary_ajax'),
]

# Payroll Entry patterns (New)
payroll_entry_new_patterns = [
    path('', payroll_entry_views_new.entry_list, name='list'),
    path('create/', payroll_entry_views_new.entry_create, name='create'),
    path('<int:entry_id>/', payroll_entry_views_new.entry_detail, name='detail'),
    path('<int:entry_id>/edit/', payroll_entry_views_new.entry_edit, name='edit'),
    path('<int:entry_id>/approve/', payroll_entry_views_new.entry_approve, name='approve'),
    path('<int:entry_id>/reject/', payroll_entry_views_new.entry_reject, name='reject'),
    path('<int:entry_id>/mark-paid/', payroll_entry_views_new.entry_mark_paid, name='mark_paid'),
    path('bulk-approve/', payroll_entry_views_new.bulk_approve_entries, name='bulk_approve'),
]

# Payroll Calculation patterns
payroll_calculation_patterns = [
    path('', payroll_calculation_views.payroll_calculation_dashboard, name='dashboard'),
    path('wizard/', payroll_calculation_views.payroll_calculation_wizard, name='wizard'),
    path('preview/', payroll_calculation_views.payroll_calculation_preview, name='preview'),
    path('status/<int:period_id>/', payroll_calculation_views.payroll_calculation_status, name='status'),
    path('recalculate/<int:entry_id>/', payroll_calculation_views.recalculate_payroll_entry, name='recalculate'),
]

# Employee Document patterns
employee_document_patterns = [
    path('', employee_document_views.document_list, name='list'),
    path('create/', employee_document_views.document_create, name='create'),
    path('<int:document_id>/', employee_document_views.document_detail, name='detail'),
    path('<int:document_id>/edit/', employee_document_views.document_edit, name='edit'),
    path('<int:document_id>/delete/', employee_document_views.document_delete, name='delete'),
    path('<int:document_id>/verify/', employee_document_views.document_verify, name='verify'),
    path('<int:document_id>/download/', employee_document_views.document_download, name='download'),
    path('by-employee/<int:employee_id>/', employee_document_views.documents_by_employee, name='by_employee'),
    path('expiring/', employee_document_views.expiring_documents, name='expiring'),
]

# Employee Emergency Contact patterns
emergency_contact_patterns = [
    path('', employee_emergency_contact_views.contact_list, name='list'),
    path('create/', employee_emergency_contact_views.contact_create, name='create'),
    path('<int:contact_id>/', employee_emergency_contact_views.contact_detail, name='detail'),
    path('<int:contact_id>/edit/', employee_emergency_contact_views.contact_edit, name='edit'),
    path('<int:contact_id>/delete/', employee_emergency_contact_views.contact_delete, name='delete'),
    path('by-employee/<int:employee_id>/', employee_emergency_contact_views.contacts_by_employee, name='by_employee'),
]

# Employee Training patterns
employee_training_patterns = [
    path('', employee_training_views.training_list, name='list'),
    path('create/', employee_training_views.training_create, name='create'),
    path('<int:training_id>/', employee_training_views.training_detail, name='detail'),
    path('<int:training_id>/edit/', employee_training_views.training_edit, name='edit'),
    path('<int:training_id>/delete/', employee_training_views.training_delete, name='delete'),
    path('<int:training_id>/complete/', employee_training_views.training_complete, name='complete'),
    path('<int:training_id>/certificate/', employee_training_views.training_certificate, name='certificate'),
    path('by-employee/<int:employee_id>/', employee_training_views.trainings_by_employee, name='by_employee'),
    path('calendar/', employee_training_views.training_calendar, name='calendar'),
]

urlpatterns = [
    # Main dashboard
    path('', dashboard, name='dashboard'),
    path('dashboard/', dashboard, name='dashboard_alt'),

    # ==================== CORE ORGANIZATIONAL STRUCTURE ====================
    path('companies/', include((company_patterns, app_name), namespace='companies')),
    path('branches/', include((branch_patterns, app_name), namespace='branches')),
    path('departments-new/', include((department_new_patterns, app_name), namespace='departments_new')),
    path('job-positions/', include((job_position_patterns, app_name), namespace='job_positions')),

    # ==================== EMPLOYEE MANAGEMENT ====================
    path('employees/', include((employee_patterns, app_name), namespace='employees')),
    path('employee-documents/', include((employee_document_patterns, app_name), namespace='employee_documents')),
    path('emergency-contacts/', include((emergency_contact_patterns, app_name), namespace='emergency_contacts')),
    path('employee-training/', include((employee_training_patterns, app_name), namespace='employee_training')),

    # ==================== LEAVE MANAGEMENT ====================
    path('leave-types/', include((leave_type_patterns, app_name), namespace='leave_types')),
    path('leave-policies/', include((leave_policy_patterns, app_name), namespace='leave_policies')),
    path('leave-requests/', include((leave_request_patterns, app_name), namespace='leave_requests')),
    path('leave-balances/', include((leave_balance_patterns, app_name), namespace='leave_balances')),

    # ==================== ATTENDANCE & TIME TRACKING ====================
    path('work-shifts/', include((work_shift_patterns, app_name), namespace='work_shifts')),
    path('attendance-machines-new/', include((attendance_machine_new_patterns, app_name), namespace='attendance_machines_new')),
    path('attendance/', include((attendance_patterns, app_name), namespace='attendance')),

    # ==================== PAYROLL MANAGEMENT ====================
    path('salary-components/', include((salary_component_patterns, app_name), namespace='salary_components')),
    path('employee-salary-structures/', include((employee_salary_structure_patterns, app_name), namespace='employee_salary_structures')),
    path('payroll-periods-new/', include((payroll_period_new_patterns, app_name), namespace='payroll_periods_new')),
    path('payroll-entries-new/', include((payroll_entry_new_patterns, app_name), namespace='payroll_entries_new')),
    path('payroll-calculation/', include((payroll_calculation_patterns, app_name), namespace='payroll_calculation')),
    path('salaries/', include((salary_patterns, app_name), namespace='salaries')),

    # ==================== LEGACY MODULES (for backward compatibility) ====================
    path('departments/', include((department_patterns, app_name), namespace='departments')),
    path('jobs/', include((job_patterns, app_name), namespace='jobs')),
    path('reports/', include((report_patterns, app_name), namespace='reports')),
    path('analytics/', include((analytics_patterns, app_name), namespace='analytics')),
    path('org_chart/', include((org_chart_patterns, app_name), namespace='org_chart')),
    path('alerts/', include((alert_patterns, app_name), namespace='alerts')),
    path('notes/', include((note_patterns, app_name), namespace='notes')),

    # Update data utility
    path('update-data/', update_data, name='update_data'),
    
    # ==================== REPORTS & ANALYTICS ====================
    # Temporarily disabled due to package structure issues
    # path('reports/', include('Hr.urls.reports_urls', namespace='reports')),
    
    # ==================== NOTIFICATIONS ====================
    path('notifications/', include('Hr.url_modules.notification_urls', namespace='notifications')),
    
    # ==================== ADVANCED SEARCH ====================
    path('search/', include('Hr.url_modules.search_urls', namespace='search')),
    
    # ==================== EXTERNAL INTEGRATIONS ====================
    path('integrations/', include('Hr.url_modules.integration_urls', namespace='integrations')),
    
    # ==================== API ENDPOINTS ====================
    # path('api/', include('Hr.api.urls', namespace='hr_api')),  # Temporarily commented out
]
