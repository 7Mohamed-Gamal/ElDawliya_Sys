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
    SystemSettings, Department, Module, Permission,
    TemplatePermission, UserGroup
)
from .forms import (
    SystemSettingsForm, DepartmentForm, ModuleForm, DatabaseConfigForm,
    PermissionForm, TemplatePermissionForm, UserGroupForm, GroupForm,
    UserPermissionForm, GroupPermissionForm
)

import pyodbc

User = get_user_model()

def is_system_admin(user):
    """Check if user is a system administrator."""
    return user.is_superuser or hasattr(user, 'is_system_admin')

# Decorator for system admin access
system_admin_required = user_passes_test(is_system_admin)

# Module Views
@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class ModuleListView(ListView):
    model = Module
    template_name = 'administrator/module_list.html'
    context_object_name = 'modules'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        return context
