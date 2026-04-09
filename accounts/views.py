from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.urls import reverse
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

# استيراد وظائف إنشاء التنبيهات
try:
    from notifications.utils import create_system_notification
except ImportError:
    create_system_notification = None

User = get_user_model()

@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    """
    Handles user login requests.
    معالجة طلبات تسجيل دخول المستخدم.
    """
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
    """
    Handles user logout requests.
    معالجة طلبات تسجيل خروج المستخدم.
    """
    logout(request)
    return redirect('accounts:login')

def access_denied(request):
    """
    Displays the access denied page.
    عرض صفحة رفض الوصول.
    """
    return render(request, 'accounts/access_denied.html', {'title': 'رفض الوصول'})

def csrf_failure(request, reason=""):
    """
    Custom view for CSRF failures.
    عرض مخصص لفشل التحقق من CSRF.
    """
    context = {
        'title': 'خطأ في التحقق من CSRF',
        'reason': reason,
        'form': CustomUserLoginForm()
    }
    return render(request, 'accounts/login.html', context)

@login_required
def dashboard_view(request):
    """
    Displays the main administrative dashboard.
    عرض لوحة التحكم الإدارية الرئيسية.
    """
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
    """
    Displays the user home dashboard with system-wide statistics.
    عرض لوحة تحكم المستخدم مع إحصائيات النظام.
    """
    # Initialize counts
    meetings_count = 0
    tasks_count = 0
    completed_tasks_count = 0
    recent_meetings = []
    recent_tasks = []
    user_tasks = []

    # Attempt to get real data from other apps
    try:
        from apps.projects.meetings.models import Meeting
        meetings_count = Meeting.objects.count()
        recent_meetings = Meeting.objects.order_by('-date')[:5]
    except (ImportError, Exception):
        logger.debug("Meeting models not available for home_view")

    try:
        from apps.projects.tasks.models import Task
        tasks_count = Task.objects.count()
        completed_tasks_count = Task.objects.filter(status='completed').count()
        recent_tasks = Task.objects.order_by('-start_date')[:5]
        user_tasks = Task.objects.filter(assigned_to=request.user).order_by('status', '-start_date')
    except (ImportError, Exception):
        logger.debug("Task models not available for home_view")

    users_count = User.objects.count()
    is_admin = request.user.Role == 'admin'

    # Get departments and modules from administrator app
    user_departments = []
    all_departments = []
    department_modules = {}
    try:
        from administrator.models import Department, Module

        departments = Department.objects.filter(is_active=True).order_by('order')
        if is_admin:
            all_departments = departments

        for dept in departments:
            if not hasattr(dept, 'url_name'):
                dept.url_name = dept.name.lower().replace(' ', '-')

            dept_modules = []
            # Check permissions for department and its modules
            if (dept.require_admin and is_admin) or not dept.require_admin:
                # Group permission check if needed
                if not dept.require_admin and dept.groups.exists() and not dept.groups.filter(id__in=request.user.groups.all()).exists():
                    continue

                user_departments.append(dept)
                modules = Module.objects.filter(department=dept, is_active=True).order_by('order')
                for module in modules:
                    if module.require_admin and not is_admin:
                        continue
                    if module.groups.exists() and not module.groups.filter(id__in=request.user.groups.all()).exists():
                        continue
                    dept_modules.append(module)
            
            department_modules[dept.url_name] = dept_modules

    except Exception as e:
        logger.error(f"Error loading departments and modules: {str(e)}")

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
    """
    Handles new user creation.
    معالجة إنشاء مستخدم جديد.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if 'groups' in request.POST:
                groups = request.POST.getlist('groups')
                user.groups.set(groups)
            messages.success(request, 'تم إنشاء المستخدم بنجاح!')
            return redirect('accounts:dashboard')
    else:
        form = CustomUserCreationForm()

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
    """
    Handles user permission and role editing.
    معالجة تحرير أذونات وأدوار المستخدم.
    """
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.Role = request.POST.get('role', user.Role)
        user.is_staff = 'is_staff' in request.POST
        selected_groups = request.POST.getlist('groups')
        user.groups.set(selected_groups)
        user.save()
        messages.success(request, 'تم تحديث صلاحيات المستخدم بنجاح!')
        return redirect('accounts:dashboard')

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
    """
    Handles user profile viewing and updates.
    معالجة عرض وتحديث ملف تعريف المستخدم.
    """
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        user.save()
        messages.success(request, 'تم تحديث ملفك الشخصي بنجاح!')
        return redirect('accounts:user_profile')

    return render(request, 'accounts/user_profile.html', {'user': user})

@csrf_exempt
def get_user_info(request):
    """API endpoint to get single user info."""
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
    """API endpoint to get all users."""
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
    """API endpoint to update user info."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id)
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
    """API endpoint to search users."""
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
    """Displays list of all users."""
    users = User.objects.all()
    return render(request, 'administrator/user_list.html', {'users': users})

@login_required
def user_detail_view(request, user_id):
    """Displays details of a specific user."""
    user = get_object_or_404(User, id=user_id)
    return render(request, 'administrator/user_detail.html', {'selected_user': user})

@login_required
def user_delete_view(request, user_id):
    """Handles user deletion."""
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'تم حذف المستخدم بنجاح!')
        return redirect('accounts:user_list')
    return render(request, 'administrator/user_delete.html', {'selected_user': user})

@login_required
def global_search_api(request):
    """Placeholder for global search API."""
    return JsonResponse({'results': []})
