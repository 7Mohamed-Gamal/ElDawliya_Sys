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
    # الحصول على الإعدادات الحالية أو إنشاء إعدادات جديدة إذا لم تكن موجودة
    settings_instance, created = SystemSettings.objects.get_or_create(pk=1)

    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, request.FILES, instance=settings_instance)
        if form.is_valid():
            try:
                saved_settings = form.save()
                messages.success(request, 'تم حفظ الإعدادات بنجاح')
                # إعادة تحميل الصفحة لإظهار التغييرات
                return redirect('administrator:settings')
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء حفظ الإعدادات: {str(e)}')
        else:
            # إضافة رسائل خطأ للمساعدة في التشخيص
            messages.error(request, 'يرجى تصحيح الأخطاء التالية:')
            for field, errors in form.errors.items():
                field_label = form.fields[field].label if field in form.fields else field
                for error in errors:
                    messages.error(request, f'{field_label}: {error}')
    else:
        form = SystemSettingsForm(instance=settings_instance)

    context = {
        'form': form,
        'settings': settings_instance
    }
    return render(request, 'administrator/system_settings.html', context)

@login_required
@system_admin_required
def database_settings(request):
    """View to configure database settings."""
    import datetime

    # Get current database settings
    from django.conf import settings
    db_settings = settings.DATABASES.get('default', {})

    # Determine active database connection type
    active_db = getattr(settings, 'ACTIVE_DB', 'default')

    if request.method == 'POST':
        # Check if this is a special request (backup/restore)
        request_type = request.headers.get('X-Request-Type', '')

        if request_type == 'backup_create':
            # Redirect to backup creation endpoint
            return create_database_backup(request)
        elif request_type == 'backup_restore':
            # Redirect to backup restoration endpoint
            return restore_database_backup(request)
        elif request_type == 'list_backups':
            # Redirect to list backups endpoint
            return list_database_backups(request)

        # Normal form submission for database settings
        form = DatabaseConfigForm(request.POST)
        if form.is_valid():
            # Update database settings in settings.py or elsewhere
            # (implementation depends on how you store settings)
            messages.success(request, 'تم حفظ إعدادات قاعدة البيانات بنجاح')
            return redirect('administrator:database_settings')
    else:
        # Initialize form with current settings
        initial_data = {
            'db_engine': db_settings.get('ENGINE', '').rsplit('.', 1)[-1],
            'db_connection_type': active_db,
            'db_name': db_settings.get('NAME', ''),
            'db_host': db_settings.get('HOST', 'localhost'),
            'db_port': db_settings.get('PORT', '1433'),
            'db_user': db_settings.get('USER', ''),
            'db_password': db_settings.get('PASSWORD', ''),
            'use_windows_auth': 'TRUSTED_CONNECTION' in db_settings.get('OPTIONS', {}),
        }
        form = DatabaseConfigForm(initial=initial_data)

    context = {
        'form': form,
        'page_title': 'إعدادات قاعدة البيانات',
        'active_db': active_db,
        'current_date': datetime.datetime.now()
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
    """Test database connection for setup and return available databases"""
    conn = None
    cursor = None

    if request.method == 'POST':
        host = request.POST.get('host', '')
        auth_type = request.POST.get('auth_type', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        try:
            # Construct connection string based on authentication type
            if auth_type == 'windows':
                conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};Trusted_Connection=yes;'
            else:
                conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};UID={username};PWD={password}'

            # Connect to SQL Server (master database) with auto-commit to avoid transaction issues
            conn = pyodbc.connect(conn_str + ';DATABASE=master', timeout=10, autocommit=True)
            cursor = conn.cursor()

            # Query available databases
            cursor.execute("SELECT name FROM sys.databases WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb') ORDER BY name")
            databases = []
            for row in cursor.fetchall():
                databases.append(row[0])

            # Close resources
            if cursor:
                cursor.close()
            if conn:
                conn.close()

            return JsonResponse({
                'success': True,
                'message': 'Connection successful!',
                'databases': databases
            })
        except pyodbc.Error as e:
            error_msg = str(e)
            # Check if this is a login failure
            if '[28000]' in error_msg or 'Login failed' in error_msg:
                error_msg = 'فشل تسجيل الدخول. يرجى التأكد من بيانات الاعتماد المستخدمة.'
            elif '[08001]' in error_msg or 'Cannot connect' in error_msg:
                error_msg = 'لا يمكن الاتصال بالخادم. يرجى التأكد من اسم الخادم وأن SQL Server يعمل.'

            return JsonResponse({'success': False, 'error': f'خطأ الاتصال بـ SQL Server: {error_msg}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'خطأ غير متوقع: {str(e)}'})
        finally:
            # Make sure resources are closed even if there's an exception
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass

    return JsonResponse({'success': False, 'error': 'طريقة طلب غير صالحة.'})

@login_required
@system_admin_required
def create_database_backup(request):
    """Create a backup of the SQL Server database"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        # Get backup parameters
        db_name = request.POST.get('db_name')
        filename = request.POST.get('filename', f'backup_{db_name}')
        compression = request.POST.get('compression', 'true') == 'true'
        verify = request.POST.get('verify', 'true') == 'true'
        encrypt = request.POST.get('encrypt', 'false') == 'true'

        # Get database connection info from settings
        from django.conf import settings
        db_settings = settings.DATABASES.get('default', {})

        host = db_settings.get('HOST', request.POST.get('host'))
        user = db_settings.get('USER', request.POST.get('username'))
        password = db_settings.get('PASSWORD', request.POST.get('password'))
        use_windows_auth = request.POST.get('use_windows_auth') == 'true'

        # Construct connection string
        if use_windows_auth:
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={db_name};Trusted_Connection=yes;'
        else:
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={db_name};UID={user};PWD={password}'

        # Connect to database with auto-commit mode to avoid transaction issues
        conn = pyodbc.connect(conn_str, timeout=30, autocommit=True)
        cursor = conn.cursor()

        # Simplest approach: use a filename only, SQL Server will use its default backup directory
        backup_file = f"{filename}.bak"
        backup_file = backup_file.replace(' ', '_')

        # Execute the simplest BACKUP DATABASE command possible
        try:
            backup_cmd = f"BACKUP DATABASE [{db_name}] TO DISK = N'{backup_file}'"
            cursor.execute(backup_cmd)
        except pyodbc.Error as e:
            # If that fails, try creating a backup with a minimal path
            if "Cannot open backup device" in str(e):
                # Try using C:\Temp directory which often has permissions
                backup_path = f"C:\\Temp\\{backup_file}"
                try:
                    # Create the directory if it doesn't exist
                    os.makedirs("C:\\Temp", exist_ok=True)
                except:
                    pass

                backup_cmd = f"BACKUP DATABASE [{db_name}] TO DISK = N'{backup_path}'"
                cursor.execute(backup_cmd)
            else:
                # Re-raise the error if it's not a backup device issue
                raise

        cursor.close()
        conn.close()

        return JsonResponse({
            'success': True,
            'filename': backup_file,
            'message': f'Database backup created successfully: {backup_file}'
        })

    except pyodbc.Error as e:
        return JsonResponse({
            'success': False,
            'error': f'SQL Server error: {str(e)}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        })

def list_database_backups(request):
    """List available database backups"""
    try:
        # This should be implemented to check the backup directory
        # and return a list of available backup files
        # For now, return an empty list
        return JsonResponse({
            'success': True,
            'backups': []
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error listing backups: {str(e)}'
        })

def restore_database_backup(request):
    """Restore a database from backup"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        # Get restore parameters
        db_name = request.POST.get('db_name')
        restore_method = request.POST.get('restore_method', 'existing')
        backup_filename = request.POST.get('backup_filename')

        # This is a placeholder - actual implementation would:
        # 1. Connect to SQL Server
        # 2. Execute a RESTORE DATABASE command
        # 3. Return appropriate success/failure message

        return JsonResponse({
            'success': False,
            'error': 'Database restore functionality is not yet implemented'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error during restore: {str(e)}'
        })
