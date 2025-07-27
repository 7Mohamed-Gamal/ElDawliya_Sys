"""
URLs للتقارير والتحليلات
"""

from django.urls import path
from Hr.views.reports_views import (
    analytics_dashboard,
    employee_reports,
    attendance_reports,
    payroll_reports,
    report_list,
    # API Views
    generate_employee_summary_report,
    generate_employee_details_report,
    generate_organizational_structure_report,
    generate_new_employees_report,
    generate_demographics_report,
    generate_birthdays_anniversaries_report,
    generate_attendance_analytics,
    generate_salary_analytics,
    export_report,
    get_dashboard_analytics,
    schedule_report
)

app_name = 'reports'

urlpatterns = [
    # صفحات التقارير
    path('', report_list, name='report_list'),
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('employees/', employee_reports, name='employee_reports'),
    path('attendance/', attendance_reports, name='attendance_reports'),
    path('payroll/', payroll_reports, name='payroll_reports'),
    
    # API endpoints للتقارير
    path('api/employee-summary/', generate_employee_summary_report, name='api_employee_summary'),
    path('api/employee-details/', generate_employee_details_report, name='api_employee_details'),
    path('api/org-structure/', generate_organizational_structure_report, name='api_org_structure'),
    path('api/new-employees/', generate_new_employees_report, name='api_new_employees'),
    path('api/demographics/', generate_demographics_report, name='api_demographics'),
    path('api/birthdays-anniversaries/', generate_birthdays_anniversaries_report, name='api_birthdays_anniversaries'),
    path('api/attendance-analytics/', generate_attendance_analytics, name='api_attendance_analytics'),
    path('api/salary-analytics/', generate_salary_analytics, name='api_salary_analytics'),
    path('api/export/', export_report, name='api_export_report'),
    path('api/dashboard-analytics/', get_dashboard_analytics, name='api_dashboard_analytics'),
    path('api/schedule/', schedule_report, name='api_schedule_report'),
]