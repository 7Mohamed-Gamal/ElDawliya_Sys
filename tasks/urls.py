from django.urls import path
from django.views.generic.base import RedirectView
from . import views
from .views import dashboard_stats

app_name = 'tasks'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Tasks
    path('list/', views.task_list, name='list'),
    path('create/', views.task_create, name='create'),
    path('<int:pk>/', views.task_detail, name='detail'),
    path('<int:pk>/update_status/', views.update_task_status, name='update_task_status'),
    path('<int:pk>/edit/', views.task_edit, name='edit'),
    path('<int:pk>/delete/', views.task_delete, name='delete'),
    path('<int:pk>/delete_step/', views.delete_step, name='delete_step'),
    path('create_from_meeting/<int:meeting_id>/', views.create_from_meeting, name='create_from_meeting'),

    # My Tasks
    path('my_tasks/', views.my_tasks, name='my_tasks'),

    # Completed Tasks
    path('completed/', views.completed_tasks, name='completed'),

    # Reports
    path('reports/', views.reports, name='reports'),

    # API
    path('api/dashboard_stats/', dashboard_stats, name='dashboard_stats'),
    
    # Legacy URL redirects
    path('detail/<int:pk>/', RedirectView.as_view(pattern_name='tasks:detail'), name='legacy_detail'),
]
