from django.urls import path
from . import views

app_name = 'administrator'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),

    # System Settings
    path('settings/', views.system_settings, name='settings'),
    path('settings/database/', views.database_settings, name='database_settings'),
    path('database-setup/', views.database_setup, name='database_setup'),
    path('test-connection/', views.test_connection, name='test_connection'),

    # Departments
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department_add'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_edit'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),

    # Modules
    path('modules/', views.ModuleListView.as_view(), name='module_list'),
    path('modules/add/', views.ModuleCreateView.as_view(), name='module_add'),
    path('modules/<int:pk>/edit/', views.ModuleUpdateView.as_view(), name='module_edit'),
    path('modules/<int:pk>/delete/', views.ModuleDeleteView.as_view(), name='module_delete'),

    # Helpers
]
