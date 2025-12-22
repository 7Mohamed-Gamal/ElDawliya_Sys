from django.urls import path, include
from django.views.generic.base import RedirectView
from . import views

app_name = 'tasks'

# Main task patterns
task_patterns = [
    path('', views.task_list, name='list'),
    path('create/', views.task_create, name='create'),
    path('<int:pk>/', views.task_detail, name='detail'),
    path('<str:pk>/', views.task_detail, name='detail'),  # Support meeting_X format
    path('<int:pk>/edit/', views.task_edit, name='edit'),
    path('<int:pk>/delete/', views.task_delete, name='delete'),
    path('<int:pk>/update_status/', views.update_task_status, name='update_task_status'),
    path('<str:pk>/update_status/', views.update_task_status, name='update_task_status'),  # Support meeting_X format
    path('<int:pk>/delete_step/', views.delete_step, name='delete_step'),
    path('<str:pk>/delete_step/', views.delete_step, name='delete_step'),  # Support meeting_X format
    path('bulk_update/', views.bulk_task_update, name='bulk_update'),
    path('export/', views.export_tasks, name='export'),
]

# API patterns
api_patterns = [
    path('dashboard_stats/', views.dashboard_stats, name='dashboard_stats'),
    path('task_stats/', views.task_stats_api, name='task_stats_api'),
    path('search/', views.task_search_api, name='search_api'),
]

# Report patterns
report_patterns = [
    path('', views.reports, name='reports'),
    path('export/', views.export_report, name='export_report'),
    path('analytics/', views.task_analytics, name='analytics'),
]

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Task management
    path('tasks/', include(task_patterns)),

    # Quick access patterns (for backward compatibility)
    path('list/', views.task_list, name='list'),
    path('create/', views.task_create, name='create'),
    path('my_tasks/', views.my_tasks, name='my_tasks'),
    path('completed/', views.completed_tasks, name='completed'),

    # Meeting integration
    path('create_from_meeting/<int:meeting_id>/', views.create_from_meeting, name='create_from_meeting'),

    # Reports
    path('reports/', include(report_patterns)),

    # API endpoints
    path('api/', include(api_patterns)),

    # Legacy URL redirects
    path('detail/<int:pk>/', RedirectView.as_view(pattern_name='tasks:detail'), name='legacy_detail'),
    path('<int:pk>/', RedirectView.as_view(pattern_name='tasks:detail'), name='legacy_task_detail'),
]
