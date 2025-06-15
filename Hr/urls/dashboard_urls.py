# =============================================================================
# ElDawliya HR Management System - Dashboard & Analytics URLs
# =============================================================================
# URL patterns for dashboard, analytics, and reporting
# Includes AJAX endpoints for charts, statistics, and real-time data
# =============================================================================

from django.urls import path, include
from django.views.generic import RedirectView

# Import dashboard and analytics views
from Hr.views.dashboard_views import (
    HRDashboardView, dashboard_data_ajax, get_overview_data,
    get_attendance_chart_data, get_leaves_chart_data, get_payroll_chart_data,
    quick_employee_search, dashboard_notifications
)

# =============================================================================
# MAIN DASHBOARD
# =============================================================================

dashboard_patterns = [
    # Main dashboard
    path('', HRDashboardView.as_view(), name='hr_dashboard_main'),
    path('overview/', HRDashboardView.as_view(), name='hr_dashboard_overview'),
    path('home/', HRDashboardView.as_view(), name='hr_dashboard_home'),
    
    # Dashboard sections
    path('employees/', HRDashboardView.as_view(), name='dashboard_employees_section'),
    path('attendance/', HRDashboardView.as_view(), name='dashboard_attendance_section'),
    path('leave/', HRDashboardView.as_view(), name='dashboard_leave_section'),
    path('payroll/', HRDashboardView.as_view(), name='dashboard_payroll_section'),
    
    # Dashboard customization
    path('customize/', HRDashboardView.as_view(), name='dashboard_customize'),
    path('widgets/', HRDashboardView.as_view(), name='dashboard_widgets'),
    path('preferences/', HRDashboardView.as_view(), name='dashboard_preferences'),
]

# =============================================================================
# ANALYTICS AND REPORTS
# =============================================================================

analytics_patterns = [
    # Main analytics dashboard
    path('', HRDashboardView.as_view(), name='hr_analytics_dashboard'),
    path('overview/', HRDashboardView.as_view(), name='analytics_overview'),
    
    # Employee analytics
    path('employees/', HRDashboardView.as_view(), name='employee_analytics'),
    path('employees/demographics/', HRDashboardView.as_view(), name='employee_demographics_analytics'),
    path('employees/performance/', HRDashboardView.as_view(), name='employee_performance_analytics'),
    path('employees/turnover/', HRDashboardView.as_view(), name='employee_turnover_analytics'),
    path('employees/satisfaction/', HRDashboardView.as_view(), name='employee_satisfaction_analytics'),
    
    # Attendance analytics
    path('attendance/', HRDashboardView.as_view(), name='attendance_analytics'),
    path('attendance/trends/', HRDashboardView.as_view(), name='attendance_trends_analytics'),
    path('attendance/patterns/', HRDashboardView.as_view(), name='attendance_patterns_analytics'),
    path('attendance/productivity/', HRDashboardView.as_view(), name='attendance_productivity_analytics'),
    
    # Leave analytics
    path('leave/', HRDashboardView.as_view(), name='leave_analytics'),
    path('leave/usage/', HRDashboardView.as_view(), name='leave_usage_analytics'),
    path('leave/trends/', HRDashboardView.as_view(), name='leave_trends_analytics'),
    path('leave/patterns/', HRDashboardView.as_view(), name='leave_patterns_analytics'),
    
    # Payroll analytics
    path('payroll/', HRDashboardView.as_view(), name='payroll_analytics'),
    path('payroll/costs/', HRDashboardView.as_view(), name='payroll_costs_analytics'),
    path('payroll/trends/', HRDashboardView.as_view(), name='payroll_trends_analytics'),
    path('payroll/distribution/', HRDashboardView.as_view(), name='payroll_distribution_analytics'),
]

# =============================================================================
# REPORTING SYSTEM
# =============================================================================

reports_patterns = [
    # Main reports dashboard
    path('', HRDashboardView.as_view(), name='hr_reports_dashboard'),
    path('builder/', HRDashboardView.as_view(), name='report_builder'),
    path('templates/', HRDashboardView.as_view(), name='report_templates'),
    
    # Standard reports
    path('standard/', HRDashboardView.as_view(), name='standard_reports'),
    path('standard/employee-roster/', HRDashboardView.as_view(), name='employee_roster_report'),
    path('standard/attendance-summary/', HRDashboardView.as_view(), name='attendance_summary_report'),
    path('standard/leave-summary/', HRDashboardView.as_view(), name='leave_summary_report'),
    path('standard/payroll-summary/', HRDashboardView.as_view(), name='payroll_summary_report'),
    
    # Custom reports
    path('custom/', HRDashboardView.as_view(), name='custom_reports'),
    path('custom/create/', HRDashboardView.as_view(), name='custom_report_create'),
    path('custom/<int:report_id>/', HRDashboardView.as_view(), name='custom_report_detail'),
    path('custom/<int:report_id>/edit/', HRDashboardView.as_view(), name='custom_report_edit'),
    path('custom/<int:report_id>/run/', HRDashboardView.as_view(), name='custom_report_run'),
    
    # Scheduled reports
    path('scheduled/', HRDashboardView.as_view(), name='scheduled_reports'),
    path('scheduled/create/', HRDashboardView.as_view(), name='scheduled_report_create'),
    path('scheduled/<int:schedule_id>/', HRDashboardView.as_view(), name='scheduled_report_detail'),
    
    # Report exports
    path('export/', HRDashboardView.as_view(), name='reports_export'),
    path('export/excel/', HRDashboardView.as_view(), name='reports_export_excel'),
    path('export/pdf/', HRDashboardView.as_view(), name='reports_export_pdf'),
    path('export/csv/', HRDashboardView.as_view(), name='reports_export_csv'),
]

# =============================================================================
# AJAX AND API ENDPOINTS
# =============================================================================

ajax_patterns = [
    # Dashboard data endpoints
    path('data/', dashboard_data_ajax, name='dashboard_data_ajax'),
    path('overview/', get_overview_data, name='dashboard_overview_ajax'),
    path('statistics/', dashboard_data_ajax, name='dashboard_statistics_ajax'),
    
    # Chart data endpoints
    path('charts/attendance/', get_attendance_chart_data, name='attendance_chart_data_ajax'),
    path('charts/leave/', get_leaves_chart_data, name='leave_chart_data_ajax'),
    path('charts/payroll/', get_payroll_chart_data, name='payroll_chart_data_ajax'),
    
    # Search endpoints
    path('search/employees/', quick_employee_search, name='quick_employee_search_ajax'),
    path('search/quick/', quick_employee_search, name='dashboard_quick_search_ajax'),
    
    # Notification endpoints
    path('notifications/', dashboard_notifications, name='dashboard_notifications_ajax'),
    path('notifications/count/', dashboard_notifications, name='dashboard_notifications_count_ajax'),
    path('notifications/mark-read/', dashboard_notifications, name='dashboard_notifications_mark_read_ajax'),
    
    # Real-time data endpoints
    path('realtime/stats/', dashboard_data_ajax, name='realtime_stats_ajax'),
    path('realtime/attendance/', get_attendance_chart_data, name='realtime_attendance_ajax'),
    path('realtime/alerts/', dashboard_notifications, name='realtime_alerts_ajax'),
    
    # Widget data endpoints
    path('widgets/employee-count/', dashboard_data_ajax, name='employee_count_widget_ajax'),
    path('widgets/attendance-today/', get_attendance_chart_data, name='attendance_today_widget_ajax'),
    path('widgets/pending-leaves/', get_leaves_chart_data, name='pending_leaves_widget_ajax'),
    path('widgets/payroll-status/', get_payroll_chart_data, name='payroll_status_widget_ajax'),
]

# =============================================================================
# KPI AND METRICS
# =============================================================================

kpi_patterns = [
    # KPI dashboard
    path('', HRDashboardView.as_view(), name='hr_kpi_dashboard'),
    path('overview/', HRDashboardView.as_view(), name='kpi_overview'),
    
    # Employee KPIs
    path('employees/', HRDashboardView.as_view(), name='employee_kpis'),
    path('employees/headcount/', HRDashboardView.as_view(), name='headcount_kpi'),
    path('employees/turnover-rate/', HRDashboardView.as_view(), name='turnover_rate_kpi'),
    path('employees/retention-rate/', HRDashboardView.as_view(), name='retention_rate_kpi'),
    path('employees/diversity/', HRDashboardView.as_view(), name='diversity_kpi'),
    
    # Attendance KPIs
    path('attendance/', HRDashboardView.as_view(), name='attendance_kpis'),
    path('attendance/rate/', HRDashboardView.as_view(), name='attendance_rate_kpi'),
    path('attendance/punctuality/', HRDashboardView.as_view(), name='punctuality_kpi'),
    path('attendance/absenteeism/', HRDashboardView.as_view(), name='absenteeism_kpi'),
    
    # Leave KPIs
    path('leave/', HRDashboardView.as_view(), name='leave_kpis'),
    path('leave/utilization/', HRDashboardView.as_view(), name='leave_utilization_kpi'),
    path('leave/approval-time/', HRDashboardView.as_view(), name='leave_approval_time_kpi'),
    
    # Payroll KPIs
    path('payroll/', HRDashboardView.as_view(), name='payroll_kpis'),
    path('payroll/cost-per-employee/', HRDashboardView.as_view(), name='cost_per_employee_kpi'),
    path('payroll/budget-variance/', HRDashboardView.as_view(), name='budget_variance_kpi'),
]

# =============================================================================
# MAIN URL PATTERNS
# =============================================================================

urlpatterns = [
    # Default redirect to main dashboard
    path('', RedirectView.as_view(pattern_name='hr:hr_dashboard_main', permanent=False), name='dashboard_home'),
    
    # Main dashboard
    path('dashboard/', include((dashboard_patterns, 'dashboard'))),
    path('main/', include((dashboard_patterns, 'main'))),  # Alternative naming
    
    # Analytics
    path('analytics/', include((analytics_patterns, 'analytics'))),
    path('insights/', include((analytics_patterns, 'insights'))),  # Alternative naming
    
    # Reports
    path('reports/', include((reports_patterns, 'reports'))),
    path('reporting/', include((reports_patterns, 'reporting'))),  # Alternative naming
    
    # KPIs and metrics
    path('kpi/', include((kpi_patterns, 'kpi'))),
    path('metrics/', include((kpi_patterns, 'metrics'))),  # Alternative naming
    
    # AJAX endpoints
    path('ajax/', include((ajax_patterns, 'ajax'))),
    path('api/', include((ajax_patterns, 'api'))),  # Alternative naming
    
    # =============================================================================
    # EXECUTIVE DASHBOARD
    # =============================================================================
    
    # Executive and management dashboards
    path('executive/', include([
        path('', HRDashboardView.as_view(), name='executive_dashboard'),
        path('summary/', HRDashboardView.as_view(), name='executive_summary'),
        path('kpis/', HRDashboardView.as_view(), name='executive_kpis'),
        path('trends/', HRDashboardView.as_view(), name='executive_trends'),
        path('alerts/', HRDashboardView.as_view(), name='executive_alerts'),
    ])),
    
    # =============================================================================
    # MANAGER DASHBOARD
    # =============================================================================
    
    # Manager and supervisor dashboards
    path('manager/', include([
        path('', HRDashboardView.as_view(), name='manager_dashboard'),
        path('team/', HRDashboardView.as_view(), name='manager_team_dashboard'),
        path('approvals/', HRDashboardView.as_view(), name='manager_approvals_dashboard'),
        path('performance/', HRDashboardView.as_view(), name='manager_performance_dashboard'),
        path('reports/', HRDashboardView.as_view(), name='manager_reports_dashboard'),
    ])),
    
    # =============================================================================
    # EMPLOYEE SELF-SERVICE DASHBOARD
    # =============================================================================
    
    # Employee self-service dashboard
    path('employee/', include([
        path('', HRDashboardView.as_view(), name='employee_dashboard'),
        path('profile/', HRDashboardView.as_view(), name='employee_profile_dashboard'),
        path('attendance/', HRDashboardView.as_view(), name='employee_attendance_dashboard'),
        path('leave/', HRDashboardView.as_view(), name='employee_leave_dashboard'),
        path('payroll/', HRDashboardView.as_view(), name='employee_payroll_dashboard'),
        path('documents/', HRDashboardView.as_view(), name='employee_documents_dashboard'),
    ])),
    
    # =============================================================================
    # REAL-TIME MONITORING
    # =============================================================================
    
    # Real-time monitoring and alerts
    path('monitoring/', include([
        path('', HRDashboardView.as_view(), name='hr_monitoring_dashboard'),
        path('realtime/', HRDashboardView.as_view(), name='realtime_monitoring'),
        path('alerts/', HRDashboardView.as_view(), name='monitoring_alerts'),
        path('notifications/', HRDashboardView.as_view(), name='monitoring_notifications'),
        path('system-health/', HRDashboardView.as_view(), name='system_health_monitoring'),
    ])),
    
    # =============================================================================
    # DASHBOARD CONFIGURATION
    # =============================================================================
    
    # Dashboard configuration and customization
    path('config/', include([
        path('', HRDashboardView.as_view(), name='dashboard_config'),
        path('widgets/', HRDashboardView.as_view(), name='dashboard_widgets_config'),
        path('layout/', HRDashboardView.as_view(), name='dashboard_layout_config'),
        path('permissions/', HRDashboardView.as_view(), name='dashboard_permissions_config'),
        path('themes/', HRDashboardView.as_view(), name='dashboard_themes_config'),
    ])),
    
    # =============================================================================
    # DATA EXPORT AND INTEGRATION
    # =============================================================================
    
    # Data export and integration
    path('export/', include([
        path('', HRDashboardView.as_view(), name='dashboard_export'),
        path('data/', dashboard_data_ajax, name='dashboard_data_export'),
        path('charts/', HRDashboardView.as_view(), name='dashboard_charts_export'),
        path('reports/', HRDashboardView.as_view(), name='dashboard_reports_export'),
        path('schedule/', HRDashboardView.as_view(), name='dashboard_scheduled_export'),
    ])),
]

# =============================================================================
# URL PATTERNS SUMMARY
# =============================================================================

"""
Dashboard & Analytics URL Patterns Summary:

Main Routes:
- /hr/analytics/ - Dashboard home (redirects to main dashboard)
- /hr/analytics/dashboard/ - Main HR dashboard
- /hr/analytics/analytics/ - Analytics and insights
- /hr/analytics/reports/ - Reporting system
- /hr/analytics/kpi/ - KPIs and metrics

Main Dashboard:
- /hr/analytics/dashboard/ - Main dashboard view
- /hr/analytics/dashboard/overview/ - Dashboard overview
- /hr/analytics/dashboard/employees/ - Employee section
- /hr/analytics/dashboard/attendance/ - Attendance section
- /hr/analytics/dashboard/customize/ - Dashboard customization

Analytics and Insights:
- /hr/analytics/analytics/ - Main analytics dashboard
- /hr/analytics/analytics/employees/ - Employee analytics
- /hr/analytics/analytics/attendance/ - Attendance analytics
- /hr/analytics/analytics/leave/ - Leave analytics
- /hr/analytics/analytics/payroll/ - Payroll analytics

Reporting System:
- /hr/analytics/reports/ - Main reports dashboard
- /hr/analytics/reports/builder/ - Report builder
- /hr/analytics/reports/standard/ - Standard reports
- /hr/analytics/reports/custom/ - Custom reports
- /hr/analytics/reports/scheduled/ - Scheduled reports

KPIs and Metrics:
- /hr/analytics/kpi/ - KPI dashboard
- /hr/analytics/kpi/employees/ - Employee KPIs
- /hr/analytics/kpi/attendance/ - Attendance KPIs
- /hr/analytics/kpi/leave/ - Leave KPIs
- /hr/analytics/kpi/payroll/ - Payroll KPIs

AJAX Endpoints:
- /hr/analytics/ajax/data/ - Dashboard data
- /hr/analytics/ajax/charts/attendance/ - Attendance charts
- /hr/analytics/ajax/search/employees/ - Employee search
- /hr/analytics/ajax/notifications/ - Notifications
- /hr/analytics/ajax/realtime/stats/ - Real-time statistics

Role-Based Dashboards:
- /hr/analytics/executive/ - Executive dashboard
- /hr/analytics/manager/ - Manager dashboard
- /hr/analytics/employee/ - Employee self-service dashboard

Real-Time Monitoring:
- /hr/analytics/monitoring/ - Monitoring dashboard
- /hr/analytics/monitoring/realtime/ - Real-time monitoring
- /hr/analytics/monitoring/alerts/ - System alerts

Dashboard Configuration:
- /hr/analytics/config/ - Dashboard configuration
- /hr/analytics/config/widgets/ - Widget configuration
- /hr/analytics/config/layout/ - Layout configuration

Data Export:
- /hr/analytics/export/ - Export dashboard
- /hr/analytics/export/data/ - Data export
- /hr/analytics/export/charts/ - Chart export

URL Naming Convention:
- hr_{entity}_dashboard - Main dashboard URLs
- {entity}_analytics - Analytics URLs
- {entity}_kpi - KPI URLs
- {action}_ajax - AJAX endpoints
"""
