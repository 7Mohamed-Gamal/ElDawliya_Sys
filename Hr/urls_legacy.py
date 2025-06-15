# =============================================================================
# ElDawliya HR Management System - Legacy URLs
# =============================================================================
# Legacy URL patterns for backward compatibility
# This file contains the original URL patterns from the existing system
# =============================================================================

from django.urls import path, include
from . import views
from .views.department_views_updated import (
    department_list, department_create, department_edit, 
    department_delete, department_performance, department_detail
)
from .views.attendance_views import (
    attendance_rule_list, attendance_rule_create, attendance_rule_edit, attendance_rule_delete,
    employee_attendance_rule_list, employee_attendance_rule_create, employee_attendance_rule_edit,
    employee_attendance_rule_delete, employee_attendance_rule_bulk_create,
    official_holiday_list, official_holiday_create, official_holiday_edit, official_holiday_delete,
    attendance_machine_list, attendance_machine_create, attendance_machine_edit, attendance_machine_delete,
    attendance_record_list, attendance_record_create, attendance_record_edit, attendance_record_delete,
    fetch_attendance_data, attendance_summary_list, attendance_summary_detail
)
from .views.insurance_views import (
    insurance_job_list, insurance_job_create, insurance_job_detail,
    insurance_job_edit, insurance_job_delete
)
from .views.employee_views import (
    dashboard, employee_list, employee_create, employee_detail,
    employee_edit, employee_delete, employee_search, employee_print,
    employee_detail_view, employee_dashboard_simple, employee_export,
    employee_list_ajax
)
from .views.car_views import (
    car_list, car_create, car_detail, car_edit, car_delete
)
from .views.pickup_point_views import (
    pickup_point_list, pickup_point_create, pickup_point_detail,
    pickup_point_edit, pickup_point_delete
)
from .views.task_views import (
    employee_task_list, employee_task_create, employee_task_detail,
    employee_task_edit, employee_task_delete, task_step_toggle, task_step_delete
)
from .views.note_views import (
    employee_notes_dashboard, employee_notes_create, employee_search_ajax,
    employee_notes_list, employee_note_detail, employee_note_edit,
    employee_note_delete, employee_notes_reports
)
from .views.file_views import (
    employee_file_list, employee_file_create, employee_file_detail,
    employee_file_edit, employee_file_delete
)
from .views.hr_task_views import (
    hr_task_list, hr_task_create, hr_task_detail,
    hr_task_edit, hr_task_delete
)
from .views.leave_views import (
    leave_type_list, leave_type_create, leave_type_edit,
    employee_leave_list, employee_leave_create, employee_leave_detail,
    employee_leave_edit, employee_leave_approve
)
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
from .views import update_data

# Import job views
from .views.job_views import job_list, job_create, job_detail, job_edit, job_delete, get_next_job_code

# أنماط عناوين URL للموظفين
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

# أنماط عناوين URL للأقسام
department_patterns = [
    path('', department_list, name='list'),
    path('create/', department_create, name='create'),
    path('<int:dept_code>/', department_detail, name='detail'),
    path('<int:dept_code>/edit/', department_edit, name='edit'),
    path('<int:dept_code>/delete/', department_delete, name='delete'),
    path('<int:dept_code>/performance/', department_performance, name='performance'),
]

# أنماط عناوين URL للوظائف
job_patterns = [
    path('', job_list, name='list'),
    path('create/', job_create, name='create'),
    path('get_next_job_code/', get_next_job_code, name='get_next_job_code'),
    path('<int:jop_code>/', job_detail, name='detail'),
    path('<int:jop_code>/edit/', job_edit, name='edit'),
    path('<int:jop_code>/delete/', job_delete, name='delete'),
]

# أنماط عناوين URL للسيارات
car_patterns = [
    path('', car_list, name='list'),
    path('create/', car_create, name='create'),
    path('<int:car_id>/', car_detail, name='detail'),
    path('<int:car_id>/edit/', car_edit, name='edit'),
    path('<int:car_id>/delete/', car_delete, name='delete'),
]

# أنماط عناوين URL لنقاط الالتقاط
pickup_point_patterns = [
    path('', pickup_point_list, name='list'),
    path('create/', pickup_point_create, name='create'),
    path('<int:pk>/', pickup_point_detail, name='detail'),
    path('<int:pk>/edit/', pickup_point_edit, name='edit'),
    path('<int:pk>/delete/', pickup_point_delete, name='delete'),
]

# أنماط عناوين URL لوظائف التأمين
insurance_job_patterns = [
    path('', insurance_job_list, name='list'),
    path('create/', insurance_job_create, name='create'),
    path('<int:job_code_insurance>/', insurance_job_detail, name='detail'),
    path('<int:job_code_insurance>/edit/', insurance_job_edit, name='edit'),
    path('<int:job_code_insurance>/delete/', insurance_job_delete, name='delete'),
]

# أنماط عناوين URL لمهام الموظفين
task_patterns = [
    path('', employee_task_list, name='list'),
    path('create/', employee_task_create, name='create'),
    path('<int:pk>/', employee_task_detail, name='detail'),
    path('<int:pk>/edit/', employee_task_edit, name='edit'),
    path('<int:pk>/delete/', employee_task_delete, name='delete'),
    # خطوات المهمة
    path('<int:task_pk>/steps/<int:step_pk>/toggle/', task_step_toggle, name='step_toggle'),
    path('<int:task_pk>/steps/<int:step_pk>/delete/', task_step_delete, name='step_delete'),
]

# أنماط عناوين URL لملاحظات الموظفين
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

# أنماط عناوين URL لملفات الموظفين
file_patterns = [
    path('', employee_file_list, name='list'),
    path('create/', employee_file_create, name='create'),
    path('<int:pk>/', employee_file_detail, name='detail'),
    path('<int:pk>/edit/', employee_file_edit, name='edit'),
    path('<int:pk>/delete/', employee_file_delete, name='delete'),
]

# أنماط عناوين URL لمهام الموارد البشرية
hr_task_patterns = [
    path('', hr_task_list, name='list'),
    path('create/', hr_task_create, name='create'),
    path('<int:pk>/', hr_task_detail, name='detail'),
    path('<int:pk>/edit/', hr_task_edit, name='edit'),
    path('<int:pk>/delete/', hr_task_delete, name='delete'),
]

# أنماط عناوين URL لأنواع الإجازات
leave_type_patterns = [
    path('', leave_type_list, name='list'),
    path('create/', leave_type_create, name='create'),
    path('<int:pk>/edit/', leave_type_edit, name='edit'),
]

employee_leave_patterns = [
    path('', employee_leave_list, name='list'),
    path('create/', employee_leave_create, name='create'),
    path('<int:pk>/', employee_leave_detail, name='detail'),
    path('<int:pk>/edit/', employee_leave_edit, name='edit'),
    path('<int:pk>/approve/', employee_leave_approve, name='approve'),
]

# أنماط عناوين URL للرواتب
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

# Attendance URL patterns
attendance_patterns = [
    path('rules/', attendance_rule_list, name='attendance_rule_list'),
    path('rules/create/', attendance_rule_create, name='attendance_rule_create'),
    path('rules/<int:pk>/edit/', attendance_rule_edit, name='attendance_rule_edit'),
    path('rules/<int:pk>/delete/', attendance_rule_delete, name='attendance_rule_delete'),

    path('employee-rules/', employee_attendance_rule_list, name='employee_attendance_rule_list'),
    path('employee-rules/create/', employee_attendance_rule_create, name='employee_attendance_rule_create'),
    path('employee-rules/<int:pk>/edit/', employee_attendance_rule_edit, name='employee_attendance_rule_edit'),
    path('employee-rules/<int:pk>/delete/', employee_attendance_rule_delete, name='employee_attendance_rule_delete'),
    path('employee-rules/bulk-create/', employee_attendance_rule_bulk_create, name='employee_attendance_rule_bulk_create'),

    path('holidays/', official_holiday_list, name='official_holiday_list'),
    path('holidays/create/', official_holiday_create, name='official_holiday_create'),
    path('holidays/<int:pk>/edit/', official_holiday_edit, name='official_holiday_edit'),
    path('holidays/<int:pk>/delete/', official_holiday_delete, name='official_holiday_delete'),

    path('machines/', attendance_machine_list, name='attendance_machine_list'),
    path('machines/create/', attendance_machine_create, name='attendance_machine_create'),
    path('machines/<int:pk>/edit/', attendance_machine_edit, name='attendance_machine_edit'),
    path('machines/<int:pk>/delete/', attendance_machine_delete, name='attendance_machine_delete'),

    path('records/', attendance_record_list, name='attendance_record_list'),
    path('records/create/', attendance_record_create, name='attendance_record_create'),
    path('records/<int:pk>/edit/', attendance_record_edit, name='attendance_record_edit'),
    path('records/<int:pk>/delete/', attendance_record_delete, name='attendance_record_delete'),
    path('records/fetch/', fetch_attendance_data, name='fetch_attendance_data'),

    path('summary/', attendance_summary_list, name='attendance_summary_list'),
    path('summary/<int:pk>/', attendance_summary_detail, name='attendance_summary_detail'),
]

urlpatterns = [
    # لوحة التحكم
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard_simple/', employee_dashboard_simple, name='dashboard_simple'),
    # تضمين أنماط URL لكل قسم
    path('employees/', include((employee_patterns, 'employees'))),
    path('employees/detail_view/', employee_detail_view, name='detail_view'),
    path('departments/', include((department_patterns, 'departments'))),
    path('jobs/', include((job_patterns, 'jobs'))),
    path('insurance_jobs/', include((insurance_job_patterns, 'insurance_jobs'))),
    path('salaries/', include((salary_patterns, 'salaries'))),
    path('notes/', include((note_patterns, 'notes'))),

    # بنود الرواتب
    path('salary_items/', salary_item_list, name='salary_item_list'),
    path('salary_items/create/', salary_item_create, name='salary_item_create'),
    path('salary_items/<int:pk>/edit/', salary_item_edit, name='salary_item_edit'),
    path('salary_items/<int:pk>/delete/', salary_item_delete, name='salary_item_delete'),

    # بنود رواتب الموظفين
    path('employee_salary_items/', employee_salary_item_list, name='employee_salary_item_list'),
    path('employee_salary_items/create/', employee_salary_item_create, name='employee_salary_item_create'),
    path('employee_salary_items/bulk_create/', employee_salary_item_bulk_create, name='employee_salary_item_bulk_create'),
    path('employee_salary_items/<int:pk>/edit/', employee_salary_item_edit, name='employee_salary_item_edit'),
    path('employee_salary_items/<int:pk>/delete/', employee_salary_item_delete, name='employee_salary_item_delete'),

    # فترات الرواتب
    path('payroll_periods/', payroll_period_list, name='payroll_period_list'),
    path('payroll_periods/create/', payroll_period_create, name='payroll_period_create'),
    path('payroll_periods/<int:pk>/edit/', payroll_period_edit, name='payroll_period_edit'),
    path('payroll_periods/<int:pk>/delete/', payroll_period_delete, name='payroll_period_delete'),

    # حساب الرواتب
    path('payrolls/calculate/', payroll_calculate, name='payroll_calculate'),
    path('payrolls/entries/', payroll_entry_list, name='payroll_entry_list'),
    path('payrolls/entries/<int:pk>/', payroll_entry_detail, name='payroll_entry_detail'),
    path('payrolls/entries/<int:pk>/approve/', payroll_entry_approve, name='payroll_entry_approve'),
    path('payrolls/entries/<int:pk>/reject/', payroll_entry_reject, name='payroll_entry_reject'),

    # قواعد الحضور والغياب
    path('attendance/', include((attendance_patterns, 'attendance'))),

    # التقارير
    path('reports/', include((
        [
            path('', report_list, name='list'),
            path('monthly_salary/', monthly_salary_report, name='monthly_salary_report'),
            path('monthly_salary/print/', monthly_salary_report, name='monthly_salary_print'),
            path('employees/', employee_report, name='employee_report'),
            path('<str:report_type>/', report_detail, name='report_detail'),
        ], 'reports'
    ))),

    # التنبيهات
    path('alerts/', include((
        [
            path('', alert_list, name='list'),
        ], 'alerts'
    ))),

    # التحليلات
    path('analytics/', include((
        [
            path('', analytics_dashboard, name='dashboard'),
            path('<str:chart_type>/', analytics_chart, name='chart'),
        ], 'analytics'
    ))),

    # الهيكل التنظيمي
    path('org_chart/', include((
        [
            path('', org_chart, name='view'),
            path('data/', org_chart_data, name='data'),
            path('department/<int:dept_code>/', department_org_chart, name='department'),
            path('employee/<int:emp_id>/', employee_hierarchy, name='employee'),
        ], 'org_chart'
    ))),

    # إعادة توجيه الجذر إلى قائمة الموظفين للتوافق مع الإصدارات السابقة
    path('', employee_list, name='list'),
    path('update-data/', update_data, name='update_data'),
]
