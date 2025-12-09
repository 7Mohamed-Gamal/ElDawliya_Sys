"""
HR API Views
عروض API الموارد البشرية
"""

import logging
from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ...permissions import HasAPIAccess, ModulePermission
from ...pagination import StandardResultsSetPagination
from ...throttling import APIKeyRateThrottle
from .serializers import (
    EmployeeSerializer, DepartmentSerializer, JobPositionSerializer,
    AttendanceSerializer, LeaveSerializer, PayrollSerializer,
    EvaluationSerializer
)

# Import HR services
from apps.hr.services.employee_service import EmployeeService
from apps.hr.services.attendance_service import AttendanceService
from apps.hr.services.leave_service import LeaveService
from apps.hr.services.payroll_service import PayrollService
from apps.hr.services.evaluation_service import EvaluationService

logger = logging.getLogger(__name__)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for employee management
    مجموعة عروض إدارة الموظفين
    """
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('hr', 'view')]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [APIKeyRateThrottle]

    filterset_fields = ['department', 'job_position', 'emp_status', 'is_active']
    search_fields = ['first_name', 'last_name', 'emp_code', 'email']
    ordering_fields = ['created_at', 'hire_date', 'first_name', 'last_name']

    def get_queryset(self):
        """Get employees based on user permissions"""
        service = EmployeeService(user=self.request.user)
        return service.get_accessible_employees()

    def perform_create(self, serializer):
        """Create employee with service layer"""
        service = EmployeeService(user=self.request.user)
        employee = service.create_employee(serializer.validated_data)
        serializer.instance = employee

    def perform_update(self, serializer):
        """Update employee with service layer"""
        service = EmployeeService(user=self.request.user)
        employee = service.update_employee(
            serializer.instance,
            serializer.validated_data
        )
        serializer.instance = employee

    @swagger_auto_schema(
        operation_description="Get employee profile with full details",
        responses={200: EmployeeSerializer}
    )
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get complete employee profile"""
        employee = self.get_object()
        service = EmployeeService(user=request.user)

        profile_data = service.get_employee_profile(employee.id)
        return Response(profile_data)

    @swagger_auto_schema(
        operation_description="Get employee attendance summary",
        manual_parameters=[
            openapi.Parameter(
                'month',
                openapi.IN_QUERY,
                description="Month (1-12)",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                description="Year",
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        """Get employee attendance summary"""
        employee = self.get_object()

        month = request.query_params.get('month', datetime.now().month)
        year = request.query_params.get('year', datetime.now().year)

        attendance_service = AttendanceService(user=request.user)
        summary = attendance_service.get_employee_attendance_summary(
            employee.id, month, year
        )

        return Response(summary)

    @swagger_auto_schema(
        operation_description="Calculate employee service years",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'service_years': openapi.Schema(type=openapi.TYPE_NUMBER),
                'service_months': openapi.Schema(type=openapi.TYPE_INTEGER),
                'service_days': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        )}
    )
    @action(detail=True, methods=['get'])
    def service_years(self, request, pk=None):
        """Calculate employee service years"""
        employee = self.get_object()
        service = EmployeeService(user=request.user)

        service_data = service.calculate_service_period(employee)
        return Response(service_data)


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for department information
    مجموعة عروض معلومات الأقسام
    """
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Get departments based on user permissions"""
        service = EmployeeService(user=self.request.user)
        return service.get_accessible_departments()

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get employees in department"""
        department = self.get_object()
        service = EmployeeService(user=request.user)

        employees = service.get_department_employees(department.id)
        serializer = EmployeeSerializer(employees, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get department statistics"""
        department = self.get_object()
        service = EmployeeService(user=request.user)

        stats = service.get_department_statistics(department.id)
        return Response(stats)


class JobPositionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for job positions
    مجموعة عروض المناصب الوظيفية
    """
    serializer_class = JobPositionSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess]

    def get_queryset(self):
        """Get job positions"""
        service = EmployeeService(user=self.request.user)
        return service.get_job_positions()


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for attendance management
    مجموعة عروض إدارة الحضور
    """
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('hr', 'view')]
    pagination_class = StandardResultsSetPagination

    filterset_fields = ['employee', 'att_date', 'status']
    ordering_fields = ['att_date', 'check_in_time']

    def get_queryset(self):
        """Get attendance records based on permissions"""
        service = AttendanceService(user=self.request.user)
        return service.get_accessible_attendance()

    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """Bulk import apps.hr.attendance from device"""
        service = AttendanceService(user=request.user)

        result = service.import_attendance_data(request.data)
        return Response(result)


class LeaveViewSet(viewsets.ModelViewSet):
    """
    ViewSet for leave management
    مجموعة عروض إدارة الإجازات
    """
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('hr', 'view')]
    pagination_class = StandardResultsSetPagination

    filterset_fields = ['employee', 'leave_type', 'status', 'start_date']
    ordering_fields = ['start_date', 'created_at']

    def get_queryset(self):
        """Get leave requests based on permissions"""
        service = LeaveService(user=self.request.user)
        return service.get_accessible_leaves()

    def perform_create(self, serializer):
        """Create leave request with workflow"""
        service = LeaveService(user=self.request.user)
        leave = service.create_leave_request(serializer.validated_data)
        serializer.instance = leave

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve leave request"""
        leave = self.get_object()
        service = LeaveService(user=request.user)

        result = service.approve_leave(leave.id, request.data.get('comments', ''))
        return Response(result)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject leave request"""
        leave = self.get_object()
        service = LeaveService(user=request.user)

        result = service.reject_leave(leave.id, request.data.get('comments', ''))
        return Response(result)


class PayrollViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for payroll information
    مجموعة عروض معلومات الرواتب
    """
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('hr', 'view')]
    pagination_class = StandardResultsSetPagination

    filterset_fields = ['employee', 'pay_period', 'status']
    ordering_fields = ['pay_period', 'created_at']

    def get_queryset(self):
        """Get payroll records based on permissions"""
        service = PayrollService(user=self.request.user)
        return service.get_accessible_payroll()


class EvaluationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for employee evaluations
    مجموعة عروض تقييمات الموظفين
    """
    serializer_class = EvaluationSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('hr', 'view')]
    pagination_class = StandardResultsSetPagination

    filterset_fields = ['employee', 'evaluation_period', 'status']
    ordering_fields = ['evaluation_period', 'created_at']

    def get_queryset(self):
        """Get evaluations based on permissions"""
        service = EvaluationService(user=self.request.user)
        return service.get_accessible_evaluations()

    def perform_create(self, serializer):
        """Create evaluation with workflow"""
        service = EvaluationService(user=self.request.user)
        evaluation = service.create_evaluation(serializer.validated_data)
        serializer.instance = evaluation


# Additional API Views

class BulkEmployeeImportView(APIView):
    """
    Bulk import apps.hr.employees from Excel/CSV
    استيراد مجمع للموظفين من Excel/CSV
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('hr', 'add')]

    @swagger_auto_schema(
        operation_description="Bulk import apps.hr.employees from file",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'file': openapi.Schema(type=openapi.TYPE_FILE),
                'format': openapi.Schema(type=openapi.TYPE_STRING, enum=['excel', 'csv']),
            }
        )
    )
    def post(self, request):
        """Import employees from uploaded file"""
        service = EmployeeService(user=request.user)

        file_obj = request.FILES.get('file')
        file_format = request.data.get('format', 'excel')

        if not file_obj:
            return Response(
                {'error': 'لم يتم رفع ملف'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = service.bulk_import_employees(file_obj, file_format)
        return Response(result)


class EmployeeExportView(APIView):
    """
    Export employees to Excel/CSV
    تصدير الموظفين إلى Excel/CSV
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('hr', 'view')]

    @swagger_auto_schema(
        operation_description="Export employees to file",
        manual_parameters=[
            openapi.Parameter(
                'format',
                openapi.IN_QUERY,
                description="Export format",
                type=openapi.TYPE_STRING,
                enum=['excel', 'csv', 'pdf']
            ),
            openapi.Parameter(
                'department',
                openapi.IN_QUERY,
                description="Filter by department",
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request):
        """Export employees to specified format"""
        service = EmployeeService(user=request.user)

        export_format = request.query_params.get('format', 'excel')
        filters = {
            'department': request.query_params.get('department'),
            'status': request.query_params.get('status'),
        }

        result = service.export_employees(export_format, filters)
        return result


class ClockInView(APIView):
    """
    Employee clock-in endpoint
    نقطة نهاية تسجيل دخول الموظف
    """
    permission_classes = [IsAuthenticated, HasAPIAccess]

    @swagger_auto_schema(
        operation_description="Clock in employee",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'employee_id': openapi.Schema(type=openapi.TYPE_STRING),
                'location': openapi.Schema(type=openapi.TYPE_STRING),
                'notes': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request):
        """Clock in employee"""
        service = AttendanceService(user=request.user)

        employee_id = request.data.get('employee_id')
        location = request.data.get('location', '')
        notes = request.data.get('notes', '')

        result = service.clock_in(employee_id, location, notes)
        return Response(result)


class ClockOutView(APIView):
    """
    Employee clock-out endpoint
    نقطة نهاية تسجيل خروج الموظف
    """
    permission_classes = [IsAuthenticated, HasAPIAccess]

    @swagger_auto_schema(
        operation_description="Clock out employee",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'employee_id': openapi.Schema(type=openapi.TYPE_STRING),
                'location': openapi.Schema(type=openapi.TYPE_STRING),
                'notes': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request):
        """Clock out employee"""
        service = AttendanceService(user=request.user)

        employee_id = request.data.get('employee_id')
        location = request.data.get('location', '')
        notes = request.data.get('notes', '')

        result = service.clock_out(employee_id, location, notes)
        return Response(result)


class AttendanceSummaryView(APIView):
    """
    Attendance summary and reports
    ملخص الحضور والتقارير
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('hr', 'view')]

    @swagger_auto_schema(
        operation_description="Get attendance summary",
        manual_parameters=[
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Start date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="End date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'department',
                openapi.IN_QUERY,
                description="Department ID",
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request):
        """Get attendance summary"""
        service = AttendanceService(user=request.user)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        department = request.query_params.get('department')

        summary = service.get_attendance_summary(start_date, end_date, department)
        return Response(summary)


class HRDashboardView(APIView):
    """
    HR dashboard data
    بيانات لوحة تحكم الموارد البشرية
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('hr', 'view')]

    def get(self, request):
        """Get HR dashboard data"""
        service = EmployeeService(user=request.user)

        dashboard_data = service.get_hr_dashboard_data()
        return Response(dashboard_data)


class HRAnalyticsView(APIView):
    """
    HR analytics and insights
    تحليلات ورؤى الموارد البشرية
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('hr', 'view')]

    def get(self, request):
        """Get HR analytics"""
        service = EmployeeService(user=request.user)

        analytics = service.get_hr_analytics()
        return Response(analytics)
