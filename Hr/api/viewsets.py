"""
HR API ViewSets - مجموعات عروض واجهة برمجة التطبيقات للموارد البشرية
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import date, datetime, timedelta
import logging

from .permissions import (
    IsHRManager, IsHRStaff, IsEmployeeOwnerOrHRStaff, IsManagerOrHRStaff,
    CanApproveLeave, CanManageAttendance, CanViewPayroll, CanManagePayroll,
    ReadOnlyOrHRStaff, DepartmentBasedPermission
)

from .filters import (
    EmployeeFilter, AttendanceRecordFilter, LeaveRequestFilter, AttendanceSummaryFilter
)

from ..models import (
    Company, Branch, Department, JobPosition, Employee,
    EmployeeEducation, EmployeeInsurance, EmployeeVehicle, EmployeeFile,
    WorkShiftEnhanced, AttendanceMachineEnhanced, AttendanceRecordEnhanced,
    AttendanceSummary, EmployeeShiftAssignment,
    LeaveType, LeaveRequest, LeaveBalance
)

from .serializers import (
    CompanySerializer, BranchSerializer, DepartmentSerializer, JobPositionSerializer,
    EmployeeBasicSerializer, EmployeeDetailSerializer, EmployeeCreateUpdateSerializer,
    EmployeeEducationSerializer, EmployeeInsuranceSerializer, EmployeeVehicleSerializer,
    EmployeeFileSerializer, WorkShiftSerializer, AttendanceMachineSerializer,
    AttendanceRecordSerializer, AttendanceSummarySerializer, EmployeeShiftAssignmentSerializer,
    LeaveTypeSerializer, LeaveRequestSerializer, LeaveBalanceSerializer
)

from ..services import (
    EmployeeService, AttendanceService, PayrollService, LeaveService
)

logger = logging.getLogger('hr_system')


# =============================================================================
# BASIC VIEWSETS - مجموعات العروض الأساسية
# =============================================================================

class CompanyViewSet(viewsets.ModelViewSet):
    """مجموعة عروض الشركة"""
    
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'name_english', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class BranchViewSet(viewsets.ModelViewSet):
    """مجموعة عروض الفرع"""
    
    queryset = Branch.objects.select_related('company', 'manager')
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['company__name', 'name']


class DepartmentViewSet(viewsets.ModelViewSet):
    """مجموعة عروض القسم"""
    
    queryset = Department.objects.select_related('company', 'branch', 'manager', 'parent_department')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'branch', 'parent_department', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['company__name', 'name']


class JobPositionViewSet(viewsets.ModelViewSet):
    """مجموعة عروض المنصب الوظيفي"""
    
    queryset = JobPosition.objects.select_related('company', 'department')
    serializer_class = JobPositionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'department', 'level', 'is_active']
    search_fields = ['title', 'title_english', 'code']
    ordering_fields = ['title', 'level', 'created_at']
    ordering = ['company__name', 'department__name', 'title']#
 =============================================================================
# EMPLOYEE VIEWSETS - مجموعات عروض الموظفين
# =============================================================================

class EmployeeViewSet(viewsets.ModelViewSet):
    """مجموعة عروض الموظفين الشاملة"""
    
    queryset = Employee.objects.select_related(
        'company', 'branch', 'department', 'job_position', 'direct_manager'
    ).prefetch_related(
        'education_records', 'insurance_records', 'vehicle_records', 'files'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'company', 'branch', 'department', 'job_position', 'direct_manager',
        'employment_type', 'status', 'gender', 'marital_status', 'is_active'
    ]
    search_fields = [
        'employee_number', 'first_name', 'last_name', 'full_name',
        'email', 'phone_primary', 'national_id'
    ]
    ordering_fields = ['employee_number', 'full_name', 'hire_date', 'created_at']
    ordering = ['employee_number']
    
    def get_serializer_class(self):
        """اختيار المسلسل المناسب"""
        if self.action == 'list':
            return EmployeeBasicSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateUpdateSerializer
        else:
            return EmployeeDetailSerializer
    
    def perform_create(self, serializer):
        """إنشاء موظف جديد"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def search_advanced(self, request):
        """البحث المتقدم في الموظفين"""
        try:
            employee_service = EmployeeService()
            
            # Build search parameters from request
            search_params = {
                'search_text': request.query_params.get('search_text'),
                'department_ids': request.query_params.getlist('department_ids'),
                'branch_ids': request.query_params.getlist('branch_ids'),
                'job_position_ids': request.query_params.getlist('job_position_ids'),
                'employment_types': request.query_params.getlist('employment_types'),
                'statuses': request.query_params.getlist('statuses'),
                'hire_date_from': request.query_params.get('hire_date_from'),
                'hire_date_to': request.query_params.get('hire_date_to'),
                'age_from': request.query_params.get('age_from'),
                'age_to': request.query_params.get('age_to'),
                'salary_from': request.query_params.get('salary_from'),
                'salary_to': request.query_params.get('salary_to'),
                'education_levels': request.query_params.getlist('education_levels'),
                'has_manager': request.query_params.get('has_manager'),
                'order_by': request.query_params.get('order_by', 'employee_number'),
                'order_desc': request.query_params.get('order_desc') == 'true',
                'page': int(request.query_params.get('page', 1)),
                'page_size': int(request.query_params.get('page_size', 50))
            }
            
            # Remove None values
            search_params = {k: v for k, v in search_params.items() if v is not None and v != []}
            
            result = employee_service.search_employees_advanced(search_params)
            
            # Serialize employees
            serializer = EmployeeBasicSerializer(result['employees'], many=True)
            
            return Response({
                'employees': serializer.data,
                'pagination': {
                    'total_count': result['total_count'],
                    'page': result['page'],
                    'page_size': result['page_size'],
                    'total_pages': result['total_pages']
                }
            })
            
        except Exception as e:
            logger.error(f"Error in advanced employee search: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """إحصائيات الموظفين"""
        try:
            employee_service = EmployeeService()
            
            # Build filters from request
            filters = {}
            if request.query_params.get('company'):
                filters['company_id'] = request.query_params.get('company')
            if request.query_params.get('department'):
                filters['department_id'] = request.query_params.get('department')
            if request.query_params.get('branch'):
                filters['branch_id'] = request.query_params.get('branch')
            
            stats = employee_service.get_employee_statistics(filters)
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error getting employee statistics: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """تحديث مجمع للموظفين"""
        try:
            employee_service = EmployeeService()
            
            employee_ids = request.data.get('employee_ids', [])
            update_data = request.data.get('update_data', {})
            
            if not employee_ids:
                return Response(
                    {'error': 'معرفات الموظفين مطلوبة'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = employee_service.bulk_update_employees(
                employee_ids, update_data, request.user
            )
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error in bulk employee update: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        """الهيكل الهرمي للموظف"""
        try:
            employee_service = EmployeeService()
            hierarchy = employee_service.get_employee_hierarchy(pk)
            return Response(hierarchy)
            
        except Exception as e:
            logger.error(f"Error getting employee hierarchy: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def cost_calculation(self, request, pk=None):
        """حساب تكلفة الموظف"""
        try:
            employee_service = EmployeeService()
            include_benefits = request.query_params.get('include_benefits', 'true') == 'true'
            
            cost = employee_service.calculate_employee_cost(pk, include_benefits)
            return Response(cost)
            
        except Exception as e:
            logger.error(f"Error calculating employee cost: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def expiring_documents(self, request):
        """الموظفون ذوو الوثائق المنتهية الصلاحية"""
        try:
            employee_service = EmployeeService()
            days_ahead = int(request.query_params.get('days_ahead', 30))
            
            employees = employee_service.get_employees_expiring_documents(days_ahead)
            return Response(employees)
            
        except Exception as e:
            logger.error(f"Error getting employees with expiring documents: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class EmployeeEducationViewSet(viewsets.ModelViewSet):
    """مجموعة عروض تعليم الموظف"""
    
    queryset = EmployeeEducation.objects.select_related('employee')
    serializer_class = EmployeeEducationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'education_type', 'is_verified']
    search_fields = ['degree_name', 'institution_name', 'field_of_study']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-end_date']


class EmployeeInsuranceViewSet(viewsets.ModelViewSet):
    """مجموعة عروض تأمين الموظف"""
    
    queryset = EmployeeInsurance.objects.select_related('employee')
    serializer_class = EmployeeInsuranceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'insurance_type', 'status']
    search_fields = ['provider_name', 'policy_number']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']


class EmployeeVehicleViewSet(viewsets.ModelViewSet):
    """مجموعة عروض مركبة الموظف"""
    
    queryset = EmployeeVehicle.objects.select_related('employee')
    serializer_class = EmployeeVehicleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'vehicle_type', 'ownership_type']
    search_fields = ['make', 'model', 'license_plate']
    ordering_fields = ['year', 'registration_date', 'created_at']
    ordering = ['-year']


class EmployeeFileViewSet(viewsets.ModelViewSet):
    """مجموعة عروض ملف الموظف"""
    
    queryset = EmployeeFile.objects.select_related('employee', 'uploaded_by')
    serializer_class = EmployeeFileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'file_type', 'is_confidential']
    search_fields = ['title', 'description']
    ordering_fields = ['expiry_date', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """إنشاء ملف جديد"""
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """الملفات المنتهية الصلاحية قريباً"""
        days_ahead = int(request.query_params.get('days_ahead', 30))
        expiry_date = date.today() + timedelta(days=days_ahead)
        
        queryset = self.get_queryset().filter(
            expiry_date__lte=expiry_date,
            expiry_date__gte=date.today()
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)# ======
=======================================================================
# ATTENDANCE VIEWSETS - مجموعات عروض الحضور
# =============================================================================

class WorkShiftViewSet(viewsets.ModelViewSet):
    """مجموعة عروض الوردية"""
    
    queryset = WorkShiftEnhanced.objects.select_related('company')
    serializer_class = WorkShiftSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'shift_type', 'is_active']
    search_fields = ['name', 'name_english', 'code']
    ordering_fields = ['name', 'start_time', 'created_at']
    ordering = ['company__name', 'name']
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """جدول الوردية"""
        try:
            attendance_service = AttendanceService()
            
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if not start_date or not end_date:
                return Response(
                    {'error': 'تاريخ البداية والنهاية مطلوبان'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            schedule = attendance_service.get_shift_schedule(pk, start_date, end_date)
            return Response(schedule)
            
        except Exception as e:
            logger.error(f"Error getting shift schedule: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AttendanceMachineViewSet(viewsets.ModelViewSet):
    """مجموعة عروض جهاز الحضور"""
    
    queryset = AttendanceMachineEnhanced.objects.select_related('company', 'branch')
    serializer_class = AttendanceMachineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'branch', 'machine_type', 'status', 'is_active']
    search_fields = ['name', 'serial_number', 'location']
    ordering_fields = ['name', 'status', 'last_sync', 'created_at']
    ordering = ['company__name', 'branch__name', 'name']
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """مزامنة جهاز الحضور"""
        try:
            attendance_service = AttendanceService()
            result = attendance_service.sync_attendance_machine(pk)
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error syncing attendance machine: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """مجموعة عروض سجل الحضور"""
    
    queryset = AttendanceRecordEnhanced.objects.select_related(
        'employee', 'machine', 'shift'
    )
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'employee', 'machine', 'shift', 'date', 'attendance_type',
        'status', 'verification_method', 'is_approved'
    ]
    search_fields = ['employee__full_name', 'employee__employee_number']
    ordering_fields = ['date', 'timestamp', 'created_at']
    ordering = ['-date', '-timestamp']
    
    @action(detail=False, methods=['post'])
    def record_attendance(self, request):
        """تسجيل الحضور"""
        try:
            attendance_service = AttendanceService()
            
            employee_id = request.data.get('employee_id')
            attendance_type = request.data.get('attendance_type')
            machine_id = request.data.get('machine_id')
            location_data = request.data.get('location_data')
            verification_data = request.data.get('verification_data')
            
            if not employee_id or not attendance_type:
                return Response(
                    {'error': 'معرف الموظف ونوع الحضور مطلوبان'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = attendance_service.record_attendance(
                employee_id, attendance_type, machine_id,
                location_data, verification_data
            )
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error recording attendance: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """استيراد مجمع لسجلات الحضور"""
        try:
            attendance_service = AttendanceService()
            
            attendance_data = request.data.get('attendance_data', [])
            machine_id = request.data.get('machine_id')
            
            if not attendance_data:
                return Response(
                    {'error': 'بيانات الحضور مطلوبة'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = attendance_service.bulk_import_attendance(attendance_data, machine_id)
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error in bulk attendance import: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def anomalies(self, request):
        """كشف الشذوذ في الحضور"""
        try:
            attendance_service = AttendanceService()
            
            employee_id = request.query_params.get('employee_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            date_range = None
            if start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                date_range = (start_date, end_date)
            
            anomalies = attendance_service.detect_attendance_anomalies(employee_id, date_range)
            return Response(anomalies)
            
        except Exception as e:
            logger.error(f"Error detecting attendance anomalies: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AttendanceSummaryViewSet(viewsets.ModelViewSet):
    """مجموعة عروض ملخص الحضور"""
    
    queryset = AttendanceSummary.objects.select_related('employee', 'shift')
    serializer_class = AttendanceSummarySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'employee', 'shift', 'date', 'is_present', 'is_absent',
        'is_late', 'is_early_leave', 'is_on_leave', 'is_holiday'
    ]
    search_fields = ['employee__full_name', 'employee__employee_number']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']
    
    @action(detail=False, methods=['get'])
    def employee_summary(self, request):
        """ملخص حضور الموظف"""
        try:
            attendance_service = AttendanceService()
            
            employee_id = request.query_params.get('employee_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if not employee_id or not start_date or not end_date:
                return Response(
                    {'error': 'معرف الموظف وتاريخ البداية والنهاية مطلوبة'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            summary = attendance_service.get_employee_attendance_summary(
                employee_id, start_date, end_date
            )
            
            return Response(summary)
            
        except Exception as e:
            logger.error(f"Error getting employee attendance summary: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def department_report(self, request):
        """تقرير حضور القسم"""
        try:
            attendance_service = AttendanceService()
            
            department_id = request.query_params.get('department_id')
            date_filter = request.query_params.get('date')
            
            if not department_id or not date_filter:
                return Response(
                    {'error': 'معرف القسم والتاريخ مطلوبان'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            date_filter = datetime.strptime(date_filter, '%Y-%m-%d').date()
            
            report = attendance_service.get_department_attendance_report(
                department_id, date_filter
            )
            
            return Response(report)
            
        except Exception as e:
            logger.error(f"Error getting department attendance report: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class EmployeeShiftAssignmentViewSet(viewsets.ModelViewSet):
    """مجموعة عروض تعيين وردية الموظف"""
    
    queryset = EmployeeShiftAssignment.objects.select_related(
        'employee', 'shift', 'assigned_by'
    )
    serializer_class = EmployeeShiftAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'shift', 'is_permanent', 'is_active']
    search_fields = ['employee__full_name', 'employee__employee_number', 'shift__name']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    
    def perform_create(self, serializer):
        """إنشاء تعيين وردية جديد"""
        serializer.save(assigned_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def assign_shift(self, request):
        """تعيين موظف لوردية"""
        try:
            attendance_service = AttendanceService()
            
            employee_id = request.data.get('employee_id')
            shift_id = request.data.get('shift_id')
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            
            if not employee_id or not shift_id or not start_date:
                return Response(
                    {'error': 'معرف الموظف ومعرف الوردية وتاريخ البداية مطلوبة'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            result = attendance_service.assign_employee_to_shift(
                employee_id, shift_id, start_date, end_date
            )
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error assigning employee to shift: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )# =
============================================================================
# LEAVE VIEWSETS - مجموعات عروض الإجازات
# =============================================================================

class LeaveTypeViewSet(viewsets.ModelViewSet):
    """مجموعة عروض نوع الإجازة"""
    
    queryset = LeaveType.objects.select_related('company')
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'company', 'category', 'accrual_method', 'requires_approval',
        'is_paid', 'gender_restriction', 'employment_type_restriction', 'is_active'
    ]
    search_fields = ['name', 'name_english', 'code']
    ordering_fields = ['name', 'category', 'default_days', 'created_at']
    ordering = ['company__name', 'name']


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """مجموعة عروض طلب الإجازة"""
    
    queryset = LeaveRequest.objects.select_related(
        'employee', 'leave_type', 'approved_by', 'rejected_by'
    )
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'employee', 'leave_type', 'status', 'priority',
        'approved_by', 'rejected_by'
    ]
    search_fields = ['employee__full_name', 'employee__employee_number', 'reason']
    ordering_fields = ['start_date', 'end_date', 'requested_at', 'created_at']
    ordering = ['-requested_at']
    
    @action(detail=False, methods=['post'])
    def create_request(self, request):
        """إنشاء طلب إجازة"""
        try:
            leave_service = LeaveService()
            
            employee_id = request.data.get('employee_id')
            leave_type_id = request.data.get('leave_type_id')
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            reason = request.data.get('reason')
            
            if not all([employee_id, leave_type_id, start_date, end_date]):
                return Response(
                    {'error': 'جميع الحقول الأساسية مطلوبة'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            result = leave_service.create_leave_request(
                employee_id, leave_type_id, start_date, end_date, reason
            )
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error creating leave request: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """الموافقة على طلب الإجازة"""
        try:
            leave_service = LeaveService()
            
            comments = request.data.get('comments')
            approved_days = request.data.get('approved_days')
            
            result = leave_service.approve_leave_request(
                pk, request.user.id, comments, approved_days
            )
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error approving leave request: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """رفض طلب الإجازة"""
        try:
            leave_service = LeaveService()
            
            rejection_reason = request.data.get('rejection_reason')
            
            if not rejection_reason:
                return Response(
                    {'error': 'سبب الرفض مطلوب'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = leave_service.reject_leave_request(
                pk, request.user.id, rejection_reason
            )
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error rejecting leave request: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def leave_report(self, request):
        """تقرير الإجازات"""
        try:
            leave_service = LeaveService()
            
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            department_id = request.query_params.get('department_id')
            leave_type_id = request.query_params.get('leave_type_id')
            
            if not start_date or not end_date:
                return Response(
                    {'error': 'تاريخ البداية والنهاية مطلوبان'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            report = leave_service.get_leave_report(
                start_date, end_date, department_id, leave_type_id
            )
            
            return Response(report)
            
        except Exception as e:
            logger.error(f"Error generating leave report: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def leave_calendar(self, request):
        """تقويم الإجازات"""
        try:
            leave_service = LeaveService()
            
            year = int(request.query_params.get('year', date.today().year))
            month = int(request.query_params.get('month', date.today().month))
            department_id = request.query_params.get('department_id')
            
            calendar_data = leave_service.get_leave_calendar(year, month, department_id)
            return Response(calendar_data)
            
        except Exception as e:
            logger.error(f"Error generating leave calendar: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    """مجموعة عروض رصيد الإجازة"""
    
    queryset = LeaveBalance.objects.select_related('employee', 'leave_type')
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'leave_type', 'year', 'is_active']
    search_fields = ['employee__full_name', 'employee__employee_number']
    ordering_fields = ['year', 'allocated_days', 'remaining_days', 'created_at']
    ordering = ['-year', 'employee__employee_number']
    
    @action(detail=False, methods=['get'])
    def employee_balance(self, request):
        """رصيد إجازات الموظف"""
        try:
            leave_service = LeaveService()
            
            employee_id = request.query_params.get('employee_id')
            year = request.query_params.get('year')
            
            if not employee_id:
                return Response(
                    {'error': 'معرف الموظف مطلوب'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if year:
                year = int(year)
            
            balance = leave_service.get_employee_leave_balance(employee_id, year)
            return Response(balance)
            
        except Exception as e:
            logger.error(f"Error getting employee leave balance: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def allocate_annual(self, request):
        """تخصيص الإجازات السنوية"""
        try:
            leave_service = LeaveService()
            
            employee_id = request.data.get('employee_id')
            year = request.data.get('year')
            leave_allocations = request.data.get('leave_allocations', {})
            
            if not all([employee_id, year, leave_allocations]):
                return Response(
                    {'error': 'جميع الحقول مطلوبة'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = leave_service.allocate_annual_leave(
                employee_id, int(year), leave_allocations
            )
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error allocating annual leave: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def bulk_allocate(self, request):
        """تخصيص مجمع للإجازات"""
        try:
            leave_service = LeaveService()
            
            employee_ids = request.data.get('employee_ids', [])
            year = request.data.get('year')
            leave_type_id = request.data.get('leave_type_id')
            days = request.data.get('days')
            
            if not all([employee_ids, year, leave_type_id, days]):
                return Response(
                    {'error': 'جميع الحقول مطلوبة'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = leave_service.bulk_allocate_leave(
                employee_ids, int(year), leave_type_id, int(days)
            )
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error in bulk leave allocation: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )