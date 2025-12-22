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

    # Leave management endpoints (using ViewSet)
    path('leaves/', views.LeaveViewSet.as_view({'get': 'list', 'post': 'create'}), name='leaves'),
    path('leaves/<int:pk>/', views.LeaveViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='leave_detail'),

    # Payroll endpoints (using ViewSet)
    path('payroll/', views.PayrollViewSet.as_view({'get': 'list'}), name='payroll'),
    path('payroll/<int:pk>/', views.PayrollViewSet.as_view({'get': 'retrieve'}), name='payroll_detail'),

    # Evaluation endpoints (using ViewSet)
    path('evaluations/', views.EvaluationViewSet.as_view({'get': 'list', 'post': 'create'}), name='evaluations'),
    path('evaluations/<int:pk>/', views.EvaluationViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='evaluation_detail'),

    # Reports and analytics
    path('reports/dashboard/', views.HRDashboardView.as_view(), name='hr_dashboard'),
    path('reports/analytics/', views.HRAnalyticsView.as_view(), name='hr_analytics'),

    # ViewSet URLs
    path('', include(router.urls)),
]
