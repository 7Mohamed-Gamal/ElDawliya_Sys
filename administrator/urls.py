from django.urls import path
from . import views
from . import rbac_views
from . import views_updated
from . import simplified_permissions
from . import views_permissions
from . import views_permissions_improved

app_name = 'administrator'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),

    # Permissions Dashboard
    path('permissions-dashboard/', views.permission_dashboard, name='permission_dashboard'),

    # Simplified Permissions System
    path('simplified-permissions/', simplified_permissions.simplified_permissions_dashboard, name='simplified_permissions_dashboard'),
    path('simplified-permissions/help/', simplified_permissions.simplified_permissions_help, name='simplified_permissions_help'),
    path('permissions/explainer/', simplified_permissions.permissions_explainer, name='permissions_explainer'),

    # System Settings
    path('settings/', views.system_settings, name='settings'),
    path('settings/database/', views.database_settings, name='database_settings'),
    path('test-connection/', views.test_connection, name='test_connection'),

    # Departments (for backward compatibility, will be deprecated)
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department_add'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_edit'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),

    # Modules (for backward compatibility, will be deprecated)
    path('modules/', views_updated.ModuleListView.as_view(), name='module_list'),
    path('modules/add/', views.ModuleCreateView.as_view(), name='module_add'),
    path('modules/<int:pk>/edit/', views.ModuleUpdateView.as_view(), name='module_edit'),
    path('modules/<int:pk>/delete/', views.ModuleDeleteView.as_view(), name='module_delete'),

    # Helpers
    path('url-paths-helper/', views.url_paths_helper, name='url_paths_helper'),
    path('template-paths-helper/', views.template_paths_helper, name='template_paths_helper'),
    path('create-modules-from-paths/', views.create_modules_from_paths, name='create_modules_from_paths'),
    path('create-templates-from-paths/', views.create_templates_from_paths, name='create_templates_from_paths'),

    # RBAC Permissions System - Main System
    path('permissions/', rbac_views.permissions_dashboard, name='rbac_dashboard'),  # Main entry point for permissions
    path('permissions/help/', views.permission_help, name='permissions_help'),  # Help page for permissions system

    # User Permission Management (RBAC)
    path('users/permissions/', rbac_views.user_list, name='user_permission_list'),
    path('users/<int:user_id>/permissions/', rbac_views.user_roles, name='edit_user_permissions'),

    # RBAC Roles
    path('permissions/roles/', rbac_views.role_list, name='rbac_role_list'),
    path('permissions/roles/create/', rbac_views.role_create, name='rbac_role_create'),
    path('permissions/roles/<int:role_id>/', rbac_views.role_detail, name='rbac_role_detail'),
    path('permissions/roles/<int:role_id>/edit/', rbac_views.role_edit, name='rbac_role_edit'),
    path('permissions/roles/<int:role_id>/delete/', rbac_views.role_delete, name='rbac_role_delete'),
    path('permissions/roles/<int:role_id>/permissions/', rbac_views.role_permissions, name='rbac_role_permissions'),
    path('permissions/roles/<int:role_id>/bulk-assign-permissions/', rbac_views.bulk_assign_permissions, name='rbac_bulk_assign_permissions'),

    # RBAC Users
    path('permissions/users/', rbac_views.user_list, name='rbac_user_list'),
    path('permissions/users/<int:user_id>/', rbac_views.user_detail, name='rbac_user_detail'),
    path('permissions/users/<int:user_id>/roles/', rbac_views.user_roles, name='rbac_user_roles'),
    path('users/<int:user_id>/detail/', rbac_views.user_detail, name='user_detail'),

    # RBAC Permissions
    path('permissions/list/', rbac_views.permission_list, name='rbac_permission_list'),
    path('permissions/create/', rbac_views.permission_create, name='rbac_permission_create'),
    path('permissions/<int:permission_id>/edit/', rbac_views.permission_edit, name='rbac_permission_edit'),
    path('permissions/<int:permission_id>/delete/', rbac_views.permission_delete, name='rbac_permission_delete'),
    path('permissions/create-defaults/', rbac_views.create_default_permissions_view, name='rbac_create_default_permissions'),
    path('permissions/auto-create/', rbac_views.create_default_permissions_view, name='auto_create_permissions'),

    # Template Permissions
    path('template-permissions/', views.TemplatePermissionListView.as_view(), name='template_permission_list'),
    path('template-permissions/add/', views.TemplatePermissionCreateView.as_view(), name='template_permission_add'),
    path('template-permissions/<int:pk>/edit/', views.TemplatePermissionUpdateView.as_view(), name='template_permission_edit'),
    path('template-permissions/improved/add/', views_permissions_improved.improved_template_permission_create, name='improved_template_permission_add'),

    # RBAC Audit Log
    path('permissions/audit-log/', rbac_views.audit_log, name='rbac_audit_log'),

    # User Permissions Management
    path('users/permissions/', rbac_views.user_list, name='user_permission_list'),
    path('users/<int:user_id>/permissions/edit/', rbac_views.user_roles, name='edit_user_permissions'),
    path('users/<int:user_id>/detail/', rbac_views.user_detail, name='user_detail'),
    path('users/create/', views_permissions.user_create, name='user_create'),

    # Group Permissions Management
    path('groups/permissions/', rbac_views.role_list, name='group_permission_list'),

    # Legacy URL patterns (for backward compatibility)
    path('rbac/', rbac_views.permissions_dashboard, name='legacy_rbac_dashboard'),
    path('rbac/roles/', rbac_views.role_list, name='legacy_rbac_role_list'),
    path('rbac/users/', rbac_views.user_list, name='legacy_rbac_user_list'),
    path('rbac/permissions/', rbac_views.permission_list, name='legacy_rbac_permission_list'),
]
