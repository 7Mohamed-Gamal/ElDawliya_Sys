from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q

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
    filterset_fields = ['is_active', 'is_paid', 'requires_approval']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'max_days_per_year']
    ordering = ['name']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for this leave type"""
        leave_type = self.get_object()
        
        current_year = timezone.now().year
        
        # Get statistics for current year
        total_requests = LeaveRequest.objects.filter(
            leave_type=leave_type,
            start_date__year=current_year
        ).count()
        
        approved_requests = LeaveRequest.objects.filter(
            leave_type=leave_type,
            start_date__year=current_year,
            status='approved'
        ).count()
        
        pending_requests = LeaveRequest.objects.filter(
            leave_type=leave_type,
            status='pending'
        ).count()
        
        total_days_used = LeaveRequest.objects.filter(
            leave_type=leave_type,
            start_date__year=current_year,
            status='approved'
        ).aggregate(total_days=models.Sum('days'))['total_days'] or 0
        
        return Response({
            'leave_type': {
                'id': str(leave_type.id),
                'name': leave_type.name,
                'max_days_per_year': leave_type.max_days_per_year
            },
            'statistics': {
                'total_requests': total_requests,
                'approved_requests': approved_requests,
                'pending_requests': pending_requests,
                'total_days_used': total_days_used,
                'approval_rate': (approved_requests / total_requests * 100) if total_requests > 0 else 0
            },
            'year': current_year
        })

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
        """Filter queryset based on user permissions"""
        queryset = LeaveRequest.objects.select_related(
            'employee', 'leave_type', 'approved_by'
        )
        
        # If user is not admin, only show their own requests or requests they can approve
        user = self.request.user
        if not user.is_superuser:
            # Show own requests or requests from subordinates
            employee_profile = getattr(user, 'employee_profile', None)
            if employee_profile:
                subordinate_ids = [emp.id for emp in employee_profile.get_all_subordinates()]
                subordinate_ids.append(employee_profile.id)
                queryset = queryset.filter(employee_id__in=subordinate_ids)
            else:
                # If no employee profile, only show own requests
                queryset = queryset.filter(employee__user_account=user)
        
        return queryset
    
    def perform_create(self, serializer):
        # Set employee to current user's employee profile if not specified
        if not serializer.validated_data.get('employee'):
            employee_profile = getattr(self.request.user, 'employee_profile', None)
            if employee_profile:
                serializer.save(employee=employee_profile)
            else:
                raise ValidationError("لا يمكن تحديد الموظف")
        else:
            serializer.save()
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced search for leave requests"""
        serializer = LeaveSearchSerializer(data=request.data)
        
        if serializer.is_valid():
            filters = {}
            
            # Add filters
            if serializer.validated_data.get('employee_id'):
                filters['employee'] = serializer.validated_data['employee_id']
            
            if serializer.validated_data.get('department_id'):
                filters['employee__department'] = serializer.validated_data['department_id']
            
            if serializer.validated_data.get('leave_type_id'):
                filters['leave_type'] = serializer.validated_data['leave_type_id']
            
            if serializer.validated_data.get('status'):
                filters['status'] = serializer.validated_data['status']
            
            # Add date filters
            if serializer.validated_data.get('start_date'):
                filters['start_date__gte'] = serializer.validated_data['start_date']
            
            if serializer.validated_data.get('end_date'):
                filters['end_date__lte'] = serializer.validated_data['end_date']
            
            # Query requests
            requests = self.get_queryset().filter(**filters)
            
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
        """Approve a leave request"""
        leave_request = self.get_object()
        serializer = LeaveApprovalSerializer(data=request.data)
        
        if serializer.is_valid():
            approval_status = serializer.validated_data['status']
            rejection_reason = serializer.validated_data.get('rejection_reason', '')
            
            try:
                if approval_status == 'approved':
                    LeaveService.approve_leave_request(
                        leave_request.id,
                        approved_by=request.user
                    )
                    message = 'تم اعتماد طلب الإجازة بنجاح'
                else:
                    LeaveService.reject_leave_request(
                        leave_request.id,
                        rejected_by=request.user,
                        rejection_reason=rejection_reason
                    )
                    message = 'تم رفض طلب الإجازة'
                
                return Response({
                    'status': 'success',
                    'message': message,
                    'leave_request_status': approval_status
                })
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a leave request"""
        leave_request = self.get_object()
        
        # Check if user can cancel this request
        if (leave_request.employee.user_account != request.user and 
            not request.user.is_superuser):
            return Response({'status': 'error', 'message': 'غير مسموح بإلغاء هذا الطلب'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if leave_request.status != 'pending':
            return Response({'status': 'error', 'message': 'لا يمكن إلغاء طلب معتمد أو مرفوض'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            LeaveService.cancel_leave_request(leave_request.id, cancelled_by=request.user)
            return Response({
                'status': 'success',
                'message': 'تم إلغاء طلب الإجازة بنجاح'
            })
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get current user's leave requests"""
        employee_profile = getattr(request.user, 'employee_profile', None)
        if not employee_profile:
            return Response({'status': 'error', 'message': 'لا يوجد ملف موظف مرتبط بالمستخدم'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        requests = LeaveRequest.objects.filter(employee=employee_profile).order_by('-created_at')
        
        # Paginate results
        page = self.paginate_queryset(requests)
        if page is not None:
            serializer = LeaveRequestListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = LeaveRequestListSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """Get leave requests pending approval by current user"""
        employee_profile = getattr(request.user, 'employee_profile', None)
        if not employee_profile:
            return Response({'status': 'error', 'message': 'لا يوجد ملف موظف مرتبط بالمستخدم'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Get requests from subordinates
        subordinate_ids = [emp.id for emp in employee_profile.get_all_subordinates()]
        
        requests = LeaveRequest.objects.filter(
            employee_id__in=subordinate_ids,
            status='pending'
        ).order_by('start_date')
        
        serializer = LeaveRequestListSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Get leave requests for calendar view"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        department_id = request.query_params.get('department_id')
        
        if not start_date or not end_date:
            return Response({'status': 'error', 'message': 'تاريخ البداية والنهاية مطلوبان'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        filters = {
            'status': 'approved',
            'start_date__lte': end_date,
            'end_date__gte': start_date
        }
        
        if department_id:
            filters['employee__department_id'] = department_id
        
        requests = LeaveRequest.objects.filter(**filters).select_related(
            'employee', 'leave_type'
        )
        
        calendar_events = []
        for request in requests:
            calendar_events.append({
                'id': str(request.id),
                'title': f"{request.employee.full_name} - {request.leave_type.name}",
                'start': request.start_date.isoformat(),
                'end': request.end_date.isoformat(),
                'employee': {
                    'id': str(request.employee.id),
                    'name': request.employee.full_name,
                    'department': request.employee.department.name if request.employee.department else ''
                },
                'leave_type': {
                    'id': str(request.leave_type.id),
                    'name': request.leave_type.name,
                    'color': request.leave_type.color or '#007bff'
                },
                'days': request.days
            })
        
        return Response({
            'events': calendar_events,
            'count': len(calendar_events)
        })

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
        """Filter queryset based on user permissions"""
        queryset = LeaveBalance.objects.select_related('employee', 'leave_type')
        
        # If user is not admin, only show their own balances or balances of subordinates
        user = self.request.user
        if not user.is_superuser:
            employee_profile = getattr(user, 'employee_profile', None)
            if employee_profile:
                subordinate_ids = [emp.id for emp in employee_profile.get_all_subordinates()]
                subordinate_ids.append(employee_profile.id)
                queryset = queryset.filter(employee_id__in=subordinate_ids)
            else:
                queryset = queryset.filter(employee__user_account=user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_balances(self, request):
        """Get current user's leave balances"""
        employee_profile = getattr(request.user, 'employee_profile', None)
        if not employee_profile:
            return Response({'status': 'error', 'message': 'لا يوجد ملف موظف مرتبط بالمستخدم'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        year = int(request.query_params.get('year', timezone.now().year))
        
        balances = LeaveBalance.objects.filter(
            employee=employee_profile,
            year=year
        ).select_related('leave_type')
        
        serializer = LeaveBalanceSerializer(balances, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def initialize_balances(self, request):
        """Initialize leave balances for employees"""
        year = request.data.get('year', timezone.now().year)
        employee_ids = request.data.get('employee_ids', [])
        department_ids = request.data.get('department_ids', [])
        
        try:
            result = LeaveService.initialize_leave_balances(
                year=year,
                employee_ids=employee_ids,
                department_ids=department_ids
            )
            
            return Response({
                'status': 'success',
                'message': 'تم تهيئة أرصدة الإجازات بنجاح',
                'employees_processed': result.get('employees_processed', 0),
                'balances_created': result.get('balances_created', 0)
            })
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def adjust_balance(self, request):
        """Adjust leave balance for an employee"""
        employee_id = request.data.get('employee_id')
        leave_type_id = request.data.get('leave_type_id')
        adjustment = request.data.get('adjustment', 0)
        reason = request.data.get('reason', '')
        year = request.data.get('year', timezone.now().year)
        
        if not all([employee_id, leave_type_id]):
            return Response({'status': 'error', 'message': 'معرف الموظف ونوع الإجازة مطلوبان'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            LeaveService.adjust_leave_balance(
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                adjustment=adjustment,
                reason=reason,
                year=year,
                adjusted_by=request.user
            )
            
            return Response({
                'status': 'success',
                'message': 'تم تعديل رصيد الإجازة بنجاح',
                'adjustment': adjustment
            })
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get leave balance summary"""
        year = int(request.query_params.get('year', timezone.now().year))
        department_id = request.query_params.get('department_id')
        
        filters = {'year': year}
        if department_id:
            filters['employee__department_id'] = department_id
        
        balances = self.get_queryset().filter(**filters)
        
        # Calculate summary statistics
        total_employees = balances.values('employee').distinct().count()
        total_allocated = balances.aggregate(total=models.Sum('allocated'))['total'] or 0
        total_used = balances.aggregate(total=models.Sum('used'))['total'] or 0
        total_balance = balances.aggregate(total=models.Sum('balance'))['total'] or 0
        
        # Group by leave type
        leave_type_summary = {}
        for balance in balances.select_related('leave_type'):
            leave_type = balance.leave_type.name
            if leave_type not in leave_type_summary:
                leave_type_summary[leave_type] = {
                    'allocated': 0,
                    'used': 0,
                    'balance': 0,
                    'employees': 0
                }
            
            leave_type_summary[leave_type]['allocated'] += balance.allocated
            leave_type_summary[leave_type]['used'] += balance.used
            leave_type_summary[leave_type]['balance'] += balance.balance
            leave_type_summary[leave_type]['employees'] += 1
        
        return Response({
            'year': year,
            'summary': {
                'total_employees': total_employees,
                'total_allocated': total_allocated,
                'total_used': total_used,
                'total_balance': total_balance,
                'utilization_rate': (total_used / total_allocated * 100) if total_allocated > 0 else 0
            },
            'by_leave_type': leave_type_summary
        })