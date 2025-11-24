"""
Monitoring URLs for ElDawliya System
مسارات المراقبة لنظام الدولية
"""

from django.urls import path
from ..views.monitoring_dashboard import (
    monitoring_dashboard,
    system_metrics_api,
    system_health_api,
    performance_metrics_api,
    alert_history_api,
    log_analysis_api,
    resource_usage_history_api,
    monitoring_settings_api,
    trigger_test_alert_api,
    export_monitoring_data_api,
    monitoring_reports_api
)

app_name = 'monitoring'

urlpatterns = [
    path('', monitoring_dashboard, name='monitoring_dashboard'),
    path('api/system-metrics/', system_metrics_api, name='system_metrics_api'),
    path('api/system-health/', system_health_api, name='system_health_api'),
    path('api/performance-metrics/', performance_metrics_api, name='performance_metrics_api'),
    path('api/alert-history/', alert_history_api, name='alert_history_api'),
    path('api/log-analysis/', log_analysis_api, name='log_analysis_api'),
    path('api/resource-history/', resource_usage_history_api, name='resource_usage_history_api'),
    path('api/settings/', monitoring_settings_api, name='monitoring_settings_api'),
    path('api/test-alert/', trigger_test_alert_api, name='trigger_test_alert_api'),
    path('api/export/', export_monitoring_data_api, name='export_monitoring_data_api'),
    path('api/reports/', monitoring_reports_api, name='monitoring_reports_api'),
]