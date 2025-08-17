from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from Hr.models import SalaryComponent, PayrollPeriod, PayrollEntry, EmployeeSalaryStructure
from Hr.services import PayrollService
from ..serializers.payroll_serializers import (
    SalaryComponentSerializer,
    PayrollPeriodSerializer,
    PayrollPeriodListSerializer,
    PayrollEntrySerializer,
    PayrollEntryListSerializer,
    PayrollEntryCreateSerializer,
    PayrollEntryUpdateSerializer,
    EmployeeSalaryStructureSerializer,
    PayrollSearchSerializer,
    PayrollCalculationSerializer
)

class SalaryComponentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing salary components"""
    queryset = SalaryComponent.objects.all()
    serializer_class = SalaryComponentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'calculation_type', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'type', 'order']
    ordering = ['type', 'order', 'name']
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get employees using this salary component"""
        component = self.get_object()
        
        # Get employees through salary structures
        structures = EmployeeSalaryStructure.objects.filter(
            salary_components=component
        ).select_related('employee')
        
        from ..serializers.employee_serializers import EmployeeListSerializer
        employees = [structure.employee for structure in structures]
        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)

class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payroll periods"""
    queryset = PayrollPeriod.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name']
    ordering_fields = ['start_date', 'end_date', 'payment_date']
    ordering = ['-start_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PayrollPeriodListSerializer
        return PayrollPeriodSerializer
    
    @action(detail=True, methods=['post'])
    def calculate_payroll(self, request, pk=None):
        """Calculate payroll for this period"""
        period = self.get_object()
        serializer = PayrollCalculationSerializer(data=request.data)
        
        if serializer.is_valid():
            employee_ids = serializer.validated_data.get('employee_ids')
            department_ids = serializer.validated_data.get('department_ids')
            recalculate_existing = serializer.validated_data.get('recalculate_existing', False)
            
            try:
                result = PayrollService.calculate_payroll_for_period(
                    period_id=period.id,
                    employee_ids=employee_ids,
                    department_ids=department_ids,
                    recalculate_existing=recalculate_existing,
                    calculated_by=request.user
                )
                
                return Response({
                    'status': 'success',
                    'message': 'تم حساب الرواتب بنجاح',
                    'entries_calculated': result.get('entries_calculated', 0),
                    'entries_updated': result.get('entries_updated', 0),
                    'total_amount': result.get('total_amount', 0),
                    'errors': result.get('errors', [])
                })
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        """Finalize payroll period"""
        period = self.get_object()
        
        try:
            PayrollService.finalize_payroll_period(
                period.id,
                finalized_by=request.user
            )
            return Response({'status': 'success', 'message': 'تم إقفال فترة الرواتب بنجاح'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Reopen payroll period"""
        period = self.get_object()
        
        try:
            PayrollService.reopen_payroll_period(
                period.id,
                reopened_by=request.user
            )
            return Response({'status': 'success', 'message': 'تم إعادة فتح فترة الرواتب بنجاح'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def entries(self, request, pk=None):
        """Get payroll entries for this period"""
        period = self.get_object()
        entries = PayrollEntry.objects.filter(payroll_period=period).select_related(
            'employee', 'employee__department'
        )
        
        # Apply filters
        department_id = request.query_params.get('department_id')
        if department_id:
            entries = entries.filter(employee__department_id=department_id)
        
        status_filter = request.query_params.get('status')
        if status_filter:
            entries = entries.filter(status=status_filter)
        
        # Paginate results
        page = self.paginate_queryset(entries)
        if page is not None:
            serializer = PayrollEntryListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PayrollEntryListSerializer(entries, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get payroll summary for this period"""
        period = self.get_object()
        summary = PayrollService.get_payroll_period_summary(period.id)
        return Response(summary)

class PayrollEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payroll entries"""
    queryset = PayrollEntry.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payroll_period', 'employee', 'status', 'payment_method']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_number']
    ordering_fields = ['employee__employee_number', 'net_salary', 'payment_date']
    ordering = ['employee__employee_number']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PayrollEntryListSerializer
        elif self.action == 'create':
            return PayrollEntryCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return PayrollEntryUpdateSerializer
        return PayrollEntrySerializer
    
    def get_queryset(self):
        queryset = PayrollEntry.objects.all()
        
        # Filter by current user if not admin
        if not self.request.user.is_staff:
            try:
                from Hr.models import Employee
                employee = Employee.objects.get(user=self.request.user)
                queryset = queryset.filter(employee=employee)
            except Employee.DoesNotExist:
                queryset = queryset.none()
        
        return queryset.select_related('employee', 'employee__department', 'payroll_period')
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced search for payroll entries"""
        serializer = PayrollSearchSerializer(data=request.data)
        
        if serializer.is_valid():
            filters = {}
            
            # Add filters
            for field in ['payroll_period_id', 'employee_id', 'department_id', 'status', 'payment_method']:
                if serializer.validated_data.get(field):
                    if field == 'payroll_period_id':
                        filters['payroll_period'] = serializer.validated_data[field]
                    elif field == 'employee_id':
                        filters['employee'] = serializer.validated_data[field]
                    elif field == 'department_id':
                        filters['employee__department'] = serializer.validated_data[field]
                    else:
                        filters[field] = serializer.validated_data[field]
            
            # Add date filters
            if serializer.validated_data.get('payment_date_from'):
                filters['payment_date__gte'] = serializer.validated_data['payment_date_from']
            
            if serializer.validated_data.get('payment_date_to'):
                filters['payment_date__lte'] = serializer.validated_data['payment_date_to']
            
            # Query entries
            entries = PayrollEntry.objects.filter(**filters).select_related(
                'employee', 'employee__department', 'payroll_period'
            )
            
            # Paginate results
            page = self.paginate_queryset(entries)
            if page is not None:
                serializer = PayrollEntryListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = PayrollEntryListSerializer(entries, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate payroll entry"""
        entry = self.get_object()
        
        try:
            updated_entry = PayrollService.recalculate_payroll_entry(
                entry.id,
                recalculated_by=request.user
            )
            
            serializer = PayrollEntrySerializer(updated_entry)
            return Response({
                'status': 'success',
                'message': 'تم إعادة حساب الراتب بنجاح',
                'entry': serializer.data
            })
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve payroll entry"""
        entry = self.get_object()
        
        try:
            PayrollService.approve_payroll_entry(
                entry.id,
                approved_by=request.user
            )
            return Response({'status': 'success', 'message': 'تم اعتماد كشف الراتب بنجاح'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark payroll entry as paid"""
        entry = self.get_object()
        payment_reference = request.data.get('payment_reference')
        payment_date = request.data.get('payment_date')
        
        try:
            PayrollService.mark_payroll_entry_paid(
                entry.id,
                payment_reference=payment_reference,
                payment_date=payment_date,
                paid_by=request.user
            )
            return Response({'status': 'success', 'message': 'تم تسجيل دفع الراتب بنجاح'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def payslip(self, request, pk=None):
        """Generate payslip for entry"""
        entry = self.get_object()
        
        try:
            payslip_data = PayrollService.generate_payslip(entry.id)
            return Response(payslip_data)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def bulk_approve(self, request):
        """Bulk approve payroll entries"""
        entry_ids = request.data.get('entry_ids', [])
        
        try:
            result = PayrollService.bulk_approve_payroll_entries(
                entry_ids,
                approved_by=request.user
            )
            
            return Response({
                'status': 'success',
                'message': 'تم اعتماد كشوف الرواتب بنجاح',
                'approved_count': result.get('approved_count', 0),
                'errors': result.get('errors', [])
            })
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EmployeeSalaryStructureViewSet(viewsets.ModelViewSet):
    """ViewSet for managing employee salary structures"""
    queryset = EmployeeSalaryStructure.objects.all()
    serializer_class = EmployeeSalaryStructureSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'is_active']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_number']
    ordering_fields = ['employee__employee_number', 'effective_date']
    ordering = ['employee__employee_number', '-effective_date']
    
    def get_queryset(self):
        return EmployeeSalaryStructure.objects.select_related('employee')
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate salary structure"""
        structure = self.get_object()
        
        try:
            PayrollService.activate_salary_structure(
                structure.id,
                activated_by=request.user
            )
            return Response({'status': 'success', 'message': 'تم تفعيل هيكل الراتب بنجاح'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate salary structure"""
        structure = self.get_object()
        
        try:
            PayrollService.deactivate_salary_structure(
                structure.id,
                deactivated_by=request.user
            )
            return Response({'status': 'success', 'message': 'تم إلغاء تفعيل هيكل الراتب بنجاح'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)