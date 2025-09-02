"""
Extended URL patterns for comprehensive employee management
"""
from django.urls import path
from . import views_extended

app_name = 'employees_extended'

urlpatterns = [
    # Comprehensive Employee Edit
    path('comprehensive-edit/<int:emp_id>/', 
         views_extended.comprehensive_employee_edit, 
         name='comprehensive_edit'),
    
    # AJAX endpoints
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
    
    # Leave Balance Management
    path('leave-balances/update/<int:emp_id>/', 
         views_extended.update_leave_balances, 
         name='update_leave_balances'),
    
    path('leave-balances/calculate/<int:emp_id>/', 
         views_extended.calculate_leave_balances, 
         name='calculate_leave_balances'),
    
    # Reports
    path('reports/employee-comprehensive/<int:emp_id>/', 
         views_extended.employee_comprehensive_report, 
         name='employee_comprehensive_report'),
    
    path('reports/salary-components/', 
         views_extended.salary_components_report, 
         name='salary_components_report'),
    
    path('reports/insurance-summary/', 
         views_extended.insurance_summary_report, 
         name='insurance_summary_report'),
    
    # Bulk Operations
    path('bulk/update-insurance/', 
         views_extended.bulk_update_insurance, 
         name='bulk_update_insurance'),
    
    path('bulk/update-salary-components/', 
         views_extended.bulk_update_salary_components, 
         name='bulk_update_salary_components'),
    
    # Import/Export
    path('import/salary-components/', 
         views_extended.import_salary_components, 
         name='import_salary_components'),
    
    path('export/employee-data/<int:emp_id>/', 
         views_extended.export_employee_data, 
         name='export_employee_data'),
]
