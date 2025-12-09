from django.urls import path
from . import views

app_name = 'payrolls'

urlpatterns = [
    # لوحة التحكم الرئيسية
    path('', views.dashboard, name='dashboard'),

    # إدارة الرواتب
    path('salaries/', views.salary_list, name='salary_list'),
    path('salary/add/', views.add_salary, name='add_salary'),
    path('salary/<int:salary_id>/', views.salary_detail, name='salary_detail'),
    path('salary/<int:salary_id>/edit/', views.edit_salary, name='edit_salary'),
    path('salary/<int:salary_id>/delete/', views.delete_salary, name='delete_salary'),
    path('salary/<int:salary_id>/copy/', views.copy_salary, name='copy_salary'),
    path('salary/<int:salary_id>/history/', views.salary_history, name='salary_history'),

    # إدارة تشغيلات الرواتب
    path('runs/', views.payroll_runs, name='payroll_runs'),
    path('runs/create/', views.create_payroll_run, name='create_payroll_run'),
    path('runs/create-advanced/', views.create_advanced_payroll_run, name='create_advanced_payroll_run'),
    path('runs/<int:run_id>/', views.payroll_run_detail, name='payroll_run_detail'),
    path('runs/<int:run_id>/edit/', views.edit_payroll_run, name='edit_payroll_run'),
    path('runs/<int:run_id>/delete/', views.delete_payroll_run, name='delete_payroll_run'),

    # معالجة الرواتب المتقدمة
    path('runs/<int:run_id>/process/', views.process_payroll_run, name='process_payroll_run'),
    path('runs/<int:run_id>/process-advanced/', views.advanced_payroll_processing, name='advanced_payroll_processing'),
    path('runs/<int:run_id>/approve/', views.approve_payroll_run_view, name='approve_payroll_run'),
    path('runs/<int:run_id>/mark-paid/', views.mark_payroll_paid_view, name='mark_payroll_paid'),
    path('runs/<int:run_id>/cancel/', views.cancel_payroll_run_view, name='cancel_payroll_run'),
    path('runs/<int:run_id>/confirm/', views.confirm_payroll_run, name='confirm_payroll_run'),

    # كشوف الرواتب
    path('payslips/', views.payslips, name='payslips'),
    path('payslip/<int:payslip_id>/', views.payslip_detail, name='payslip_detail'),
    path('payslip/<int:payslip_id>/detailed/', views.detailed_payslip_view, name='detailed_payslip'),
    path('payslip/<int:payslip_id>/print/', views.print_payslip, name='print_payslip'),

    # بوابة الموظف
    path('my-payslips/', views.my_payslips, name='my_payslips'),
    path('my-salary/', views.my_salary, name='my_salary'),

    # التقارير والتحليلات
    path('reports/', views.reports, name='reports'),
    path('runs/<int:run_id>/summary-report/', views.payroll_summary_report, name='payroll_summary_report'),
    path('export/', views.export_payroll, name='export_payroll'),
    path('analytics/', views.payroll_analytics, name='payroll_analytics'),

    # العمليات الجماعية
    path('bulk/salary-update/', views.bulk_salary_update, name='bulk_salary_update'),
    path('bulk/payslip-generation/', views.bulk_payslip_generation, name='bulk_payslip_generation'),
    path('generate-payslips/', views.bulk_payslip_generation, name='generate_payslips'),

    # AJAX APIs
    path('ajax/calculate-salary/', views.calculate_salary_ajax, name='calculate_salary_ajax'),
    path('ajax/employee-salary/<int:emp_id>/', views.employee_salary_ajax, name='employee_salary_ajax'),
    path('ajax/runs/<int:run_id>/status/', views.payroll_processing_status, name='payroll_processing_status'),
    path('ajax/runs/<int:run_id>/employee/<int:emp_id>/recalculate/', views.recalculate_employee_payroll, name='recalculate_employee_payroll'),
    path('ajax/runs/<int:run_id>/employee/<int:emp_id>/preview/', views.employee_payroll_preview, name='employee_payroll_preview'),
]
