from django.urls import path, include
from . import views
from . import views_extended

app_name = 'employees'

urlpatterns = [
    # Employee URLs
    path('', views.dashboard, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('list/', views.employee_list, name='list'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('add/', views.add_employee, name='add'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('<int:emp_id>/', views.employee_detail, name='detail'),
    path('<int:emp_id>/edit/', views.edit_employee, name='edit'),
    path('<int:emp_id>/delete/', views.delete_employee, name='delete'),

    # Comprehensive Employee Edit
    path('<int:emp_id>/comprehensive-edit/',
         views_extended.comprehensive_employee_edit,
         name='comprehensive_edit'),

    # Document Management URLs
    path('<int:emp_id>/documents/', views.employee_documents, name='employee_documents'),
    path('<int:emp_id>/documents/upload/', views.upload_document, name='upload_document'),
    path('<int:emp_id>/documents/ajax-upload/', views.ajax_upload_document, name='ajax_upload_document'),
    path('documents/<int:doc_id>/download/', views.download_document, name='download_document'),
    path('documents/<int:doc_id>/delete/', views.delete_document, name='delete_document'),
    path('documents/<int:doc_id>/preview/', views.preview_document, name='preview_document'),
    path('<int:emp_id>/test-upload/', views.test_upload_endpoint, name='test_upload_endpoint'),
    path('<int:emp_id>/test-upload-page/', views.test_upload_page, name='test_upload_page'),

    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/<int:dept_id>/', views.department_detail, name='department_detail'),
    path('departments/<int:dept_id>/edit/', views.edit_department, name='edit_department'),
    path('departments/<int:dept_id>/delete/', views.delete_department, name='delete_department'),
    path('departments/summary/', views.department_summary, name='department_summary'),

    # Job URLs
    path('jobs/', views.job_list, name='job_list'),

    # AJAX URLs
    path('api/departments-by-branch/', views.get_departments_by_branch, name='departments_by_branch'),
    path('api/employees-by-department/', views.get_employees_by_department, name='employees_by_department'),
    path('api/departments/<int:dept_id>/employees/', views.department_employees_ajax, name='department_employees_ajax'),

    # Extended AJAX endpoints
    path('ajax/vehicle-details/<int:vehicle_id>/',
         views_extended.get_vehicle_details,
         name='get_vehicle_details'),

    path('ajax/salary-deductions/<int:emp_id>/',
         views_extended.calculate_salary_deductions,
         name='calculate_salary_deductions'),

    # Health Insurance Management
    path('health-insurance-providers/',
         views_extended.health_insurance_providers_list,
         name='health_insurance_providers_list'),

    path('health-insurance-providers/create/',
         views_extended.health_insurance_provider_create,
         name='health_insurance_provider_create'),

    path('health-insurance-providers/edit/<int:provider_id>/',
         views_extended.health_insurance_provider_edit,
         name='health_insurance_provider_edit'),

    # Social Insurance Job Titles Management
    path('social-insurance-job-titles/',
         views_extended.social_insurance_job_titles_list,
         name='social_insurance_job_titles_list'),

    path('social-insurance-job-titles/create/',
         views_extended.social_insurance_job_title_create,
         name='social_insurance_job_title_create'),

    path('social-insurance-job-titles/edit/<int:job_title_id>/',
         views_extended.social_insurance_job_title_edit,
         name='social_insurance_job_title_edit'),

    # Salary Components Management
    path('salary-components/',
         views_extended.salary_components_list,
         name='salary_components_list'),

    path('salary-components/create/',
         views_extended.salary_component_create,
         name='salary_component_create'),

    path('salary-components/edit/<int:component_id>/',
         views_extended.salary_component_edit,
         name='salary_component_edit'),

    # Vehicle Management
    path('vehicles/',
         views_extended.vehicles_list,
         name='vehicles_list'),

    path('vehicles/create/',
         views_extended.vehicle_create,
         name='vehicle_create'),

    path('vehicles/edit/<int:vehicle_id>/',
         views_extended.vehicle_edit,
         name='vehicle_edit'),

    # Pickup Points Management
    path('pickup-points/',
         views_extended.pickup_points_list,
         name='pickup_points_list'),

    path('pickup-points/create/',
         views_extended.pickup_point_create,
         name='pickup_point_create'),

    path('pickup-points/edit/<int:pickup_point_id>/',
         views_extended.pickup_point_edit,
         name='pickup_point_edit'),

    # Work Schedules Management
    path('work-schedules/',
         views_extended.work_schedules_list,
         name='work_schedules_list'),

    path('work-schedules/create/',
         views_extended.work_schedule_create,
         name='work_schedule_create'),

    path('work-schedules/edit/<int:schedule_id>/',
         views_extended.work_schedule_edit,
         name='work_schedule_edit'),

    # Evaluation Criteria Management
    path('evaluation-criteria/',
         views_extended.evaluation_criteria_list,
         name='evaluation_criteria_list'),

    path('evaluation-criteria/create/',
         views_extended.evaluation_criteria_create,
         name='evaluation_criteria_create'),

    path('evaluation-criteria/edit/<int:criteria_id>/',
         views_extended.evaluation_criteria_edit,
         name='evaluation_criteria_edit'),

    # Performance Evaluation
    path('performance-evaluation/create/<int:emp_id>/',
         views_extended.performance_evaluation_create,
         name='performance_evaluation_create'),

    path('performance-evaluation/detail/<int:evaluation_id>/',
         views_extended.performance_evaluation_detail,
         name='performance_evaluation_detail'),

    path('performance-evaluation/edit/<int:evaluation_id>/',
         views_extended.performance_evaluation_edit,
         name='performance_evaluation_edit'),

    # Leave Balances Management
    path('initialize-leave-balances/<int:emp_id>/',
         views_extended.initialize_leave_balances,
         name='initialize_leave_balances'),

    # Document Management
    path('upload-document/',
         views_extended.upload_document,
         name='upload_document'),
    path('delete-document/',
         views_extended.delete_document,
         name='delete_document'),

    # Salary Components Management
    path('add-salary-component/',
         views_extended.add_salary_component,
         name='add_salary_component'),
    path('remove-salary-component/',
         views_extended.remove_salary_component,
         name='remove_salary_component'),
]

