"""
Core URLs for ElDawliya System
روابط أساسية لنظام الدولية

This module defines URL patterns for core functionality including:
- Reporting dashboard
- System administration
- Data integration interfaces
- Health checks and monitoring
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Reporting URLs
    path('reporting/', views.reporting_dashboard, name='reporting_dashboard'),
    path('reporting/dashboard/', views.ReportingDashboardView.as_view(), name='reporting_dashboard_class'),
    
    # System Administration URLs
    path('admin/system/', views.system_administration, name='system_administration'),
    path('admin/health/', views.system_health_check, name='system_health_check'),
    path('admin/cache/clear/', views.clear_all_caches, name='clear_all_caches'),
    
    # Data Integration URLs
    path('integration/', views.integration_dashboard, name='integration_dashboard'),
    path('integration/status/', views.data_integration_status, name='data_integration_status'),
]
