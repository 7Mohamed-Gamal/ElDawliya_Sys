from django.urls import path
from . import views
from . import views_permissions
from . import views_permissions_fixed
from . import simplified_permissions
from . import views_permissions_improved
from . import rbac_views
from . import views_new
from . import views_updated

app_name = 'administrator'

urlpatterns = [
    # New Permissions System
    path('new-permissions/', views_new.permissions_dashboard, name='new_permissions_dashboard'),

    # App Modules
    path('new-permissions/app-modules/', views_new.app_module_list, name='app_module_list'),
    path('new-permissions/app-modules/create/', views_new.app_module_create, name='app_module_create'),
    path('new-permissions/app-modules/<int:pk>/edit/', views_new.app_module_edit, name='app_module_edit'),
    path('new-permissions/app-modules/<int:pk>/delete/', views_new.app_module_delete, name='app_module_delete'),

    # Operation Permissions
    path('new-permissions/operations/', views_new.operation_permission_list, name='operation_permission_list'),
    path('new-permissions/operations/create/', views_new.operation_permission_create, name='operation_permission_create'),
    path('new-permissions/operations/<int:pk>/edit/', views_new.operation_permission_edit, name='operation_permission_edit'),
    path('new-permissions/operations/<int:pk>/delete/', views_new.operation_permission_delete, name='operation_permission_delete'),

    # Page Permissions
    path('new-permissions/pages/', views_new.page_permission_list, name='page_permission_list'),
    path('new-permissions/pages/create/', views_new.page_permission_create, name='page_permission_create'),
    path('new-permissions/pages/<int:pk>/edit/', views_new.page_permission_edit, name='page_permission_edit'),
    path('new-permissions/pages/<int:pk>/delete/', views_new.page_permission_delete, name='page_permission_delete'),

    # User Permissions
    path('new-permissions/users/', views_new.user_permission_list, name='user_permission_list'),
    path('new-permissions/users/<int:user_id>/permissions/', views_new.manage_user_permissions, name='manage_user_permissions'),
    path('new-permissions/users/<int:user_id>/detail/', views_new.user_permission_detail, name='user_permission_detail'),

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
    path('modules/', views_updated.ModuleListView.as_view(), name='module_list'),
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
path('group-permissions/<int:group_id>/edit-fixed/', views_permissions_fixed.edit_group_permissions, name='edit_group_permissions_fixed'),
path('group-permissions/<int:group_id>/select-all/', views_permissions.select_all_permissions, name='group_select_all_permissions'),
path('group-permissions/<int:group_id>/clear-all/', views_permissions.clear_all_permissions, name='group_clear_all_permissions'),

    # User Permissions Actions
    path('user-permissions/<int:user_id>/select-all/', views_permissions.select_all_permissions, name='user_select_all_permissions'),
    path('user-permissions/<int:user_id>/clear-all/', views_permissions.clear_all_permissions, name='user_clear_all_permissions'),

    # Simplified Permissions System
    path('simplified-permissions/', simplified_permissions.simplified_permissions_dashboard, name='simplified_permissions_dashboard'),
    path('simplified-permissions/help/', simplified_permissions.simplified_permissions_help, name='simplified_permissions_help'),
    path('simplified-permissions/explainer/', simplified_permissions.permissions_explainer, name='permissions_explainer'),
    path('simplified-permissions/group/<int:group_id>/departments/', simplified_permissions.manage_group_departments, name='manage_group_departments'),
    path('simplified-permissions/user/<int:user_id>/groups/', simplified_permissions.manage_user_groups, name='manage_user_groups'),
    path('simplified-permissions/user/<int:user_id>/permissions/', simplified_permissions.manage_user_permissions, name='manage_user_permissions'),

    # Improved Permissions System
    path('improved-permissions/groups/', views_permissions_improved.improved_group_permissions, name='improved_group_permissions'),
    path('improved-permissions/groups/<int:group_id>/', views_permissions_improved.improved_group_permissions, name='improved_group_permissions'),
    path('improved-permissions/template-permissions/add/', views_permissions_improved.improved_template_permission_create, name='improved_template_permission_add'),
    path('improved-permissions/template-permissions/<int:pk>/edit/', views_permissions_improved.improved_template_permission_update, name='improved_template_permission_update'),
    path('improved-permissions/modules/add/', views_permissions_improved.improved_module_create, name='improved_module_create'),
    path('improved-permissions/modules/<int:pk>/edit/', views_permissions_improved.improved_module_update, name='improved_module_update'),

    # Helpers
    path('url-paths-helper/', views.url_paths_helper, name='url_paths_helper'),
    path('template-paths-helper/', views.template_paths_helper, name='template_paths_helper'),
    path('create-modules-from-paths/', views.create_modules_from_paths, name='create_modules_from_paths'),
    path('create-templates-from-paths/', views.create_templates_from_paths, name='create_templates_from_paths'),

    # RBAC Permissions System
    path('rbac/', rbac_views.permissions_dashboard, name='rbac_dashboard'),

    # RBAC Roles
    path('rbac/roles/', rbac_views.role_list, name='rbac_role_list'),
    path('rbac/roles/create/', rbac_views.role_create, name='rbac_role_create'),
    path('rbac/roles/<int:role_id>/', rbac_views.role_detail, name='rbac_role_detail'),
    path('rbac/roles/<int:role_id>/edit/', rbac_views.role_edit, name='rbac_role_edit'),
    path('rbac/roles/<int:role_id>/delete/', rbac_views.role_delete, name='rbac_role_delete'),
    path('rbac/roles/<int:role_id>/permissions/', rbac_views.role_permissions, name='rbac_role_permissions'),
    path('rbac/roles/<int:role_id>/bulk-assign-permissions/', rbac_views.bulk_assign_permissions, name='rbac_bulk_assign_permissions'),

    # RBAC Users
    path('rbac/users/', rbac_views.user_list, name='rbac_user_list'),
    path('rbac/users/<int:user_id>/', rbac_views.user_detail, name='rbac_user_detail'),
    path('rbac/users/<int:user_id>/roles/', rbac_views.user_roles, name='rbac_user_roles'),

    # RBAC Permissions
    path('rbac/permissions/', rbac_views.permission_list, name='rbac_permission_list'),
    path('rbac/permissions/create/', rbac_views.permission_create, name='rbac_permission_create'),
    path('rbac/permissions/<int:permission_id>/edit/', rbac_views.permission_edit, name='rbac_permission_edit'),
    path('rbac/permissions/<int:permission_id>/delete/', rbac_views.permission_delete, name='rbac_permission_delete'),
    path('rbac/permissions/create-defaults/', rbac_views.create_default_permissions_view, name='rbac_create_default_permissions'),

    # RBAC Audit Log
    path('rbac/audit-log/', rbac_views.audit_log, name='rbac_audit_log'),
]
