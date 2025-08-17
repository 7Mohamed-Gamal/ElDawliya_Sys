"""
روابط مراقبة النظام
"""

from django.urls import path
from Hr.views.monitoring_views import (
    SystemMonitoringDashboard,
    SystemStatusAPI,
    SystemAlertsAPI,
    MonitoringHistoryAPI,
    SystemMetricsAPI,
    TriggerSystemCheckAPI,
    ClearAlertsAPI,
    MonitoringSettingsAPI,
    monitoring_dashboard_view,
    system_logs_view,
    performance_report_view
)

app_name = 'monitoring'

urlpatterns = [
    # لوحة تحكم المراقبة
    path('', monitoring_dashboard_view, name='dashboard'),
    path('dashboard/', SystemMonitoringDashboard.as_view(), name='dashboard_class'),
    
    # السجلات والتقارير
    path('logs/', system_logs_view, name='logs'),
    path('performance/', performance_report_view, name='performance_report'),
    
    # API endpoints
    path('api/status/', SystemStatusAPI.as_view(), name='api_status'),
    path('api/alerts/', SystemAlertsAPI.as_view(), name='api_alerts'),
    path('api/alerts/clear/', ClearAlertsAPI.as_view(), name='api_clear_alerts'),
    path('api/history/', MonitoringHistoryAPI.as_view(), name='api_history'),
    path('api/metrics/', SystemMetricsAPI.as_view(), name='api_metrics'),
    path('api/check/', TriggerSystemCheckAPI.as_view(), name='api_trigger_check'),
    path('api/settings/', MonitoringSettingsAPI.as_view(), name='api_settings'),
]