"""
خدمات التقارير والتحليلات المتقدمة
Advanced Reporting and Analytics Services
"""
from django.db import models
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q, F
from datetime import date, timedelta
from decimal import Decimal
from core.services.base import BaseService


class ReportEngine(BaseService):
    """
    محرك التقارير المرن
    Flexible report generation engine
    """

    def __init__(self, user=None):
        """__init__ function"""
        super().__init__(user)
        self.filters = {}
        self.aggregations = {}
        self.groupings = []
        self.ordering = []

    def add_filter(self, field, operator, value):
        """إضافة فلتر للتقرير"""
        self.filters[field] = {'operator': operator, 'value': value}
        return self

    def add_aggregation(self, field, function, alias=None):
        """إضافة تجميع للتقرير"""
        alias = alias or f"{function}_{field}"
        self.aggregations[alias] = function(field)
        return self

    def group_by(self, *fields):
        """تجميع البيانات حسب الحقول"""
        self.groupings.extend(fields)
        return self

    def order_by(self, *fields):
        """ترتيب النتائج"""
        self.ordering.extend(fields)
        return self

    def generate(self, model_class, format='json'):
        """توليد التقرير"""
        queryset = model_class.objects.all()

        # تطبيق الفلاتر
        for field, filter_data in self.filters.items():
            operator = filter_data['operator']
            value = filter_data['value']

            if operator == 'equals':
                queryset = queryset.filter(**{field: value})
            elif operator == 'contains':
                queryset = queryset.filter(**{f"{field}__icontains": value})
            elif operator == 'gte':
                queryset = queryset.filter(**{f"{field}__gte": value})
            elif operator == 'lte':
                queryset = queryset.filter(**{f"{field}__lte": value})
            elif operator == 'in':
                queryset = queryset.filter(**{f"{field}__in": value})

        # تطبيق التجميع
        if self.groupings:
            queryset = queryset.values(*self.groupings)

        # تطبيق التجميعات
        if self.aggregations:
            queryset = queryset.annotate(**self.aggregations)

        # تطبيق الترتيب
        if self.ordering:
            queryset = queryset.order_by(*self.ordering)

        # تحويل النتائج
        if format == 'json':
            return list(queryset)
        elif format == 'excel':
            return self._export_to_excel(queryset)
        elif format == 'pdf':
            return self._export_to_pdf(queryset)

        return list(queryset)

    def _export_to_excel(self, data):
        """تصدير إلى Excel"""
        # Implementation would use openpyxl or similar
        return "Excel export placeholder"

    def _export_to_pdf(self, data):
        """تصدير إلى PDF"""
        # Implementation would use reportlab or similar
        return "PDF export placeholder"


class AnalyticsService(BaseService):
    """
    خدمة التحليلات المتقدمة
    Advanced analytics service
    """

    def get_hr_analytics(self, start_date=None, end_date=None):
        """تحليلات الموارد البشرية"""
        from core.models.hr import Employee
        from core.models.attendance import EmployeeAttendance
        from core.models.leaves import LeaveRequest

        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Employee statistics
        employee_stats = Employee.objects.aggregate(
            total_employees=Count('id'),
            active_employees=Count('id', filter=Q(is_active=True)),
            new_hires=Count('id', filter=Q(
                hire_date__range=[start_date, end_date]
            ))
        )

        # Attendance statistics
        attendance_stats = EmployeeAttendance.objects.filter(
            att_date__range=[start_date, end_date]
        ).aggregate(
            total_records=Count('id'),
            present_days=Count('id', filter=Q(status='present')),
            late_days=Count('id', filter=Q(status='late')),
            absent_days=Count('id', filter=Q(status='absent'))
        )

        # Leave statistics
        leave_stats = LeaveRequest.objects.filter(
            start_date__range=[start_date, end_date]
        ).aggregate(
            total_requests=Count('id'),
            approved_requests=Count('id', filter=Q(status='approved')),
            pending_requests=Count('id', filter=Q(status='pending'))
        )

        return {
            'period': {'start_date': start_date, 'end_date': end_date},
            'employee_statistics': employee_stats,
            'attendance_statistics': attendance_stats,
            'leave_statistics': leave_stats
        }

    def get_inventory_analytics(self, warehouse_id=None):
        """تحليلات المخزون"""
        from core.models.inventory import Product, StockLevel, InventoryMovement

        queryset = StockLevel.objects.all()
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)

        # Stock statistics
        stock_stats = queryset.aggregate(
            total_products=Count('id'),
            total_stock_value=Sum(F('current_stock') * F('average_cost')),
            low_stock_items=Count('id', filter=Q(
                current_stock__lte=F('reorder_level')
            ))
        )

        # Movement statistics (last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        movement_stats = InventoryMovement.objects.filter(
            movement_date__range=[start_date, end_date]
        ).aggregate(
            total_movements=Count('id'),
            inbound_movements=Count('id', filter=Q(
                movement_type__in=['receipt', 'purchase', 'transfer_in']
            )),
            outbound_movements=Count('id', filter=Q(
                movement_type__in=['issue', 'sale', 'transfer_out']
            ))
        )

        return {
            'stock_statistics': stock_stats,
            'movement_statistics': movement_stats
        }

    def get_project_analytics(self, project_id=None):
        """تحليلات المشاريع"""
        from core.models.projects import Project, Task

        project_queryset = Project.objects.all()
        if project_id:
            project_queryset = project_queryset.filter(id=project_id)

        # Project statistics
        project_stats = project_queryset.aggregate(
            total_projects=Count('id'),
            active_projects=Count('id', filter=Q(status='active')),
            completed_projects=Count('id', filter=Q(status='completed')),
            overdue_projects=Count('id', filter=Q(
                end_date__lt=timezone.now().date(),
                status__in=['active', 'planning']
            ))
        )

        # Task statistics
        task_queryset = Task.objects.all()
        if project_id:
            task_queryset = task_queryset.filter(project_id=project_id)

        task_stats = task_queryset.aggregate(
            total_tasks=Count('id'),
            completed_tasks=Count('id', filter=Q(status='completed')),
            in_progress_tasks=Count('id', filter=Q(status='in_progress')),
            overdue_tasks=Count('id', filter=Q(
                due_date__lt=timezone.now().date(),
                status__in=['pending', 'in_progress']
            ))
        )

        return {
            'project_statistics': project_stats,
            'task_statistics': task_stats
        }


class DashboardService(BaseService):
    """
    خدمة لوحات التحكم التفاعلية
    Interactive dashboard service
    """

    def get_executive_dashboard(self):
        """لوحة تحكم تنفيذية"""
        analytics = AnalyticsService(user=self.user)

        return {
            'hr_summary': analytics.get_hr_analytics(),
            'inventory_summary': analytics.get_inventory_analytics(),
            'project_summary': analytics.get_project_analytics(),
            'generated_at': timezone.now()
        }

    def get_hr_dashboard(self):
        """لوحة تحكم الموارد البشرية"""
        analytics = AnalyticsService(user=self.user)
        return analytics.get_hr_analytics()

    def get_inventory_dashboard(self, warehouse_id=None):
        """لوحة تحكم المخزون"""
        analytics = AnalyticsService(user=self.user)
        return analytics.get_inventory_analytics(warehouse_id)


class ExportService(BaseService):
    """
    خدمة تصدير البيانات
    Data export service
    """

    def export_to_excel(self, data, filename, sheet_name='Sheet1'):
        """تصدير إلى Excel"""
        # Implementation would use openpyxl
        return f"Excel file: {filename}"

    def export_to_pdf(self, data, template_name, filename):
        """تصدير إلى PDF"""
        # Implementation would use reportlab
        return f"PDF file: {filename}"

    def export_to_csv(self, data, filename):
        """تصدير إلى CSV"""
        # Implementation would use csv module
        return f"CSV file: {filename}"


class ScheduledReportService(BaseService):
    """
    خدمة التقارير المجدولة
    Scheduled reports service
    """

    def create_scheduled_report(self, data):
        """إنشاء تقرير مجدول"""
        # Implementation would create scheduled report configuration
        return self.format_response(
            message='تم إنشاء التقرير المجدول بنجاح'
        )

    def execute_scheduled_reports(self):
        """تنفيذ التقارير المجدولة"""
        # Implementation would run scheduled reports
        return self.format_response(
            message='تم تنفيذ التقارير المجدولة بنجاح'
        )
