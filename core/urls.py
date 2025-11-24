"""
Core URLs for ElDawliya System
روابط أساسية لنظام الدولية

This module defines URL patterns for core functionality including:
- Reporting dashboard
- System administration
- Data integration interfaces
- Health checks and monitoring
- Cache monitoring and management
"""

from django.urls import path, include
from . import views
from .views.cache_monitoring import (
    cache_dashboard,
    cache_stats_api,
    slow_queries_api,
    cache_operations_api,
    cache_key_browser,
    cache_health_check
)

app_name = 'core'

urlpatterns = [
    # Reporting URLs
    path('reporting/', views.reporting_dashboard, name='reporting_dashboard'),
    path('reporting/dashboard/', views.ReportingDashboardView.as_view(), name='reporting_dashboard_class'),

    # System Administration URLs
    path('admin/system/', views.system_administration, name='system_administration'),
    path('admin/health/', views.system_health_check, name='system_health_check'),
    path('admin/cache/clear/', views.clear_all_caches, name='clear_all_caches'),

    # Cache Monitoring URLs
    path('cache/', cache_dashboard, name='cache_dashboard'),
    path('cache/stats/', cache_stats_api, name='cache_stats_api'),
    path('cache/slow-queries/', slow_queries_api, name='slow_queries_api'),
    path('cache/operations/', cache_operations_api, name='cache_operations_api'),
    path('cache/keys/', cache_key_browser, name='cache_key_browser_api'),
    path('cache/health/', cache_health_check, name='cache_health_check'),

    # System Monitoring URLs
    path('monitoring/', include([
        path('', 'core.views.monitoring_dashboard.monitoring_dashboard', name='monitoring_dashboard'),
        path('api/system-metrics/', 'core.views.monitoring_dashboard.system_metrics_api', name='system_metrics_api'),
        path('api/system-health/', 'core.views.monitoring_dashboard.system_health_api', name='system_health_api'),
        path('api/performance-metrics/', 'core.views.monitoring_dashboard.performance_metrics_api', name='performance_metrics_api'),
        path('api/alert-history/', 'core.views.monitoring_dashboard.alert_history_api', name='alert_history_api'),
        path('api/log-analysis/', 'core.views.monitoring_dashboard.log_analysis_api', name='log_analysis_api'),
        path('api/resource-history/', 'core.views.monitoring_dashboard.resource_usage_history_api', name='resource_usage_history_api'),
        path('api/settings/', 'core.views.monitoring_dashboard.monitoring_settings_api', name='monitoring_settings_api'),
        path('api/test-alert/', 'core.views.monitoring_dashboard.trigger_test_alert_api', name='trigger_test_alert_api'),
        path('api/export/', 'core.views.monitoring_dashboard.export_monitoring_data_api', name='export_monitoring_data_api'),
        path('api/reports/', 'core.views.monitoring_dashboard.monitoring_reports_api', name='monitoring_reports_api'),
    ])),

    # Data Integration URLs
    path('integration/', views.integration_dashboard, name='integration_dashboard'),
    path('integration/status/', views.data_integration_status, name='data_integration_status'),
]
