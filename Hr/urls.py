from django.urls import path, include
from . import views
from .views.department_views_updated import department_list, department_create, department_edit, department_delete, department_performance, department_detail
from .views.employee_views import dashboard as employee_dashboard_simple

app_name = 'Hr'

# Patrones de URL para empleados
employee_patterns = [
    path('', views.employee_list, name='list'),
    path('create/', views.employee_create, name='create'),
    path('<int:emp_id>/', views.employee_detail, name='detail'),
    path('<int:emp_id>/edit/', views.employee_edit, name='edit'),
    path('<int:emp_id>/delete/', views.employee_delete, name='delete'),
    path('search/', views.employee_search, name='employee_search'),
]

# New employee search page
# Removed duplicate path outside patterns list

# Patrones de URL para departamentos
department_patterns = [
    path('', department_list, name='list'),
    path('create/', department_create, name='create'),
    path('<int:dept_code>/', department_detail, name='detail'),
    path('<int:dept_code>/edit/', department_edit, name='edit'),
    path('<int:dept_code>/delete/', department_delete, name='delete'),
    path('<int:dept_code>/performance/', department_performance, name='performance'),
]

# Patrones de URL para trabajos/puestos
job_patterns = [
    path('', views.job_list, name='list'),
    path('create/', views.job_create, name='create'),
    path('<int:jop_code>/', views.job_detail, name='detail'),
    path('<int:jop_code>/edit/', views.job_edit, name='edit'),
    path('<int:jop_code>/delete/', views.job_delete, name='delete'),
]

# Patrones de URL para vehículos
car_patterns = [
    path('', views.car_list, name='list'),
    path('create/', views.car_create, name='create'),
    path('<int:car_id>/', views.car_detail, name='detail'),
    path('<int:car_id>/edit/', views.car_edit, name='edit'),
    path('<int:car_id>/delete/', views.car_delete, name='delete'),
]

# Patrones de URL para puntos de recogida
pickup_point_patterns = [
    path('', views.pickup_point_list, name='list'),
    path('create/', views.pickup_point_create, name='create'),
    path('<int:pk>/', views.pickup_point_detail, name='detail'),
    path('<int:pk>/edit/', views.pickup_point_edit, name='edit'),
    path('<int:pk>/delete/', views.pickup_point_delete, name='delete'),
]

# Patrones de URL para trabajos de seguro
insurance_job_patterns = [
    path('', views.insurance_job_list, name='list'),
    path('create/', views.insurance_job_create, name='create'),
    path('<int:job_code_insurance>/', views.insurance_job_detail, name='detail'),
    path('<int:job_code_insurance>/edit/', views.insurance_job_edit, name='edit'),
    path('<int:job_code_insurance>/delete/', views.insurance_job_delete, name='delete'),
]

# Patrones de URL para tareas de empleados
task_patterns = [
    path('', views.employee_task_list, name='list'),
    path('create/', views.employee_task_create, name='create'),
    path('<int:pk>/', views.employee_task_detail, name='detail'),
    path('<int:pk>/edit/', views.employee_task_edit, name='edit'),
    path('<int:pk>/delete/', views.employee_task_delete, name='delete'),
]

# Patrones de URL para notas de empleados
note_patterns = [
    path('', views.employee_note_list, name='list'),
    path('create/', views.employee_note_create, name='create'),
    path('<int:pk>/', views.employee_note_detail, name='detail'),
    path('<int:pk>/edit/', views.employee_note_edit, name='edit'),
    path('<int:pk>/delete/', views.employee_note_delete, name='delete'),
]

# Patrones de URL para archivos de empleados
file_patterns = [
    path('', views.employee_file_list, name='list'),
    path('create/', views.employee_file_create, name='create'),
    path('<int:pk>/', views.employee_file_detail, name='detail'),
    path('<int:pk>/edit/', views.employee_file_edit, name='edit'),
    path('<int:pk>/delete/', views.employee_file_delete, name='delete'),
]

# Patrones de URL para tareas de RRHH
hr_task_patterns = [
    path('', views.hr_task_list, name='list'),
    path('create/', views.hr_task_create, name='create'),
    path('<int:pk>/', views.hr_task_detail, name='detail'),
    path('<int:pk>/edit/', views.hr_task_edit, name='edit'),
    path('<int:pk>/delete/', views.hr_task_delete, name='delete'),
]

# Patrones de URL para tipos de permisos
leave_type_patterns = [
    path('', views.leave_type_list, name='list'),
    path('create/', views.leave_type_create, name='create'),
    path('<int:pk>/', views.leave_type_detail, name='detail'),
    path('<int:pk>/edit/', views.leave_type_edit, name='edit'),
    path('<int:pk>/delete/', views.leave_type_delete, name='delete'),
]

# Patrones de URL para permisos de empleados
leave_patterns = [
    path('', views.employee_leave_list, name='list'),
    path('create/', views.employee_leave_create, name='create'),
    path('<int:pk>/', views.employee_leave_detail, name='detail'),
    path('<int:pk>/edit/', views.employee_leave_edit, name='edit'),
    path('<int:pk>/delete/', views.employee_leave_delete, name='delete'),
    path('<int:pk>/approve/', views.employee_leave_approve, name='approve'),
    path('<int:pk>/reject/', views.employee_leave_reject, name='reject'),
]

# Patrones de URL para evaluaciones de empleados
evaluation_patterns = [
    path('', views.employee_evaluation_list, name='list'),
    path('create/', views.employee_evaluation_create, name='create'),
    path('<int:pk>/', views.employee_evaluation_detail, name='detail'),
    path('<int:pk>/edit/', views.employee_evaluation_edit, name='edit'),
    path('<int:pk>/delete/', views.employee_evaluation_delete, name='delete'),
]

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard_simple/', employee_dashboard_simple, name='dashboard_simple'),
    # Incluir patrones de URL para cada sección
    path('employees/', include((employee_patterns, 'employees'))),
    path('departments/', include((department_patterns, 'departments'))),
    path('jobs/', include((job_patterns, 'jobs'))),
    path('cars/', include((car_patterns, 'cars'))),
    path('pickup_points/', include((pickup_point_patterns, 'pickup_points'))),
    path('insurance_jobs/', include((insurance_job_patterns, 'insurance_jobs'))),
    path('tasks/', include((task_patterns, 'tasks'))),
    path('notes/', include((note_patterns, 'notes'))),
    path('files/', include((file_patterns, 'files'))),
    path('hr_tasks/', include((hr_task_patterns, 'hr_tasks'))),
    path('leave_types/', include((leave_type_patterns, 'leave_types'))),
    path('leaves/', include((leave_patterns, 'leaves'))),
    path('evaluations/', include((evaluation_patterns, 'evaluations'))),

    # Salary Items
    path('salary_items/', views.salary_item_list, name='salary_item_list'),
    path('salary_items/create/', views.salary_item_create, name='salary_item_create'),
    path('salary_items/<int:pk>/edit/', views.salary_item_edit, name='salary_item_edit'),
    path('salary_items/<int:pk>/delete/', views.salary_item_delete, name='salary_item_delete'),

    # Employee Salary Items
    path('employee_salary_items/', views.employee_salary_item_list, name='employee_salary_item_list'),
    path('employee_salary_items/create/', views.employee_salary_item_create, name='employee_salary_item_create'),
    path('employee_salary_items/bulk_create/', views.employee_salary_item_bulk_create, name='employee_salary_item_bulk_create'),
    path('employee_salary_items/<int:pk>/edit/', views.employee_salary_item_edit, name='employee_salary_item_edit'),
    path('employee_salary_items/<int:pk>/delete/', views.employee_salary_item_delete, name='employee_salary_item_delete'),

    # Payroll Periods
    path('payroll_periods/', views.payroll_period_list, name='payroll_period_list'),
    path('payroll_periods/create/', views.payroll_period_create, name='payroll_period_create'),
    path('payroll_periods/<int:pk>/edit/', views.payroll_period_edit, name='payroll_period_edit'),
    path('payroll_periods/<int:pk>/delete/', views.payroll_period_delete, name='payroll_period_delete'),

    # Payroll Calculation
    path('payrolls/calculate/', views.payroll_calculate, name='payroll_calculate'),
    path('payrolls/entries/', views.payroll_entry_list, name='payroll_entry_list'),
    path('payrolls/entries/<int:pk>/', views.payroll_entry_detail, name='payroll_entry_detail'),

    # Attendance Rules
    path('attendance_rules/', views.attendance_rule_list, name='attendance_rule_list'),
    path('attendance_rules/create/', views.attendance_rule_create, name='attendance_rule_create'),
    path('attendance_rules/<int:pk>/edit/', views.attendance_rule_edit, name='attendance_rule_edit'),
    path('attendance_rules/<int:pk>/delete/', views.attendance_rule_delete, name='attendance_rule_delete'),

    # Employee Attendance Rules
    path('employee_attendance_rules/', views.employee_attendance_rule_list, name='employee_attendance_rule_list'),
    path('employee_attendance_rules/create/', views.employee_attendance_rule_create, name='employee_attendance_rule_create'),
    path('employee_attendance_rules/bulk_create/', views.employee_attendance_rule_bulk_create, name='employee_attendance_rule_bulk_create'),
    path('employee_attendance_rules/<int:pk>/edit/', views.employee_attendance_rule_edit, name='employee_attendance_rule_edit'),
    path('employee_attendance_rules/<int:pk>/delete/', views.employee_attendance_rule_delete, name='employee_attendance_rule_delete'),

    # Official Holidays
    path('attendance/holidays/', views.official_holiday_list, name='official_holiday_list'),
    path('attendance/holidays/create/', views.official_holiday_create, name='official_holiday_create'),
    path('attendance/holidays/<int:pk>/edit/', views.official_holiday_edit, name='official_holiday_edit'),
    path('attendance/holidays/<int:pk>/delete/', views.official_holiday_delete, name='official_holiday_delete'),

    # Attendance Machines
    path('attendance/machines/', views.attendance_machine_list, name='attendance_machine_list'),
    path('attendance/machines/create/', views.attendance_machine_create, name='attendance_machine_create'),
    path('attendance/machines/<int:pk>/edit/', views.attendance_machine_edit, name='attendance_machine_edit'),
    path('attendance/machines/<int:pk>/delete/', views.attendance_machine_delete, name='attendance_machine_delete'),

    # Attendance Records
    path('attendance/records/', views.attendance_record_list, name='attendance_record_list'),
    path('attendance/records/create/', views.attendance_record_create, name='attendance_record_create'),
    path('attendance/records/<int:pk>/edit/', views.attendance_record_edit, name='attendance_record_edit'),
    path('attendance/records/<int:pk>/delete/', views.attendance_record_delete, name='attendance_record_delete'),

    # Fetch Attendance Data
    path('attendance/fetch_data/', views.fetch_attendance_data, name='fetch_attendance_data'),

    # Reports
    path('reports/', include((
        [
            path('', views.report_list, name='list'),
            path('monthly_salary/', views.monthly_salary_report, name='monthly_salary_report'),
            path('monthly_salary/print/', views.monthly_salary_report, name='monthly_salary_print'),
            path('<str:report_type>/', views.report_detail, name='report_detail'),
        ], 'reports'
    ))),

    # Alerts
    path('alerts/', include((
        [
            path('', views.alert_list, name='list'),
        ], 'alerts'
    ))),

    # Analytics
    path('analytics/', include((
        [
            path('', views.analytics_dashboard, name='dashboard'),
            path('<str:chart_type>/', views.analytics_chart, name='chart'),
        ], 'analytics'
    ))),

    # Organizational Chart
    path('org_chart/', include((
        [
            path('', views.org_chart, name='view'),
            path('data/', views.org_chart_data, name='data'),
            path('department/<int:dept_code>/', views.department_org_chart, name='department'),
            path('employee/<int:emp_id>/', views.employee_hierarchy, name='employee'),
        ], 'org_chart'
    ))),

    # Redirect root to employees list for backward compatibility
    path('', views.employee_list, name='list'),
]
