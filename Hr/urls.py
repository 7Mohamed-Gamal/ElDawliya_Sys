from django.urls import path, include
from . import views
from .views.department_views_updated import department_list, department_create, department_edit, department_delete, department_performance, department_detail
from .views.leave_views import leave_analytics
from .views.employee_views import dashboard as employee_dashboard_simple, employee_detail_view  # Added import

app_name = 'Hr'

# أنماط عناوين URL للموظفين
employee_patterns = [
    path('', views.employee_list, name='list'),
    path('create/', views.employee_create, name='create'),
    path('<int:emp_id>/', views.employee_detail, name='detail'),
    path('<int:emp_id>/edit/', views.employee_edit, name='edit'),
    path('<int:emp_id>/delete/', views.employee_delete, name='delete'),
    path('<int:emp_id>/print/', views.employee_print, name='print'),
    path('search/', views.employee_search, name='employee_search'),
]

# صفحة بحث الموظفين الجديدة
# تمت إزالة المسار المكرر خارج قائمة الأنماط

# أنماط عناوين URL للأقسام
department_patterns = [
    path('', department_list, name='list'),
    path('create/', department_create, name='create'),
    path('<int:dept_code>/', department_detail, name='detail'),
    path('<int:dept_code>/edit/', department_edit, name='edit'),
    path('<int:dept_code>/delete/', department_delete, name='delete'),
    path('<int:dept_code>/performance/', department_performance, name='performance'),
]

# Import job views
from .views.job_views import job_list, job_create, job_detail, job_edit, job_delete, get_next_job_code

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
    path('', views.car_list, name='list'),
    path('create/', views.car_create, name='create'),
    path('<int:car_id>/', views.car_detail, name='detail'),
    path('<int:car_id>/edit/', views.car_edit, name='edit'),
    path('<int:car_id>/delete/', views.car_delete, name='delete'),
]

# أنماط عناوين URL لنقاط الالتقاط
pickup_point_patterns = [
    path('', views.pickup_point_list, name='list'),
    path('create/', views.pickup_point_create, name='create'),
    path('<int:pk>/', views.pickup_point_detail, name='detail'),
    path('<int:pk>/edit/', views.pickup_point_edit, name='edit'),
    path('<int:pk>/delete/', views.pickup_point_delete, name='delete'),
]

# أنماط عناوين URL لوظائف التأمين
insurance_job_patterns = [
    path('', views.insurance_job_list, name='list'),
    path('create/', views.insurance_job_create, name='create'),
    path('<int:job_code_insurance>/', views.insurance_job_detail, name='detail'),
    path('<int:job_code_insurance>/edit/', views.insurance_job_edit, name='edit'),
    path('<int:job_code_insurance>/delete/', views.insurance_job_delete, name='delete'),
]

# أنماط عناوين URL لمهام الموظفين
task_patterns = [
    path('', views.employee_task_list, name='list'),
    path('create/', views.employee_task_create, name='create'),
    path('<int:pk>/', views.employee_task_detail, name='detail'),
    path('<int:pk>/edit/', views.employee_task_edit, name='edit'),
    path('<int:pk>/delete/', views.employee_task_delete, name='delete'),
    # خطوات المهمة
    path('<int:task_pk>/steps/<int:step_pk>/toggle/', views.task_views.task_step_toggle, name='step_toggle'),
    path('<int:task_pk>/steps/<int:step_pk>/delete/', views.task_views.task_step_delete, name='step_delete'),
]

# أنماط عناوين URL لملاحظات الموظفين
note_patterns = [
    path('', views.employee_note_list, name='list'),
    path('create/', views.employee_note_create, name='create'),
    path('<int:pk>/', views.employee_note_detail, name='detail'),
    path('<int:pk>/edit/', views.employee_note_edit, name='edit'),
    path('<int:pk>/delete/', views.employee_note_delete, name='delete'),
]

# أنماط عناوين URL لملفات الموظفين
file_patterns = [
    path('', views.employee_file_list, name='list'),
    path('create/', views.employee_file_create, name='create'),
    path('<int:pk>/', views.employee_file_detail, name='detail'),
    path('<int:pk>/edit/', views.employee_file_edit, name='edit'),
    path('<int:pk>/delete/', views.employee_file_delete, name='delete'),
]

# أنماط عناوين URL لمهام الموارد البشرية
hr_task_patterns = [
    path('', views.hr_task_list, name='list'),
    path('create/', views.hr_task_create, name='create'),
    path('<int:pk>/', views.hr_task_detail, name='detail'),
    path('<int:pk>/edit/', views.hr_task_edit, name='edit'),
    path('<int:pk>/delete/', views.hr_task_delete, name='delete'),
]

# أنماط عناوين URL لأنواع الإجازات
leave_type_patterns = [
    path('', views.leave_type_list, name='list'),
    path('create/', views.leave_type_create, name='create'),
    path('<int:pk>/edit/', views.leave_type_edit, name='edit'),
]

employee_leave_patterns = [
    path('', views.employee_leave_list, name='list'),
    path('create/', views.employee_leave_create, name='create'),
    path('<int:pk>/', views.employee_leave_detail, name='detail'),
    path('<int:pk>/edit/', views.employee_leave_edit, name='edit'),
    path('<int:pk>/approve/', views.employee_leave_approve, name='approve'),
]

urlpatterns = [
    # لوحة التحكم
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard_simple/', employee_dashboard_simple, name='dashboard_simple'),
    # تضمين أنماط URL لكل قسم
    path('employees/', include((employee_patterns, 'employees'))),
    path('employees/detail_view/', employee_detail_view, name='detail_view'),  # Moved outside employee_patterns
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
    path('leaves/', include((employee_leave_patterns, 'leaves'))),
    path('leaves/analytics/', leave_analytics, name='leave_analytics'),
    # TODO: Implement leave_balance_list and leave_balance_create functions
    # path('leaves/balance/', views.leave_balance_list, name='leave_balance_list'),
    # path('leaves/balance/create/', views.leave_balance_create, name='leave_balance_create'),

    # بنود الرواتب
    path('salary_items/', views.salary_item_list, name='salary_item_list'),
    path('salary_items/create/', views.salary_item_create, name='salary_item_create'),
    path('salary_items/<int:pk>/edit/', views.salary_item_edit, name='salary_item_edit'),
    path('salary_items/<int:pk>/delete/', views.salary_item_delete, name='salary_item_delete'),

    # بنود رواتب الموظفين
    path('employee_salary_items/', views.employee_salary_item_list, name='employee_salary_item_list'),
    path('employee_salary_items/create/', views.employee_salary_item_create, name='employee_salary_item_create'),
    path('employee_salary_items/bulk_create/', views.employee_salary_item_bulk_create, name='employee_salary_item_bulk_create'),
    path('employee_salary_items/<int:pk>/edit/', views.employee_salary_item_edit, name='employee_salary_item_edit'),
    path('employee_salary_items/<int:pk>/delete/', views.employee_salary_item_delete, name='employee_salary_item_delete'),

    # فترات الرواتب
    path('payroll_periods/', views.payroll_period_list, name='payroll_period_list'),
    path('payroll_periods/create/', views.payroll_period_create, name='payroll_period_create'),
    path('payroll_periods/<int:pk>/edit/', views.payroll_period_edit, name='payroll_period_edit'),
    path('payroll_periods/<int:pk>/delete/', views.payroll_period_delete, name='payroll_period_delete'),

    # حساب الرواتب
    path('payrolls/calculate/', views.payroll_calculate, name='payroll_calculate'),
    path('payrolls/entries/', views.payroll_entry_list, name='payroll_entry_list'),
    path('payrolls/entries/<int:pk>/', views.payroll_entry_detail, name='payroll_entry_detail'),

    # قواعد الحضور
    path('attendance_rules/', views.attendance_rule_list, name='attendance_rule_list'),
    path('attendance_rules/create/', views.attendance_rule_create, name='attendance_rule_create'),
    path('attendance_rules/<int:pk>/edit/', views.attendance_rule_edit, name='attendance_rule_edit'),
    path('attendance_rules/<int:pk>/delete/', views.attendance_rule_delete, name='attendance_rule_delete'),

    # قواعد حضور الموظفين
    path('employee_attendance_rules/', views.employee_attendance_rule_list, name='employee_attendance_rule_list'),
    path('employee_attendance_rules/create/', views.employee_attendance_rule_create, name='employee_attendance_rule_create'),
    path('employee_attendance_rules/bulk_create/', views.employee_attendance_rule_bulk_create, name='employee_attendance_rule_bulk_create'),
    path('employee_attendance_rules/<int:pk>/edit/', views.employee_attendance_rule_edit, name='employee_attendance_rule_edit'),
    path('employee_attendance_rules/<int:pk>/delete/', views.employee_attendance_rule_delete, name='employee_attendance_rule_delete'),

    # الإجازات الرسمية
    path('attendance/holidays/', views.official_holiday_list, name='official_holiday_list'),
    path('attendance/holidays/create/', views.official_holiday_create, name='official_holiday_create'),
    path('attendance/holidays/<int:pk>/edit/', views.official_holiday_edit, name='official_holiday_edit'),
    path('attendance/holidays/<int:pk>/delete/', views.official_holiday_delete, name='official_holiday_delete'),

    # أجهزة الحضور
    path('attendance/machines/', views.attendance_machine_list, name='attendance_machine_list'),
    path('attendance/machines/create/', views.attendance_machine_create, name='attendance_machine_create'),
    path('attendance/machines/<int:pk>/edit/', views.attendance_machine_edit, name='attendance_machine_edit'),
    path('attendance/machines/<int:pk>/delete/', views.attendance_machine_delete, name='attendance_machine_delete'),

    # سجلات الحضور
    path('attendance/records/', views.attendance_record_list, name='attendance_record_list'),
    path('attendance/records/create/', views.attendance_record_create, name='attendance_record_create'),
    path('attendance/records/<int:pk>/edit/', views.attendance_record_edit, name='attendance_record_edit'),
    path('attendance/records/<int:pk>/delete/', views.attendance_record_delete, name='attendance_record_delete'),

    # جلب بيانات الحضور
    path('attendance/fetch_data/', views.fetch_attendance_data, name='fetch_attendance_data'),

    # التقارير
    path('reports/', include((
        [
            path('', views.report_list, name='list'),
            path('monthly_salary/', views.monthly_salary_report, name='monthly_salary_report'),
            path('monthly_salary/print/', views.monthly_salary_report, name='monthly_salary_print'),
            path('employees/', views.employee_report, name='employee_report'),
            path('<str:report_type>/', views.report_detail, name='report_detail'),
        ], 'reports'
    ))),

    # التنبيهات
    path('alerts/', include((
        [
            path('', views.alert_list, name='list'),
        ], 'alerts'
    ))),

    # التحليلات
    path('analytics/', include((
        [
            path('', views.analytics_dashboard, name='dashboard'),
            path('<str:chart_type>/', views.analytics_chart, name='chart'),
        ], 'analytics'
    ))),

    # الهيكل التنظيمي
    path('org_chart/', include((
        [
            path('', views.org_chart, name='view'),
            path('data/', views.org_chart_data, name='data'),
            path('department/<int:dept_code>/', views.department_org_chart, name='department'),
            path('employee/<int:emp_id>/', views.employee_hierarchy, name='employee'),
        ], 'org_chart'
    ))),

    # إعادة توجيه الجذر إلى قائمة الموظفين للتوافق مع الإصدارات السابقة
    path('', views.employee_list, name='list'),
]
