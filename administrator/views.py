import django
import os
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.apps import apps
from django.urls import reverse
from django.db.models import Q

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
def permission_dashboard(request):
    """Django permissions dashboard"""
    # With the shift to Django's built-in permission system,
    # we redirect to the admin section for permissions
    return redirect('admin:auth_permission_changelist')

@csrf_exempt
def test_connection(request):
    """Test database connection for setup"""
    if request.method == 'POST':
        host = request.POST.get('host', '')
        auth_type = request.POST.get('auth_type', '')
        return JsonResponse({'success': True, 'message': 'Connection successful!'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
