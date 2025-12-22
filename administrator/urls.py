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
    path('create-database-backup/', views.create_database_backup, name='create_database_backup'),
    path('list-database-backups/', views.list_database_backups, name='list_database_backups'),
    path('restore-database-backup/', views.restore_database_backup, name='restore_database_backup'),

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

    # Groups
    path('groups/', views.GroupListView.as_view(), name='group_list'),
    path('groups/add/', views.GroupCreateView.as_view(), name='group_add'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('groups/<int:pk>/edit/', views.GroupUpdateView.as_view(), name='group_edit'),
    path('groups/<int:pk>/delete/', views.GroupDeleteView.as_view(), name='group_delete'),
    path('groups/<int:pk>/permissions/', views.group_permissions, name='group_permissions'),

    # Users
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/add/', views.UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/groups/', views.UserGroupsUpdateView.as_view(), name='user_groups'),
    path('users/<int:pk>/permissions/', views.user_permissions, name='user_permissions'),

    # Permissions
    path('permissions/', views.permission_dashboard, name='permission_dashboard'),
    path('permissions/help/', views.permissions_help, name='permissions_help'),
]
