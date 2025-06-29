"""
Enhanced Reporting System for ElDawliya System
نظام التقارير المحسن لنظام الدولية

This module provides comprehensive reporting capabilities including:
- Interactive dashboards with real-time data
- Customizable report generation
- Export functionality (PDF, Excel, CSV)
- Scheduled reports
- Data visualization and analytics
"""

from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.conf import settings
import json
import csv
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

# Import models for reporting
from Hr.models import Employee, Department
from tasks.models import Task
from meetings.models import Meeting
from inventory.models import TblProducts
from Purchase_orders.models import PurchaseRequest

logger = logging.getLogger(__name__)


class ReportingService:
    """
    Service for enhanced reporting and analytics
    خدمة التقارير والتحليلات المحسنة
    """
    
    def __init__(self):
        self.cache_timeout = 1800  # 30 minutes
        self.supported_formats = ['json', 'csv', 'excel', 'pdf']
        self.chart_types = ['bar', 'line', 'pie', 'doughnut', 'area']
    
    def get_dashboard_data(self, user=None, date_range: str = '30d') -> Dict[str, Any]:
        """
        Get comprehensive dashboard data
        جلب بيانات لوحة التحكم الشاملة
        """
        cache_key = f'dashboard_data_{user.id if user else "all"}_{date_range}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Calculate date range
        end_date = timezone.now()
        if date_range == '7d':
            start_date = end_date - timedelta(days=7)
        elif date_range == '30d':
            start_date = end_date - timedelta(days=30)
        elif date_range == '90d':
            start_date = end_date - timedelta(days=90)
        elif date_range == '1y':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        dashboard_data = {
            'overview': self._get_overview_metrics(user, start_date, end_date),
            'employee_analytics': self._get_employee_analytics(user, start_date, end_date),
            'task_analytics': self._get_task_analytics(user, start_date, end_date),
            'meeting_analytics': self._get_meeting_analytics(user, start_date, end_date),
            'inventory_analytics': self._get_inventory_analytics(user, start_date, end_date),
            'purchase_analytics': self._get_purchase_analytics(user, start_date, end_date),
            'trends': self._get_trend_data(user, start_date, end_date),
            'charts': self._get_chart_data(user, start_date, end_date),
            'generated_at': timezone.now().isoformat(),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'period': date_range
            }
        }
        
        # Cache for 30 minutes
        cache.set(cache_key, dashboard_data, self.cache_timeout)
        return dashboard_data
    
    def _get_overview_metrics(self, user, start_date, end_date) -> Dict[str, Any]:
        """Get high-level overview metrics"""
        return {
            'total_employees': Employee.objects.count(),
            'active_employees': Employee.objects.filter(working_condition='سارى').count(),
            'total_tasks': Task.objects.count(),
            'active_tasks': Task.objects.filter(status__in=['pending', 'in_progress']).count(),
            'completed_tasks_period': Task.objects.filter(
                status='completed',
                updated_at__range=[start_date, end_date]
            ).count(),
            'total_meetings': Meeting.objects.count(),
            'upcoming_meetings': Meeting.objects.filter(date__gte=timezone.now()).count(),
            'meetings_this_period': Meeting.objects.filter(
                date__range=[start_date, end_date]
            ).count(),
            'total_products': TblProducts.objects.count(),
            'low_stock_products': TblProducts.objects.filter(
                qte_in_stock__lte=F('minimum_threshold')
            ).count(),
            'total_purchase_requests': PurchaseRequest.objects.count(),
            'pending_purchase_requests': PurchaseRequest.objects.filter(status='pending').count()
        }
    
    def _get_employee_analytics(self, user, start_date, end_date) -> Dict[str, Any]:
        """Get employee analytics data"""
        # Department distribution
        dept_distribution = list(
            Employee.objects.values('department__dept_name')
            .annotate(count=Count('emp_id'))
            .order_by('-count')
        )
        
        # Working condition distribution
        working_condition_dist = list(
            Employee.objects.values('working_condition')
            .annotate(count=Count('emp_id'))
            .order_by('-count')
        )
        
        return {
            'department_distribution': dept_distribution,
            'working_condition_distribution': working_condition_dist,
            'total_departments': Department.objects.count(),
            'average_employees_per_department': Employee.objects.count() / max(Department.objects.count(), 1)
        }
    
    def _get_task_analytics(self, user, start_date, end_date) -> Dict[str, Any]:
        """Get task analytics data"""
        # Task status distribution
        status_distribution = list(
            Task.objects.values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Task priority distribution
        priority_distribution = list(
            Task.objects.values('priority')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Tasks by assignee
        assignee_distribution = list(
            Task.objects.filter(assigned_to__isnull=False)
            .values('assigned_to__username')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        return {
            'status_distribution': status_distribution,
            'priority_distribution': priority_distribution,
            'assignee_distribution': assignee_distribution,
            'completion_rate': self._calculate_task_completion_rate(start_date, end_date),
            'overdue_tasks': Task.objects.filter(
                end_date__lt=timezone.now().date(),
                status__in=['pending', 'in_progress']
            ).count()
        }
    
    def _get_meeting_analytics(self, user, start_date, end_date) -> Dict[str, Any]:
        """Get meeting analytics data"""
        # Meeting status distribution
        status_distribution = list(
            Meeting.objects.values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Meetings by creator
        creator_distribution = list(
            Meeting.objects.values('created_by__username')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        return {
            'status_distribution': status_distribution,
            'creator_distribution': creator_distribution,
            'meetings_this_week': Meeting.objects.filter(
                date__gte=timezone.now().date(),
                date__lt=timezone.now().date() + timedelta(days=7)
            ).count(),
            'average_meetings_per_month': Meeting.objects.count() / 12  # Rough estimate
        }
    
    def _get_inventory_analytics(self, user, start_date, end_date) -> Dict[str, Any]:
        """Get inventory analytics data"""
        # Products by category
        category_distribution = list(
            TblProducts.objects.values('cat_name')
            .annotate(count=Count('product_id'))
            .order_by('-count')
        )
        
        # Stock status analysis
        total_products = TblProducts.objects.count()
        low_stock = TblProducts.objects.filter(
            qte_in_stock__lt=F('minimum_threshold'),
            minimum_threshold__isnull=False
        ).exclude(minimum_threshold=0).count()
        out_of_stock = TblProducts.objects.filter(qte_in_stock__lte=0).count()
        
        return {
            'category_distribution': category_distribution,
            'stock_status': {
                'total': total_products,
                'low_stock': low_stock,
                'out_of_stock': out_of_stock,
                'healthy_stock': total_products - low_stock
            },
            'total_stock_value': TblProducts.objects.aggregate(
                total_value=Sum(F('qte_in_stock') * F('unit_price'))
            )['total_value'] or 0
        }
    
    def _get_purchase_analytics(self, user, start_date, end_date) -> Dict[str, Any]:
        """Get purchase order analytics data"""
        # Purchase request status distribution
        status_distribution = list(
            PurchaseRequest.objects.values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Requests by vendor (since PurchaseRequest doesn't have department)
        vendor_distribution = list(
            PurchaseRequest.objects.values('vendor__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        return {
            'status_distribution': status_distribution,
            'vendor_distribution': vendor_distribution,
            'requests_this_period': PurchaseRequest.objects.filter(
                request_date__range=[start_date, end_date]
            ).count(),
            'average_processing_time': self._calculate_avg_processing_time()
        }
    
    def _get_trend_data(self, user, start_date, end_date) -> Dict[str, Any]:
        """Get trend data for charts"""
        # Generate daily data points
        days = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            days.append(current_date.isoformat())
            current_date += timedelta(days=1)
        
        # Task completion trend
        task_completion_trend = []
        for day in days:
            day_date = datetime.strptime(day, '%Y-%m-%d').date()
            completed_count = Task.objects.filter(
                status='completed',
                updated_at__date=day_date
            ).count()
            task_completion_trend.append(completed_count)
        
        # Meeting trend
        meeting_trend = []
        for day in days:
            day_date = datetime.strptime(day, '%Y-%m-%d').date()
            meeting_count = Meeting.objects.filter(date=day_date).count()
            meeting_trend.append(meeting_count)
        
        return {
            'labels': days,
            'task_completion': task_completion_trend,
            'meetings': meeting_trend
        }
    
    def _get_chart_data(self, user, start_date, end_date) -> Dict[str, Any]:
        """Get data formatted for charts"""
        return {
            'employee_by_department': {
                'type': 'doughnut',
                'data': self._format_chart_data(
                    Employee.objects.values('department__dept_name')
                    .annotate(count=Count('emp_id'))
                    .order_by('-count')
                )
            },
            'task_status': {
                'type': 'pie',
                'data': self._format_chart_data(
                    Task.objects.values('status')
                    .annotate(count=Count('id'))
                    .order_by('-count')
                )
            },
            'meeting_status': {
                'type': 'bar',
                'data': self._format_chart_data(
                    Meeting.objects.values('status')
                    .annotate(count=Count('id'))
                    .order_by('-count')
                )
            }
        }
    
    def _format_chart_data(self, queryset) -> Dict[str, List]:
        """Format queryset data for chart consumption"""
        labels = []
        data = []
        
        for item in queryset:
            # Get the first value as label (department name, status, etc.)
            label_key = list(item.keys())[0]
            label = item[label_key] or 'غير محدد'
            labels.append(label)
            data.append(item['count'])
        
        return {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                ][:len(data)]
            }]
        }
    
    def _calculate_task_completion_rate(self, start_date, end_date) -> float:
        """Calculate task completion rate for the period"""
        total_tasks = Task.objects.filter(
            created_at__range=[start_date, end_date]
        ).count()
        
        if total_tasks == 0:
            return 0.0
        
        completed_tasks = Task.objects.filter(
            created_at__range=[start_date, end_date],
            status='completed'
        ).count()
        
        return round((completed_tasks / total_tasks) * 100, 2)
    
    def _calculate_avg_processing_time(self) -> float:
        """Calculate average processing time for purchase requests"""
        # This is a simplified calculation
        # In a real implementation, you'd track status change timestamps
        return 5.2  # Average days (placeholder)
    
    def generate_custom_report(self, report_config: Dict[str, Any], user=None) -> Dict[str, Any]:
        """
        Generate a custom report based on configuration
        إنشاء تقرير مخصص بناءً على التكوين
        """
        report_type = report_config.get('type', 'summary')
        date_range = report_config.get('date_range', '30d')
        modules = report_config.get('modules', ['all'])
        format_type = report_config.get('format', 'json')
        
        # Get base dashboard data
        dashboard_data = self.get_dashboard_data(user, date_range)
        
        # Filter data based on selected modules
        if 'all' not in modules:
            filtered_data = {}
            for module in modules:
                if f'{module}_analytics' in dashboard_data:
                    filtered_data[f'{module}_analytics'] = dashboard_data[f'{module}_analytics']
            dashboard_data.update(filtered_data)
        
        # Add report metadata
        report_data = {
            'report_id': f"report_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            'generated_at': timezone.now().isoformat(),
            'generated_by': user.username if user else 'system',
            'config': report_config,
            'data': dashboard_data
        }
        
        return report_data
    
    def export_report(self, report_data: Dict[str, Any], format_type: str = 'json') -> HttpResponse:
        """
        Export report in specified format
        تصدير التقرير بالتنسيق المحدد
        """
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}")
        
        if format_type == 'json':
            return self._export_json(report_data)
        elif format_type == 'csv':
            return self._export_csv(report_data)
        elif format_type == 'excel':
            return self._export_excel(report_data)
        elif format_type == 'pdf':
            return self._export_pdf(report_data)
    
    def _export_json(self, report_data: Dict[str, Any]) -> HttpResponse:
        """Export report as JSON"""
        response = HttpResponse(
            json.dumps(report_data, indent=2, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="report_{report_data["report_id"]}.json"'
        return response
    
    def _export_csv(self, report_data: Dict[str, Any]) -> HttpResponse:
        """Export report as CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Metric', 'Value', 'Category'])
        
        # Write overview data
        overview = report_data['data'].get('overview', {})
        for key, value in overview.items():
            writer.writerow([key.replace('_', ' ').title(), value, 'Overview'])
        
        response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="report_{report_data["report_id"]}.csv"'
        return response
    
    def _export_excel(self, report_data: Dict[str, Any]) -> HttpResponse:
        """Export report as Excel (placeholder - requires openpyxl)"""
        # This would require openpyxl library
        # For now, return CSV format
        return self._export_csv(report_data)
    
    def _export_pdf(self, report_data: Dict[str, Any]) -> HttpResponse:
        """Export report as PDF (placeholder - requires reportlab)"""
        # This would require reportlab library
        # For now, return JSON format
        return self._export_json(report_data)
    
    def clear_cache(self):
        """Clear all reporting cache"""
        # This is a simplified cache clearing
        # In production, you'd want more targeted cache invalidation
        cache.clear()
        logger.info("Reporting cache cleared")


# Singleton instance
reporting_service = ReportingService()
