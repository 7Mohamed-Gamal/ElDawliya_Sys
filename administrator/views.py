import django
import os
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.apps import apps
from django.urls import reverse
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from .models import (
    SystemSettings, Department, Module
)
from .forms import (
    SystemSettingsForm, DepartmentForm, ModuleForm, DatabaseConfigForm,
    GroupForm, 
    UserPermissionForm, GroupPermissionForm
)

import pyodbc

User = get_user_model()

def is_system_admin(user):
    """Check if user is a system administrator."""
    return user.is_superuser or getattr(user, 'Role', None) == 'admin'

# Decorator for system admin access
system_admin_required = user_passes_test(is_system_admin)

# Special exception to be raised when the database connection is being configured
class DatabaseSetupMode(Exception):
    """Exception raised to indicate the system is in database setup mode."""
    pass

def database_setup(request):
    """View for database setup accessible without authentication."""
    from django.conf import settings
    import datetime
    import os
    from urllib.parse import unquote
    
    # Simple context - minimum needed
    context = {
        'form': DatabaseConfigForm(),
        'page_title': 'إعداد قاعدة البيانات',
        'connection_error': '',
        'setup_mode': True,
        'current_date': datetime.datetime.now()
    }

    # Use simplified template
    return render(request, 'administrator/database_setup.html', context)

@login_required
@system_admin_required
def admin_dashboard(request):
    """Dashboard view for system administrators."""
    try:
        settings = SystemSettings.objects.first()
    except:
        settings = None

    departments_count = Department.objects.count()
    modules_count = Module.objects.count()

    context = {
        'settings': settings,
        'departments_count': departments_count,
        'modules_count': modules_count,
    }
    return render(request, 'administrator/dashboard.html', context)

@login_required
@system_admin_required
def system_settings(request):
    """View to edit system settings."""
    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ الإعدادات بنجاح')
            return redirect('administrator:settings')
    else:
        form = SystemSettingsForm(instance=SystemSettings.objects.first())

    context = {
        'form': form,
        'settings': SystemSettings.objects.first()
    }
    return render(request, 'administrator/system_settings.html', context)

@login_required
@system_admin_required
def database_settings(request):
    """View to configure database settings."""
    context = {
        'form': DatabaseConfigForm(),
        'page_title': 'إعدادات قاعدة البيانات'
    }
    return render(request, 'administrator/database_settings.html', context)

# Department Views
@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class DepartmentListView(ListView):
    model = Department
    template_name = 'administrator/department_list.html'
    context_object_name = 'departments'

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'administrator/department_form.html'
    success_url = reverse_lazy('administrator:department_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'administrator/department_form.html'
    success_url = reverse_lazy('administrator:department_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'administrator/department_confirm_delete.html'
    success_url = reverse_lazy('administrator:department_list')

# Module Views
@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class ModuleListView(ListView):
    model = Module
    template_name = 'administrator/module_list.html'
    context_object_name = 'modules'

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class ModuleCreateView(CreateView):
    model = Module
    form_class = ModuleForm
    template_name = 'administrator/module_form.html'
    success_url = reverse_lazy('administrator:module_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class ModuleUpdateView(UpdateView):
    model = Module
    form_class = ModuleForm
    template_name = 'administrator/module_form.html'
    success_url = reverse_lazy('administrator:module_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class ModuleDeleteView(DeleteView):
    model = Module
    template_name = 'administrator/module_confirm_delete.html'
    success_url = reverse_lazy('administrator:module_list')

# Group Views
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

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class GroupUpdateView(UpdateView):
    """Update an existing user group"""
    model = Group
    form_class = GroupForm
    template_name = 'administrator/group_form.html'
    success_url = reverse_lazy('administrator:group_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class GroupDeleteView(DeleteView):
    """Delete a user group"""
    model = Group
    template_name = 'administrator/group_confirm_delete.html'
    success_url = reverse_lazy('administrator:group_list')

@login_required
@system_admin_required
def group_detail(request, pk):
    """View to display group details"""
    group = get_object_or_404(Group, pk=pk)
    
    context = {
        'group': group,
        'page_title': f'تفاصيل المجموعة: {group.name}'
    }
    return render(request, 'administrator/group_detail.html', context)

# User Views
from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    """Custom user creation form"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserCreateView(CreateView):
    """Create a new user"""
    model = User
    form_class = UserCreateForm
    template_name = 'administrator/user_create.html'
    success_url = reverse_lazy('administrator:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        return context

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserDetailView(DetailView):
    """View user details"""
    model = User
    template_name = 'administrator/user_detail.html'
    context_object_name = 'user_obj'

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserUpdateView(UpdateView):
    """Update an existing user"""
    model = User
    fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
    template_name = 'administrator/user_edit.html'
    success_url = reverse_lazy('administrator:user_list')
    context_object_name = 'user_obj'

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserDeleteView(DeleteView):
    """Delete a user"""
    model = User
    template_name = 'administrator/user_confirm_delete.html'
    success_url = reverse_lazy('administrator:user_list')
    context_object_name = 'user_obj'

@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserListView(ListView):
    """List all users"""
    model = User
    template_name = 'administrator/user_list.html'
    context_object_name = 'users'

class UserGroupsUpdateView(UpdateView):
    """Update user's group memberships"""
    model = User
    template_name = 'administrator/user_groups_form.html'
    fields = []
    success_url = reverse_lazy('administrator:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        context['user_groups'] = self.object.groups.all()
        return context

    def form_valid(self, form):
        user = self.object
        user.groups.clear()
        
        # Get selected group IDs from POST data
        group_ids = self.request.POST.getlist('groups')
        
        # Add user to selected groups
        if group_ids:
            groups = Group.objects.filter(id__in=group_ids)
            user.groups.add(*groups)
        
        messages.success(self.request, f'تم تحديث مجموعات المستخدم {user.username} بنجاح')
        return super().form_valid(form)

@login_required
@system_admin_required
def user_permissions(request, pk):
    """Manage permissions for a user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserPermissionForm(request.POST)
        if form.is_valid():
            # Clear user's existing permissions
            user.user_permissions.clear()
            
            # Add selected permissions
            permissions = form.cleaned_data.get('permissions')
            if permissions:
                user.user_permissions.add(*permissions)
                
            messages.success(request, f'تم تحديث صلاحيات المستخدم {user.username} بنجاح')
            return redirect('administrator:user_list')
    else:
        # Pre-select user's current permissions
        initial_permissions = user.user_permissions.all()
        form = UserPermissionForm(initial={'permissions': initial_permissions})
    
    context = {
        'form': form,
        'user_obj': user,
    }
    return render(request, 'administrator/user_permissions.html', context)

@login_required
@system_admin_required
def group_permissions(request, pk):
    """Manage permissions for a group"""
    group = get_object_or_404(Group, pk=pk)
    
    if request.method == 'POST':
        form = GroupPermissionForm(request.POST)
        if form.is_valid():
            # Clear group's existing permissions
            group.permissions.clear()
            
            # Add selected permissions
            permissions = form.cleaned_data.get('permissions')
            if permissions:
                group.permissions.add(*permissions)
                
            messages.success(request, f'تم تحديث صلاحيات المجموعة {group.name} بنجاح')
            return redirect('administrator:group_list')
    else:
        # Pre-select group's current permissions
        initial_permissions = group.permissions.all()
        form = GroupPermissionForm(initial={'permissions': initial_permissions})
    
    context = {
        'form': form,
        'group': group,
    }
    return render(request, 'administrator/group_permissions.html', context)

@login_required
@system_admin_required
def permission_dashboard(request):
    """Django permissions dashboard"""
    app_permissions = {}
    content_types = ContentType.objects.all().order_by('app_label')
    
    for content_type in content_types:
        app_label = content_type.app_label
        if app_label not in app_permissions:
            app_permissions[app_label] = {}
        
        model_name = content_type.model
        if model_name not in app_permissions[app_label]:
            app_permissions[app_label][model_name] = []
        
        permissions = Permission.objects.filter(content_type=content_type)
        for permission in permissions:
            app_permissions[app_label][model_name].append(permission)
    
    context = {
        'app_permissions': app_permissions,
    }
    return render(request, 'administrator/permissions_dashboard.html', context)

@login_required
@system_admin_required
def permissions_help(request):
    """Help page for understanding permissions system"""
    context = {
        'page_title': 'دليل نظام الصلاحيات'
    }
    return render(request, 'administrator/permissions_help.html', context)

@csrf_exempt
def test_connection(request):
    """Test database connection for setup"""
    if request.method == 'POST':
        host = request.POST.get('host', '')
        auth_type = request.POST.get('auth_type', '')
        return JsonResponse({'success': True, 'message': 'Connection successful!'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
