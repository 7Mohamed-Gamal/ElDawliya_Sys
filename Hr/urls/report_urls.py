"""
روابط نظام التقارير الشاملة
"""

from django.urls import path
from ..views import report_views
from ..views import export_views

app_name = 'reports'

urlpatterns = [
    # لوحة التحكم الرئيسية
    path('', report_views.reports_dashboard, name='dashboard'),
    
    # قوالب التقارير
    path('templates/', report_views.report_templates, name='templates'),
    path('templates/<uuid:template_id>/', report_views.report_template_detail, name='template_detail'),
    path('templates/<uuid:template_id>/generate/', report_views.generate_report, name='generate_report'),
    path('templates/<uuid:template_id>/filters/', report_views.get_filter_data, name='get_filter_data'),
    
    # مثيلات التقارير
    path('instances/<uuid:instance_id>/', report_views.report_instance_detail, name='instance_detail'),
    path('instances/<uuid:instance_id>/download/', report_views.download_report, name='download_report'),
    path('instances/<uuid:instance_id>/share/', report_views.share_report, name='share_report'),
    
    # تقاريري
    path('my-reports/', report_views.my_reports, name='my_reports'),
    
    # المفضلة
    path('favorites/', report_views.favorites, name='favorites'),
    path('favorites/add/<uuid:template_id>/', report_views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<uuid:favorite_id>/', report_views.remove_from_favorites, name='remove_from_favorites'),
    
    # التقارير المشاركة
    path('shared/', report_views.shared_with_me, name='shared_with_me'),
    path('shared/<uuid:share_id>/', report_views.view_shared_report, name='view_shared_report'),
    
    # التصدير المتقدم
    path('export/<uuid:instance_id>/options/', export_views.export_options, name='export_options'),
    path('export/<uuid:instance_id>/multiple/', export_views.export_multiple_formats, name='export_multiple_formats'),
    path('export/<uuid:instance_id>/email/', export_views.send_report_email, name='send_report_email'),
    path('export/bulk/', export_views.bulk_export, name='bulk_export'),
    path('export/history/', export_views.export_history, name='export_history'),
    path('export/statistics/', export_views.export_statistics, name='export_statistics'),
    path('export/progress/<str:task_id>/', export_views.get_export_progress, name='get_export_progress'),
    
    # الجدولة
    path('schedule/<uuid:template_id>/', export_views.schedule_report, name='schedule_report'),
    path('scheduled/', export_views.scheduled_reports, name='scheduled_reports'),
    path('scheduled/<uuid:scheduled_id>/toggle/', export_views.toggle_scheduled_report, name='toggle_scheduled_report'),
    path('scheduled/<uuid:scheduled_id>/delete/', export_views.delete_scheduled_report, name='delete_scheduled_report'),
]