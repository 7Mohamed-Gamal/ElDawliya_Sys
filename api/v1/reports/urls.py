"""
Reports API URLs
روابط API التقارير
"""

from django.urls import path
from . import views

app_name = 'reports_api'

urlpatterns = [
    # Dashboard and overview
    path('dashboard/', views.DashboardDataView.as_view(), name='dashboard_data'),
    path('overview/', views.SystemOverviewView.as_view(), name='system_overview'),

    # Report generation
    path('generate/', views.GenerateReportView.as_view(), name='generate_report'),
    path('templates/', views.ReportTemplatesView.as_view(), name='report_templates'),
    path('custom/', views.CustomReportView.as_view(), name='custom_report'),

    # Export functionality
    path('export/', views.ExportReportView.as_view(), name='export_report'),
    path('export/excel/', views.ExportExcelView.as_view(), name='export_excel'),
    path('export/pdf/', views.ExportPDFView.as_view(), name='export_pdf'),
    path('export/csv/', views.ExportCSVView.as_view(), name='export_csv'),

    # Scheduled reports
    path('scheduled/', views.ScheduledReportsView.as_view(), name='scheduled_reports'),
    path('schedule/', views.ScheduleReportView.as_view(), name='schedule_report'),

    # Analytics and insights
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('insights/', views.InsightsView.as_view(), name='insights'),
    path('trends/', views.TrendsAnalysisView.as_view(), name='trends_analysis'),

    # Performance metrics
    path('performance/', views.PerformanceMetricsView.as_view(), name='performance_metrics'),
    path('kpi/', views.KPIView.as_view(), name='kpi'),

    # Cache management
    path('cache/clear/', views.ClearReportCacheView.as_view(), name='clear_report_cache'),
    path('cache/status/', views.CacheStatusView.as_view(), name='cache_status'),
]
