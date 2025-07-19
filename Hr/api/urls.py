"""HR API URLs

This module defines URL patterns for the HR API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    # Employee ViewSets
    EmployeeViewSet,
    EmployeeDocumentViewSet,
    
    # Core ViewSets
    CompanyViewSet,
    BranchViewSet,
    DepartmentViewSet,
    JobPositionViewSet,
    JobLevelViewSet,
    
    # Attendance ViewSets
    AttendanceRecordViewSet,
    WorkShiftViewSet,
    AttendanceMachineViewSet,
    
    # Leave ViewSets
    LeaveTypeViewSet,
    LeaveRequestViewSet,
    LeaveBalanceViewSet,
    
    # Payroll ViewSets
    SalaryComponentViewSet,
    PayrollPeriodViewSet,
    PayrollEntryViewSet,
    EmployeeSalaryStructureViewSet,
    
    # Analytics ViewSets
    AnalyticsViewSet,
)

# Create router and register viewsets
router = DefaultRouter()

# Core/Organization endpoints
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'job-positions', JobPositionViewSet, basename='job-position')
router.register(r'job-levels', JobLevelViewSet, basename='job-level')

# Employee endpoints
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'employee-documents', EmployeeDocumentViewSet, basename='employee-document')

# Attendance endpoints
router.register(r'attendance-records', AttendanceRecordViewSet, basename='attendance-record')
router.register(r'work-shifts', WorkShiftViewSet, basename='work-shift')
router.register(r'attendance-machines', AttendanceMachineViewSet, basename='attendance-machine')

# Leave endpoints
router.register(r'leave-types', LeaveTypeViewSet, basename='leave-type')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'leave-balances', LeaveBalanceViewSet, basename='leave-balance')

# Payroll endpoints
router.register(r'salary-components', SalaryComponentViewSet, basename='salary-component')
router.register(r'payroll-periods', PayrollPeriodViewSet, basename='payroll-period')
router.register(r'payroll-entries', PayrollEntryViewSet, basename='payroll-entry')
router.register(r'employee-salary-structures', EmployeeSalaryStructureViewSet, basename='employee-salary-structure')

# Analytics endpoints
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

app_name = 'hr_api'
urlpatterns = [
    path('', include(router.urls)),
]