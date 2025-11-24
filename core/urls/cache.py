"""
Cache monitoring URLs
"""

from django.urls import path
from core.views.cache_monitoring import (
    cache_dashboard,
    cache_stats_api,
    slow_queries_api,
    cache_operations_api,
    cache_key_browser,
    cache_health_check
)

app_name = 'cache'

urlpatterns = [
    path('dashboard/', cache_dashboard, name='dashboard'),
    path('api/stats/', cache_stats_api, name='stats_api'),
    path('api/slow-queries/', slow_queries_api, name='slow_queries_api'),
    path('api/operations/', cache_operations_api, name='operations_api'),
    path('api/keys/', cache_key_browser, name='key_browser_api'),
    path('api/health/', cache_health_check, name='health_check_api'),
]