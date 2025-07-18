"""HR API ViewSets

This module contains ViewSets for the HR API endpoints, including:
- Employee ViewSets
- Organization ViewSets (Company, Branch, Department, JobPosition)
- Attendance ViewSets
- Payroll ViewSets
- Analytics and Reporting ViewSets
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import (
    IsHRManager, IsHRStaff, IsEmployeeOwnerOrHRStaff, IsPayrollManager,
    IsAttendanceManager, CanViewReports, CanManageOrganization,
    ReadOnlyOrHRStaff, DepartmentManagerPermission
)
from django.db.models import Q
from django.utils import timezone
from datetime import date, datetime, timedelta

from Hr.models.employee.employee_models import Employee
from Hr.models import Company, Branch, Department, JobPosition
from Hr.models.attendance.attendance_record_models import AttendanceRecord
from Hr.models.attendance.work_shift_models import WorkShift
from Hr.models.attendance.attendance_machine_models import AttendanceMachine
from Hr.models.payroll.payroll_period_models import PayrollPeriod
from Hr.models.payroll.employee_salary_structure_models import EmployeeSalaryStructure, SalaryComponent

from Hr.services import (
    EmployeeService, CompanyService, BranchService, DepartmentService, 
    JobPositionService, AttendanceService, PayrollService, LeaveService, 
    ReportService
)

from .serializers import (
    CompanySerializer, BranchSerializer, DepartmentSerializer, JobPositionSerializer,
    EmployeeListSerializer, EmployeeDetailSerializer, EmployeeCreateUpdateSerializer,
    AttendanceRecordSerializer, WorkShiftSerializer, AttendanceMachineSerializer,
    PayrollPeriodSerializer, SalaryComponentSerializer, EmployeeSalaryStructureSerializer,
    EmployeeStatisticsSerializer, AttendanceSummarySerializer, PayrollCalculationSerializer,
    LeaveBalanceSerializer, DashboardAnalyticsSerializer
)


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for Company management"""
    
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [CanManageOrganization]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'name_en']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a company"""
        company = self.get_object()
        success, message = CompanyService.activate_company(company.id)
        
        if success:
            return Response({'message': message}, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a company"""
        company = self.get_object()
        success, message = CompanyService.deactivate_company(company.id)
        
        if success:
            return Response({'message': message}, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)


class BranchViewSet(viewsets.ModelViewSet):
    """ViewSet for Branch management"""
    
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [ReadOnlyOrHRStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'is_active']
    search_fields = ['name', 'name_en', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get branch statistics"""
        branch = self.get_object()
        stats = BranchService.get_branch_statistics(branch.id)
        return Response(stats)


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department management"""
    
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [ReadOnlyOrHRStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branch', 'parent', 'is_active']
    search_fields = ['name', 'name_en', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get department statistics"""
        department = self.get_object()
        stats = DepartmentService.get_department_statistics(department.id)
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get employees in this department"""
        department = self.get_object()
        employees = EmployeeService.get_employees_by_department(department.id)
        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)


class JobPositionViewSet(viewsets.ModelViewSet):
    """ViewSet for JobPosition management"""
    
    queryset = JobPosition.objects.all()
    serializer_class = JobPositionSerializer
    permission_classes = [ReadOnlyOrHRStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'level', 'is_active']
    search_fields = ['name', 'name_en', 'code']
    ordering_fields = ['name', 'level', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get employees in this position"""
        position = self.get_object()
        employees = EmployeeService.get_employees_by_position(position.id)
        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet for Employee management"""
    
    queryset = Employee.objects.all()
    permission_classes = [IsHRStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'branch', 'position', 'is_active', 'status', 'gender']
    search_fields = ['full_name', 'employee_number', 'email', 'phone', 'national_id']
    ordering_fields = ['full_name', 'employee_number', 'hire_date', 'created_at']
    ordering = ['full_name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateUpdateSerializer
        else:
            return EmployeeDetailSerializer
    
    def perform_create(self, serializer):
        """Set created_by when creating employee"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate an employee"""
        employee = self.get_object()
        success, message = EmployeeService.activate_employee(employee.id)
        
        if success:
            return Response({'message': message}, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate an employee"""
        employee = self.get_object()
        reason = request.data.get('reason', '')
        success, message = EmployeeService.deactivate_employee(employee.id, reason)
        
        if success:
            return Response({'message': message}, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def change_department(self, request, pk=None):
        """Change employee's department"""
        employee = self.get_object()
        department_id = request.data.get('department_id')
        effective_date = request.data.get('effective_date')
        notes = request.data.get('notes', '')
        
        if not department_id:
            return Response({'error': 'department_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        success, message = EmployeeService.change_employee_department(
            employee.id, department_id, effective_date, notes
        )
        
        if success:
            return Response({'message': message}, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def change_position(self, request, pk=None):
        """Change employee's position"""
        employee = self.get_object()
        position_id = request.data.get('position_id')
        effective_date = request.data.get('effective_date')
        notes = request.data.get('notes', '')
        
        if not position_id:
            return Response({'error': 'position_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        success, message = EmployeeService.change_employee_position(
            employee.id, position_id, effective_date, notes
        )
        
        if success:
            return Response({'message': message}, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        """Get attendance summary for employee"""
        employee = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = date.today().replace(day=1)  # First day of current month
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = date.today()
        
        summary = AttendanceService.get_employee_attendance_summary(
            employee.id, start_date, end_date
        )
        
        serializer = AttendanceSummarySerializer(summary)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def leave_balance(self, request, pk=None):
        """Get leave balance for employee"""
        employee = self.get_object()
        year = request.query_params.get('year')
        
        if not year:
            year = date.today().year
        else:
            year = int(year)
        
        summary = LeaveService.get_employee_leave_summary(employee.id, year)
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def salary_calculation(self, request, pk=None):
        """Get salary calculation for employee"""
        employee = self.get_object()
        period_id = request.query_params.get('period_id')
        
        if not period_id:
            # Get current payroll period
            current_period = PayrollService.get_current_payroll_period()
            if current_period:
                period_id = current_period.id
            else:
                return Response({'error': 'No active payroll period found'}, status=status.HTTP_400_BAD_REQUEST)
        
        calculation = PayrollService.calculate_employee_salary(employee.id, period_id)
        
        if 'error' in calculation:
            return Response(calculation, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PayrollCalculationSerializer(calculation)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get employee statistics"""
        stats = EmployeeService.get_employee_statistics()
        serializer = EmployeeStatisticsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """Bulk import employees from file"""
        # This would be implemented with file processing logic
        return Response({'message': 'Bulk import functionality to be implemented'})


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for AttendanceRecord management"""
    
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAttendanceManager]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'date', 'machine']
    ordering_fields = ['date', 'check_in_time', 'created_at']
    ordering = ['-date', 'employee__full_name']
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """Record employee check-in"""
        employee_id = request.data.get('employee_id')
        machine_id = request.data.get('machine_id')
        notes = request.data.get('notes', '')
        
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        record, success, message = AttendanceService.record_check_in(
            employee_id, machine_id=machine_id, notes=notes
        )
        
        if success:
            serializer = AttendanceRecordSerializer(record)
            return Response({
                'message': message,
                'record': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        """Record employee check-out"""
        employee_id = request.data.get('employee_id')
        machine_id = request.data.get('machine_id')
        notes = request.data.get('notes', '')
        
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        record, success, message = AttendanceService.record_check_out(
            employee_id, machine_id=machine_id, notes=notes
        )
        
        if success:
            serializer = AttendanceRecordSerializer(record)
            return Response({
                'message': message,
                'record': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """Get daily attendance summary"""
        target_date = request.query_params.get('date')
        department_id = request.query_params.get('department_id')
        
        if target_date:
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        else:
            target_date = date.today()
        
        if department_id:
            summary = AttendanceService.get_department_attendance_summary(department_id, target_date)
        else:
            # Get overall summary
            records = AttendanceService.get_daily_attendance_records(target_date)
            summary = {
                'date': target_date,
                'total_records': len(records),
                'present_count': len([r for r in records if r.check_in_time]),
                'records': AttendanceRecordSerializer(records, many=True).data
            }
        
        return Response(summary)
    
    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """Bulk import attendance records"""
        # This would be implemented with file processing logic
        return Response({'message': 'Bulk import functionality to be implemented'})


class WorkShiftViewSet(viewsets.ModelViewSet):
    """ViewSet for WorkShift management"""
    
    queryset = WorkShift.objects.all()
    serializer_class = WorkShiftSerializer
    permission_classes = [IsAttendanceManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'name_en']
    ordering_fields = ['name', 'start_time']
    ordering = ['start_time']


class AttendanceMachineViewSet(viewsets.ModelViewSet):
    """ViewSet for AttendanceMachine management"""
    
    queryset = AttendanceMachine.objects.all()
    serializer_class = AttendanceMachineSerializer
    permission_classes = [IsAttendanceManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'model', 'serial_number', 'ip_address']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test connection to attendance machine"""
        machine = self.get_object()
        success, message = AttendanceMachineService.test_machine_connection(machine.id)
        
        if success:
            return Response({'message': message}, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for PayrollPeriod management"""
    
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    permission_classes = [IsPayrollManager]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'is_active']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a payroll period"""
        period = self.get_object()
        success, message = PayrollService.close_payroll_period(period.id)
        
        if success:
            return Response({'message': message}, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get payroll summary for period"""
        period = self.get_object()
        summary = PayrollService.get_payroll_summary(period.id)
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active payroll period"""
        period = PayrollService.get_current_payroll_period()
        if period:
            serializer = PayrollPeriodSerializer(period)
            return Response(serializer.data)
        else:
            return Response({'message': 'No active payroll period found'}, status=status.HTTP_404_NOT_FOUND)


class SalaryComponentViewSet(viewsets.ModelViewSet):
    """ViewSet for SalaryComponent management"""
    
    queryset = SalaryComponent.objects.all()
    serializer_class = SalaryComponentSerializer
    permission_classes = [IsPayrollManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['component_type', 'calculation_type', 'is_active']
    search_fields = ['name', 'name_en']
    ordering_fields = ['name', 'component_type']
    ordering = ['component_type', 'name']


class EmployeeSalaryStructureViewSet(viewsets.ModelViewSet):
    """ViewSet for EmployeeSalaryStructure management"""
    
    queryset = EmployeeSalaryStructure.objects.all()
    serializer_class = EmployeeSalaryStructureSerializer
    permission_classes = [IsPayrollManager]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'is_active']
    ordering_fields = ['effective_date', 'created_at']
    ordering = ['-effective_date']


class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for analytics and reporting"""
    
    permission_classes = [CanViewReports]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard analytics"""
        analytics = ReportService.get_dashboard_analytics()
        serializer = DashboardAnalyticsSerializer(analytics)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def employee_report(self, request):
        """Generate employee report"""
        report_type = request.data.get('report_type', 'summary')
        filters = request.data.get('filters', {})
        
        report = ReportService.generate_employee_report(report_type, filters)
        return Response(report)
    
    @action(detail=False, methods=['post'])
    def attendance_report(self, request):
        """Generate attendance report"""
        report_type = request.data.get('report_type', 'summary')
        filters = request.data.get('filters', {})
        
        report = ReportService.generate_attendance_report(report_type, filters)
        return Response(report)
    
    @action(detail=False, methods=['get'])
    def report_templates(self, request):
        """Get available report templates"""
        templates = ReportService.get_report_templates()
        return Response(templates)
    
    @action(detail=False, methods=['post'])
    def employee_summary_report(self, request):
        """Generate employee summary report"""
        filters = request.data.get('filters', {})
        
        try:
            report = ReportService.get_employee_summary_report(filters)
            return Response(report)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def employee_details_report(self, request):
        """Generate employee details report"""
        filters = request.data.get('filters', {})
        
        try:
            report = ReportService.get_employee_details_report(filters)
            return Response(report)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def organizational_structure_report(self, request):
        """Generate organizational structure report"""
        try:
            report = ReportService.get_organizational_structure_report()
            return Response(report)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def new_employees_report(self, request):
        """Generate new employees report"""
        filters = request.data.get('filters', {})
        
        try:
            report = ReportService.get_new_employees_report(filters)
            return Response(report)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def demographics_report(self, request):
        """Generate demographics report"""
        filters = request.data.get('filters', {})
        
        try:
            report = ReportService.get_demographics_report(filters)
            return Response(report)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def birthdays_anniversaries_report(self, request):
        """Generate birthdays and anniversaries report"""
        filters = request.data.get('filters', {})
        
        try:
            report = ReportService.get_birthdays_anniversaries_report(filters)
            return Response(report)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def attendance_analytics(self, request):
        """Generate attendance analytics"""
        filters = request.data.get('filters', {})
        
        try:
            report = ReportService.get_attendance_analytics(filters)
            return Response(report)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def salary_analytics(self, request):
        """Generate salary analytics"""
        filters = request.data.get('filters', {})
        
        try:
            report = ReportService.get_salary_analytics(filters)
            return Response(report)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def export_report(self, request):
        """Export report to Excel or PDF"""
        report_type = request.data.get('report_type')
        export_format = request.data.get('format', 'excel')
        filters = request.data.get('filters', {})
        
        if not report_type:
            return Response({'error': 'report_type is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Generate report data first
            if report_type == 'employee_summary':
                report_data = ReportService.get_employee_summary_report(filters)
            elif report_type == 'employee_details':
                report_data = ReportService.get_employee_details_report(filters)
            elif report_type == 'org_structure':
                report_data = ReportService.get_organizational_structure_report()
            elif report_type == 'new_employees':
                report_data = ReportService.get_new_employees_report(filters)
            elif report_type == 'demographics':
                report_data = ReportService.get_demographics_report(filters)
            elif report_type == 'birthdays_anniversaries':
                report_data = ReportService.get_birthdays_anniversaries_report(filters)
            else:
                return Response({'error': 'Invalid report type'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Export to requested format
            if export_format == 'excel':
                file_content = ReportService.export_report_to_excel(report_data, report_type)
                response = HttpResponse(
                    file_content,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
                return response
            
            elif export_format == 'pdf':
                file_content = ReportService.export_report_to_pdf(report_data, report_type)
                response = HttpResponse(file_content, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
                return response
            
            else:
                return Response({'error': 'Invalid export format'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)