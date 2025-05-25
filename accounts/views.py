from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from meetings.models import Meeting
from tasks.models import Task
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

# استيراد وظائف إنشاء التنبيهات
try:
    from notifications.utils import create_system_notification
except ImportError:
    create_system_notification = None

User = get_user_model()

@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    # Add debugging information
    print("Starting login_view function")

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

            return redirect('accounts:home')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
    else:
        form = CustomUserLoginForm()

    # Add more debugging information
    print("Rendering login template")

    # Simplify the context to rule out any issues
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
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
    # Get real-time stats for dashboard
    meetings_count = Meeting.objects.count()
    tasks_count = Task.objects.count()
    completed_tasks_count = Task.objects.filter(status='completed').count()
    users_count = User.objects.count()

    # Get recent meetings
    recent_meetings = Meeting.objects.order_by('-date')[:5]

    # Get recent tasks
    recent_tasks = Task.objects.order_by('-start_date')[:5]

    # Get user's tasks
    user_tasks = Task.objects.filter(assigned_to=request.user).order_by('status', '-start_date')

    # Check if user is admin
    is_admin = request.user.Role == 'admin'

    # Get departments from administrator app if it's installed
    user_departments = []
    all_departments = []
    try:
        from administrator.models import Department

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
                    print(f"Found HR department with url_name: {dept.url_name}")
            else:
                # If url_name doesn't exist, set a default based on department name
                dept.url_name = dept.name.lower().replace(' ', '-')
                print(f"Set url_name for {dept.name}: {dept.url_name}")

        # Filter departments based on user permissions
        for dept in departments:
            # If department requires admin and user is admin, add it
            if dept.require_admin and is_admin:
                user_departments.append(dept)
            # If department doesn't require admin, check group permissions
            elif not dept.require_admin:
                # If no groups specified, everyone can access
                if not dept.groups.exists():
                    user_departments.append(dept)
                # Otherwise, check if user is in any of the allowed groups
                else:
                    # Check if any of the user's groups are in the department's allowed groups
                    if dept.groups.filter(id__in=request.user.groups.all()).exists():
                        user_departments.append(dept)
    except Exception as e:
        # If administrator app is not installed or any error occurs
        print(f"Error loading departments: {str(e)}")

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
        'is_admin': is_admin
    }

    return render(request, 'home_dashboard.html', context)

@login_required
def create_user_view(request):
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
        # تحديث بيانات المستخدم
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.Role = request.POST.get('Role', user.Role)
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'

        # تحديث المجموعات
        if 'groups' in request.POST:
            groups = request.POST.getlist('groups')
            user.groups.set(groups)

        user.save()
        messages.success(request, 'تم تحديث بيانات المستخدم بنجاح!')
        return redirect('accounts:dashboard')

    # استخدام نظام المجموعات الخاص بـ Django
    from django.contrib.auth.models import Group
    groups = Group.objects.all()

    context = {
        'user_to_edit': user,
        'groups': groups,
        'system_settings': {'system_name': 'نظام الدولية'}
    }

    return render(request, 'accounts/edit_permissions.html', context)


