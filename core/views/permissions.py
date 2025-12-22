"""
Views for hierarchical permissions management
عروض إدارة الصلاحيات الهرمية
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count

from ..models.permissions import (
    Module, Permission, Role, UserRole, ObjectPermission,
    ApprovalWorkflow, ApprovalStep
)
from ..services.permission_service import HierarchicalPermissionService, require_permission

User = get_user_model()


@login_required
@require_permission('administration.view')
def permissions_dashboard(request):
    """
    Main dashboard for permissions management
    لوحة التحكم الرئيسية لإدارة الصلاحيات
    """
    permission_service = HierarchicalPermissionService(request.user)

    # Get statistics
    stats = {
        'total_users': User.objects.filter(is_active=True).count(),
        'total_roles': Role.objects.filter(is_active=True).count(),
        'total_permissions': Permission.objects.filter(is_active=True).count(),
        'total_modules': Module.objects.filter(is_active=True).count(),
        'pending_approvals': ApprovalWorkflow.objects.filter(status='pending').count(),
    }

    # Get recent activities
    recent_role_assignments = UserRole.objects.select_related(
        'user', 'role', 'granted_by'
    ).order_by('-granted_at')[:10]

    recent_approvals = ApprovalWorkflow.objects.select_related(
        'requested_by', 'target_user'
    ).order_by('-created_at')[:10]

    # Get user's permissions summary
    user_permissions = permission_service.get_user_permissions()

    context = {
        'stats': stats,
        'recent_role_assignments': recent_role_assignments,
        'recent_approvals': recent_approvals,
        'user_permissions': user_permissions,
        'can_manage_users': permission_service.has_permission('administration.manage_users'),
        'can_manage_roles': permission_service.has_permission('administration.manage_roles'),
        'can_manage_permissions': permission_service.has_permission('administration.manage_permissions'),
    }

    return render(request, 'core/permissions/dashboard.html', context)


@login_required
@require_permission('administration.view')
def modules_list(request):
    """
    List all system modules
    قائمة جميع وحدات النظام
    """
    modules = Module.objects.filter(is_active=True).prefetch_related('permissions')

    # Add permission counts
    for module in modules:
        module.permissions_count = module.permissions.filter(is_active=True).count()

    context = {
        'modules': modules,
        'can_manage': request.user.has_perm('administration.manage_permissions')
    }

    return render(request, 'core/permissions/modules_list.html', context)


@login_required
@require_permission('administration.view')
def roles_list(request):
    """
    List all roles with filtering and search
    قائمة جميع الأدوار مع الفلترة والبحث
    """
    roles_queryset = Role.objects.filter(is_active=True).annotate(
        users_count=Count('user_roles', filter=Q(user_roles__is_active=True))
    ).prefetch_related('permissions')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        roles_queryset = roles_queryset.filter(
            Q(name__icontains=search_query) |
            Q(display_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filter by role type
    role_type = request.GET.get('role_type', '')
    if role_type:
        roles_queryset = roles_queryset.filter(role_type=role_type)

    # Pagination
    paginator = Paginator(roles_queryset, 20)
    page_number = request.GET.get('page')
    roles = paginator.get_page(page_number)

    context = {
        'roles': roles,
        'search_query': search_query,
        'role_type': role_type,
        'role_types': Role.ROLE_TYPES,
        'can_manage': request.user.has_perm('administration.manage_roles')
    }

    return render(request, 'core/permissions/roles_list.html', context)


@login_required
@require_permission('administration.view')
def role_detail(request, role_id):
    """
    Detailed view of a specific role
    عرض تفصيلي لدور معين
    """
    role = get_object_or_404(Role, id=role_id, is_active=True)

    # Get users assigned to this role
    user_roles = UserRole.objects.filter(
        role=role, is_active=True
    ).select_related('user', 'granted_by').order_by('-granted_at')

    # Get role permissions grouped by module
    permissions_by_module = {}
    for permission in role.permissions.filter(is_active=True).select_related('module'):
        module_name = permission.module.display_name
        if module_name not in permissions_by_module:
            permissions_by_module[module_name] = []
        permissions_by_module[module_name].append(permission)

    context = {
        'role': role,
        'user_roles': user_roles,
        'permissions_by_module': permissions_by_module,
        'can_manage': request.user.has_perm('administration.manage_roles'),
        'can_assign_users': request.user.has_perm('administration.manage_users')
    }

    return render(request, 'core/permissions/role_detail.html', context)


@login_required
@require_permission('administration.manage_users')
def assign_role_to_user(request):
    """
    Assign role to user with approval workflow if needed
    تعيين دور للمستخدم مع سير عمل الموافقة إذا لزم الأمر
    """
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role_id = request.POST.get('role_id')
        expires_at = request.POST.get('expires_at')
        notes = request.POST.get('notes', '')

        try:
            user = get_object_or_404(User, id=user_id, is_active=True)
            role = get_object_or_404(Role, id=role_id, is_active=True)

            # Parse expiration date
            expires_datetime = None
            if expires_at:
                expires_datetime = timezone.datetime.fromisoformat(expires_at)

            # Use permission service to assign role
            permission_service = HierarchicalPermissionService(request.user)

            if not permission_service.can_manage_user(user):
                return HttpResponseForbidden('ليس لديك صلاحية لإدارة هذا المستخدم')

            result = permission_service.assign_role(user, role, expires_datetime, notes)

            if isinstance(result, UserRole):
                messages.success(request, f'تم تعيين دور "{role.display_name}" للمستخدم "{user.username}" بنجاح')
            else:
                # Approval workflow created
                messages.info(request, f'تم إنشاء طلب موافقة لتعيين دور "{role.display_name}" للمستخدم "{user.username}"')

            return redirect('core:role_detail', role_id=role.id)

        except Exception as e:
            messages.error(request, f'خطأ في تعيين الدور: {str(e)}')
            return redirect('core:roles_list')

    # GET request - show assignment form
    users = User.objects.filter(is_active=True).order_by('username')
    roles = Role.objects.filter(is_active=True).order_by('display_name')

    context = {
        'users': users,
        'roles': roles
    }

    return render(request, 'core/permissions/assign_role.html', context)


@login_required
@require_permission('administration.view')
def user_permissions(request, user_id):
    """
    View user's permissions and roles
    عرض صلاحيات وأدوار المستخدم
    """
    user = get_object_or_404(User, id=user_id, is_active=True)

    permission_service = HierarchicalPermissionService(user)

    # Get user's roles
    user_roles = permission_service.get_user_roles()

    # Get user's permissions summary
    user_permissions = permission_service.get_user_permissions()

    # Get object-level permissions
    object_permissions = permission_service.get_user_object_permissions()

    context = {
        'target_user': user,
        'user_roles': user_roles,
        'user_permissions': user_permissions,
        'object_permissions': object_permissions,
        'can_manage': request.user.has_perm('administration.manage_users')
    }

    return render(request, 'core/permissions/user_permissions.html', context)


@login_required
@require_permission('administration.view')
def approval_workflows_list(request):
    """
    List approval workflows
    قائمة سير عمل الموافقات
    """
    workflows_queryset = ApprovalWorkflow.objects.select_related(
        'requested_by', 'target_user'
    ).prefetch_related('approval_steps')

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        workflows_queryset = workflows_queryset.filter(status=status)

    # Filter by workflow type
    workflow_type = request.GET.get('workflow_type', '')
    if workflow_type:
        workflows_queryset = workflows_queryset.filter(workflow_type=workflow_type)

    # Pagination
    paginator = Paginator(workflows_queryset.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    workflows = paginator.get_page(page_number)

    context = {
        'workflows': workflows,
        'status': status,
        'workflow_type': workflow_type,
        'status_choices': ApprovalWorkflow.STATUS_CHOICES,
        'workflow_type_choices': ApprovalWorkflow.WORKFLOW_TYPES,
        'can_approve': request.user.has_perm('administration.approve')
    }

    return render(request, 'core/permissions/approval_workflows.html', context)


@login_required
@require_http_methods(["POST"])
def approve_workflow_step(request, workflow_id, step_id):
    """
    Approve a workflow step
    الموافقة على خطوة في سير العمل
    """
    workflow = get_object_or_404(ApprovalWorkflow, id=workflow_id)
    step = get_object_or_404(ApprovalStep, id=step_id, workflow=workflow)

    permission_service = HierarchicalPermissionService(request.user)

    # Check if user can approve this step
    if not step.can_approve(request.user):
        return JsonResponse({
            'success': False,
            'message': 'ليس لديك صلاحية للموافقة على هذه الخطوة'
        })

    action = request.POST.get('action')  # 'approve' or 'reject'
    comments = request.POST.get('comments', '')

    try:
        with transaction.atomic():
            if action == 'approve':
                step.status = 'approved'
                step.approved_by = request.user
                step.approved_at = timezone.now()
                step.comments = comments
                step.save()

                # Check if all steps are approved
                pending_steps = workflow.approval_steps.filter(status='pending')
                if not pending_steps.exists():
                    workflow.status = 'approved'
                    workflow.save()

                    # Execute the approved action
                    _execute_approved_workflow(workflow)

                message = 'تم الموافقة على الخطوة بنجاح'

            elif action == 'reject':
                step.status = 'rejected'
                step.approved_by = request.user
                step.approved_at = timezone.now()
                step.comments = comments
                step.save()

                workflow.status = 'rejected'
                workflow.save()

                message = 'تم رفض الطلب'

            return JsonResponse({
                'success': True,
                'message': message
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في معالجة الطلب: {str(e)}'
        })


def _execute_approved_workflow(workflow):
    """
    Execute approved workflow action
    تنفيذ إجراء سير العمل المعتمد
    """
    if workflow.workflow_type == 'role_assignment':
        data = workflow.data

        try:
            target_user = User.objects.get(id=data['target_user_id'])
            role = Role.objects.get(id=data['role_id'])

            expires_at = None
            if data.get('expires_at'):
                expires_at = timezone.datetime.fromisoformat(data['expires_at'])

            # Create user role assignment
            UserRole.objects.create(
                user=target_user,
                role=role,
                granted_by=workflow.requested_by,
                expires_at=expires_at,
                notes=data.get('notes', ''),
                is_active=True
            )

        except (User.DoesNotExist, Role.DoesNotExist) as e:
            # Log error
            pass


@login_required
@require_http_methods(["GET"])
def permissions_api_data(request):
    """
    API endpoint for permissions data (for AJAX requests)
    نقطة API لبيانات الصلاحيات (لطلبات AJAX)
    """
    data_type = request.GET.get('type')

    if data_type == 'user_permissions':
        user_id = request.GET.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id, is_active=True)
                permission_service = HierarchicalPermissionService(user)
                permissions = permission_service.get_user_permissions()

                return JsonResponse({
                    'success': True,
                    'permissions': permissions
                })
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'المستخدم غير موجود'
                })

    elif data_type == 'role_permissions':
        role_id = request.GET.get('role_id')
        if role_id:
            try:
                role = Role.objects.get(id=role_id, is_active=True)
                permissions = list(role.permissions.filter(is_active=True).values(
                    'id', 'name', 'codename', 'module__name', 'module__display_name'
                ))

                return JsonResponse({
                    'success': True,
                    'permissions': permissions
                })
            except Role.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'الدور غير موجود'
                })

    return JsonResponse({
        'success': False,
        'message': 'نوع البيانات غير صحيح'
    })


@login_required
@require_permission('administration.manage_permissions')
def clear_permissions_cache(request):
    """
    Clear permissions cache for all users or specific user
    مسح ذاكرة تخزين الصلاحيات لجميع المستخدمين أو مستخدم معين
    """
    if request.method == 'POST':
        user_id = request.POST.get('user_id')

        try:
            if user_id:
                user = User.objects.get(id=user_id)
                permission_service = HierarchicalPermissionService(user)
                permission_service._invalidate_user_cache(user)
                messages.success(request, f'تم مسح ذاكرة التخزين المؤقت للمستخدم {user.username}')
            else:
                # Clear cache for all users
                from django.core.cache import cache
                from ..models.permissions import PermissionCache

                cache.clear()
                PermissionCache.objects.all().delete()
                messages.success(request, 'تم مسح ذاكرة التخزين المؤقت لجميع المستخدمين')

        except User.DoesNotExist:
            messages.error(request, 'المستخدم غير موجود')
        except Exception as e:
            messages.error(request, f'خطأ في مسح ذاكرة التخزين المؤقت: {str(e)}')

    return redirect('core:permissions_dashboard')


# Class-based views for CRUD operations

class RoleCreateView(CreateView):
    """Create new role"""
    model = Role
    fields = ['name', 'display_name', 'description', 'role_type', 'parent_role', 'max_users', 'permissions']
    template_name = 'core/permissions/role_form.html'
    success_url = reverse_lazy('core:roles_list')

    def dispatch(self, request, *args, **kwargs):
        """dispatch function"""
        if not request.user.has_perm('administration.manage_roles'):
            return HttpResponseForbidden('ليس لديك صلاحية لإنشاء الأدوار')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """form_valid function"""
        messages.success(self.request, f'تم إنشاء الدور "{form.instance.display_name}" بنجاح')
        return super().form_valid(form)


class RoleUpdateView(UpdateView):
    """Update existing role"""
    model = Role
    fields = ['display_name', 'description', 'role_type', 'parent_role', 'max_users', 'permissions', 'is_active']
    template_name = 'core/permissions/role_form.html'
    success_url = reverse_lazy('core:roles_list')

    def dispatch(self, request, *args, **kwargs):
        """dispatch function"""
        if not request.user.has_perm('administration.manage_roles'):
            return HttpResponseForbidden('ليس لديك صلاحية لتعديل الأدوار')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """form_valid function"""
        messages.success(self.request, f'تم تحديث الدور "{form.instance.display_name}" بنجاح')
        return super().form_valid(form)
