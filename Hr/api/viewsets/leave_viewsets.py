from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from Hr.models import LeaveType, LeaveRequest, LeaveBalance
from Hr.services import LeaveService
from ..serializers.leave_serializers import (
    LeaveTypeSerializer,
    LeaveRequestSerializer,
    LeaveRequestListSerializer,
    LeaveRequestCreateSerializer,
    LeaveRequestUpdateSerializer,
    LeaveApprovalSerializer,
    LeaveBalanceSerializer,
    LeaveSearchSerializer
)

class LeaveTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing leave types"""
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_paid']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'max_days_per_year']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def balances(self, request, pk=None):
        """Get leave balances for this leave type"""
        leave_type = self.get_object()
        year = int(request.query_params.get('year', timezone.now().year))
        
        balances = LeaveBalance.objects.filter(
            leave_type=leave_type,
            year=year
        ).select_related('employee')
        
        serializer = LeaveBalanceSerializer(balances, many=True)
        return Response(serializer.data)

class LeaveRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing leave requests"""
    queryset = LeaveRequest.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'leave_type', 'status']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_number', 'reason']
    ordering_fields = ['start_date', 'created_at', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LeaveRequestListSerializer
        elif self.action == 'create':
            return LeaveRequestCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return LeaveRequestUpdateSerializer
        return LeaveRequestSerializer
    
    def get_queryset(self):
        queryset = LeaveRequest.objects.all()
        
        # Filter by current user if not admin
        if not self.request.user.is_staff:
            # Get employee record for current user
            try:
                from Hr.models import Employee
                employee = Employee.objects.get(user=self.request.user)
                queryset = queryset.filter(employee=employee)
            except Employee.DoesNotExist:
                queryset = queryset.none()
        
        return queryset.select_related('employee', 'leave_type', 'approved_by')
    
    def perform_create(self, serializer):
        # If not admin, set employee to current user's employee record
        if not self.request.user.is_staff:
            try:
                from Hr.models import Employee
                employee = Employee.objects.get(user=self.request.user)
                serializer.save(employee=employee, created_by=self.request.user)
            except Employee.DoesNotExist:
                raise serializers.ValidationError("لا يوجد سجل موظف مرتبط بحسابك")
        else:
            serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced search for leave requests"""
        serializer = LeaveSearchSerializer(data=request.data)
        
        if serializer.is_valid():
            filters = {}
            
            # Add filters
            for field in ['employee_id', 'department_id', 'leave_type_id', 'status']:
                if serializer.validated_data.get(field):
                    if field == 'employee_id':
                        filters['employee'] = serializer.validated_data[field]
                    elif field == 'department_id':
                        filters['employee__department'] = serializer.validated_data[field]
                    elif field == 'leave_type_id':
                        filters['leave_type'] = serializer.validated_data[field]
                    else:
                        filters[field] = serializer.validated_data[field]
            
            # Add date filters
            if serializer.validated_data.get('start_date'):
                filters['start_date__gte'] = serializer.validated_data['start_date']
            
            if serializer.validated_data.get('end_date'):
                filters['end_date__lte'] = serializer.validated_data['end_date']
            
            # Query requests
            requests = LeaveRequest.objects.filter(**filters).select_related(
                'employee', 'employee__department', 'leave_type', 'approved_by'
            )
            
            # Paginate results
            page = self.paginate_queryset(requests)
            if page is not None:
                serializer = LeaveRequestListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = LeaveRequestListSerializer(requests, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve or reject leave request"""
        leave_request = self.get_object()
        serializer = LeaveApprovalSerializer(data=request.data)
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            rejection_reason = serializer.validated_data.get('rejection_reason')
            
            try:
                if new_status == 'approved':
                    LeaveService.approve_leave_request(
                        leave_request.id,
                        approved_by=request.user
                    )
                    message = 'تم اعتماد طلب الإجازة بنجاح'
                else:
                    LeaveService.reject_leave_request(
                        leave_request.id,
                        rejection_reason=rejection_reason,
                        rejected_by=request.user
                    )
                    message = 'تم رفض طلب الإجازة'
                
                return Response({'status': 'success', 'message': message})
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel leave request"""
        leave_request = self.get_object()
        
        # Check if user can cancel this request
        if leave_request.employee.user != request.user and not request.user.is_staff:
            return Response({'status': 'error', 'message': 'غير مسموح لك بإلغاء هذا الطلب'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            LeaveService.cancel_leave_request(
                leave_request.id,
                cancelled_by=request.user
            )
            return Response({'status': 'success', 'message': 'تم إلغاء طلب الإجازة بنجاح'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """Get leave requests pending approval"""
        # Get requests that need approval from current user
        # This would typically check manager hierarchy
        pending_requests = LeaveRequest.objects.filter(
            status='pending'
        ).select_related('employee', 'leave_type')
        
        serializer = LeaveRequestListSerializer(pending_requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Get leave calendar data"""
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        department_id = request.query_params.get('department_id')
        
        calendar_data = LeaveService.get_leave_calendar(
            year=year,
            month=month,
            department_id=department_id
        )
        
        return Response(calendar_data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get leave statistics"""
        year = int(request.query_params.get('year', timezone.now().year))
        department_id = request.query_params.get('department_id')
        
        stats = LeaveService.get_leave_statistics(
            year=year,
            department_id=department_id
        )
        
        return Response(stats)

class LeaveBalanceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing leave balances"""
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'leave_type', 'year']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_number']
    ordering_fields = ['year', 'balance']
    ordering = ['-year', 'employee__employee_number']
    
    def get_queryset(self):
        queryset = LeaveBalance.objects.all()
        
        # Filter by current user if not admin
        if not self.request.user.is_staff:
            try:
                from Hr.models import Employee
                employee = Employee.objects.get(user=self.request.user)
                queryset = queryset.filter(employee=employee)
            except Employee.DoesNotExist:
                queryset = queryset.none()
        
        return queryset.select_related('employee', 'leave_type')
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update leave balances"""
        year = request.data.get('year', timezone.now().year)
        leave_type_id = request.data.get('leave_type_id')
        department_id = request.data.get('department_id')
        
        try:
            result = LeaveService.bulk_update_leave_balances(
                year=year,
                leave_type_id=leave_type_id,
                department_id=department_id
            )
            
            return Response({
                'status': 'success',
                'message': 'تم تحديث أرصدة الإجازات بنجاح',
                'updated_count': result.get('updated_count', 0),
                'created_count': result.get('created_count', 0)
            })
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get leave balance summary"""
        year = int(request.query_params.get('year', timezone.now().year))
        department_id = request.query_params.get('department_id')
        
        summary = LeaveService.get_leave_balance_summary(
            year=year,
            department_id=department_id
        )
        
        return Response(summary)