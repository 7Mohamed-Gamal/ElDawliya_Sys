from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date, timedelta, datetime
from django.db.models import Count, Sum, Avg, Q
from django.http import HttpResponse

from Hr.services import (
    EmployeeService, 
    AttendanceService, 
    PayrollService, 
    LeaveService,
    ReportService
)
from ..serializers.analytics_serializers import (
    EmployeeStatisticsSerializer,
    AttendanceStatisticsSerializer,
    PayrollStatisticsSerializer,
    LeaveStatisticsSerializer,
    DashboardDataSerializer,
    KPISerializer,
    ChartDataSerializer,
    ReportParametersSerializer,
    AnalyticsFilterSerializer,
    TrendAnalysisSerializer,
    ComparisonAnalysisSerializer,
    CustomMetricSerializer
)
from ..permissions import CanViewReports

class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for analytics and reporting"""
    permission_classes = [IsAuthenticated, CanViewReports]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard data with key metrics"""
        try:
            # Get filter parameters
            date_range = request.query_params.get('date_range', 'month')
            department_id = request.query_params.get('department_id')
            
            # Calculate date range
            end_date = date.today()
            if date_range == 'week':
                start_date = end_date - timedelta(days=7)
            elif date_range == 'month':
                start_date = end_date.replace(day=1)
            elif date_range == 'quarter':
                quarter_start_month = ((end_date.month - 1) // 3) * 3 + 1
                start_date = end_date.replace(month=quarter_start_month, day=1)
            elif date_range == 'year':
                start_date = end_date.replace(month=1, day=1)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get statistics
            employee_stats = EmployeeService.get_employees_statistics(
                department_id=department_id
            )
            
            attendance_stats = AttendanceService.get_attendance_statistics(
                start_date=start_date,
                end_date=end_date,
                department_id=department_id
            )
            
            payroll_stats = PayrollService.get_payroll_statistics(
                start_date=start_date,
                end_date=end_date,
                department_id=department_id
            )
            
            leave_stats = LeaveService.get_leave_statistics(
                start_date=start_date,
                end_date=end_date,
                department_id=department_id
            )
            
            # Get recent activities and upcoming events
            recent_activities = self._get_recent_activities()
            upcoming_events = self._get_upcoming_events()
            
            dashboard_data = {
                'employee_stats': employee_stats,
                'attendance_stats': attendance_stats,
                'payroll_stats': payroll_stats,
                'leave_stats': leave_stats,
                'recent_activities': recent_activities,
                'upcoming_events': upcoming_events
            }
            
            serializer = DashboardDataSerializer(dashboard_data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def kpis(self, request):
        """Get Key Performance Indicators"""
        try:
            date_range = request.query_params.get('date_range', 'month')
            department_id = request.query_params.get('department_id')
            
            kpis = []
            
            # Employee KPIs
            employee_kpis = EmployeeService.get_employee_kpis(
                date_range=date_range,
                department_id=department_id
            )
            kpis.extend(employee_kpis)
            
            # Attendance KPIs
            attendance_kpis = AttendanceService.get_attendance_kpis(
                date_range=date_range,
                department_id=department_id
            )
            kpis.extend(attendance_kpis)
            
            # Payroll KPIs
            payroll_kpis = PayrollService.get_payroll_kpis(
                date_range=date_range,
                department_id=department_id
            )
            kpis.extend(payroll_kpis)
            
            # Leave KPIs
            leave_kpis = LeaveService.get_leave_kpis(
                date_range=date_range,
                department_id=department_id
            )
            kpis.extend(leave_kpis)
            
            serializer = KPISerializer(kpis, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def charts(self, request):
        """Get chart data for analytics"""
        try:
            chart_type = request.query_params.get('chart_type', 'all')
            date_range = request.query_params.get('date_range', 'month')
            department_id = request.query_params.get('department_id')
            
            charts = []
            
            if chart_type in ['all', 'employee']:
                # Employee distribution charts
                employee_charts = EmployeeService.get_employee_charts(
                    date_range=date_range,
                    department_id=department_id
                )
                charts.extend(employee_charts)
            
            if chart_type in ['all', 'attendance']:
                # Attendance charts
                attendance_charts = AttendanceService.get_attendance_charts(
                    date_range=date_range,
                    department_id=department_id
                )
                charts.extend(attendance_charts)
            
            if chart_type in ['all', 'payroll']:
                # Payroll charts
                payroll_charts = PayrollService.get_payroll_charts(
                    date_range=date_range,
                    department_id=department_id
                )
                charts.extend(payroll_charts)
            
            if chart_type in ['all', 'leave']:
                # Leave charts
                leave_charts = LeaveService.get_leave_charts(
                    date_range=date_range,
                    department_id=department_id
                )
                charts.extend(leave_charts)
            
            serializer = ChartDataSerializer(charts, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Generate custom reports"""
        serializer = ReportParametersSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                report_data = ReportService.generate_report(
                    report_type=serializer.validated_data['report_type'],
                    start_date=serializer.validated_data.get('start_date'),
                    end_date=serializer.validated_data.get('end_date'),
                    department_ids=serializer.validated_data.get('department_ids'),
                    employee_ids=serializer.validated_data.get('employee_ids'),
                    format=serializer.validated_data['format'],
                    include_charts=serializer.validated_data['include_charts'],
                    include_summary=serializer.validated_data['include_summary'],
                    generated_by=request.user
                )
                
                if serializer.validated_data['format'] in ['pdf', 'excel']:
                    # Return file response
                    response = HttpResponse(
                        report_data['content'],
                        content_type=report_data['content_type']
                    )
                    response['Content-Disposition'] = f'attachment; filename="{report_data["filename"]}"'
                    return response
                else:
                    # Return JSON data
                    return Response(report_data)
                    
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def trend_analysis(self, request):
        """Get trend analysis for specific metrics"""
        serializer = AnalyticsFilterSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                metric_name = request.data.get('metric_name')
                time_period = request.data.get('time_period', 'monthly')
                
                trend_data = ReportService.get_trend_analysis(
                    metric_name=metric_name,
                    time_period=time_period,
                    filters=serializer.validated_data
                )
                
                serializer = TrendAnalysisSerializer(trend_data)
                return Response(serializer.data)
                
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def comparison_analysis(self, request):
        """Get comparison analysis between departments, branches, or periods"""
        try:
            comparison_type = request.data.get('comparison_type')
            metric_name = request.data.get('metric_name')
            filters = request.data.get('filters', {})
            
            comparison_data = ReportService.get_comparison_analysis(
                comparison_type=comparison_type,
                metric_name=metric_name,
                filters=filters
            )
            
            serializer = ComparisonAnalysisSerializer(comparison_data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def export_data(self, request):
        """Export analytics data in various formats"""
        try:
            data_type = request.query_params.get('data_type', 'dashboard')
            format = request.query_params.get('format', 'excel')
            filters = {
                'date_range': request.query_params.get('date_range', 'month'),
                'department_id': request.query_params.get('department_id'),
                'start_date': request.query_params.get('start_date'),
                'end_date': request.query_params.get('end_date')
            }
            
            export_data = ReportService.export_analytics_data(
                data_type=data_type,
                format=format,
                filters=filters,
                exported_by=request.user
            )
            
            response = HttpResponse(
                export_data['content'],
                content_type=export_data['content_type']
            )
            response['Content-Disposition'] = f'attachment; filename="{export_data["filename"]}"'
            return response
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def custom_metric(self, request):
        """Calculate custom metrics based on user-defined formulas"""
        serializer = CustomMetricSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = ReportService.calculate_custom_metric(
                    name=serializer.validated_data['name'],
                    formula=serializer.validated_data['formula'],
                    data_sources=serializer.validated_data['data_sources'],
                    filters=serializer.validated_data.get('filters', {}),
                    aggregation_type=serializer.validated_data['aggregation_type']
                )
                
                return Response({
                    'metric_name': serializer.validated_data['name'],
                    'value': result['value'],
                    'unit': serializer.validated_data.get('unit', ''),
                    'calculation_details': result.get('details', {}),
                    'timestamp': timezone.now()
                })
                
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_recent_activities(self):
        """Get recent system activities"""
        # This would typically fetch from an audit log or activity model
        return [
            {
                'type': 'employee_added',
                'description': 'تم إضافة موظف جديد',
                'timestamp': timezone.now() - timedelta(hours=2),
                'user': 'HR Manager'
            },
            {
                'type': 'payroll_calculated',
                'description': 'تم حساب رواتب شهر ديسمبر',
                'timestamp': timezone.now() - timedelta(hours=5),
                'user': 'Payroll Manager'
            },
            {
                'type': 'leave_approved',
                'description': 'تم اعتماد طلب إجازة',
                'timestamp': timezone.now() - timedelta(hours=8),
                'user': 'Department Manager'
            }
        ]
    
    def _get_upcoming_events(self):
        """Get upcoming events and deadlines"""
        return [
            {
                'type': 'payroll_deadline',
                'title': 'موعد صرف الرواتب',
                'date': date.today() + timedelta(days=3),
                'description': 'موعد صرف رواتب شهر ديسمبر'
            },
            {
                'type': 'employee_birthday',
                'title': 'عيد ميلاد موظف',
                'date': date.today() + timedelta(days=5),
                'description': 'عيد ميلاد أحمد محمد'
            },
            {
                'type': 'work_anniversary',
                'title': 'ذكرى توظيف',
                'date': date.today() + timedelta(days=7),
                'description': 'ذكرى توظيف فاطمة علي - 5 سنوات'
            }
        ]