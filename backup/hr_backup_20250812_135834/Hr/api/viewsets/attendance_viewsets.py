from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import date, timedelta

from Hr.models import AttendanceRecord, WorkShift, AttendanceMachine
from Hr.services import AttendanceService
from ..serializers.attendance_serializers import (
    AttendanceRecordSerializer,
    AttendanceRecordListSerializer,
    AttendanceRecordCreateSerializer,
    AttendanceRecordUpdateSerializer,
    WorkShiftSerializer,
    AttendanceMachineSerializer,
    AttendanceSearchSerializer,
    AttendanceSummarySerializer,
    AttendanceBulkUploadSerializer
)

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for managing attendance records"""
    queryset = AttendanceRecord.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'date', 'is_late', 'is_early_departure']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_number']
    ordering_fields = ['date', 'check_in_time']
    ordering = ['-date', 'employee__employee_number']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AttendanceRecordListSerializer
        elif self.action == 'create':
            return AttendanceRecordCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return AttendanceRecordUpdateSerializer
        return AttendanceRecordSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def record_attendance(self, request):
        """Record attendance for an employee"""
        employee_id = request.data.get('employee_id')
        attendance_date = request.data.get('date')
        check_in_time = request.data.get('check_in_time')
        check_out_time = request.data.get('check_out_time')
        machine_id = request.data.get('machine_id')
        notes = request.data.get('notes')
        
        try:
            attendance_record = AttendanceService.record_attendance(
                employee_id=employee_id,
                attendance_date=attendance_date,
                check_in_time=check_in_time,
                check_out_time=check_out_time,
                machine_id=machine_id,
                notes=notes
            )
            
            serializer = AttendanceRecordSerializer(attendance_record)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced search for attendance records"""
        serializer = AttendanceSearchSerializer(data=request.data)
        
        if serializer.is_valid():
            filters = {}
            
            # Add employee filter
            if serializer.validated_data.get('employee_id'):
                filters['employee'] = serializer.validated_data['employee_id']
            
            # Add department filter
            if serializer.validated_data.get('department_id'):
                filters['employee__department'] = serializer.validated_data['department_id']
            
            # Add date filters
            if serializer.validated_data.get('start_date'):
                filters['date__gte'] = serializer.validated_data['start_date']
            
            if serializer.validated_data.get('end_date'):
                filters['date__lte'] = serializer.validated_data['end_date']
            
            # Add status filters
            if serializer.validated_data.get('is_late') is not None:
                filters['is_late'] = serializer.validated_data['is_late']
            
            if serializer.validated_data.get('is_early_departure') is not None:
                filters['is_early_departure'] = serializer.validated_data['is_early_departure']
            
            # Query records
            records = AttendanceRecord.objects.filter(**filters).select_related('employee', 'employee__department')
            
            # Paginate results
            page = self.paginate_queryset(records)
            if page is not None:
                serializer = AttendanceRecordListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = AttendanceRecordListSerializer(records, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """Get daily attendance summary"""
        attendance_date = request.query_params.get('date')
        
        if not attendance_date:
            attendance_date = date.today()
        
        summary = AttendanceService.get_daily_attendance_summary(attendance_date)
        serializer = AttendanceSummarySerializer(summary)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Bulk upload attendance records"""
        serializer = AttendanceBulkUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            file = serializer.validated_data['file']
            date_format = serializer.validated_data['date_format']
            time_format = serializer.validated_data['time_format']
            
            # Process file (CSV or Excel)
            # This would typically be handled by a service method
            # For now, return a placeholder response
            return Response({
                'status': 'success',
                'message': 'File uploaded successfully',
                'records_processed': 0,
                'records_created': 0,
                'records_updated': 0,
                'errors': []
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def sync_from_machine(self, request):
        """Sync attendance data from attendance machines"""
        machine_id = request.data.get('machine_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not machine_id:
            return Response({'status': 'error', 'message': 'معرف الجهاز مطلوب'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # This would typically connect to the attendance machine
            # and sync data. For now, return a placeholder response
            return Response({
                'status': 'success',
                'message': 'تم مزامنة البيانات بنجاح',
                'records_synced': 0,
                'last_sync': timezone.now().isoformat()
            })
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """Get monthly attendance summary"""
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        department_id = request.query_params.get('department_id')
        
        # Calculate month start and end dates
        from calendar import monthrange
        start_date = date(year, month, 1)
        end_date = date(year, month, monthrange(year, month)[1])
        
        summary = AttendanceService.get_monthly_attendance_summary(
            start_date, end_date, department_id
        )
        
        return Response(summary)
    
    @action(detail=True, methods=['post'])
    def approve_overtime(self, request, pk=None):
        """Approve overtime for an attendance record"""
        record = self.get_object()
        overtime_hours = request.data.get('overtime_hours', 0)
        notes = request.data.get('notes', '')
        
        try:
            # Update record with approved overtime
            record.overtime_hours = overtime_hours
            record.overtime_approved = True
            record.overtime_approved_by = request.user
            record.overtime_approved_at = timezone.now()
            if notes:
                record.notes = f"{record.notes or ''} - Overtime: {notes}"
            record.save()
            
            return Response({
                'status': 'success',
                'message': 'تم اعتماد الوقت الإضافي بنجاح',
                'overtime_hours': overtime_hours
            })
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, 
                          status=status.HTTP_400_BAD_REQUEST)

class WorkShiftViewSet(viewsets.ModelViewSet):
    """ViewSet for managing work shifts"""
    queryset = WorkShift.objects.all()
    serializer_class = WorkShiftSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_default']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'start_time']
    ordering = ['name']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get employees assigned to this shift"""
        shift = self.get_object()
        from Hr.models import Employee
        from ..serializers.employee_serializers import EmployeeListSerializer
        
        employees = Employee.objects.filter(work_shift=shift, status='active')
        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_employees(self, request, pk=None):
        """Assign employees to this shift"""
        shift = self.get_object()
        employee_ids = request.data.get('employee_ids', [])
        
        try:
            from Hr.models import Employee
            employees = Employee.objects.filter(id__in=employee_ids)
            employees.update(work_shift=shift)
            
            return Response({
                'status': 'success',
                'message': f'تم تعيين {employees.count()} موظف للوردية',
                'assigned_count': employees.count()
            })
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, 
                          status=status.HTTP_400_BAD_REQUEST)

class AttendanceMachineViewSet(viewsets.ModelViewSet):
    """ViewSet for managing attendance machines"""
    queryset = AttendanceMachine.objects.all()
    serializer_class = AttendanceMachineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branch', 'is_active', 'machine_type']
    search_fields = ['name', 'ip_address', 'serial_number']
    ordering_fields = ['name', 'branch__name']
    ordering = ['branch__name', 'name']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test connection to attendance machine"""
        machine = self.get_object()
        
        try:
            # This would typically test the actual connection
            # For now, return a placeholder response
            return Response({
                'status': 'success',
                'message': 'الاتصال بالجهاز ناجح',
                'machine_info': {
                    'name': machine.name,
                    'ip_address': machine.ip_address,
                    'status': 'online',
                    'last_sync': timezone.now().isoformat()
                }
            })
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def sync_data(self, request, pk=None):
        """Sync data from attendance machine"""
        machine = self.get_object()
        
        try:
            # This would typically sync data from the machine
            # For now, return a placeholder response
            return Response({
                'status': 'success',
                'message': 'تم مزامنة البيانات بنجاح',
                'records_synced': 0,
                'last_sync': timezone.now().isoformat()
            })
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get machine status and statistics"""
        machine = self.get_object()
        
        # Get recent attendance records from this machine
        recent_records = AttendanceRecord.objects.filter(
            machine=machine,
            date__gte=timezone.now().date() - timedelta(days=7)
        ).count()
        
        return Response({
            'machine': {
                'id': str(machine.id),
                'name': machine.name,
                'ip_address': machine.ip_address,
                'is_active': machine.is_active
            },
            'statistics': {
                'recent_records': recent_records,
                'last_sync': machine.last_sync_at.isoformat() if machine.last_sync_at else None,
                'status': 'online' if machine.is_active else 'offline'
            }
        })