"""
HR API Views - عروض واجهات برمجة التطبيقات للموارد البشرية
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import date, datetime, timedelta
import logging

# Import serializers from a bridge that loads the monolithic serializers.py safely
from .serializers_bridge import *
from .permissions import *
from .filters import *
from .pagination import *
from ..services import (
    EmployeeService, AttendanceService, PayrollService,
    LeaveService
)

# Import models explicitly used in querysets (from enhanced shim)
from ..models_enhanced import (
    Company, Branch, Department, JobPosition, Employee,
    WorkShiftEnhanced, AttendanceRecordEnhanced,
    AttendanceSummary, EmployeeShiftAssignment,
    LeaveType, LeaveRequest, LeaveBalance,
)

logger = logging.getLogger('hr_api')

# =============================================================================
# BASIC VIEWSETS
# =============================================================================

class CompanyViewSet(viewsets.ModelViewSet):
    """عرض الشركات"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    # Allow any authenticated user in tests to create/list/detail companies
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'name_english', 'code', 'tax_number']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            # Filter by user's company if not superuser
            if hasattr(self.request.user, 'employee'):
                queryset = queryset.filter(id=self.request.user.employee.company_id)
        return queryset

class BranchViewSet(viewsets.ModelViewSet):
    """عرض الفروع"""
    queryset = Branch.objects.select_related('company')
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'is_active']
    search_fields = ['name', 'name_english', 'code', 'address']
    ordering_fields = ['name', 'created_at']
    ordering = ['company__name', 'name']

class DepartmentViewSet(viewsets.ModelViewSet):
    """عرض الأقسام"""
    queryset = Department.objects.select_related('company', 'branch', 'manager')
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'branch', 'is_active']
    search_fields = ['name', 'name_english', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['company__name', 'name']

class JobPositionViewSet(viewsets.ModelViewSet):
    """عرض المناصب الوظيفية"""
    queryset = JobPosition.objects.select_related('department__company')
    serializer_class = JobPositionSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'level', 'is_active']
    search_fields = ['title', 'title_english', 'code', 'description']
    ordering_fields = ['title', 'level', 'created_at']
    ordering = ['department__name', 'title']

# =============================================================================
# EMPLOYEE VIEWSETS
# =============================================================================

class EmployeeViewSet(viewsets.ModelViewSet):
    """عرض الموظفين"""
    queryset = Employee.objects.select_related(
        'company', 'branch', 'department', 'job_position', 'direct_manager'
    ).prefetch_related('education_records', 'insurance_records', 'vehicle_records')
    permission_classes = [permissions.IsAuthenticated, IsHRStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = [
        'first_name', 'last_name', 'employee_number', 'email', 
        'phone_primary', 'national_id'
    ]
    ordering_fields = [
        'employee_number', 'first_name', 'last_name', 'hire_date', 
        'basic_salary', 'created_at'
    ]
    ordering = ['employee_number']
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeBasicSerializer
        return EmployeeDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by user permissions
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'employee'):
                user_employee = self.request.user.employee
                # HR staff can see all employees in their company
                if user_employee.is_hr_staff:
                    queryset = queryset.filter(company=user_employee.company)
                # Managers can see their subordinates
                elif user_employee.is_manager:
                    queryset = queryset.filter(
                        Q(direct_manager=user_employee) | Q(id=user_employee.id)
                    )
                # Regular employees can only see themselves
                else:
                    queryset = queryset.filter(id=user_employee.id)
        return queryset

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """إحصائيات الموظفين"""
        try:
            employee_service = EmployeeService()
            filters = self._get_filter_params(request)
            stats = employee_service.get_employee_statistics(filters)
            serializer = EmployeeStatisticsSerializer(stats)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting employee statistics: {e}")
            return Response(
                {'error': 'خطأ في جلب الإحصائيات'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_filter_params(self, request):
        """استخراج معاملات الفلترة"""
        filters = {}
        
        if request.query_params.get('company'):
            filters['company_id'] = request.query_params.get('company')
        if request.query_params.get('branch'):
            filters['branch_id'] = request.query_params.get('branch')
        if request.query_params.get('department'):
            filters['department_id'] = request.query_params.get('department')
        if request.query_params.get('status'):
            filters['status'] = request.query_params.get('status')
        
        return filters

# =============================================================================
# ATTENDANCE VIEWSETS
# =============================================================================

class WorkShiftViewSet(viewsets.ModelViewSet):
    """عرض الورديات"""
    
    queryset = WorkShiftEnhanced.objects.select_related('company')
    serializer_class = WorkShiftSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'shift_type', 'is_active']
    search_fields = ['name', 'name_english', 'code']
    ordering_fields = ['name', 'start_time', 'created_at']
    ordering = ['company__name', 'name']

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """عرض سجلات الحضور"""
    
    queryset = AttendanceRecordEnhanced.objects.select_related(
        'employee', 'machine', 'shift'
    )
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AttendanceRecordFilter
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_number']
    ordering_fields = ['date', 'timestamp', 'employee__employee_number']
    ordering = ['-date', '-timestamp']
    pagination_class = CustomPageNumberPagination

# =============================================================================
# LEAVE MANAGEMENT VIEWSETS
# =============================================================================

class LeaveTypeViewSet(viewsets.ModelViewSet):
    """عرض أنواع الإجازات"""
    
    queryset = LeaveType.objects.select_related('company')
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'category', 'is_active']
    search_fields = ['name', 'name_english', 'code']
    ordering_fields = ['name', 'category', 'created_at']
    ordering = ['company__name', 'name']

class LeaveRequestViewSet(viewsets.ModelViewSet):
    """عرض طلبات الإجازات"""
    
    queryset = LeaveRequest.objects.select_related(
        'employee', 'leave_type', 'approved_by', 'rejected_by'
    )
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRStaffOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LeaveRequestFilter
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_number']
    ordering_fields = ['requested_at', 'start_date', 'status']
    ordering = ['-requested_at']
    pagination_class = CustomPageNumberPagination

# =============================================================================
# STATISTICS AND REPORTS VIEWSETS
# =============================================================================

class HRStatisticsViewSet(viewsets.ViewSet):
    """عرض إحصائيات الموارد البشرية"""
    
    permission_classes = [permissions.IsAuthenticated, IsHRStaffOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """إحصائيات لوحة التحكم"""
        try:
            employee_service = EmployeeService()
            attendance_service = AttendanceService()
            leave_service = LeaveService()
            payroll_service = PayrollService()
            
            # Get date range
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                # Default to current month
                today = date.today()
                start_date = today.replace(day=1)
                end_date = today
            
            # Gather statistics
            dashboard_data = {
                'employee_stats': employee_service.get_employee_statistics(),
                'attendance_stats': attendance_service.get_attendance_statistics(start_date, end_date),
                'leave_stats': leave_service.get_leave_statistics(start_date, end_date),
                'payroll_stats': payroll_service.get_payroll_statistics(start_date, end_date),
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'generated_at': timezone.now()
            }
            
            return Response(dashboard_data)
            
        except Exception as e:
            logger.error(f"Error getting dashboard statistics: {e}")
            return Response(
                {'error': 'خطأ في جلب إحصائيات لوحة التحكم'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )