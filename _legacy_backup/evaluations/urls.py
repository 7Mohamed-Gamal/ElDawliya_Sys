from django.urls import path
from . import views

app_name = 'evaluations'

urlpatterns = [
    # لوحة التحكم الرئيسية
    path('', views.dashboard, name='dashboard'),

    # إدارة التقييمات
    path('evaluations/', views.evaluation_list, name='evaluation_list'),
    path('evaluations/create/', views.create_evaluation, name='create_evaluation'),
    path('evaluations/<int:eval_id>/', views.evaluation_detail, name='evaluation_detail'),
    path('evaluations/<int:eval_id>/edit/', views.edit_evaluation, name='edit_evaluation'),
    path('evaluations/<int:eval_id>/delete/', views.delete_evaluation, name='delete_evaluation'),
    path('evaluations/<int:eval_id>/print/', views.print_evaluation, name='print_evaluation'),

    # إدارة فترات التقييم
    path('periods/', views.periods, name='periods'),
    path('periods/add/', views.add_period, name='add_period'),
    path('periods/<int:period_id>/', views.get_period, name='get_period'),
    path('periods/<int:period_id>/edit/', views.update_period, name='update_period'),
    path('periods/<int:period_id>/delete/', views.delete_period, name='delete_period'),

    # التقارير والتحليلات
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.export_evaluations, name='export_evaluations'),
    path('performance-comparison/', views.performance_comparison, name='performance_comparison'),
    path('performance-analytics/', views.performance_analytics, name='performance_analytics'),

    # بوابة الموظف
    path('my-evaluations/', views.my_evaluations, name='my_evaluations'),
    path('my-performance/', views.my_performance, name='my_performance'),

    # العمليات المجمعة
    path('bulk/create/', views.bulk_create_evaluations, name='bulk_create_evaluations'),
    path('bulk/export/', views.bulk_export_evaluations, name='bulk_export_evaluations'),

    # AJAX APIs
    path('ajax/employee-performance/<int:emp_id>/', views.employee_performance_ajax, name='employee_performance_ajax'),
    path('ajax/evaluation-stats/', views.evaluation_stats_ajax, name='evaluation_stats_ajax'),
]
