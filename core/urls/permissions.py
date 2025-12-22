"""
URL patterns for hierarchical permissions system
أنماط URL لنظام الصلاحيات الهرمي
"""

from django.urls import path, include
from ..views.permissions import (
    permissions_dashboard, modules_list, roles_list, role_detail,
    assign_role_to_user, user_permissions, approval_workflows_list,
    approve_workflow_step, permissions_api_data, clear_permissions_cache,
    RoleCreateView, RoleUpdateView
)

app_name = 'permissions'

urlpatterns = [
    # Dashboard
    path('', permissions_dashboard, name='dashboard'),

    # Modules
    path('modules/', modules_list, name='modules_list'),

    # Roles
    path('roles/', roles_list, name='roles_list'),
    path('roles/create/', RoleCreateView.as_view(), name='role_create'),
    path('roles/<uuid:pk>/edit/', RoleUpdateView.as_view(), name='role_edit'),
    path('roles/<uuid:role_id>/', role_detail, name='role_detail'),

    # User Management
    path('assign-role/', assign_role_to_user, name='assign_role'),
    path('users/<int:user_id>/permissions/', user_permissions, name='user_permissions'),

    # Approval Workflows
    path('approvals/', approval_workflows_list, name='approval_workflows'),
    path('approvals/<uuid:workflow_id>/steps/<uuid:step_id>/approve/',
         approve_workflow_step, name='approve_workflow_step'),

    # API Endpoints
    path('api/data/', permissions_api_data, name='api_data'),

    # Cache Management
    path('cache/clear/', clear_permissions_cache, name='clear_cache'),
]
