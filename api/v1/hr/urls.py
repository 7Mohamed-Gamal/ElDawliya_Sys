"""
HR API URLs
روابط API الموارد البشرية
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for HR ViewSets
router = DefaultRouter()
router.register(r'employees', views.EmployeeViewSet, basename='employee')
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'positions', views.JobPositionViewSet, basename='position')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
router.register(r'leaves', views.LeaveViewSet, basename='leave')
router.register(r'payroll', views.PayrollViewSet, basename='payroll')
router.register(r'evaluations', views.EvaluationViewSet, basename='evaluation')

app_name = 'hr_api'

urlpatterns = [
    # Employee management endpoints
    path('employees/bulk-import/', views.BulkEmployeeImportView.as_view(), name='bulk_employee_import'),
    path('employees/export/', views.EmployeeExportView.as_view(), name='employee_export'),

    # Attendance endpoints
    path('attendance/clock-in/', views.ClockInView.as_view(), name='clock_in'),
    path('attendance/clock-out/', views.ClockOutView.as_view(), name='clock_out'),
    path('attendance/summary/', views.AttendanceSummaryView.as_view(), name='attendance_summary'),

    # Leave management endpoints
    path('leaves/apply/', views.LeaveApplicationView.as_view(), name='leave_apply'),
    path('leaves/approve/', views.LeaveApprovalView.as_view(), name='leave_approve'),
    path('leaves/balance/', views.LeaveBalanceView.as_view(), name='leave_balance'),

    # Payroll endpoints
    path('payroll/calculate/', views.PayrollCalculationView.as_view(), name='payroll_calculate'),
    path('payroll/generate/', views.PayrollGenerationView.as_view(), name='payroll_generate'),
    path('payroll/reports/', views.PayrollReportsView.as_view(), name='payroll_reports'),

    # Evaluation endpoints
    path('evaluations/templates/', views.EvaluationTemplatesView.as_view(), name='evaluation_templates'),
    path('evaluations/submit/', views.EvaluationSubmissionView.as_view(), name='evaluation_submit'),

    # Reports and analytics
    path('reports/dashboard/', views.HRDashboardView.as_view(), name='hr_dashboard'),
    path('reports/analytics/', views.HRAnalyticsView.as_view(), name='hr_analytics'),

    # ViewSet URLs
    path('', include(router.urls)),
]
