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
    View to edit system settings - direct database approach.
    """
    print("****** DIRECT DATABASE APPROACH FOR SETTINGS ******")
    
    # Default values for required fields
    default_values = {
        'db_host': 'localhost',
        'db_name': 'el_dawliya',
        'db_user': 'sa',
        'db_password': 'password',
        'db_port': '1433',
        'company_name': 'الشركة الدولية',
        'company_address': '',
        'company_phone': '',
        'company_email': '',
        'company_website': '',
        'system_name': 'نظام الدولية',
        'enable_debugging': False,
        'maintenance_mode': False,
        'timezone': 'Asia/Riyadh',
        'date_format': 'Y-m-d',
        'language': 'ar',
        'font_family': 'cairo',
        'text_direction': 'rtl',
    }
    
    # Step 1: Get or create the SystemSettings object
    try:
        # First try to get existing setting
        settings_obj = SystemSettings.objects.all().order_by('id').first()
        if not settings_obj:
            print("Creating new settings with default values")
            settings_obj = SystemSettings(**default_values)
            settings_obj.save()
            print(f"Created settings with ID: {settings_obj.id}")
    except Exception as e:
        print(f"Error with settings object: {str(e)}")
        messages.error(request, f"Error with settings: {str(e)}")
        settings_obj = None
    
    if request.method == 'POST':
        print("Handling POST request with direct DB update")
        
        # Create form for validation only, but don't use its save method
        form = SystemSettingsForm(request.POST, request.FILES, instance=settings_obj)
        
        if form.is_valid():
            print("Form validation passed, processing data manually")
            
            try:
                # Get or create settings object if needed
                if not settings_obj:
                    settings_obj = SystemSettings()
                    # Set defaults for db fields, which won't change
                    settings_obj.db_host = default_values['db_host']
                    settings_obj.db_name = default_values['db_name']
                    settings_obj.db_user = default_values['db_user']
                    settings_obj.db_password = default_values['db_password']
                    settings_obj.db_port = default_values['db_port']
                
                # MANUALLY update fields from POST data
                # Non-database fields that are in the form
                form_fields = [
                    'company_name', 'company_address', 'company_phone', 
                    'company_email', 'company_website',
                    'system_name', 'enable_debugging', 'maintenance_mode',
                    'timezone', 'date_format', 
                    'language', 'font_family', 'text_direction'
                ]
                
                # Update each field from form data
                for field in form_fields:
                    if field in form.cleaned_data:
                        print(f"Setting {field} = {form.cleaned_data[field]}")
                        setattr(settings_obj, field, form.cleaned_data[field])
                    else:
                        print(f"Field {field} not in form data")
                
                # Handle logo upload separately
                if 'company_logo' in request.FILES:
                    print(f"Handling logo: {request.FILES['company_logo']}")
                    settings_obj.company_logo = request.FILES['company_logo']
                    
                # Save to database
                settings_obj.save()
                print(f"Settings saved with ID: {settings_obj.id}")
                
                # Apply language settings
                from django.utils import translation
                translation.activate(form.cleaned_data['language'])
                request.session[translation.LANGUAGE_SESSION_KEY] = form.cleaned_data['language']
                
                # Success message
                messages.success(request, 'تم حفظ الإعدادات بنجاح')
                
                # Refresh the page to show updated settings
                return redirect('administrator:settings')
            
            except Exception as e:
                print(f"ERROR during manual save: {str(e)}")
                messages.error(request, f'حدث خطأ أثناء حفظ الإعدادات: {str(e)}')
        
        else:
            print(f"Form validation failed: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"خطأ في حقل {field}: {error}")
    
    else:
        # GET request - create form with current settings
        if settings_obj:
            form = SystemSettingsForm(instance=settings_obj)
        else:
            form = SystemSettingsForm(initial=default_values)
    
    # Prepare context
    context = {
        'form': form,
        'settings': settings_obj
    }
    
    return render(request, 'administrator/system_settings.html', context)

@login_required
@system_admin_required
def database_settings(request):
    """
    View to configure database settings directly in settings.py file.
    """
    from django.conf import settings
    import datetime
    import os

    # We're always using SQL Server now
    using_sqlite = False
    
    # Get active database connection type
    active_db = getattr(settings, 'ACTIVE_DB', 'default')

    # Check if this is a backup or restore request
    request_type = request.headers.get('X-Request-Type', '')
    
    # Handle backup creation request
    if request.method == 'POST' and request_type == 'backup_create':
        return handle_database_backup(request)
    
    # Handle backup restore request
    if request.method == 'POST' and request_type == 'backup_restore':
        return handle_database_restore(request)
    
    # Handle backup list request
    if request.method == 'GET' and request_type == 'list_backups':
        return list_database_backups(request)

    # Get current database configuration
    # Always using SQL Server now
    db_config = {
        'db_engine': 'mssql',
        'db_host': settings.DATABASES['default'].get('HOST', ''),
        'db_name': settings.DATABASES['default'].get('NAME', ''),
        'db_user': settings.DATABASES['default'].get('USER', ''),
        'db_password': settings.DATABASES['default'].get('PASSWORD', ''),
        'db_port': settings.DATABASES['default'].get('PORT', '1433'),
        'db_connection_type': active_db,
    }
    
    # Also get primary database settings if available
    if 'primary' in settings.DATABASES:
        primary_config = settings.DATABASES['primary']
        if active_db == 'primary':
            # If primary is active, update the form values with primary settings
            db_config.update({
                'db_host': primary_config.get('HOST', ''),
                'db_name': primary_config.get('NAME', ''),
                'db_user': primary_config.get('USER', ''),
                'db_password': primary_config.get('PASSWORD', ''),
                'db_port': primary_config.get('PORT', '1433'),
            })


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
                
                # Get the selected database connection type
                db_connection_type = form.cleaned_data['db_connection_type']
                
                # Update the ACTIVE_DB setting
                if 'ACTIVE_DB =' in settings_content:
                    settings_content = re.sub(
                        r"ACTIVE_DB = os\.environ\.get\('DJANGO_ACTIVE_DB', '[^']*'\)",
                        f"ACTIVE_DB = os.environ.get('DJANGO_ACTIVE_DB', '{db_connection_type}')",
                        settings_content
                    )
                else:
                    # If ACTIVE_DB setting doesn't exist, add it after the DATABASES definition
                    settings_content = re.sub(
                        r"(DATABASES = \{[^\}]*\})",
                        f"\\1\n\n# تحديد قاعدة البيانات النشطة من ملف الإعدادات\nACTIVE_DB = os.environ.get('DJANGO_ACTIVE_DB', '{db_connection_type}')",
                        settings_content
                    )

                # Always using SQL Server now
                # Get the selected connection type
                db_connection_type = form.cleaned_data['db_connection_type']
                
                # Update the ACTIVE_DB setting
                if 'ACTIVE_DB =' in settings_content:
                    settings_content = re.sub(
                        r"ACTIVE_DB = os\.environ\.get\('DJANGO_ACTIVE_DB', '[^']*'\)",
                        f"ACTIVE_DB = os.environ.get('DJANGO_ACTIVE_DB', '{db_connection_type}')",
                        settings_content
                    )
                else:
                    # If ACTIVE_DB setting doesn't exist, add it after the DATABASES definition
                    settings_content = re.sub(
                        r"(DATABASES = \{[^\}]*\})",
                        f"\1\n\n# تحديد قاعدة البيانات النشطة من ملف الإعدادات\nACTIVE_DB = os.environ.get('DJANGO_ACTIVE_DB', '{db_connection_type}')",
                        settings_content
                    )
                
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
                
                # Update the primary database configuration
                primary_config = (
                    "'primary': {\n"
                    "        'ENGINE': 'mssql',\n"
                    f"        'NAME': '{form.cleaned_data['db_name']}',\n"
                    f"        'HOST': '{form.cleaned_data['db_host']}',\n"
                    f"        'PORT': '{form.cleaned_data['db_port']}',\n"
                )

                # Add authentication details based on the selected method
                if not form.cleaned_data.get('use_windows_auth', True):
                    primary_config += (
                        f"        'USER': '{form.cleaned_data['db_user']}',\n"
                        f"        'PASSWORD': '{form.cleaned_data['db_password']}',\n"
                    )

                primary_config += (
                    "        'OPTIONS': {\n"
                    "            'driver': 'ODBC Driver 17 for SQL Server',\n"
                    f"            'Trusted_Connection': '{trusted_connection}',\n"
                    "        },\n"
                    "    }"
                )
                
                # Check if primary configuration exists
                if "'primary':" in settings_content:
                    # Update existing primary configuration - use careful regex to avoid syntax issues
                    settings_content = re.sub(
                        r"'primary': \{[^\}]*\}",  # Note: no comma at the end
                        f"{primary_config}",
                        settings_content
                    )
                else:
                    # Add primary configuration if it doesn't exist
                    # Find the position right after the default configuration block
                    default_pattern = r"'default': \{.*?\},\s*\n"
                    default_match = re.search(default_pattern, settings_content, re.DOTALL)
                    if default_match:
                        # Insert the primary configuration after the default configuration
                        insert_pos = default_match.end()
                        settings_content = (
                            settings_content[:insert_pos] +
                            f"\n    # الإعدادات الاحتياطية\n    {primary_config}\n" +
                            settings_content[insert_pos:]
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

    # Add current date for backup filename
    context['current_date'] = datetime.datetime.now()
    
    return render(request, 'administrator/database_settings.html', context)
    
def handle_database_backup(request):
    """
    Handle database backup creation request.
    Creates a backup of the specified database using SQL Server's BACKUP DATABASE command.
    """
    from django.conf import settings
    import os
    import pyodbc
    import datetime
    
    try:
        # Get database connection details
        db_engine = request.POST.get('db_engine', 'mssql')
        db_name = request.POST.get('db_name')
        
        # Get backup options
        filename = request.POST.get('filename', f'backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M")}')
        compression = request.POST.get('compression') == 'true'
        verify = request.POST.get('verify') == 'true'
        encrypt = request.POST.get('encrypt') == 'true'
        
        # Make sure we have a valid database name
        if not db_name:
            return JsonResponse({
                'success': False, 
                'error': 'يرجى تحديد قاعدة بيانات صالحة'
            })
            
        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        # Full path to backup file - Use a location SQL Server can access
        backup_filename = f"{filename}.bak"
        
        # First try using a system temp directory
        import tempfile
        temp_dir = tempfile.gettempdir()
        backup_path = os.path.join(temp_dir, backup_filename)
        
        # Make sure path is using correct format for SQL Server
        backup_path = backup_path.replace('/', '\\')
        
        # Connect to the database with autocommit mode
        connection_string = get_connection_string(settings.DATABASES['default'])
        conn = pyodbc.connect(connection_string, timeout=30, autocommit=True)
        cursor = conn.cursor()
        
        # Build the backup SQL command
        backup_sql = f"BACKUP DATABASE [{db_name}] TO DISK = N'{backup_path}'"
        
        # Add options
        options = []
        if compression:
            options.append("COMPRESSION")
            
        # Skip encryption option as it might require certificate setup
        # if encrypt:
        #     options.append("ENCRYPTION (ALGORITHM = AES_256, SERVER CERTIFICATE = BackupEncryptCert)")
        
        if options:
            backup_sql += " WITH " + ", ".join(options)
            
        print(f"Executing SQL: {backup_sql}")
        
        # Execute the backup command - no need for commit with autocommit=True
        cursor.execute(backup_sql)
        
        # Verify the backup if requested
        if verify:
            verify_sql = f"RESTORE VERIFYONLY FROM DISK = N'{backup_path}'"
            cursor.execute(verify_sql)
            
        cursor.close()
        conn.close()
        
        # Move the backup file from temp directory to our backups directory
        import shutil
        final_backup_path = os.path.join(backup_dir, backup_filename)
        shutil.copy2(backup_path, final_backup_path)
        
        # Return success response
        return JsonResponse({
            'success': True,
            'filename': backup_filename,
            'message': f'تم إنشاء النسخة الاحتياطية بنجاح'
        })
        
    except Exception as e:
        print(f"Backup error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'فشل إنشاء النسخة الاحتياطية: {str(e)}'
        })

def handle_database_restore(request):
    """
    Handle database restore request.
    Restores a database from a backup file using SQL Server's RESTORE DATABASE command.
    """
    from django.conf import settings
    import os
    import pyodbc
    import tempfile
    import shutil
    
    try:
        # Get database connection details
        db_engine = request.POST.get('db_engine', 'mssql')
        db_name = request.POST.get('db_name')
        
        # Get restore method and filename
        restore_method = request.POST.get('restore_method', 'existing')
        
        # Make sure we have a valid database name
        if not db_name:
            return JsonResponse({
                'success': False, 
                'error': 'يرجى تحديد قاعدة بيانات صالحة'
            })
            
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Get backup file path based on method
        if restore_method == 'upload':
            # Handle uploaded file
            if 'backup_file' not in request.FILES:
                return JsonResponse({
                    'success': False, 
                    'error': 'يرجى تحديد ملف النسخة الاحتياطية'
                })
                
            # Save the uploaded file to a temp location first
            backup_file = request.FILES['backup_file']
            temp_path = os.path.join(tempfile.gettempdir(), backup_file.name)
            
            with open(temp_path, 'wb+') as destination:
                for chunk in backup_file.chunks():
                    destination.write(chunk)
                    
            # Copy to our backups directory
            backup_path = os.path.join(backup_dir, backup_file.name)
            shutil.copy2(temp_path, backup_path)
        else:
            # Use existing backup file
            backup_filename = request.POST.get('backup_filename')
            if not backup_filename:
                return JsonResponse({
                    'success': False, 
                    'error': 'يرجى اختيار نسخة احتياطية موجودة'
                })
                
            backup_path = os.path.join(backup_dir, backup_filename)
            
        # Make sure path is using correct format for SQL Server
        backup_path = backup_path.replace('/', '\\')
            
        # Connect to the database with autocommit mode
        connection_string = get_connection_string(settings.DATABASES['default'])
        conn = pyodbc.connect(connection_string, timeout=30, autocommit=True)
        cursor = conn.cursor()
        
        print(f"Attempting to restore database [{db_name}] from [{backup_path}]")
        
        # First, set database to single user mode
        try:
            cursor.execute(f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        except Exception as e:
            print(f"Error setting database to single user mode: {str(e)}")
            # Continue anyway, might be already in single user mode
        
        try:
            # Restore the database
            restore_sql = f"RESTORE DATABASE [{db_name}] FROM DISK = N'{backup_path}' WITH REPLACE"
            print(f"Executing: {restore_sql}")
            cursor.execute(restore_sql)
            
            # Set database back to multi-user mode
            cursor.execute(f"ALTER DATABASE [{db_name}] SET MULTI_USER")
        except Exception as e:
            print(f"Error during restore: {str(e)}")
            # Ensure database is set back to multi-user mode even if restore fails
            try:
                cursor.execute(f"ALTER DATABASE [{db_name}] SET MULTI_USER")
            except:
                pass
            raise e
        finally:
            cursor.close()
            conn.close()
        
        # Return success response
        return JsonResponse({
            'success': True,
            'message': 'تم استعادة قاعدة البيانات بنجاح'
        })
        
    except Exception as e:
        print(f"Restore error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'فشل استعادة قاعدة البيانات: {str(e)}'
        })

def list_database_backups(request):
    """
    List available database backups.
    """
    from django.conf import settings
    import os
    import datetime
    
    try:
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        
        # Create the directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        backups = []
        
        # Get list of backup files
        for filename in os.listdir(backup_dir):
            if filename.endswith('.bak'):
                file_path = os.path.join(backup_dir, filename)
                file_stats = os.stat(file_path)
                
                # Get file size in human-readable format
                size_bytes = file_stats.st_size
                size = convert_size(size_bytes)
                
                # Get file creation date
                ctime = datetime.datetime.fromtimestamp(file_stats.st_ctime)
                date = ctime.strftime('%Y-%m-%d %H:%M')
                
                # Add backup to list
                backups.append({
                    'filename': filename,
                    'display_name': filename.replace('.bak', ''),
                    'size': size,
                    'size_bytes': size_bytes,
                    'date': date,
                    'timestamp': file_stats.st_ctime
                })
                
        # Sort backups by date (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'backups': backups
        })
        
    except Exception as e:
        print(f"List backups error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'فشل قراءة النسخ الاحتياطية: {str(e)}'
        })

def get_connection_string(db_config):
    """
    Build a connection string for SQL Server from database configuration.
    """
    driver = db_config.get('OPTIONS', {}).get('driver', 'ODBC Driver 17 for SQL Server')
    server = db_config.get('HOST', 'localhost')
    database = db_config.get('NAME', '')
    
    # Determine authentication method
    trusted_conn = db_config.get('OPTIONS', {}).get('Trusted_Connection', 'no')
    
    if trusted_conn.lower() == 'yes':
        # Windows authentication
        conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    else:
        # SQL Server authentication
        user = db_config.get('USER', '')
        password = db_config.get('PASSWORD', '')
        conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={user};PWD={password};"
        
    return conn_str

def convert_size(size_bytes):
    """
    Convert file size in bytes to human-readable format.
    """
    if size_bytes < 1024:
        return f"{size_bytes} بايت"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.2f} كيلوبايت"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.2f} ميجابايت"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f} جيجابايت"


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
    """Redirect to RBAC dashboard for permissions management"""
    # Redirecting to RBAC dashboard which is now the main permissions system
    return redirect('administrator:rbac_dashboard')


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

    # We're always using SQL Server now
    using_sqlite = False
    
    # Get active database connection type
    active_db = getattr(settings, 'ACTIVE_DB', 'default')

    # Get current database configuration
    # Always using SQL Server now
    db_config = {
        'db_engine': 'mssql',
        'db_host': settings.DATABASES['default'].get('HOST', ''),
        'db_name': settings.DATABASES['default'].get('NAME', ''),
        'db_user': settings.DATABASES['default'].get('USER', ''),
        'db_password': settings.DATABASES['default'].get('PASSWORD', ''),
        'db_port': settings.DATABASES['default'].get('PORT', '1433'),
        'db_connection_type': active_db,
    }
    
    # Also get primary database settings if available
    if 'primary' in settings.DATABASES:
        primary_config = settings.DATABASES['primary']
        if active_db == 'primary':
            # If primary is active, update the form values with primary settings
            db_config.update({
                'db_host': primary_config.get('HOST', ''),
                'db_name': primary_config.get('NAME', ''),
                'db_user': primary_config.get('USER', ''),
                'db_password': primary_config.get('PASSWORD', ''),
                'db_port': primary_config.get('PORT', '1433'),
            })


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
                
                # Get the selected database connection type
                db_connection_type = form.cleaned_data['db_connection_type']
                
                # Update the ACTIVE_DB setting
                if 'ACTIVE_DB =' in settings_content:
                    settings_content = re.sub(
                        r"ACTIVE_DB = os\.environ\.get\('DJANGO_ACTIVE_DB', '[^']*'\)",
                        f"ACTIVE_DB = os.environ.get('DJANGO_ACTIVE_DB', '{db_connection_type}')",
                        settings_content
                    )
                else:
                    # If ACTIVE_DB setting doesn't exist, add it after the DATABASES definition
                    settings_content = re.sub(
                        r"(DATABASES = \{[^\}]*\})",
                        f"\\1\n\n# تحديد قاعدة البيانات النشطة من ملف الإعدادات\nACTIVE_DB = os.environ.get('DJANGO_ACTIVE_DB', '{db_connection_type}')",
                        settings_content
                    )

                # Always using SQL Server now
                # Get the selected connection type
                db_connection_type = form.cleaned_data['db_connection_type']
                
                # Update the ACTIVE_DB setting
                if 'ACTIVE_DB =' in settings_content:
                    settings_content = re.sub(
                        r"ACTIVE_DB = os\.environ\.get\('DJANGO_ACTIVE_DB', '[^']*'\)",
                        f"ACTIVE_DB = os.environ.get('DJANGO_ACTIVE_DB', '{db_connection_type}')",
                        settings_content
                    )
                else:
                    # If ACTIVE_DB setting doesn't exist, add it after the DATABASES definition
                    settings_content = re.sub(
                        r"(DATABASES = \{[^\}]*\})",
                        f"\1\n\n# تحديد قاعدة البيانات النشطة من ملف الإعدادات\nACTIVE_DB = os.environ.get('DJANGO_ACTIVE_DB', '{db_connection_type}')",
                        settings_content
                    )
                
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
                
                # Update the primary database configuration
                primary_config = (
                    "'primary': {\n"
                    "        'ENGINE': 'mssql',\n"
                    f"        'NAME': '{form.cleaned_data['db_name']}',\n"
                    f"        'HOST': '{form.cleaned_data['db_host']}',\n"
                    f"        'PORT': '{form.cleaned_data['db_port']}',\n"
                )

                # Add authentication details based on the selected method
                if not form.cleaned_data.get('use_windows_auth', True):
                    primary_config += (
                        f"        'USER': '{form.cleaned_data['db_user']}',\n"
                        f"        'PASSWORD': '{form.cleaned_data['db_password']}',\n"
                    )

                primary_config += (
                    "        'OPTIONS': {\n"
                    "            'driver': 'ODBC Driver 17 for SQL Server',\n"
                    f"            'Trusted_Connection': '{trusted_connection}',\n"
                    "        },\n"
                    "    }"
                )
                
                # Check if primary configuration exists
                if "'primary':" in settings_content:
                    # Update existing primary configuration
                    settings_content = re.sub(
                        r"'primary': \{[^\}]*\},",
                        f"{primary_config},\n    ",
                        settings_content
                    )
                else:
                    # Add primary configuration if it doesn't exist
                    default_match = re.search(r"'default': \{[^\}]*\},", settings_content)
                    if default_match:
                        # Insert the primary configuration after the default configuration
                        insert_pos = default_match.end()
                        settings_content = (
                            settings_content[:insert_pos] +
                            f"\n    {primary_config}," +
                            settings_content[insert_pos:]
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




@login_required
@system_admin_required
def url_paths_helper(request):
    """
    عرض صفحة مساعدة تحتوي على جميع المسارات المتاحة في النظام
    لتسهيل إنشاء الوحدات (Modules) بمسارات صحيحة
    """
    # المسارات الثابتة المعروفة (للاحتياط في حالة فشل الاكتشاف التلقائي)
    default_app_paths = {
        'Hr': [
            {'name': 'الصفحة الرئيسية للموارد البشرية', 'path': '/Hr/'},
            {'name': 'لوحة التحكم', 'path': '/Hr/dashboard/'},
            {'name': 'قائمة الموظفين', 'path': '/Hr/employees/'},
            {'name': 'إضافة موظف جديد', 'path': '/Hr/employees/create/'},
        ],
        'inventory': [
            {'name': 'الصفحة الرئيسية للمخزن', 'path': '/inventory/'},
            {'name': 'قائمة المنتجات', 'path': '/inventory/products/'},
            {'name': 'إضافة منتج جديد', 'path': '/inventory/products/add/'},
        ],
        'tasks': [
            {'name': 'الصفحة الرئيسية للمهام', 'path': '/tasks/'},
            {'name': 'قائمة المهام', 'path': '/tasks/list/'},
            {'name': 'إنشاء مهمة جديدة', 'path': '/tasks/create/'},
        ],
        'meetings': [
            {'name': 'الصفحة الرئيسية للاجتماعات', 'path': '/meetings/'},
            {'name': 'قائمة الاجتماعات', 'path': '/meetings/list/'},
            {'name': 'إنشاء اجتماع جديد', 'path': '/meetings/create/'},
        ],
        'Purchase_orders': [
            {'name': 'الصفحة الرئيسية لطلبات الشراء', 'path': '/purchase/'},
            {'name': 'قائمة طلبات الشراء', 'path': '/purchase/requests/'},
            {'name': 'إنشاء طلب شراء جديد', 'path': '/purchase/requests/create/'},
        ],
        'administrator': [
            {'name': 'الصفحة الرئيسية للإدارة', 'path': '/administrator/'},
            {'name': 'إعدادات النظام', 'path': '/administrator/settings/'},
            {'name': 'قائمة الوحدات', 'path': '/administrator/modules/'},
        ],
        'accounts': [
            {'name': 'تسجيل الدخول', 'path': '/accounts/login/'},
            {'name': 'تسجيل الخروج', 'path': '/accounts/logout/'},
            {'name': 'الصفحة الرئيسية', 'path': '/accounts/home/'},
        ],
    }

    # تحديث المسارات إذا تم طلب ذلك
    if request.method == 'POST' and 'refresh_paths' in request.POST:
        app_paths = discover_url_paths()
        messages.success(request, 'تم تحديث المسارات بنجاح!')
    else:
        # استخدام المسارات المكتشفة تلقائيًا أو الافتراضية
        try:
            app_paths = discover_url_paths()
        except Exception as e:
            app_paths = default_app_paths
            messages.warning(request, f'حدث خطأ أثناء اكتشاف المسارات: {str(e)}. تم استخدام المسارات الافتراضية.')

    context = {
        'app_paths': app_paths,
        'page_title': 'دليل المسارات المتاحة في النظام',
    }
    return render(request, 'administrator/url_paths_helper.html', context)


@login_required
@system_admin_required
def template_paths_helper(request):
    """
    عرض صفحة مساعدة تحتوي على جميع القوالب المتاحة في النظام
    لتسهيل إنشاء صلاحيات القوالب (Template Permissions) بمسارات صحيحة
    """
    # القوالب الثابتة المعروفة (للاحتياط في حالة فشل الاكتشاف التلقائي)
    default_app_templates = {
        'Hr': [
            {'name': 'قائمة الموظفين', 'path': 'Hr/employees/employee_list.html'},
            {'name': 'تفاصيل الموظف', 'path': 'Hr/employees/employee_detail.html'},
            {'name': 'نموذج الموظف', 'path': 'Hr/employees/employee_form.html'},
        ],
        'inventory': [
            {'name': 'قائمة المنتجات', 'path': 'inventory/product_list.html'},
            {'name': 'تفاصيل المنتج', 'path': 'inventory/product_detail.html'},
            {'name': 'نموذج المنتج', 'path': 'inventory/product_form.html'},
        ],
        'tasks': [
            {'name': 'قائمة المهام', 'path': 'tasks/task_list.html'},
            {'name': 'تفاصيل المهمة', 'path': 'tasks/task_detail.html'},
            {'name': 'نموذج المهمة', 'path': 'tasks/task_form.html'},
        ],
        'meetings': [
            {'name': 'قائمة الاجتماعات', 'path': 'meetings/meeting_list.html'},
            {'name': 'تفاصيل الاجتماع', 'path': 'meetings/meeting_detail.html'},
            {'name': 'نموذج الاجتماع', 'path': 'meetings/meeting_form.html'},
        ],
        'administrator': [
            {'name': 'لوحة التحكم', 'path': 'administrator/dashboard.html'},
            {'name': 'إعدادات النظام', 'path': 'administrator/system_settings.html'},
            {'name': 'قائمة الوحدات', 'path': 'administrator/module_list.html'},
        ],
        'accounts': [
            {'name': 'تسجيل الدخول', 'path': 'accounts/login.html'},
            {'name': 'الصفحة الرئيسية', 'path': 'accounts/home.html'},
            {'name': 'الملف الشخصي', 'path': 'accounts/profile.html'},
        ],
        'common': [
            {'name': 'القالب الأساسي', 'path': 'base.html'},
            {'name': 'القالب الأساسي المحدث', 'path': 'base_updated.html'},
            {'name': 'قالب الصفحة الرئيسية', 'path': 'home_dashboard.html'},
        ],
    }

    # تحديث القوالب إذا تم طلب ذلك
    if request.method == 'POST' and 'refresh_templates' in request.POST:
        try:
            app_templates = discover_templates()
            messages.success(request, 'تم تحديث القوالب بنجاح!')
        except Exception as e:
            app_templates = default_app_templates
            messages.error(request, f'حدث خطأ أثناء تحديث القوالب: {str(e)}. تم استخدام القوالب الافتراضية.')
    else:
        # استخدام القوالب المكتشفة تلقائيًا أو الافتراضية
        try:
            app_templates = discover_templates()

            # دمج القوالب المكتشفة مع القوالب الثابتة
            for app_name, templates in default_app_templates.items():
                if app_name not in app_templates:
                    app_templates[app_name] = []

                for template_item in templates:
                    # التحقق من عدم وجود القالب بالفعل
                    template_exists = False
                    for existing_template in app_templates[app_name]:
                        if existing_template['path'] == template_item['path']:
                            template_exists = True
                            break

                    if not template_exists:
                        app_templates[app_name].append(template_item)

        except Exception as e:
            app_templates = default_app_templates
            messages.warning(request, f'حدث خطأ أثناء اكتشاف القوالب: {str(e)}. تم استخدام القوالب الافتراضية.')

    context = {
        'app_templates': app_templates,
        'page_title': 'دليل القوالب المتاحة في النظام',
    }
    return render(request, 'administrator/template_paths_helper.html', context)


@login_required
@system_admin_required
def create_modules_from_paths(request):
    """
    إنشاء وحدات من المسارات المكتشفة في النظام
    """
    if request.method == 'POST':
        app_name = request.POST.get('app_name')
        if not app_name:
            messages.error(request, 'لم يتم تحديد اسم التطبيق!')
            return redirect('administrator:url_paths_helper')

        # الحصول على المسارات المكتشفة
        try:
            app_paths = discover_url_paths()
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء اكتشاف المسارات: {str(e)}')
            return redirect('administrator:url_paths_helper')

        # تحديد الأيقونة والألوان حسب التطبيق
        icon_map = {
            'Hr': 'fa-users',
            'inventory': 'fa-boxes',
            'tasks': 'fa-tasks',
            'meetings': 'fa-handshake',
            'Purchase_orders': 'fa-shopping-cart',
            'administrator': 'fa-cogs',
            'accounts': 'fa-user-circle',
        }

        color_map = {
            'Hr': '#28a745',
            'inventory': '#fd7e14',
            'tasks': '#6f42c1',
            'meetings': '#e83e8c',
            'Purchase_orders': '#20c997',
            'administrator': '#0d6efd',
            'accounts': '#6c757d',
        }

        # الحصول على الأقسام المتاحة
        departments = Department.objects.filter(is_active=True)
        if not departments.exists():
            messages.error(request, 'لا توجد أقسام متاحة. يرجى إنشاء قسم أولاً.')
            return redirect('administrator:department_list')

        # إنشاء قاموس للربط بين أسماء التطبيقات والأقسام
        app_department_map = {}
        for dept in departments:
            # محاولة مطابقة اسم القسم مع اسم التطبيق
            dept_name_lower = dept.name.lower()
            dept_url_name_lower = dept.url_name.lower() if dept.url_name else ''

            for app in app_paths.keys():
                app_lower = app.lower()
                if app_lower == dept_name_lower or app_lower == dept_url_name_lower:
                    app_department_map[app] = dept

        # إنشاء الوحدات
        total_created = 0
        total_skipped = 0

        # إذا كان app_name هو "all"، نقوم بإنشاء وحدات لجميع التطبيقات
        if app_name == 'all':
            for current_app, paths in app_paths.items():
                # البحث عن القسم المناسب للتطبيق
                department = app_department_map.get(current_app)

                # إذا لم يتم العثور على قسم مطابق، نستخدم أول قسم متاح
                if not department:
                    department = departments.first()

                # الحصول على الأيقونة واللون المناسبين
                icon = icon_map.get(current_app, 'fa-link')
                bg_color = color_map.get(current_app, '#0d6efd')

                # إنشاء الوحدات لهذا التطبيق
                app_created, app_skipped = create_modules_for_app(current_app, paths, department, icon, bg_color)

                total_created += app_created
                total_skipped += app_skipped

            # إرسال رسالة نجاح
            if total_created > 0:
                messages.success(request, f'تم إنشاء {total_created} وحدة جديدة بنجاح لجميع التطبيقات.')
            if total_skipped > 0:
                messages.info(request, f'تم تخطي {total_skipped} وحدة موجودة بالفعل.')
            if total_created == 0 and total_skipped == 0:
                messages.warning(request, 'لم يتم إنشاء أي وحدات.')
        else:
            # التحقق من وجود المسارات للتطبيق المحدد
            if app_name not in app_paths:
                messages.error(request, f'لا توجد مسارات متاحة للتطبيق: {app_name}')
                return redirect('administrator:url_paths_helper')

            # البحث عن القسم المناسب للتطبيق
            department = app_department_map.get(app_name)

            # إذا لم يتم العثور على القسم، نستخدم أول قسم متاح
            if not department:
                department = departments.first()
                messages.warning(request, f'لم يتم العثور على قسم مطابق لـ {app_name}. تم استخدام القسم: {department.name}')

            # الحصول على الأيقونة واللون المناسبين
            icon = icon_map.get(app_name, 'fa-link')
            bg_color = color_map.get(app_name, '#0d6efd')

            # إنشاء الوحدات لهذا التطبيق
            created_count, skipped_count = create_modules_for_app(app_name, app_paths[app_name], department, icon, bg_color)

            # إرسال رسالة نجاح
            if created_count > 0:
                messages.success(request, f'تم إنشاء {created_count} وحدة جديدة بنجاح لـ {app_name}.')
            if skipped_count > 0:
                messages.info(request, f'تم تخطي {skipped_count} وحدة موجودة بالفعل.')
            if created_count == 0 and skipped_count == 0:
                messages.warning(request, f'لم يتم إنشاء أي وحدات لـ {app_name}.')

        return redirect('administrator:module_list')

    # إذا لم تكن الطريقة POST، نعيد توجيه المستخدم إلى صفحة دليل المسارات
    return redirect('administrator:url_paths_helper')


@login_required
@system_admin_required
def create_templates_from_paths(request):
    """
    إنشاء قوالب من المسارات المكتشفة في النظام
    """
    if request.method == 'POST':
        app_name = request.POST.get('app_name')
        if not app_name:
            messages.error(request, 'لم يتم تحديد اسم التطبيق!')
            return redirect('administrator:template_paths_helper')

        # الحصول على القوالب المكتشفة
        try:
            app_templates = discover_templates()
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء اكتشاف القوالب: {str(e)}')
            return redirect('administrator:template_paths_helper')

        # إنشاء صلاحيات القوالب
        total_created = 0
        total_skipped = 0

        # إذا كان app_name هو "all"، نقوم بإنشاء صلاحيات لجميع التطبيقات
        if app_name == 'all':
            for current_app, templates in app_templates.items():
                app_created, app_skipped = create_template_permissions_for_app(current_app, templates)
                total_created += app_created
                total_skipped += app_skipped

            # إرسال رسالة نجاح
            if total_created > 0:
                messages.success(request, f'تم إنشاء {total_created} صلاحية قالب جديدة بنجاح لجميع التطبيقات.')
            if total_skipped > 0:
                messages.info(request, f'تم تخطي {total_skipped} صلاحية قالب موجودة بالفعل.')
            if total_created == 0 and total_skipped == 0:
                messages.warning(request, 'لم يتم إنشاء أي صلاحيات قوالب.')
        else:
            # التحقق من وجود القوالب للتطبيق المحدد
            if app_name not in app_templates:
                messages.error(request, f'لا توجد قوالب متاحة للتطبيق: {app_name}')
                return redirect('administrator:template_paths_helper')

            # إنشاء صلاحيات القوالب لهذا التطبيق
            created_count, skipped_count = create_template_permissions_for_app(app_name, app_templates[app_name])

            # إرسال رسالة نجاح
            if created_count > 0:
                messages.success(request, f'تم إنشاء {created_count} صلاحية قالب جديدة بنجاح لـ {app_name}.')
            if skipped_count > 0:
                messages.info(request, f'تم تخطي {skipped_count} صلاحية قالب موجودة بالفعل.')
            if created_count == 0 and skipped_count == 0:
                messages.warning(request, f'لم يتم إنشاء أي صلاحيات قوالب لـ {app_name}.')

        return redirect('administrator:template_permission_list')

    # إذا لم تكن الطريقة POST، نعيد توجيه المستخدم إلى صفحة دليل القوالب
    return redirect('administrator:template_paths_helper')


def create_template_permissions_for_app(app_name, templates):
    """
    إنشاء صلاحيات قوالب لتطبيق محدد
    """
    created_count = 0
    skipped_count = 0

    for template_item in templates:
        # التحقق من وجود صلاحية القالب بالفعل
        existing_permission = TemplatePermission.objects.filter(
            template_path=template_item['path']
        ).first()

        if existing_permission:
            skipped_count += 1
            continue

        # إنشاء صلاحية قالب جديدة
        name = template_item['name']
        # Always include the app name in the template permission name
        name = f"{name} - {app_name}"

        new_permission = TemplatePermission(
            name=name,
            app_name=app_name,  # إضافة اسم التطبيق إلى حقل app_name
            template_path=template_item['path'],
            description=f"صلاحية الوصول لقالب {name}",
            is_active=True
        )
        new_permission.save()
        created_count += 1

    return created_count, skipped_count


def create_modules_for_app(app_name, paths, department, icon, bg_color):
    """
    إنشاء وحدات لتطبيق محدد
    """
    created_count = 0
    skipped_count = 0

    for path_item in paths:
        # التحقق من وجود الوحدة بالفعل
        existing_module = Module.objects.filter(
            url=path_item['path'],
            department=department
        ).first()

        if existing_module:
            skipped_count += 1
            continue

        # إنشاء وحدة جديدة
        new_module = Module(
            name=path_item['name'],
            url=path_item['path'],
            department=department,
            icon=icon,
            bg_color=bg_color,
            is_active=True,
            order=Module.objects.filter(department=department).count() + 1
        )
        new_module.save()
        created_count += 1

    return created_count, skipped_count


def normalize_url_path(path):
    """
    تنظيف وتنسيق مسار URL بالشكل الصحيح:
    1. التأكد من أن المسار يبدأ بعلامة /
    2. إزالة العلامات المتكررة // وتحويلها إلى / واحدة
    3. التأكد من أن المسار ينتهي بعلامة / إذا كان مسار قائمة/فهرس
    """
    # إضافة / في بداية المسار إذا لم تكن موجودة
    if not path.startswith('/'):
        path = '/' + path
    
    # إزالة // المتكررة
    while '//' in path:
        path = path.replace('//', '/')
    
    # إضافة / في نهاية المسار إذا كانت آخر عنصر ليس / وليس له امتداد ملف مثل .html
    if not path.endswith('/') and '.' not in path.split('/')[-1]:
        path = path + '/'
    
    return path

def discover_url_paths():
    """
    اكتشاف المسارات المتاحة في النظام بشكل ديناميكي ومع تنظيف المسارات
    """
    from django.urls import get_resolver, URLPattern, URLResolver
    from django.conf import settings
    import re

    # قاموس لتخزين المسارات حسب التطبيق
    app_paths = {}

    # الحصول على جميع المسارات المسجلة في النظام
    resolver = get_resolver()

    # قاموس لتخزين أسماء التطبيقات الفعلية وأسماء العرض
    app_display_names = {
        'hr': 'Hr',
        'inventory': 'inventory',
        'tasks': 'tasks',
        'meetings': 'meetings',
        'purchase_orders': 'Purchase_orders',
        'administrator': 'administrator',
        'accounts': 'accounts',
        'eldawliya_sys': 'ElDawliya_sys',
        'admin_permissions': 'admin_permissions',
    }

    # قاموس لتخزين أسماء المسارات بناءً على أنماط الاسم
    path_name_patterns = {
        'list': 'قائمة',
        'create': 'إضافة',
        'add': 'إضافة',
        'edit': 'تعديل',
        'update': 'تحديث',
        'delete': 'حذف',
        'detail': 'تفاصيل',
        'view': 'عرض',
        'dashboard': 'لوحة التحكم',
        'settings': 'الإعدادات',
        'report': 'تقرير',
        'reports': 'التقارير',
        'export': 'تصدير',
        'import': 'استيراد',
        'print': 'طباعة',
        'search': 'بحث',
        'calendar': 'التقويم',
        'profile': 'الملف الشخصي',
        'login': 'تسجيل الدخول',
        'logout': 'تسجيل الخروج',
        'home': 'الصفحة الرئيسية',
    }

    # قاموس لتخزين أسماء الكيانات
    entity_name_patterns = {
        'employee': 'موظف',
        'employees': 'الموظفين',
        'department': 'قسم',
        'departments': 'الأقسام',
        'job': 'وظيفة',
        'jobs': 'الوظائف',
        'car': 'سيارة',
        'cars': 'السيارات',
        'product': 'منتج',
        'products': 'المنتجات',
        'category': 'تصنيف',
        'categories': 'التصنيفات',
        'unit': 'وحدة',
        'units': 'وحدات القياس',
        'invoice': 'فاتورة',
        'invoices': 'الفواتير',
        'task': 'مهمة',
        'tasks': 'المهام',
        'meeting': 'اجتماع',
        'meetings': 'الاجتماعات',
        'request': 'طلب',
        'requests': 'الطلبات',
        'vendor': 'مورد',
        'vendors': 'الموردين',
        'module': 'وحدة',
        'modules': 'الوحدات',
        'permission': 'صلاحية',
        'permissions': 'الصلاحيات',
        'group': 'مجموعة',
        'groups': 'المجموعات',
        'user': 'مستخدم',
        'users': 'المستخدمين',
        'stock': 'المخزون',
        'attendance': 'الحضور',
        'leave': 'إجازة',
        'leaves': 'الإجازات',
        'salary': 'راتب',
        'salaries': 'الرواتب',
        'evaluation': 'تقييم',
        'evaluations': 'التقييمات',
        'note': 'ملاحظة',
        'notes': 'الملاحظات',
        'file': 'ملف',
        'files': 'الملفات',
    }

    # وظيفة مساعدة للاكتشاف التفصيلي للمسارات من خلال العقد
    def extract_paths_from_resolver_node(resolver_node, current_path='', namespace=''):
        paths = []

        # استخراج المسارات من أنماط URL والمحللات الفرعية
        if hasattr(resolver_node, 'url_patterns'):
            for pattern in resolver_node.url_patterns:
                # استخراج المسار الحالي
                pattern_path = current_path
                if hasattr(pattern, 'pattern'):
                    pattern_str = str(pattern.pattern)
                    # تنظيف المسار (إزالة أنماط التعبير العادي وإزالة المعلمات)
                    cleaned_path = re.sub(r'<[^>]+>', '', pattern_str)
                    cleaned_path = cleaned_path.replace('^', '').replace('$', '')
                    pattern_path = current_path + cleaned_path

                # إذا كان نمط URL، استخرج اسمه وأضف المسار
                if isinstance(pattern, URLPattern) and hasattr(pattern, 'name') and pattern.name:
                    path_name = pattern.name
                    full_namespace = namespace
                    if resolver_node.namespace:
                        full_namespace = resolver_node.namespace

                    url_name = path_name
                    if full_namespace:
                        url_name = f"{full_namespace}:{path_name}"
                    
                    paths.append({
                        'name': url_name,
                        'path': pattern_path
                    })

                # إذا كان محلل URL، استخرج المسارات بشكل متكرر
                elif isinstance(pattern, URLResolver):
                    new_namespace = namespace
                    if pattern.namespace:
                        if namespace:
                            new_namespace = f"{namespace}:{pattern.namespace}"
                        else:
                            new_namespace = pattern.namespace
                    
                    # استدعاء الدالة بشكل متكرر للمحلل الفرعي
                    paths.extend(extract_paths_from_resolver_node(
                        pattern,
                        current_path=pattern_path,
                        namespace=new_namespace
                    ))

        return paths

    # استخراج المسارات باستخدام الطريقة المباشرة من reverse_dict
    for url_name, url_pattern in resolver.reverse_dict.items():
        # تجاهل العناصر التي ليست سلاسل نصية (مثل الدوال)
        if not isinstance(url_name, str):
            continue

        # تحديد التطبيق الذي ينتمي إليه المسار
        if ':' in url_name:
            app_name = url_name.split(':')[0]
            pattern_name = url_name.split(':')[1]
        else:
            app_name = url_name
            pattern_name = ''

        # تحويل اسم التطبيق إلى الاسم المعروض
        display_app_name = app_display_names.get(app_name.lower(), app_name)

        # إنشاء قائمة للتطبيق إذا لم تكن موجودة
        if display_app_name not in app_paths:
            app_paths[display_app_name] = []

        # تحديد المسار الكامل
        path = f'/{app_name}/'
        if pattern_name:
            # استخراج النمط من الاسم
            pattern = pattern_name.replace('_', '/').lower()
            path = f'/{app_name}/{pattern}/'

        # تحديد اسم المسار
        path_name = ''

    # استخراج المسارات بشكل أكثر تفصيلاً من محلل URL
    detailed_paths = extract_paths_from_resolver_node(resolver)
    
    # تنظيم المسارات التفصيلية حسب التطبيق
    for path_info in detailed_paths:
        url_name = path_info['name']
        path_value = path_info['path']
        
        # تنظيف المسار باستخدام الدالة المخصصة
        path_value = normalize_url_path(path_value)
        
        # تحديد التطبيق
        app_name = None
        pattern_name = ''
        
        if ':' in url_name:
            app_name = url_name.split(':')[0]
            pattern_name = url_name.split(':')[1]
        else:
            # محاولة استنتاج التطبيق من المسار
            path_parts = path_value.strip('/').split('/')
            if path_parts:
                app_name = path_parts[0]
                if len(path_parts) > 1:
                    # استخدام الجزء الثاني من المسار كاسم النمط
                    pattern_name = path_parts[1]
        
        if not app_name:
            app_name = 'common'
        
        # تحويل اسم التطبيق إلى الاسم المعروض
        display_app_name = app_display_names.get(app_name.lower(), app_name)
        
        # إنشاء قائمة للتطبيق إذا لم تكن موجودة
        if display_app_name not in app_paths:
            app_paths[display_app_name] = []

        # تحديد اسم المسار
        path_name = ''

        # محاولة استخراج اسم المسار من النمط
        parts = pattern_name.split('_') if pattern_name else []
        if parts:
            # البحث عن أنماط الاسم المعروفة
            for part in parts:
                if part.lower() in path_name_patterns:
                    action = path_name_patterns[part.lower()]

                    # البحث عن الكيان
                    for other_part in parts:
                        if other_part.lower() in entity_name_patterns:
                            entity = entity_name_patterns[other_part.lower()]
                            if action in ['إضافة', 'تعديل', 'حذف']:
                                # تحويل الكيان إلى المفرد للإضافة والتعديل والحذف
                                if entity.endswith('ين'):
                                    entity = entity[:-2]
                                elif entity.endswith('ات'):
                                    entity = entity[:-2]

                            path_name = f"{action} {entity}"
                            break

                    if not path_name:
                        path_name = action
                    break

        # إذا لم نتمكن من تحديد اسم، نستخدم الاسم الأصلي
        if not path_name:
            if not pattern_name:
                if display_app_name == 'Hr':
                    path_name = 'الصفحة الرئيسية للموارد البشرية'
                elif display_app_name == 'inventory':
                    path_name = 'الصفحة الرئيسية للمخزن'
                elif display_app_name == 'tasks':
                    path_name = 'الصفحة الرئيسية للمهام'
                elif display_app_name == 'meetings':
                    path_name = 'الصفحة الرئيسية للاجتماعات'
                elif display_app_name == 'Purchase_orders':
                    path_name = 'الصفحة الرئيسية لطلبات الشراء'
                elif display_app_name == 'administrator':
                    path_name = 'الصفحة الرئيسية للإدارة'
                elif display_app_name == 'accounts':
                    path_name = 'الصفحة الرئيسية للحسابات'
                else:
                    path_name = f'الصفحة الرئيسية لـ {display_app_name}'
            else:
                path_name = pattern_name.replace('_', ' ').title()

        # اسم المسار النهائي
        if path_name:
            # إضافة المسار إلى قائمة المسارات إذا كان عندنا اسم للمسار
            app_paths[display_app_name].append({
                'name': path_name,
                'path': path_value
            })
        else:
            # اسم افتراضي بناء على المسار
            path_name = url_name.replace(':', ' - ').replace('_', ' ').title()
            app_paths[display_app_name].append({
                'name': path_name,
                'path': path_value
            })

    # إضافة المسارات الثابتة المعروفة
    default_app_paths = {
        'Hr': [
            {'name': 'الصفحة الرئيسية للموارد البشرية', 'path': '/Hr/'},
            {'name': 'لوحة التحكم', 'path': '/Hr/dashboard/'},
            {'name': 'قائمة الموظفين', 'path': '/Hr/employees/'},
            {'name': 'إضافة موظف جديد', 'path': '/Hr/employees/create/'},
        ],
        'inventory': [
            {'name': 'الصفحة الرئيسية للمخزن', 'path': '/inventory/'},
            {'name': 'قائمة المنتجات', 'path': '/inventory/products/'},
            {'name': 'إضافة منتج جديد', 'path': '/inventory/products/add/'},
        ],
        'tasks': [
            {'name': 'الصفحة الرئيسية للمهام', 'path': '/tasks/'},
            {'name': 'قائمة المهام', 'path': '/tasks/list/'},
            {'name': 'إنشاء مهمة جديدة', 'path': '/tasks/create/'},
        ],
        'meetings': [
            {'name': 'الصفحة الرئيسية للاجتماعات', 'path': '/meetings/'},
            {'name': 'قائمة الاجتماعات', 'path': '/meetings/list/'},
            {'name': 'إنشاء اجتماع جديد', 'path': '/meetings/create/'},
        ],
        'Purchase_orders': [
            {'name': 'الصفحة الرئيسية لطلبات الشراء', 'path': '/purchase/'},
            {'name': 'قائمة طلبات الشراء', 'path': '/purchase/requests/'},
            {'name': 'إنشاء طلب شراء جديد', 'path': '/purchase/requests/create/'},
        ],
        'administrator': [
            {'name': 'الصفحة الرئيسية للإدارة', 'path': '/administrator/'},
            {'name': 'إعدادات النظام', 'path': '/administrator/settings/'},
            {'name': 'قائمة الوحدات', 'path': '/administrator/modules/'},
        ],
        'accounts': [
            {'name': 'تسجيل الدخول', 'path': '/accounts/login/'},
            {'name': 'تسجيل الخروج', 'path': '/accounts/logout/'},
            {'name': 'الصفحة الرئيسية', 'path': '/accounts/home/'},
        ],
    }

    # دمج المسارات المكتشفة مع المسارات الثابتة
    for app_name, paths in default_app_paths.items():
        if app_name not in app_paths:
            app_paths[app_name] = []

        for path_item in paths:
            app_paths[app_name].append(path_item)

    # إزالة المسارات المكررة
    for app_name in app_paths:
        unique_paths = []
        path_set = set()

        for path_item in app_paths[app_name]:
            if path_item['path'] not in path_set:
                path_set.add(path_item['path'])
                unique_paths.append(path_item)

        app_paths[app_name] = unique_paths

    # إذا لم نجد أي مسارات، نرفع استثناء
    if not app_paths:
        raise Exception("لم يتم العثور على أي مسارات")

    return app_paths


def discover_templates():
    """
    اكتشاف القوالب المتاحة في النظام بشكل ديناميكي
    """
    import os
    from django.conf import settings
    from django.template.loaders.app_directories import get_app_template_dirs

    # قاموس لتخزين القوالب حسب التطبيق
    app_templates = {}

    # قاموس لتخزين أسماء التطبيقات الفعلية وأسماء العرض
    app_display_names = {
        'hr': 'Hr',
        'inventory': 'inventory',
        'tasks': 'tasks',
        'meetings': 'meetings',
        'purchase_orders': 'Purchase_orders',
        'administrator': 'administrator',
        'accounts': 'accounts',
    }

    # قاموس لتخزين أسماء القوالب بناءً على أنماط الاسم
    template_name_patterns = {
        'list': 'قائمة',
        'create': 'إنشاء',
        'add': 'إضافة',
        'edit': 'تعديل',
        'update': 'تحديث',
        'delete': 'حذف',
        'detail': 'تفاصيل',
        'view': 'عرض',
        'dashboard': 'لوحة التحكم',
        'settings': 'الإعدادات',
        'report': 'تقرير',
        'reports': 'التقارير',
        'form': 'نموذج',
        'profile': 'الملف الشخصي',
        'login': 'تسجيل الدخول',
        'logout': 'تسجيل الخروج',
        'home': 'الصفحة الرئيسية',
        'base': 'القالب الأساسي',
    }

    # قاموس لتخزين أسماء الكيانات
    entity_name_patterns = {
        'employee': 'موظف',
        'employees': 'الموظفين',
        'department': 'قسم',
        'departments': 'الأقسام',
        'job': 'وظيفة',
        'jobs': 'الوظائف',
        'car': 'سيارة',
        'cars': 'السيارات',
        'product': 'منتج',
        'products': 'المنتجات',
        'category': 'تصنيف',
        'categories': 'التصنيفات',
        'unit': 'وحدة',
        'units': 'وحدات القياس',
        'invoice': 'فاتورة',
        'invoices': 'الفواتير',
        'task': 'مهمة',
        'tasks': 'المهام',
        'meeting': 'اجتماع',
        'meetings': 'الاجتماعات',
        'request': 'طلب',
        'requests': 'الطلبات',
        'vendor': 'مورد',
        'vendors': 'الموردين',
        'module': 'وحدة',
        'modules': 'الوحدات',
        'permission': 'صلاحية',
        'permissions': 'الصلاحيات',
        'group': 'مجموعة',
        'groups': 'المجموعات',
        'user': 'مستخدم',
        'users': 'المستخدمين',
        'stock': 'المخزون',
        'attendance': 'الحضور',
        'leave': 'إجازة',
        'leaves': 'الإجازات',
        'salary': 'راتب',
        'salaries': 'الرواتب',
        'evaluation': 'تقييم',
        'evaluations': 'التقييمات',
        'note': 'ملاحظة',
        'notes': 'الملاحظات',
        'file': 'ملف',
        'files': 'الملفات',
    }

    # الحصول على مجلدات القوالب لكل تطبيق
    app_template_dirs = list(get_app_template_dirs('templates'))

    # إضافة مجلد القوالب الرئيسي
    template_dirs = list(settings.TEMPLATES[0]['DIRS']) + app_template_dirs

    # البحث عن القوالب في كل مجلد
    for template_dir in template_dirs:
        if not os.path.exists(template_dir):
            continue

        # تحديد اسم التطبيق من مسار المجلد
        app_name = None
        for installed_app in settings.INSTALLED_APPS:
            if installed_app in str(template_dir):
                app_name = installed_app
                break

        # إذا لم نتمكن من تحديد اسم التطبيق، نستخدم "عام"
        if not app_name:
            app_name = "common"

        # تحويل اسم التطبيق إلى الاسم المعروض
        display_app_name = app_display_names.get(app_name.lower(), app_name)

        # إنشاء قائمة للتطبيق إذا لم تكن موجودة
        if display_app_name not in app_templates:
            app_templates[display_app_name] = []

        # البحث عن القوالب في المجلد وجميع المجلدات الفرعية
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    # الحصول على المسار النسبي للقالب
                    template_path = os.path.join(root, file)
                    relative_path = os.path.relpath(template_path, template_dir)

                    # تحديد اسم القالب
                    template_name = os.path.splitext(file)[0]

                    # محاولة استخراج اسم القالب من النمط
                    template_display_name = ''

                    # البحث عن أنماط الاسم المعروفة
                    for pattern, name in template_name_patterns.items():
                        if pattern in template_name:
                            action = name

                            # البحث عن الكيان
                            for entity_pattern, entity_name in entity_name_patterns.items():
                                if entity_pattern in template_name:
                                    if action in ['إضافة', 'تعديل', 'حذف']:
                                        # تحويل الكيان إلى المفرد للإضافة والتعديل والحذف
                                        if entity_name.endswith('ين'):
                                            entity_name = entity_name[:-2]
                                        elif entity_name.endswith('ات'):
                                            entity_name = entity_name[:-2]

                                    template_display_name = f"{action} {entity_name}"
                                    break

                            if not template_display_name:
                                template_display_name = action
                            break

                    # إذا لم نتمكن من تحديد اسم، نستخدم اسم الملف
                    if not template_display_name:
                        template_display_name = template_name.replace('_', ' ').replace('-', ' ').title()

                    # إضافة القالب إلى قائمة القوالب
                    app_templates[display_app_name].append({
                        'name': template_display_name,
                        'path': relative_path,
                        'full_path': template_path,
                    })

    # إزالة القوالب المكررة
    for app_name in app_templates:
        unique_templates = []
        path_set = set()

        for template_item in app_templates[app_name]:
            if template_item['path'] not in path_set:
                path_set.add(template_item['path'])
                unique_templates.append(template_item)

        app_templates[app_name] = unique_templates

    # إذا لم نجد أي قوالب، نرفع استثناء
    if not app_templates:
        raise Exception("لم يتم العثور على أي قوالب")

    return app_templates


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
