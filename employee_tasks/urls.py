from django.urls import path
from . import views

app_name = 'employee_tasks'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/my/', views.my_tasks, name='my_tasks'),
    path('tasks/assigned/', views.assigned_tasks, name='assigned_tasks'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/update-status/', views.update_task_status, name='update_task_status'),
    path('tasks/<int:pk>/update-progress/', views.update_task_progress, name='update_task_progress'),
    
    # Task Steps
    path('tasks/<int:pk>/steps/<int:step_id>/edit/', views.step_edit, name='step_edit'),
    path('tasks/<int:pk>/steps/<int:step_id>/delete/', views.step_delete, name='step_delete'),
    path('tasks/<int:pk>/steps/<int:step_id>/toggle/', views.toggle_step_status, name='toggle_step_status'),
    
    # Task Reminders
    path('tasks/<int:pk>/reminders/<int:reminder_id>/delete/', views.reminder_delete, name='reminder_delete'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Calendar
    path('calendar/', views.calendar, name='calendar'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]
