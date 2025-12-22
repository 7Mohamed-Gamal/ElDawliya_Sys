# Core URLs package
from django.urls import path, include
from .. import views
from ..views.cache_monitoring import (
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

    # System Monitoring URLs - Include monitoring dashboard URLs
    path('monitoring/', include('core.urls.monitoring')),

    # Data Integration URLs
    path('integration/', views.integration_dashboard, name='integration_dashboard'),
    path('integration/status/', views.data_integration_status, name='data_integration_status'),
]