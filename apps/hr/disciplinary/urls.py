from django.urls import path
from . import views

app_name = 'disciplinary'

urlpatterns = [
    # Dashboard
    path('', views.disciplinary_dashboard, name='dashboard'),
    path('home/', views.disciplinary_dashboard, name='home'),

    # Disciplinary Actions
    path('actions/', views.action_list, name='action_list'),
    path('actions/create/', views.action_create, name='action_create'),
    path('actions/<int:action_id>/', views.action_detail, name='action_detail'),
    path('actions/<int:action_id>/edit/', views.action_update, name='action_update'),
    path('actions/<int:action_id>/delete/', views.action_delete, name='action_delete'),

    # Employee History
    path('employee/<int:emp_id>/history/', views.employee_history, name='employee_history'),

    # Reports & Export
    path('reports/', views.reports, name='reports'),
    path('export/', views.export_actions, name='export_actions'),
]

