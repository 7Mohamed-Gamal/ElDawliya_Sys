"""
واجهة برمجة التطبيقات للموارد البشرية (HR API)

هذا الملف يحتوي على واجهات برمجة REST لنظام الموارد البشرية
للسماح بالتكامل مع الأنظمة الأخرى مثل الأنظمة المالية والمحاسبية
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q

from Hr.models.employee.employee_models import Employee
from Hr.models.attendance.attendance_models import AttendanceRecord
from Hr.models.leave.leave_models import LeaveRequest, LeaveBalance
from Hr.models.payroll.payroll_models import Payroll, PayrollEmployee
from Hr.serializers.api_serializers import (
    EmployeeSerializer, AttendanceRecordSerializer, LeaveRequestSerializer,
    LeaveBalanceSerializer, PayrollEmployeeSerializer, PayrollSerializer
)
from Hr.services.integration_service import HrIntegrationService

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    واجهة برمجة للموظفين

    توفر عمليات CRUD للموظفين مع دعم التصفية والبحث
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'department', 'job_position', 'employment_status', 'is_active']
    search_fields = ['first_name', 'last_name', 'employee_id', 'national_id', 'email']
    ordering_fields = ['first_name', 'last_name', 'joining_date', 'department__name']

    def get_queryset(self):
        """
        تقييد النتائج حسب شركة المستخدم إن وجدت
        """
        queryset = super().get_queryset()
        user = self.request.user

        if hasattr(user, 'employee') and user.employee and user.employee.company:
            queryset = queryset.filter(company=user.employee.company)

        return queryset

    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """
        الحصول على سجلات حضور الموظف
        """
        employee = self.get_object()

        # فلتر حسب الفترة إن وجد
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = AttendanceRecord.objects.filter(employee=employee)

        if start_date:
            queryset = queryset.filter(attendance_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(attendance_date__lte=end_date)

        # ترتيب حسب التاريخ تنازلياً
        queryset = queryset.order_by('-attendance_date')

        serializer = AttendanceRecordSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def leave_balance(self, request, pk=None):
        """
        الحصول على أرصدة إجازات الموظف
        """
        employee = self.get_object()
        year = request.query_params.get('year', timezone.now().year)

        queryset = LeaveBalance.objects.filter(employee=employee, year=year)
        serializer = LeaveBalanceSerializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def payroll_history(self, request, pk=None):
        """
        الحصول على سجل رواتب الموظف
        """
        employee = self.get_object()
        year = request.query_params.get('year', timezone.now().year)

        queryset = PayrollEmployee.objects.filter(employee=employee, payroll__payroll_year=year)
        serializer = PayrollEmployeeSerializer(queryset, many=True)

        return Response(serializer.data)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """
    واجهة برمجة لسجلات الحضور والانصراف

    توفر عمليات CRUD لسجلات الحضور مع دعم التصفية والبحث
    """
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['company', 'employee', 'attendance_date', 'status']
    ordering_fields = ['attendance_date', 'check_in', 'check_out']

    def get_queryset(self):
        """
        تقييد النتائج حسب شركة المستخدم إن وجدت
        """
        queryset = super().get_queryset()
        user = self.request.user

        if hasattr(user, 'employee') and user.employee and user.employee.company:
            queryset = queryset.filter(company=user.employee.company)

        return queryset

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        إنشاء سجلات حضور متعددة دفعة واحدة
        """
        serializer = AttendanceRecordSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    واجهة برمجة لطلبات الإجازات

    توفر عمليات CRUD لطلبات الإجازات مع دعم التصفية والبحث
    """
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['company', 'employee', 'leave_type', 'status', 'start_date']
    ordering_fields = ['start_date', 'created_at', 'status']

    def get_queryset(self):
        """
        تقييد النتائج حسب شركة المستخدم إن وجدت
        """
        queryset = super().get_queryset()
        user = self.request.user

        if hasattr(user, 'employee') and user.employee and user.employee.company:
            queryset = queryset.filter(company=user.employee.company)

        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        الموافقة على طلب إجازة
        """
        leave_request = self.get_object()

        if leave_request.status != 'pending':
            return Response(
                {'detail': 'لا يمكن الموافقة على طلب إجازة غير معلق.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # تحديث حالة طلب الإجازة
        leave_request.status = 'approved'
        leave_request.approved_by = request.user
        leave_request.approved_at = timezone.now()
        leave_request.save()

        # تحديث رصيد الإجازات
        HrIntegrationService.update_leave_balance(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            days_count=leave_request.days,
            transaction_type='confirm',
            remarks=f'الموافقة على طلب إجازة #{leave_request.id}'
        )

        # تحديث سجلات الحضور
        HrIntegrationService.update_attendance_from_leave(leave_request)

        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        رفض طلب إجازة
        """
        leave_request = self.get_object()

        if leave_request.status != 'pending':
            return Response(
                {'detail': 'لا يمكن رفض طلب إجازة غير معلق.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # تحديث حالة طلب الإجازة
        leave_request.status = 'rejected'
        leave_request.rejected_reason = request.data.get('reason', '')
        leave_request.approved_by = request.user
        leave_request.approved_at = timezone.now()
        leave_request.save()

        # إعادة الرصيد المحجوز
        HrIntegrationService.update_leave_balance(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            days_count=leave_request.days,
            transaction_type='add',
            remarks=f'رفض طلب إجازة #{leave_request.id}'
        )

        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)


class PayrollViewSet(viewsets.ModelViewSet):
    """
    واجهة برمجة لكشوف الرواتب

    توفر عمليات CRUD لكشوف الرواتب مع دعم التصفية والبحث
    """
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['company', 'payroll_month', 'payroll_year', 'status']
    ordering_fields = ['payroll_month', 'payroll_year', 'created_at']

    def get_queryset(self):
        """
        تقييد النتائج حسب شركة المستخدم إن وجدت
        """
        queryset = super().get_queryset()
        user = self.request.user

        if hasattr(user, 'employee') and user.employee and user.employee.company:
            queryset = queryset.filter(company=user.employee.company)

        return queryset

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """
        الحصول على سجلات الموظفين في كشف الراتب
        """
        payroll = self.get_object()
        queryset = payroll.payroll_employees.all()

        serializer = PayrollEmployeeSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        معالجة كشف الراتب
        """
        payroll = self.get_object()
        from Hr.services.payroll_service import PayrollService

        success, message = PayrollService.process_payroll(payroll)

        if success:
            serializer = self.get_serializer(payroll)
            return Response(serializer.data)

        return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        الموافقة على كشف الراتب
        """
        payroll = self.get_object()

        if payroll.status != 'submitted':
            return Response(
                {'detail': 'لا يمكن الموافقة على كشف راتب غير مقدم.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payroll.status = 'approved'
        payroll.approved_by = request.user
        payroll.approved_at = timezone.now()
        payroll.save()

        serializer = self.get_serializer(payroll)
        return Response(serializer.data)
