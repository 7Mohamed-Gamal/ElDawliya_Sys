import django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Q

from .models import (
    Department, Module, Permission,
    TemplatePermission, UserGroup
)
from .forms import (
    PermissionForm, TemplatePermissionForm, UserGroupForm, GroupForm,
    UserPermissionForm, GroupPermissionForm, UnifiedPermissionForm
)
from .views import system_admin_required
from accounts.forms import CustomUserCreationForm

User = get_user_model()


# Permission Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class PermissionListView(ListView):
    """List all permissions for modules"""
    model = Permission
    template_name = 'administrator/permission_list.html'
    context_object_name = 'permissions'

    def get_queryset(self):
        return Permission.objects.select_related('module').all()


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class PermissionCreateView(CreateView):
    """Create a new permission"""
    model = Permission
    form_class = PermissionForm
    template_name = 'administrator/permission_form.html'
    success_url = reverse_lazy('administrator:permission_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء الصلاحية بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class PermissionUpdateView(UpdateView):
    """Update an existing permission"""
    model = Permission
    form_class = PermissionForm
    template_name = 'administrator/permission_form.html'
    success_url = reverse_lazy('administrator:permission_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الصلاحية بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class PermissionDeleteView(DeleteView):
    """Delete a permission"""
    model = Permission
    template_name = 'administrator/permission_confirm_delete.html'
    success_url = reverse_lazy('administrator:permission_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف الصلاحية بنجاح')
        return super().delete(request, *args, **kwargs)


# Template Permission Views
@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class TemplatePermissionListView(ListView):
    """List all template permissions"""
    model = TemplatePermission
    template_name = 'administrator/template_permission_list.html'
    context_object_name = 'template_permissions'


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class TemplatePermissionCreateView(CreateView):
    """Create a new template permission"""
    model = TemplatePermission
    form_class = TemplatePermissionForm
    template_name = 'administrator/template_permission_form.html'
    success_url = reverse_lazy('administrator:template_permission_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء صلاحية القالب بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class TemplatePermissionUpdateView(UpdateView):
    """Update an existing template permission"""
    model = TemplatePermission
    form_class = TemplatePermissionForm
    template_name = 'administrator/template_permission_form.html'
    success_url = reverse_lazy('administrator:template_permission_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث صلاحية القالب بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class TemplatePermissionDeleteView(DeleteView):
    """Delete a template permission"""
    model = TemplatePermission
    template_name = 'administrator/template_permission_confirm_delete.html'
    success_url = reverse_lazy('administrator:template_permission_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف صلاحية القالب بنجاح')
        return super().delete(request, *args, **kwargs)


# Group Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class GroupListView(ListView):
    """List all user groups"""
    model = Group
    template_name = 'administrator/group_list.html'
    context_object_name = 'groups'


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class GroupCreateView(CreateView):
    """Create a new user group"""
    model = Group
    form_class = GroupForm
    template_name = 'administrator/group_form.html'
    success_url = reverse_lazy('administrator:group_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء المجموعة بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class GroupDetailView(DetailView):
    """View details of a user group"""
    model = Group
    template_name = 'administrator/group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        # Get users in this group
        context['users'] = User.objects.filter(groups=group)
        # Get permissions for this group
        context['permissions'] = Permission.objects.filter(groups=group)
        # Get template permissions for this group
        context['template_permissions'] = TemplatePermission.objects.filter(groups=group)
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class GroupUpdateView(UpdateView):
    """Update an existing user group"""
    model = Group
    form_class = GroupForm
    template_name = 'administrator/group_form.html'
    success_url = reverse_lazy('administrator:group_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث المجموعة بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class GroupDeleteView(DeleteView):
    """Delete a user group"""
    model = Group
    template_name = 'administrator/group_confirm_delete.html'
    success_url = reverse_lazy('administrator:group_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف المجموعة بنجاح')
        return super().delete(request, *args, **kwargs)


# User-Group Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserGroupListView(ListView):
    """List all user-group memberships"""
    model = UserGroup
    template_name = 'administrator/user_group_list.html'
    context_object_name = 'user_groups'

    def get_queryset(self):
        return UserGroup.objects.select_related('user', 'group').all()


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserGroupCreateView(CreateView):
    """Create a new user-group membership"""
    model = UserGroup
    form_class = UserGroupForm
    template_name = 'administrator/user_group_form.html'
    success_url = reverse_lazy('administrator:user_group_list')

    def get_initial(self):
        initial = super().get_initial()
        # If user_id is provided in URL parameters, pre-select that user
        user_id = self.kwargs.get('user_id') or self.request.GET.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                initial['user'] = user
            except User.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة المستخدم للمجموعة بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserGroupUpdateView(UpdateView):
    """Update an existing user-group membership"""
    model = UserGroup
    form_class = UserGroupForm
    template_name = 'administrator/user_group_form.html'
    success_url = reverse_lazy('administrator:user_group_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث عضوية المجموعة بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserGroupDeleteView(DeleteView):
    """Delete a user-group membership"""
    model = UserGroup
    template_name = 'administrator/user_group_confirm_delete.html'
    success_url = reverse_lazy('administrator:user_group_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم إزالة المستخدم من المجموعة بنجاح')
        return super().delete(request, *args, **kwargs)


# Permission Dashboard and Management
@login_required
@system_admin_required
def permission_dashboard(request):
    """Dashboard for permissions management"""
    users_count = User.objects.count()
    groups_count = Group.objects.count()
    permissions_count = Permission.objects.count()
    template_permissions_count = TemplatePermission.objects.count()

    context = {
        'users_count': users_count,
        'groups_count': groups_count,
        'permissions_count': permissions_count,
        'template_permissions_count': template_permissions_count,
        'page_title': 'إدارة الصلاحيات'
    }

    return render(request, 'administrator/permission_dashboard.html', context)


@login_required
@system_admin_required
def permissions_help(request):
    """Help page for permissions system"""
    return render(request, 'administrator/permission_help.html', {'page_title': 'دليل نظام الصلاحيات'})


@login_required
@system_admin_required
def user_create(request):
    """Create a new user with quick links to manage permissions and groups"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'تم إنشاء المستخدم {user.username} بنجاح!')

            # Check if we should redirect to add user to group
            if 'save_and_add_to_group' in request.POST:
                return redirect('administrator:user_group_add_with_user', user_id=user.id)
            # Check if we should redirect to edit permissions
            elif 'save_and_edit_permissions' in request.POST:
                return redirect('administrator:edit_user_permissions', user_id=user.id)
            # Default redirect to user list
            return redirect('administrator:user_permission_list')
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
        'page_title': 'إضافة مستخدم جديد',
        'groups': Group.objects.all(),
    }

    return render(request, 'administrator/user_create.html', context)


@login_required
@system_admin_required
def user_detail(request, pk):
    """View details of a user"""
    user = get_object_or_404(User, id=pk)

    # Get user's groups
    user_groups = user.groups.all()

    # Get user's permissions
    user_permissions = user.user_permissions.all()

    # Get user's department permissions
    from .models import UserDepartmentPermission, UserModulePermission
    user_dept_permissions = UserDepartmentPermission.objects.filter(user=user).select_related('department')

    # Get user's module permissions
    user_module_permissions = UserModulePermission.objects.filter(user=user).select_related('module')

    context = {
        'user_obj': user,
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'user_dept_permissions': user_dept_permissions,
        'user_module_permissions': user_module_permissions,
        'page_title': f'تفاصيل المستخدم: {user.username}'
    }

    return render(request, 'administrator/user_detail.html', context)


@login_required
@system_admin_required
def user_permission_list(request):
    """List all user permissions."""
    users = User.objects.filter(is_active=True)
    context = {
        'users': users,
        'title': 'صلاحيات المستخدمين'
    }
    return render(request, 'administrator/user_permission_list.html', context)


@login_required
@system_admin_required
def auto_create_permissions(request):
    """Automatically create permissions for all modules."""
    if request.method == 'POST':
        # Get all modules
        modules = Module.objects.filter(is_active=True)
        permission_types = dict(Permission.PERMISSION_TYPES).keys()

        # Create permissions for each module and permission type
        created_count = 0
        for module in modules:
            for perm_type in permission_types:
                # Check if permission already exists
                perm, created = Permission.objects.get_or_create(
                    module=module,
                    permission_type=perm_type,
                    defaults={'is_active': True}
                )
                if created:
                    created_count += 1

        messages.success(request, f'تم إنشاء {created_count} صلاحية جديدة بنجاح')
        return redirect('administrator:permission_list')

    # GET request - show confirmation page
    return render(request, 'administrator/auto_create_permissions.html', {
        'title': 'إنشاء صلاحيات تلقائياً'
    })


@login_required
@system_admin_required
def edit_user_permissions(request, user_id):
    """Edit permissions for a specific user."""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserPermissionForm(request.POST)
        if form.is_valid():
            # Update user's groups
            user.groups.set(form.cleaned_data['groups'])

            # Update user's permissions
            # First, clear existing permissions
            user.user_permissions.clear()

            # Add new permissions
            for perm_type in ['view', 'add', 'change', 'delete', 'print']:
                perms = form.cleaned_data[f'{perm_type}_permissions']
                for perm in perms:
                    user.user_permissions.add(perm)

            # Update template permissions
            for template in form.cleaned_data['templates']:
                template.users.add(user)

            messages.success(request, f'تم تحديث صلاحيات المستخدم {user.username} بنجاح')
            return redirect('administrator:user_permission_list')
    else:
        # Initialize form with current permissions
        initial_data = {
            'user': user,
            'groups': user.groups.all(),
            'view_permissions': Permission.objects.filter(permission_type='view', users=user),
            'add_permissions': Permission.objects.filter(permission_type='add', users=user),
            'change_permissions': Permission.objects.filter(permission_type='change', users=user),
            'delete_permissions': Permission.objects.filter(permission_type='delete', users=user),
            'print_permissions': Permission.objects.filter(permission_type='print', users=user),
            'templates': TemplatePermission.objects.filter(users=user),
        }
        form = UserPermissionForm(initial=initial_data)

    context = {
        'form': form,
        'user_obj': user,
        'title': f'تعديل صلاحيات {user.username}'
    }
    return render(request, 'administrator/edit_user_permissions.html', context)


@login_required
@system_admin_required
def group_permission_list(request):
    """List all groups for permission management."""
    groups = Group.objects.all()
    context = {
        'groups': groups,
        'title': 'صلاحيات المجموعات'
    }
    return render(request, 'administrator/group_permission_list.html', context)


@login_required
@system_admin_required
def edit_group_permissions(request, group_id):
    """Edit permissions for a specific group."""
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        form = GroupPermissionForm(request.POST)
        if form.is_valid():
            # Update departments and modules
            departments = form.cleaned_data['departments']
            modules = form.cleaned_data['modules']

            # Update permissions
            for perm_type in ['view', 'add', 'change', 'delete', 'print']:
                perms = form.cleaned_data[f'{perm_type}_permissions']
                for perm in perms:
                    perm.groups.add(group)

            # Update template permissions
            templates = form.cleaned_data['templates']
            for template in templates:
                template.groups.add(group)

            messages.success(request, f'تم تحديث صلاحيات المجموعة {group.name} بنجاح')
            return redirect('administrator:group_permission_list')
    else:
        # Initialize form with current permissions
        initial_data = {
            'group': group,
            'departments': Department.objects.filter(modules__permissions__groups=group).distinct(),
            'modules': Module.objects.filter(permissions__groups=group).distinct(),
            'view_permissions': Permission.objects.filter(permission_type='view', groups=group),
            'add_permissions': Permission.objects.filter(permission_type='add', groups=group),
            'change_permissions': Permission.objects.filter(permission_type='change', groups=group),
            'delete_permissions': Permission.objects.filter(permission_type='delete', groups=group),
            'print_permissions': Permission.objects.filter(permission_type='print', groups=group),
            'templates': TemplatePermission.objects.filter(groups=group),
        }
        form = GroupPermissionForm(initial=initial_data)

    context = {
        'form': form,
        'group': group,
        'title': f'تعديل صلاحيات {group.name}'
    }
    return render(request, 'administrator/edit_group_permissions.html', context)
