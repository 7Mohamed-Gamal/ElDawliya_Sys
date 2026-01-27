from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'reports'

urlpatterns = [
    # لوحة التحكم الرئيسية
    # لوحة التحكم الرئيسية
    path('', views.dashboard, name='dashboard'),
    
    # Aliases for dashboard links
    path('hr/', RedirectView.as_view(pattern_name='reports:dashboard', permanent=False), name='hr'),
    path('finance/', RedirectView.as_view(pattern_name='reports:dashboard', permanent=False), name='finance'),
    path('projects/', RedirectView.as_view(pattern_name='reports:dashboard', permanent=False), name='projects'),
    path('inventory/', RedirectView.as_view(pattern_name='reports:dashboard', permanent=False), name='inventory'),

    # فئات التقارير
    path('categories/', views.report_categories, name='categories'),
    path('category/<int:category_id>/', views.category_templates, name='category_templates'),

    # إنتاج التقارير
    path('generate/<int:template_id>/', views.generate_report, name='generate_report'),
    path('<int:report_id>/', views.report_detail, name='report_detail'),
    path('<int:report_id>/download/', views.download_report, name='download_report'),
    path('<int:report_id>/delete/', views.delete_report, name='delete_report'),

    # التقارير الشخصية
    path('my-reports/', views.my_reports, name='my_reports'),

    # الجدولة
    path('schedules/', views.scheduled_reports, name='scheduled_reports'),
    path('schedule/create/<int:template_id>/', views.create_schedule, name='create_schedule'),

    # التحليلات
    path('analytics/', views.analytics, name='analytics'),

    # AJAX APIs
    path('ajax/report-status/<int:report_id>/', views.check_report_status, name='check_report_status'),
    path('ajax/template-parameters/<int:template_id>/', views.get_template_parameters, name='get_template_parameters'),
]
