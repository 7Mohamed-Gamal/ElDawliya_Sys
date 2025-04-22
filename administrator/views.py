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
    return user.is_superuser or getattr(user, 'Role', None) == 'admin'

# Decorator for system admin access
system_admin_required = user_passes_test(is_system_admin)

@login_required
@system_admin_required
def admin_dashboard(request):
    """
    Dashboard view for system administrators.
    """
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
    """
    View to edit system settings.
    """
    # Try to get existing settings or create new
    try:
        settings = SystemSettings.objects.first()
    except ObjectDoesNotExist:
        settings = None

    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            settings = form.save()

            # Apply language settings
            from django.utils import translation
            translation.activate(form.cleaned_data['language'])
            request.session[translation.LANGUAGE_SESSION_KEY] = form.cleaned_data['language']

            messages.success(request, 'تم حفظ الإعدادات بنجاح')
            return redirect('administrator:settings')
    else:
        form = SystemSettingsForm(instance=settings)

    context = {
        'form': form,
        'settings': settings
    }
    return render(request, 'administrator/system_settings.html', context)

@login_required
@system_admin_required
def database_settings(request):
    """
    View to configure database settings directly in settings.py file.
    """
    # Get current settings from settings.py
    from django.conf import settings

    # Check if we're using SQLite or SQL Server
    using_sqlite = 'sqlite' in settings.DATABASES['default']['ENGINE']

    # Get current database configuration
    if using_sqlite:
        # Using SQLite (development mode)
        db_config = {
            'db_engine': 'sqlite3',
            'db_name': str(settings.DATABASES['default']['NAME']),
            'db_host': '',
            'db_user': '',
            'db_password': '',
            'db_port': '',
        }

        # Also get SQL Server settings if available
        if 'mssql' in settings.DATABASES:
            mssql_config = settings.DATABASES['mssql']
            db_config.update({
                'db_host': mssql_config.get('HOST', ''),
                'db_name': mssql_config.get('NAME', ''),
                'db_user': mssql_config.get('USER', ''),
                'db_password': mssql_config.get('PASSWORD', ''),
                'db_port': mssql_config.get('PORT', '1433'),
            })
    else:
        # Using SQL Server
        db_config = {
            'db_engine': 'mssql',
            'db_host': settings.DATABASES['default'].get('HOST', ''),
            'db_name': settings.DATABASES['default'].get('NAME', ''),
            'db_user': settings.DATABASES['default'].get('USER', ''),
            'db_password': settings.DATABASES['default'].get('PASSWORD', ''),
            'db_port': settings.DATABASES['default'].get('PORT', '1433'),
        }

    # Try to get settings from SystemSettings model if available
    try:
        system_settings = SystemSettings.objects.first()
        if system_settings:
            # Update config with values from database if they exist
            if system_settings.db_host:
                db_config['db_host'] = system_settings.db_host
            if system_settings.db_name:
                db_config['db_name'] = system_settings.db_name
            if system_settings.db_user:
                db_config['db_user'] = system_settings.db_user
            if system_settings.db_password:
                db_config['db_password'] = system_settings.db_password
            if system_settings.db_port:
                db_config['db_port'] = system_settings.db_port
    except Exception:
        # If there's an error accessing the model (e.g., table doesn't exist yet),
        # just continue with the settings from settings.py
        pass

    if request.method == 'POST':
        form = DatabaseConfigForm(request.POST)
        if form.is_valid():
            # Update settings.py file
            try:
                # Read settings file
                settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ElDawliya_sys/settings.py')
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings_content = f.read()

                # Get the selected database engine
                db_engine = form.cleaned_data['db_engine']

                # Determine which database configuration to update
                if db_engine == 'sqlite3':
                    # Switch to SQLite
                    # Update the default configuration to use SQLite
                    sqlite_config = (
                        "'default': {\n"
                        "        'ENGINE': 'django.db.backends.sqlite3',\n"
                        f"        'NAME': BASE_DIR / '{form.cleaned_data['db_name']}',\n"
                        "    }"
                    )

                    # Update the default database configuration
                    settings_content = re.sub(
                        r"'default': \{[^\}]*\},",
                        f"{sqlite_config},\n    ",
                        settings_content
                    )

                    # Make sure we have the SQL Server configuration saved as 'mssql'
                    if 'mssql' not in settings.DATABASES:
                        # Add mssql configuration if it doesn't exist
                        mssql_config = (
                            "'mssql': {\n"
                            "        'ENGINE': 'mssql',\n"
                            f"        'NAME': '{form.cleaned_data.get('db_name_mssql', 'El_Dawliya_International')}',\n"
                            f"        'HOST': '{form.cleaned_data.get('db_host', '192.168.1.48')}',\n"
                            f"        'PORT': '{form.cleaned_data.get('db_port', '1433')}',\n"
                            f"        'USER': '{form.cleaned_data.get('db_user', '')}',\n"
                            f"        'PASSWORD': '{form.cleaned_data.get('db_password', '')}',\n"
                            "        'OPTIONS': {\n"
                            "            'driver': 'ODBC Driver 17 for SQL Server',\n"
                            "            'Trusted_Connection': 'yes',\n"
                            "        },\n"
                            "    }"
                        )

                        # Add mssql configuration after default
                        # First, find the default configuration
                        default_match = re.search(r"'default': \{[^\}]*\},", settings_content)
                        if default_match:
                            # Insert the mssql configuration after the default configuration
                            insert_pos = default_match.end()
                            settings_content = (
                                settings_content[:insert_pos] +
                                f"\n    {mssql_config}," +
                                settings_content[insert_pos:]
                            )
                    else:
                        # Update existing mssql configuration
                        mssql_config = (
                            "'mssql': {\n"
                            "        'ENGINE': 'mssql',\n"
                            f"        'NAME': '{form.cleaned_data.get('db_name_mssql', 'El_Dawliya_International')}',\n"
                            f"        'HOST': '{form.cleaned_data.get('db_host', '192.168.1.48')}',\n"
                            f"        'PORT': '{form.cleaned_data.get('db_port', '1433')}',\n"
                            f"        'USER': '{form.cleaned_data.get('db_user', '')}',\n"
                            f"        'PASSWORD': '{form.cleaned_data.get('db_password', '')}',\n"
                            "        'OPTIONS': {\n"
                            "            'driver': 'ODBC Driver 17 for SQL Server',\n"
                            "            'Trusted_Connection': 'yes',\n"
                            "        },\n"
                            "    }"
                        )
                        settings_content = re.sub(
                            r"'mssql': \{[^\}]*\},",
                            f"{mssql_config},\n    ",
                            settings_content
                        )
                else:
                    # Switch to SQL Server
                    # Update the default configuration to use SQL Server
                    trusted_connection = 'yes' if form.cleaned_data.get('use_windows_auth', True) else 'no'

                    default_config = (
                        "'default': {\n"
                        "        'ENGINE': 'mssql',\n"
                        f"        'NAME': '{form.cleaned_data['db_name']}',\n"
                        f"        'HOST': '{form.cleaned_data['db_host']}',\n"
                        f"        'PORT': '{form.cleaned_data['db_port']}',\n"
                    )

                    # Add authentication details based on the selected method
                    if not form.cleaned_data.get('use_windows_auth', True):
                        default_config += (
                            f"        'USER': '{form.cleaned_data['db_user']}',\n"
                            f"        'PASSWORD': '{form.cleaned_data['db_password']}',\n"
                        )

                    default_config += (
                        "        'OPTIONS': {\n"
                        "            'driver': 'ODBC Driver 17 for SQL Server',\n"
                        f"            'Trusted_Connection': '{trusted_connection}',\n"
                        "        },\n"
                        "    }"
                    )

                    # Update the default database configuration
                    settings_content = re.sub(
                        r"'default': \{[^\}]*\},",
                        f"{default_config},\n    ",
                        settings_content
                    )

                    # Make sure we have the SQLite configuration saved as 'sqlite'
                    if 'sqlite' not in settings.DATABASES:
                        # Add sqlite configuration if it doesn't exist
                        sqlite_config = (
                            "'sqlite': {\n"
                            "        'ENGINE': 'django.db.backends.sqlite3',\n"
                            f"        'NAME': BASE_DIR / '{form.cleaned_data.get('db_name_sqlite', 'db.sqlite3')}',\n"
                            "    }"
                        )

                        # Add sqlite configuration after default
                        # First, find the default configuration
                        default_match = re.search(r"'default': \{[^\}]*\},", settings_content)
                        if default_match:
                            # Insert the sqlite configuration after the default configuration
                            insert_pos = default_match.end()
                            settings_content = (
                                settings_content[:insert_pos] +
                                f"\n    {sqlite_config}," +
                                settings_content[insert_pos:]
                            )
                    else:
                        # Update existing sqlite configuration
                        sqlite_config = (
                            "'sqlite': {\n"
                            "        'ENGINE': 'django.db.backends.sqlite3',\n"
                            f"        'NAME': BASE_DIR / '{form.cleaned_data.get('db_name_sqlite', 'db.sqlite3')}',\n"
                            "    }"
                        )
                        settings_content = re.sub(
                            r"'sqlite': \{[^\}]*\},",
                            f"{sqlite_config},\n    ",
                            settings_content
                        )

                # Write back to settings file
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(settings_content)

                # Save settings to SystemSettings model too
                try:
                    settings_obj = SystemSettings.objects.first()
                    if not settings_obj:
                        settings_obj = SystemSettings()

                    settings_obj.db_host = form.cleaned_data['db_host']
                    settings_obj.db_name = form.cleaned_data['db_name']
                    settings_obj.db_user = form.cleaned_data['db_user']
                    settings_obj.db_password = form.cleaned_data['db_password']
                    settings_obj.db_port = form.cleaned_data['db_port']
                    settings_obj.save()
                except Exception as e:
                    # If we can't save to the model, just log it but don't fail
                    print(f"Error saving to SystemSettings model: {str(e)}")

                messages.success(request, 'تم تحديث إعدادات قاعدة البيانات بنجاح. قد تحتاج إلى إعادة تشغيل الخادم لتطبيق التغييرات.')
                return redirect('administrator:admin_dashboard')

            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء تحديث إعدادات قاعدة البيانات: {str(e)}')
    else:
        form = DatabaseConfigForm(initial=db_config)

    # Add context about current database engine
    context = {
        'form': form,
        'using_sqlite': using_sqlite,
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

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء القسم بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'administrator/department_form.html'
    success_url = reverse_lazy('administrator:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث القسم بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'administrator/department_confirm_delete.html'
    success_url = reverse_lazy('administrator:department_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف القسم بنجاح')
        return super().delete(request, *args, **kwargs)


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

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء الوحدة بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class ModuleUpdateView(UpdateView):
    model = Module
    form_class = ModuleForm
    template_name = 'administrator/module_form.html'
    success_url = reverse_lazy('administrator:module_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الوحدة بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class ModuleDeleteView(DeleteView):
    model = Module
    template_name = 'administrator/module_confirm_delete.html'
    success_url = reverse_lazy('administrator:module_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف الوحدة بنجاح')
        return super().delete(request, *args, **kwargs)




@csrf_exempt
def test_connection(request):
    if request.method == 'POST':
        try:
            host = request.POST.get('host')
            auth_type = request.POST.get('auth_type')
            username = request.POST.get('username')
            password = request.POST.get('password')

            # Print debug information
            print(f"Attempting to connect to: {host}")
            print(f"Authentication type: {auth_type}")
            print(f"Username: {username if auth_type == 'sql' else 'Using Windows Auth'}")

            # Try different ODBC drivers in order of preference
            drivers = [
                'ODBC Driver 17 for SQL Server',
                'ODBC Driver 13 for SQL Server',
                'SQL Server Native Client 11.0',
                'SQL Server',
            ]

            connection_error = None
            conn = None

            for driver in drivers:
                try:
                    # Build connection string based on authentication type
                    if auth_type == 'windows':
                        conn_str = f'DRIVER={{{driver}}};SERVER={host};Trusted_Connection=yes;'
                    else:
                        conn_str = f'DRIVER={{{driver}}};SERVER={host};UID={username};PWD={password}'

                    print(f"Trying connection with driver: {driver}")
                    # Test connection with a short timeout
                    conn = pyodbc.connect(conn_str, timeout=5)
                    print(f"Connection successful with driver: {driver}")
                    break
                except pyodbc.Error as e:
                    connection_error = str(e)
                    print(f"Failed with driver {driver}: {connection_error}")
                    continue

            if conn is None:
                return JsonResponse({
                    'success': False,
                    'error': f'Could not connect with any available driver. Last error: {connection_error}'
                })

            # Connection successful, get databases
            cursor = conn.cursor()

            try:
                # Get all databases (excluding system databases)
                cursor.execute("""
                    SELECT name
                    FROM sys.databases
                    WHERE database_id > 4
                    AND state_desc = 'ONLINE'
                    ORDER BY name
                """)

                databases = [row[0] for row in cursor.fetchall()]
                print(f"Found {len(databases)} databases: {', '.join(databases)}")
            except pyodbc.Error as e:
                print(f"Error querying databases: {str(e)}")
                # If we can't query databases, try a simpler query
                try:
                    cursor.execute("SELECT DB_NAME()")
                    current_db = cursor.fetchone()[0]
                    databases = [current_db]
                    print(f"Using current database: {current_db}")
                except Exception as e2:
                    print(f"Error with fallback query: {str(e2)}")
                    databases = []

            cursor.close()
            conn.close()

            return JsonResponse({
                'success': True,
                'databases': databases,
                'message': 'Connection successful!'
            })

        except pyodbc.Error as e:
            error_msg = str(e)
            print(f"ODBC Error: {error_msg}")

            # Provide more helpful error messages
            if "IM002" in error_msg:
                error_msg = "Driver not found. Please install SQL Server ODBC drivers."
            elif "28000" in error_msg and "Login failed" in error_msg:
                if auth_type == 'windows':
                    error_msg = "Windows authentication failed. Try SQL Server authentication instead."
                else:
                    error_msg = "Login failed. Please check your username and password."
            elif "08001" in error_msg:
                error_msg = "Server not found or connection refused. Check server name and firewall settings."

            return JsonResponse({
                'success': False,
                'error': f'Database Error: {error_msg}'
            })
        except Exception as e:
            print(f"General Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method. POST required.'
    })


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
def permission_help(request):
    """Help page for permissions system"""
    return render(request, 'administrator/permission_help.html', {'page_title': 'دليل نظام الصلاحيات'})


@login_required
@system_admin_required
def user_permission_list(request):
    """List all users with links to edit their permissions"""
    users = User.objects.all().order_by('username')

    context = {
        'users': users,
        'page_title': 'صلاحيات المستخدمين'
    }

    return render(request, 'administrator/user_permission_list.html', context)


@login_required
@system_admin_required
def edit_user_permissions(request, user_id):
    """Edit permissions for a specific user"""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserPermissionForm(request.POST, user=user)

        if form.is_valid():
            # Update user's groups
            user.groups.clear()
            for group in form.cleaned_data['groups']:
                user.groups.add(group)

            # Update individual permissions
            # First remove all individual permissions
            Permission.objects.filter(users=user).update(users=None)
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

@login_required
@system_admin_required
def admin_dashboard(request):
    """
    Dashboard view for system administrators.
    """
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
    """
    View to edit system settings.
    """
    # Try to get existing settings or create new
    try:
        settings = SystemSettings.objects.first()
    except ObjectDoesNotExist:
        settings = None

    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            settings = form.save()

            # Apply language settings
            from django.utils import translation
            translation.activate(form.cleaned_data['language'])
            request.session[translation.LANGUAGE_SESSION_KEY] = form.cleaned_data['language']

            messages.success(request, 'تم حفظ الإعدادات بنجاح')
            return redirect('administrator:settings')
    else:
        form = SystemSettingsForm(instance=settings)

    context = {
        'form': form,
        'settings': settings
    }
    return render(request, 'administrator/system_settings.html', context)

@login_required
@system_admin_required
def database_settings(request):
    """
    View to configure database settings directly in settings.py file.
    """
    # Get current settings from settings.py
    from django.conf import settings

    # Check if we're using SQLite or SQL Server
    using_sqlite = 'sqlite' in settings.DATABASES['default']['ENGINE']

    # Get current database configuration
    if using_sqlite:
        # Using SQLite (development mode)
        db_config = {
            'db_engine': 'sqlite3',
            'db_name': str(settings.DATABASES['default']['NAME']),
            'db_host': '',
            'db_user': '',
            'db_password': '',
            'db_port': '',
        }

        # Also get SQL Server settings if available
        if 'mssql' in settings.DATABASES:
            mssql_config = settings.DATABASES['mssql']
            db_config.update({
                'db_host': mssql_config.get('HOST', ''),
                'db_name': mssql_config.get('NAME', ''),
                'db_user': mssql_config.get('USER', ''),
                'db_password': mssql_config.get('PASSWORD', ''),
                'db_port': mssql_config.get('PORT', '1433'),
            })
    else:
        # Using SQL Server
        db_config = {
            'db_engine': 'mssql',
            'db_host': settings.DATABASES['default'].get('HOST', ''),
            'db_name': settings.DATABASES['default'].get('NAME', ''),
            'db_user': settings.DATABASES['default'].get('USER', ''),
            'db_password': settings.DATABASES['default'].get('PASSWORD', ''),
            'db_port': settings.DATABASES['default'].get('PORT', '1433'),
        }

    # Try to get settings from SystemSettings model if available
    try:
        system_settings = SystemSettings.objects.first()
        if system_settings:
            # Update config with values from database if they exist
            if system_settings.db_host:
                db_config['db_host'] = system_settings.db_host
            if system_settings.db_name:
                db_config['db_name'] = system_settings.db_name
            if system_settings.db_user:
                db_config['db_user'] = system_settings.db_user
            if system_settings.db_password:
                db_config['db_password'] = system_settings.db_password
            if system_settings.db_port:
                db_config['db_port'] = system_settings.db_port
    except Exception:
        # If there's an error accessing the model (e.g., table doesn't exist yet),
        # just continue with the settings from settings.py
        pass

    if request.method == 'POST':
        form = DatabaseConfigForm(request.POST)
        if form.is_valid():
            # Update settings.py file
            try:
                # Read settings file
                settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ElDawliya_sys/settings.py')
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings_content = f.read()

                # Get the selected database engine
                db_engine = form.cleaned_data['db_engine']

                # Determine which database configuration to update
                if db_engine == 'sqlite3':
                    # Switch to SQLite
                    # Update the default configuration to use SQLite
                    sqlite_config = (
                        "'default': {\n"
                        "        'ENGINE': 'django.db.backends.sqlite3',\n"
                        f"        'NAME': BASE_DIR / '{form.cleaned_data['db_name']}',\n"
                        "    }"
                    )

                    # Update the default database configuration
                    settings_content = re.sub(
                        r"'default': \{[^\}]*\},",
                        f"{sqlite_config},\n    ",
                        settings_content
                    )

                    # Make sure we have the SQL Server configuration saved as 'mssql'
                    if 'mssql' not in settings.DATABASES:
                        # Add mssql configuration if it doesn't exist
                        mssql_config = (
                            "'mssql': {\n"
                            "        'ENGINE': 'mssql',\n"
                            f"        'NAME': '{form.cleaned_data.get('db_name_mssql', 'El_Dawliya_International')}',\n"
                            f"        'HOST': '{form.cleaned_data.get('db_host', '192.168.1.48')}',\n"
                            f"        'PORT': '{form.cleaned_data.get('db_port', '1433')}',\n"
                            f"        'USER': '{form.cleaned_data.get('db_user', '')}',\n"
                            f"        'PASSWORD': '{form.cleaned_data.get('db_password', '')}',\n"
                            "        'OPTIONS': {\n"
                            "            'driver': 'ODBC Driver 17 for SQL Server',\n"
                            "            'Trusted_Connection': 'yes',\n"
                            "        },\n"
                            "    }"
                        )

                        # Add mssql configuration after default
                        # First, find the default configuration
                        default_match = re.search(r"'default': \{[^\}]*\},", settings_content)
                        if default_match:
                            # Insert the mssql configuration after the default configuration
                            insert_pos = default_match.end()
                            settings_content = (
                                settings_content[:insert_pos] +
                                f"\n    {mssql_config}," +
                                settings_content[insert_pos:]
                            )
                    else:
                        # Update existing mssql configuration
                        mssql_config = (
                            "'mssql': {\n"
                            "        'ENGINE': 'mssql',\n"
                            f"        'NAME': '{form.cleaned_data.get('db_name_mssql', 'El_Dawliya_International')}',\n"
                            f"        'HOST': '{form.cleaned_data.get('db_host', '192.168.1.48')}',\n"
                            f"        'PORT': '{form.cleaned_data.get('db_port', '1433')}',\n"
                            f"        'USER': '{form.cleaned_data.get('db_user', '')}',\n"
                            f"        'PASSWORD': '{form.cleaned_data.get('db_password', '')}',\n"
                            "        'OPTIONS': {\n"
                            "            'driver': 'ODBC Driver 17 for SQL Server',\n"
                            "            'Trusted_Connection': 'yes',\n"
                            "        },\n"
                            "    }"
                        )
                        settings_content = re.sub(
                            r"'mssql': \{[^\}]*\},",
                            f"{mssql_config},\n    ",
                            settings_content
                        )
                else:
                    # Switch to SQL Server
                    # Update the default configuration to use SQL Server
                    trusted_connection = 'yes' if form.cleaned_data.get('use_windows_auth', True) else 'no'

                    default_config = (
                        "'default': {\n"
                        "        'ENGINE': 'mssql',\n"
                        f"        'NAME': '{form.cleaned_data['db_name']}',\n"
                        f"        'HOST': '{form.cleaned_data['db_host']}',\n"
                        f"        'PORT': '{form.cleaned_data['db_port']}',\n"
                    )

                    # Add authentication details based on the selected method
                    if not form.cleaned_data.get('use_windows_auth', True):
                        default_config += (
                            f"        'USER': '{form.cleaned_data['db_user']}',\n"
                            f"        'PASSWORD': '{form.cleaned_data['db_password']}',\n"
                        )

                    default_config += (
                        "        'OPTIONS': {\n"
                        "            'driver': 'ODBC Driver 17 for SQL Server',\n"
                        f"            'Trusted_Connection': '{trusted_connection}',\n"
                        "        },\n"
                        "    }"
                    )

                    # Update the default database configuration
                    settings_content = re.sub(
                        r"'default': \{[^\}]*\},",
                        f"{default_config},\n    ",
                        settings_content
                    )

                    # Make sure we have the SQLite configuration saved as 'sqlite'
                    if 'sqlite' not in settings.DATABASES:
                        # Add sqlite configuration if it doesn't exist
                        sqlite_config = (
                            "'sqlite': {\n"
                            "        'ENGINE': 'django.db.backends.sqlite3',\n"
                            f"        'NAME': BASE_DIR / '{form.cleaned_data.get('db_name_sqlite', 'db.sqlite3')}',\n"
                            "    }"
                        )

                        # Add sqlite configuration after default
                        # First, find the default configuration
                        default_match = re.search(r"'default': \{[^\}]*\},", settings_content)
                        if default_match:
                            # Insert the sqlite configuration after the default configuration
                            insert_pos = default_match.end()
                            settings_content = (
                                settings_content[:insert_pos] +
                                f"\n    {sqlite_config}," +
                                settings_content[insert_pos:]
                            )
                    else:
                        # Update existing sqlite configuration
                        sqlite_config = (
                            "'sqlite': {\n"
                            "        'ENGINE': 'django.db.backends.sqlite3',\n"
                            f"        'NAME': BASE_DIR / '{form.cleaned_data.get('db_name_sqlite', 'db.sqlite3')}',\n"
                            "    }"
                        )
                        settings_content = re.sub(
                            r"'sqlite': \{[^\}]*\},",
                            f"{sqlite_config},\n    ",
                            settings_content
                        )

                # Write back to settings file
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(settings_content)

                # Save settings to SystemSettings model too
                try:
                    settings_obj = SystemSettings.objects.first()
                    if not settings_obj:
                        settings_obj = SystemSettings()

                    settings_obj.db_host = form.cleaned_data['db_host']
                    settings_obj.db_name = form.cleaned_data['db_name']
                    settings_obj.db_user = form.cleaned_data['db_user']
                    settings_obj.db_password = form.cleaned_data['db_password']
                    settings_obj.db_port = form.cleaned_data['db_port']
                    settings_obj.save()
                except Exception as e:
                    # If we can't save to the model, just log it but don't fail
                    print(f"Error saving to SystemSettings model: {str(e)}")

                messages.success(request, 'تم تحديث إعدادات قاعدة البيانات بنجاح. قد تحتاج إلى إعادة تشغيل الخادم لتطبيق التغييرات.')
                return redirect('administrator:admin_dashboard')

            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء تحديث إعدادات قاعدة البيانات: {str(e)}')
    else:
        form = DatabaseConfigForm(initial=db_config)

    # Add context about current database engine
    context = {
        'form': form,
        'using_sqlite': using_sqlite,
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

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء القسم بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'administrator/department_form.html'
    success_url = reverse_lazy('administrator:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث القسم بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'administrator/department_confirm_delete.html'
    success_url = reverse_lazy('administrator:department_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف القسم بنجاح')
        return super().delete(request, *args, **kwargs)


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

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء الوحدة بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class ModuleUpdateView(UpdateView):
    model = Module
    form_class = ModuleForm
    template_name = 'administrator/module_form.html'
    success_url = reverse_lazy('administrator:module_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الوحدة بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class ModuleDeleteView(DeleteView):
    model = Module
    template_name = 'administrator/module_confirm_delete.html'
    success_url = reverse_lazy('administrator:module_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف الوحدة بنجاح')
        return super().delete(request, *args, **kwargs)




@csrf_exempt
def test_connection(request):
    if request.method == 'POST':
        try:
            host = request.POST.get('host')
            auth_type = request.POST.get('auth_type')
            username = request.POST.get('username')
            password = request.POST.get('password')

            # Print debug information
            print(f"Attempting to connect to: {host}")
            print(f"Authentication type: {auth_type}")
            print(f"Username: {username if auth_type == 'sql' else 'Using Windows Auth'}")

            # Try different ODBC drivers in order of preference
            drivers = [
                'ODBC Driver 17 for SQL Server',
                'ODBC Driver 13 for SQL Server',
                'SQL Server Native Client 11.0',
                'SQL Server',
            ]

            connection_error = None
            conn = None

            for driver in drivers:
                try:
                    # Build connection string based on authentication type
                    if auth_type == 'windows':
                        conn_str = f'DRIVER={{{driver}}};SERVER={host};Trusted_Connection=yes;'
                    else:
                        conn_str = f'DRIVER={{{driver}}};SERVER={host};UID={username};PWD={password}'

                    print(f"Trying connection with driver: {driver}")
                    # Test connection with a short timeout
                    conn = pyodbc.connect(conn_str, timeout=5)
                    print(f"Connection successful with driver: {driver}")
                    break
                except pyodbc.Error as e:
                    connection_error = str(e)
                    print(f"Failed with driver {driver}: {connection_error}")
                    continue

            if conn is None:
                return JsonResponse({
                    'success': False,
                    'error': f'Could not connect with any available driver. Last error: {connection_error}'
                })

            # Connection successful, get databases
            cursor = conn.cursor()

            try:
                # Get all databases (excluding system databases)
                cursor.execute("""
                    SELECT name
                    FROM sys.databases
                    WHERE database_id > 4
                    AND state_desc = 'ONLINE'
                    ORDER BY name
                """)

                databases = [row[0] for row in cursor.fetchall()]
                print(f"Found {len(databases)} databases: {', '.join(databases)}")
            except pyodbc.Error as e:
                print(f"Error querying databases: {str(e)}")
                # If we can't query databases, try a simpler query
                try:
                    cursor.execute("SELECT DB_NAME()")
                    current_db = cursor.fetchone()[0]
                    databases = [current_db]
                    print(f"Using current database: {current_db}")
                except Exception as e2:
                    print(f"Error with fallback query: {str(e2)}")
                    databases = []

            cursor.close()
            conn.close()

            return JsonResponse({
                'success': True,
                'databases': databases,
                'message': 'Connection successful!'
            })

        except pyodbc.Error as e:
            error_msg = str(e)
            print(f"ODBC Error: {error_msg}")

            # Provide more helpful error messages
            if "IM002" in error_msg:
                error_msg = "Driver not found. Please install SQL Server ODBC drivers."
            elif "28000" in error_msg and "Login failed" in error_msg:
                if auth_type == 'windows':
                    error_msg = "Windows authentication failed. Try SQL Server authentication instead."
                else:
                    error_msg = "Login failed. Please check your username and password."
            elif "08001" in error_msg:
                error_msg = "Server not found or connection refused. Check server name and firewall settings."

            return JsonResponse({
                'success': False,
                'error': f'Database Error: {error_msg}'
            })
        except Exception as e:
            print(f"General Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method. POST required.'
    })
