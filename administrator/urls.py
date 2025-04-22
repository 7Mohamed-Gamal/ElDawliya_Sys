from django.urls import path
from . import views
from . import views_permissions
from . import simplified_permissions

app_name = 'administrator'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),

    # System Settings
    path('settings/', views.system_settings, name='settings'),
    path('settings/database/', views.database_settings, name='database_settings'),
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

    # Permissions Dashboard
    path('permissions/', views_permissions.permission_dashboard, name='permission_dashboard'),
    path('permissions/help/', views_permissions.permissions_help, name='permissions_help'),

    # Module Permissions
    path('permissions/list/', views_permissions.PermissionListView.as_view(), name='permission_list'),
    path('permissions/add/', views_permissions.PermissionCreateView.as_view(), name='permission_add'),
    path('permissions/<int:pk>/edit/', views_permissions.PermissionUpdateView.as_view(), name='permission_edit'),
    path('permissions/<int:pk>/delete/', views_permissions.PermissionDeleteView.as_view(), name='permission_delete'),
    path('permissions/auto-create/', views_permissions.auto_create_permissions, name='auto_create_permissions'),

    # Template Permissions
    path('template-permissions/', views_permissions.TemplatePermissionListView.as_view(), name='template_permission_list'),
    path('template-permissions/add/', views_permissions.TemplatePermissionCreateView.as_view(), name='template_permission_add'),
    path('template-permissions/<int:pk>/edit/', views_permissions.TemplatePermissionUpdateView.as_view(), name='template_permission_edit'),
    path('template-permissions/<int:pk>/delete/', views_permissions.TemplatePermissionDeleteView.as_view(), name='template_permission_delete'),

    # Groups
    path('groups/', views_permissions.GroupListView.as_view(), name='group_list'),
    path('groups/add/', views_permissions.GroupCreateView.as_view(), name='group_add'),
    path('groups/<int:pk>/', views_permissions.GroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/edit/', views_permissions.GroupUpdateView.as_view(), name='group_edit'),
    path('groups/<int:pk>/delete/', views_permissions.GroupDeleteView.as_view(), name='group_delete'),

    # User-Group Management
    path('user-groups/', views_permissions.UserGroupListView.as_view(), name='user_group_list'),
    path('user-groups/add/', views_permissions.UserGroupCreateView.as_view(), name='user_group_add'),
    path('user-groups/add/<int:user_id>/', views_permissions.UserGroupCreateView.as_view(), name='user_group_add_with_user'),
    path('user-groups/<int:pk>/edit/', views_permissions.UserGroupUpdateView.as_view(), name='user_group_edit'),
    path('user-groups/<int:pk>/delete/', views_permissions.UserGroupDeleteView.as_view(), name='user_group_delete'),

    # User Management
    path('users/add/', views_permissions.user_create, name='user_create'),
    path('users/<int:pk>/', views_permissions.user_detail, name='user_detail'),
    path('user-permissions/', views_permissions.user_permission_list, name='user_permission_list'),
    path('user-permissions/<int:user_id>/edit/', views_permissions.edit_user_permissions, name='edit_user_permissions'),

    # Group Permissions
    path('group-permissions/', views_permissions.group_permission_list, name='group_permission_list'),
    path('group-permissions/<int:group_id>/edit/', views_permissions.edit_group_permissions, name='edit_group_permissions'),

    # Simplified Permissions System
    path('simplified-permissions/', simplified_permissions.simplified_permissions_dashboard, name='simplified_permissions_dashboard'),
    path('simplified-permissions/help/', simplified_permissions.simplified_permissions_help, name='simplified_permissions_help'),
    path('simplified-permissions/explainer/', simplified_permissions.permissions_explainer, name='permissions_explainer'),
    path('simplified-permissions/group/<int:group_id>/departments/', simplified_permissions.manage_group_departments, name='manage_group_departments'),
    path('simplified-permissions/user/<int:user_id>/groups/', simplified_permissions.manage_user_groups, name='manage_user_groups'),
    path('simplified-permissions/user/<int:user_id>/permissions/', simplified_permissions.manage_user_permissions, name='manage_user_permissions'),
]
