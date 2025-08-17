"""
HR API URLs - روابط واجهات برمجة التطبيقات للموارد البشرية
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    # Basic ViewSets
    CompanyViewSet, BranchViewSet, DepartmentViewSet, JobPositionViewSet,
    
    # Employee ViewSets
    EmployeeViewSet,
    
    # Attendance ViewSets
    WorkShiftViewSet, AttendanceRecordViewSet,
    
    # Leave Management ViewSets
    LeaveTypeViewSet, LeaveRequestViewSet,
    
    # Statistics and Reports
    HRStatisticsViewSet,
)

app_name = 'hr_api'

# Create router and register viewsets
router = DefaultRouter()

# Basic endpoints
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'job-positions', JobPositionViewSet, basename='jobposition')

# Employee endpoints
router.register(r'employees', EmployeeViewSet, basename='employee')

# Attendance endpoints
router.register(r'work-shifts', WorkShiftViewSet, basename='workshift')
router.register(r'attendance-records', AttendanceRecordViewSet, basename='attendancerecord')

# Leave management endpoints
router.register(r'leave-types', LeaveTypeViewSet, basename='leavetype')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leaverequest')

# Statistics and reports
router.register(r'statistics', HRStatisticsViewSet, basename='statistics')

urlpatterns = [
    # JWT Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API endpoints
    path('', include(router.urls)),
    
    # Custom endpoints
    path('employees/statistics/', EmployeeViewSet.as_view({'get': 'statistics'}), name='employee-statistics'),
    path('statistics/dashboard/', HRStatisticsViewSet.as_view({'get': 'dashboard'}), name='dashboard-statistics'),
    path('statistics/attendance-report/', HRStatisticsViewSet.as_view({'get': 'attendance_report'}), name='attendance-report'),
    path('statistics/payroll-summary/', HRStatisticsViewSet.as_view({'get': 'payroll_summary'}), name='payroll-summary'),
]

# Add API documentation if available
try:
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    from rest_framework import permissions
    
    schema_view = get_schema_view(
        openapi.Info(
            title="HR Management API",
            default_version='v1',
            description="واجهات برمجة التطبيقات لنظام إدارة الموارد البشرية",
            terms_of_service="https://www.example.com/policies/terms/",
            contact=openapi.Contact(email="contact@hrmanagement.local"),
            license=openapi.License(name="MIT License"),
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
        patterns=[path('api/hr/', include('Hr.api.urls'))],
    )
    
    urlpatterns += [
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    ]
    
except ImportError:
    # drf_yasg not installed
    pass