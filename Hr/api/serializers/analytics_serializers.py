from rest_framework import serializers
from datetime import date

class EmployeeStatisticsSerializer(serializers.Serializer):
    """Serializer for employee statistics"""
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    inactive_employees = serializers.IntegerField()
    terminated_employees = serializers.IntegerField()
    new_hires_this_month = serializers.IntegerField()
    employees_by_department = serializers.DictField()
    employees_by_gender = serializers.DictField()
    employees_by_employment_type = serializers.DictField()
    average_age = serializers.FloatField()
    average_years_of_service = serializers.FloatField()

class AttendanceStatisticsSerializer(serializers.Serializer):
    """Serializer for attendance statistics"""
    total_records = serializers.IntegerField()
    present_today = serializers.IntegerField()
    absent_today = serializers.IntegerField()
    late_arrivals_today = serializers.IntegerField()
    early_departures_today = serializers.IntegerField()
    average_attendance_rate = serializers.FloatField()
    total_overtime_hours = serializers.FloatField()
    attendance_by_department = serializers.DictField()
    monthly_attendance_trend = serializers.ListField()

class PayrollStatisticsSerializer(serializers.Serializer):
    """Serializer for payroll statistics"""
    total_payroll_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_salary = serializers.DecimalField(max_digits=15, decimal_places=2)
    highest_salary = serializers.DecimalField(max_digits=15, decimal_places=2)
    lowest_salary = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_allowances = serializers.DecimalField(max_digits=15, decimal_places=2)
    payroll_by_department = serializers.DictField()
    salary_distribution = serializers.ListField()

class LeaveStatisticsSerializer(serializers.Serializer):
    """Serializer for leave statistics"""
    total_leave_requests = serializers.IntegerField()
    approved_requests = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    rejected_requests = serializers.IntegerField()
    total_leave_days = serializers.IntegerField()
    average_leave_days_per_employee = serializers.FloatField()
    leave_by_type = serializers.DictField()
    leave_by_department = serializers.DictField()
    monthly_leave_trend = serializers.ListField()

class DashboardDataSerializer(serializers.Serializer):
    """Serializer for dashboard data"""
    employee_stats = EmployeeStatisticsSerializer()
    attendance_stats = AttendanceStatisticsSerializer()
    payroll_stats = PayrollStatisticsSerializer()
    leave_stats = LeaveStatisticsSerializer()
    recent_activities = serializers.ListField()
    upcoming_events = serializers.ListField()

class KPISerializer(serializers.Serializer):
    """Serializer for Key Performance Indicators"""
    name = serializers.CharField()
    value = serializers.FloatField()
    target = serializers.FloatField(required=False, allow_null=True)
    unit = serializers.CharField()
    trend = serializers.CharField()  # 'up', 'down', 'stable'
    change_percentage = serializers.FloatField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)

class ChartDataSerializer(serializers.Serializer):
    """Serializer for chart data"""
    chart_type = serializers.CharField()  # 'bar', 'line', 'pie', 'doughnut'
    title = serializers.CharField()
    labels = serializers.ListField()
    datasets = serializers.ListField()
    options = serializers.DictField(required=False)

class ReportParametersSerializer(serializers.Serializer):
    """Serializer for report parameters"""
    report_type = serializers.ChoiceField(choices=[
        ('employee', 'Employee Report'),
        ('attendance', 'Attendance Report'),
        ('payroll', 'Payroll Report'),
        ('leave', 'Leave Report'),
        ('custom', 'Custom Report')
    ])
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    department_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    employee_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    format = serializers.ChoiceField(choices=[
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON')
    ], default='pdf')
    include_charts = serializers.BooleanField(default=True)
    include_summary = serializers.BooleanField(default=True)

class AnalyticsFilterSerializer(serializers.Serializer):
    """Serializer for analytics filters"""
    date_range = serializers.ChoiceField(choices=[
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('quarter', 'This Quarter'),
        ('year', 'This Year'),
        ('custom', 'Custom Range')
    ], default='month')
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    department_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    branch_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    employee_status = serializers.ChoiceField(choices=[
        ('all', 'All'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated')
    ], default='active')
    
    def validate(self):
        data = super().validate()
        
        # If custom date range is selected, start_date and end_date are required
        if data.get('date_range') == 'custom':
            if not data.get('start_date') or not data.get('end_date'):
                raise serializers.ValidationError(
                    "Start date and end date are required for custom date range"
                )
            
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError(
                    "Start date must be before end date"
                )
        
        return data

class TrendAnalysisSerializer(serializers.Serializer):
    """Serializer for trend analysis data"""
    metric_name = serializers.CharField()
    time_period = serializers.CharField()  # 'daily', 'weekly', 'monthly', 'yearly'
    data_points = serializers.ListField()
    trend_direction = serializers.CharField()  # 'increasing', 'decreasing', 'stable'
    growth_rate = serializers.FloatField(required=False, allow_null=True)
    forecast = serializers.ListField(required=False)

class ComparisonAnalysisSerializer(serializers.Serializer):
    """Serializer for comparison analysis"""
    comparison_type = serializers.CharField()  # 'department', 'branch', 'period'
    metric_name = serializers.CharField()
    categories = serializers.ListField()
    values = serializers.ListField()
    percentages = serializers.ListField(required=False)
    insights = serializers.ListField(required=False)

class CustomMetricSerializer(serializers.Serializer):
    """Serializer for custom metrics"""
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    formula = serializers.CharField()
    data_sources = serializers.ListField()
    filters = serializers.DictField(required=False)
    aggregation_type = serializers.ChoiceField(choices=[
        ('sum', 'Sum'),
        ('average', 'Average'),
        ('count', 'Count'),
        ('min', 'Minimum'),
        ('max', 'Maximum')
    ])
    unit = serializers.CharField(required=False, allow_blank=True)