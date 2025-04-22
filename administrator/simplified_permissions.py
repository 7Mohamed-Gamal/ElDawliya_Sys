from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse

from .models import Department, Module, UserDepartmentPermission, UserModulePermission
from .views import system_admin_required

User = get_user_model()

@login_required
@system_admin_required
def simplified_permissions_dashboard(request):
    """Dashboard for simplified permissions management"""
    groups = Group.objects.all()
    departments = Department.objects.all()
    users = User.objects.filter(is_active=True)

    context = {
        'groups': groups,
        'departments': departments,
        'users': users,
        'title': 'إدارة الصلاحيات المبسطة'
    }

    return render(request, 'administrator/simplified_permissions_dashboard.html', context)

@login_required
@system_admin_required
def manage_group_departments(request, group_id):
    """Manage which departments a group has access to"""
    group = get_object_or_404(Group, id=group_id)
    departments = Department.objects.all()

    if request.method == 'POST':
        # Get selected department IDs from form
        selected_departments = request.POST.getlist('departments')

        # Clear existing department associations
        group.allowed_departments.clear()

        # Add new department associations
        for dept_id in selected_departments:
            try:
                department = Department.objects.get(id=dept_id)
                department.groups.add(group)
            except Department.DoesNotExist:
                pass

        messages.success(request, f'تم تحديث صلاحيات المجموعة {group.name} بنجاح')
        return redirect('administrator:group_detail', pk=group.id)

    context = {
        'group': group,
        'departments': departments,
        'selected_departments': [dept.id for dept in group.allowed_departments.all()],
        'title': f'إدارة أقسام المجموعة: {group.name}'
    }

    return render(request, 'administrator/manage_group_departments.html', context)

@login_required
@system_admin_required
def manage_user_groups(request, user_id):
    """Manage which groups a user belongs to"""
    user = get_object_or_404(User, id=user_id)
    groups = Group.objects.all()

    if request.method == 'POST':
        # Get selected group IDs from form
        selected_groups = request.POST.getlist('groups')

        # Clear existing group memberships
        user.groups.clear()

        # Add new group memberships
        for group_id in selected_groups:
            try:
                group = Group.objects.get(id=group_id)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass

        messages.success(request, f'تم تحديث مجموعات المستخدم {user.username} بنجاح')
        return redirect('administrator:user_detail', pk=user.id)

    context = {
        'user_obj': user,
        'groups': groups,
        'selected_groups': [group.id for group in user.groups.all()],
        'title': f'إدارة مجموعات المستخدم: {user.username}'
    }

    return render(request, 'administrator/manage_user_groups.html', context)

@login_required
@system_admin_required
def simplified_permissions_help(request):
    """Help page for simplified permissions system"""
    context = {
        'title': 'دليل نظام الصلاحيات المبسط'
    }

    return render(request, 'administrator/simplified_permissions_help.html', context)

@login_required
@system_admin_required
def permissions_explainer(request):
    """Comprehensive explainer for the permissions system"""
    context = {
        'title': 'شرح نظام الصلاحيات'
    }

    return render(request, 'administrator/permissions_explainer.html', context)

@login_required
@system_admin_required
def manage_user_permissions(request, user_id):
    """Manage permissions for a specific user using the new permission models"""
    user = get_object_or_404(User, id=user_id)
    departments = Department.objects.filter(is_active=True).order_by('order')

    if request.method == 'POST':
        # Delete existing permissions
        UserDepartmentPermission.objects.filter(user=user).delete()
        UserModulePermission.objects.filter(user=user).delete()

        # Process department permissions
        for dept in departments:
            dept_permission = request.POST.get(f'dept_{dept.id}', False) == 'on'
            if dept_permission:
                UserDepartmentPermission.objects.create(
                    user=user,
                    department=dept,
                    can_view=True
                )

                # Process module permissions for this department
                modules = Module.objects.filter(department=dept, is_active=True).order_by('order')
                for module in modules:
                    module_view = request.POST.get(f'module_{module.id}_view', False) == 'on'
                    module_add = request.POST.get(f'module_{module.id}_add', False) == 'on'
                    module_edit = request.POST.get(f'module_{module.id}_edit', False) == 'on'
                    module_delete = request.POST.get(f'module_{module.id}_delete', False) == 'on'
                    module_print = request.POST.get(f'module_{module.id}_print', False) == 'on'

                    if module_view:
                        UserModulePermission.objects.create(
                            user=user,
                            module=module,
                            can_view=module_view,
                            can_add=module_add,
                            can_edit=module_edit,
                            can_delete=module_delete,
                            can_print=module_print
                        )

        messages.success(request, f'تم تحديث صلاحيات المستخدم {user.username} بنجاح')
        return redirect('administrator:user_detail', pk=user.id)

    # Get user's current permissions
    user_dept_permissions = {
        perm.department_id: perm.can_view
        for perm in UserDepartmentPermission.objects.filter(user=user)
    }

    user_module_permissions = {
        perm.module_id: {
            'can_view': perm.can_view,
            'can_add': perm.can_add,
            'can_edit': perm.can_edit,
            'can_delete': perm.can_delete,
            'can_print': perm.can_print
        }
        for perm in UserModulePermission.objects.filter(user=user)
    }

    context = {
        'user_obj': user,
        'departments': departments,
        'user_dept_permissions': user_dept_permissions,
        'user_module_permissions': user_module_permissions,
        'title': f'إدارة صلاحيات المستخدم: {user.username}'
    }

    return render(request, 'administrator/manage_user_permissions.html', context)
