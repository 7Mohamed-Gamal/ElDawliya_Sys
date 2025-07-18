"""HR API URLs

This module defines URL patterns for the HR API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    CompanyViewSet, BranchViewSet, DepartmentViewSet, JobPositionViewSet,
    EmployeeViewSet, AttendanceRecordViewSet, WorkShiftViewSet, 
    AttendanceMachineViewSet, PayrollPeriodViewSet, SalaryComponentViewSet,
    EmployeeSalaryStructureViewSet, AnalyticsViewSet
)

# Create router and register viewsets
router = DefaultRouter()

# Organization endpoints
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'positions', JobPositionViewSet, basename='position')

# Employee endpoints
router.register(r'employees', EmployeeViewSet, basename='employee')

# Attendance endpoints
router.register(r'attendance-records', AttendanceRecordViewSet, basename='attendance-record')
router.register(r'work-shifts', WorkShiftViewSet, basename='work-shift')
router.register(r'attendance-machines', AttendanceMachineViewSet, basename='attendance-machine')

# Payroll endpoints
router.register(r'payroll-periods', PayrollPeriodViewSet, basename='payroll-period')
router.register(r'salary-components', SalaryComponentViewSet, basename='salary-component')
router.register(r'salary-structures', EmployeeSalaryStructureViewSet, basename='salary-structure')

# Analytics endpoints
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

app_name = 'hr_api'
urlpatterns = [
    path('', include(router.urls)),
]