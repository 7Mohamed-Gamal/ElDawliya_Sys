from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Temporarily commented out to avoid import errors
# from apps.projects.meetings.models import Meeting
# from apps.projects.tasks.models import Task
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.urls import reverse
import json

# استيراد وظائف إنشاء التنبيهات
try:
    from notifications.utils import create_system_notification
except ImportError:
    create_system_notification = None

User = get_user_model()

@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    """login_view function"""
    if request.method == 'POST':
        form = CustomUserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()

            login(request, user)
            messages.success(request, f'مرحباً بك في نظام الشركة الدولية انترناشونال، {user.username}!')

            # إنشاء تنبيه نظام عند تسجيل الدخول
            if create_system_notification:
                create_system_notification(
                    user=user,
                    title='تسجيل دخول ناجح',
                    message=f'تم تسجيل دخولك بنجاح في {timezone.now().strftime("%Y-%m-%d %H:%M")}',
                    priority='low',
                    icon='fas fa-sign-in-alt'
                )

            return redirect('frontend:dashboard')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
    else:
        form = CustomUserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """logout_view function"""
    logout(request)
    return redirect('accounts:login')

def access_denied(request):
    """عرض صفحة رفض الوصول"""
    return render(request, 'accounts/access_denied.html', {'title': 'رفض الوصول'})

def csrf_failure(request, reason=""):
    """
    Custom CSRF failure view
    """
    context = {
        'title': 'خطأ في التحقق من CSRF',
        'reason': reason,
        'form': CustomUserLoginForm()
    }
    return render(request, 'accounts/login.html', context)

@login_required
def dashboard_view(request):
    """dashboard_view function"""
    # Get all users
    users = User.objects.all()

    # Count statistics
    total_users = users.count()
    admin_users = users.filter(Role='admin').count()
    manager_users = users.filter(Role='Manager').count()
    employee_users = users.filter(Role='employee').count()
    active_users = users.filter(is_active=True).count()

    context = {
        'users': users,
        'total_users': total_users,
        'admin_users': admin_users,
        'manager_users': manager_users,
        'employee_users': employee_users,
        'active_users': active_users,
        'recent_activities': []  # Add recent activity logic if available
    }

    return render(request, 'accounts/dashboard.html', context)

@login_required
def home_view(request):
    """home_view function"""
    # Get real-time stats for dashboard (temporarily using placeholder data)
    meetings_count = 0  # Meeting.objects.count()
    tasks_count = 0  # Task.objects.count()
    completed_tasks_count = 0  # Task.objects.filter(status='completed').count()
    users_count = User.objects.count()

    # Get recent meetings (temporarily empty)
    recent_meetings = []  # Meeting.objects.order_by('-date')[:5]

    # Get recent tasks (temporarily empty)
    recent_tasks = []  # Task.objects.order_by('-start_date')[:5]

    # Get user's tasks (temporarily empty)
    user_tasks = []  # Task.objects.filter(assigned_to=request.user).order_by('status', '-start_date')

    # Check if user is admin
    is_admin = request.user.Role == 'admin'

    # Get departments and modules from administrator app if it's installed
    user_departments = []
    all_departments = []
    department_modules = {}
    try:
        from administrator.models import Department, Module

        # Get all active departments
        departments = Department.objects.filter(is_active=True).order_by('order')

        # For admin users, store all departments
        if is_admin:
            all_departments = departments

        # Ensure url_name is set correctly for JavaScript matching
        for dept in departments:
            # Make sure url_name doesn't include '-cards' suffix
            if hasattr(dept, 'url_name'):
                if dept.url_name == 'hr':
                    pass
            else:
                # If url_name doesn't exist, set a default based on department name
                dept.url_name = dept.name.lower().replace(' ', '-')

        # Filter departments based on user permissions and get their modules
        for dept in departments:
            dept_modules = []
            # If department requires admin and user is admin, add it
            if dept.require_admin and is_admin:
                user_departments.append(dept)
                # Get active modules for this department
                modules = Module.objects.filter(
                    department=dept,
                    is_active=True
                ).order_by('order')
                # Filter modules based on user permissions
                for module in modules:
                    if module.require_admin and not is_admin:
                        continue  # Skip admin-only modules for non-admin users
                    if module.groups.exists() and not module.groups.filter(id__in=request.user.groups.all()).exists():
                        continue  # Skip modules restricted to specific groups
                    dept_modules.append(module)
            # If department doesn't require admin, check group permissions
            elif not dept.require_admin:
                # If no groups specified, everyone can access
                if not dept.groups.exists():
                    user_departments.append(dept)
                    # Get active modules for this department
                    modules = Module.objects.filter(
                        department=dept,
                        is_active=True
                    ).order_by('order')
                    # Filter modules based on user permissions
                    for module in modules:
                        if module.require_admin and not is_admin:
                            continue  # Skip admin-only modules for non-admin users
                        if module.groups.exists() and not module.groups.filter(id__in=request.user.groups.all()).exists():
                            continue  # Skip modules restricted to specific groups
                        dept_modules.append(module)
                # Otherwise, check if user is in any of the allowed groups
                else:
                    # Check if any of the user's groups are in the department's allowed groups
                    if dept.groups.filter(id__in=request.user.groups.all()).exists():
                        user_departments.append(dept)
                        # Get active modules for this department
                        modules = Module.objects.filter(
                            department=dept,
                            is_active=True
                        ).order_by('order')
                        # Filter modules based on user permissions
                        for module in modules:
                            if module.require_admin and not is_admin:
                                continue  # Skip admin-only modules for non-admin users
                            if module.groups.exists() and not module.groups.filter(id__in=request.user.groups.all()).exists():
                                continue  # Skip modules restricted to specific groups
                            dept_modules.append(module)

            # Store modules for this department
            if dept.url_name:
                department_modules[dept.url_name] = dept_modules
            else:
                dept_url_key = dept.name.lower().replace(' ', '-')
                department_modules[dept_url_key] = dept_modules

    except Exception as e:
        # If administrator app is not installed or any error occurs
        import traceback
        traceback.print_exc()

    context = {
        'meetings_count': meetings_count,
        'tasks_count': tasks_count,
        'completed_tasks_count': completed_tasks_count,
        'users_count': users_count,
        'recent_meetings': recent_meetings,
        'recent_tasks': recent_tasks,
        'user_tasks': user_tasks,
        'user_departments': user_departments,
        'all_departments': all_departments,
        'department_modules': department_modules,
        'is_admin': is_admin
    }

    return render(request, 'home_dashboard.html', context)

@login_required
def create_user_view(request):
    """create_user_view function"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # إضافة المستخدم إلى المجموعات المحددة (إذا تم تحديدها)
            if 'groups' in request.POST:
                groups = request.POST.getlist('groups')
                user.groups.set(groups)

            messages.success(request, 'تم إنشاء المستخدم بنجاح!')
            return redirect('accounts:dashboard')
    else:
        form = CustomUserCreationForm()

    # استخدام نظام المجموعات الخاص بـ Django
    from django.contrib.auth.models import Group
    groups = Group.objects.all()

    context = {
        'form': form,
        'groups': groups,
        'system_settings': {'system_name': 'نظام الدولية'}
    }

    return render(request, 'administrator/user_create.html', context)

@login_required
def edit_permissions_view(request, user_id):
    """عرض وتحرير صلاحيات المستخدم"""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # تحديث دور المستخدم
        user.Role = request.POST.get('role', user.Role)

        # تحديث حالة is_staff
        user.is_staff = 'is_staff' in request.POST

        # تحديث المجموعات
        selected_groups = request.POST.getlist('groups')
        user.groups.set(selected_groups)

        user.save()
        messages.success(request, 'تم تحديث صلاحيات المستخدم بنجاح!')
        return redirect('accounts:dashboard')

    # الحصول على جميع المجموعات لعرضها في النموذج
    from django.contrib.auth.models import Group
    all_groups = Group.objects.all()

    context = {
        'selected_user': user,
        'all_groups': all_groups,
        'user_groups': user.groups.all()
    }

    return render(request, 'administrator/edit_permissions.html', context)

@login_required
def user_profile_view(request):
    """عرض وتحديث ملف المستخدم"""
    user = request.user

    if request.method == 'POST':
        # تحديث معلومات المستخدم
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)

        # تحديث كلمة المرور إذا تم إدخالها
        password = request.POST.get('password')
        if password:
            user.set_password(password)

        user.save()
        messages.success(request, 'تم تحديث ملفك الشخصي بنجاح!')
        return redirect('accounts:user_profile')

    context = {
        'user': user
    }

    return render(request, 'accounts/user_profile.html', context)

@csrf_exempt
def get_user_info(request):
    """get_user_info function"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id)
            return JsonResponse({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.Role,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
            })
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_all_users(request):
    """get_all_users function"""
    if request.method == 'GET':
        try:
            users = User.objects.all().values(
                'id', 'username', 'email', 'first_name', 'last_name', 'Role', 'is_active', 'is_staff'
            )
            return JsonResponse(list(users), safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def update_user_info(request):
    """update_user_info function"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id)

            # Update fields if they exist in the request
            for key, value in data.items():
                if hasattr(user, key) and key != 'user_id':
                    setattr(user, key, value)

            user.save()
            return JsonResponse({'success': 'User updated successfully'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def search_users(request):
    """search_users function"""
    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).values('id', 'username', 'email', 'first_name', 'last_name')
            return JsonResponse(list(users), safe=False)
        return JsonResponse([], safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def user_list_view(request):
    """user_list_view function"""
    users = User.objects.all()
    return render(request, 'administrator/user_list.html', {'users': users})

@login_required
def user_detail_view(request, user_id):
    """user_detail_view function"""
    user = get_object_or_404(User, id=user_id)
    return render(request, 'administrator/user_detail.html', {'selected_user': user})

@login_required
def user_delete_view(request, user_id):
    """user_delete_view function"""
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'تم حذف المستخدم بنجاح!')
        return redirect('accounts:user_list')
    return render(request, 'administrator/user_delete.html', {'selected_user': user})
