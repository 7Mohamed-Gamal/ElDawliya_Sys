"""
URLs خاصة بمراقبة النظام
"""

from django.urls import path
from ..views.monitoring_views import (
    SystemMonitoringDashboard,
    get_current_metrics_api,
    get_metrics_history_api,
    get_alerts_api,
    acknowledge_alert_api,
    get_health_score_api,
    get_daily_summary_api,
    SystemMetricsDetailView,
    AlertsManagementView,
    system_performance_report,
    export_metrics_data
)

app_name = 'monitoring'

urlpatterns = [
    # Dashboard
    path('', SystemMonitoringDashboard.as_view(), name='dashboard'),
    
    # API endpoints
    path('api/current-metrics/', get_current_metrics_api, name='current_metrics_api'),
    path('api/metrics-history/', get_metrics_history_api, name='metrics_history_api'),
    path('api/alerts/', get_alerts_api, name='alerts_api'),
    path('api/acknowledge-alert/', acknowledge_alert_api, name='acknowledge_alert_api'),
    path('api/health-score/', get_health_score_api, name='health_score_api'),
    path('api/daily-summary/', get_daily_summary_api, name='daily_summary_api'),
    
    # Detail views
    path('metrics/<str:category>/', SystemMetricsDetailView.as_view(), name='metrics_detail'),
    path('alerts/', AlertsManagementView.as_view(), name='alerts_management'),
    path('report/', system_performance_report, name='performance_report'),
    path('export/', export_metrics_data, name='export_data'),
]