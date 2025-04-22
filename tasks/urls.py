from django.urls import path
from . import views
from .views import dashboard_stats

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='create'),
    path('<int:pk>/', views.task_detail, name='detail'),
    path('<int:pk>/update_status/', views.update_task_status, name='update_task_status'),
    path('list/', views.task_list, name='list'),
    path('<int:pk>/edit/', views.task_edit, name='edit'),
    path('<int:pk>/delete/', views.task_delete, name='delete'),
    path('<int:pk>/delete_step/', views.delete_step, name='delete_step'),
    path('create_from_meeting/<int:meeting_id>/', views.create_from_meeting, name='create_from_meeting'),
    path('api/dashboard_stats/', dashboard_stats, name='dashboard_stats'),
]
