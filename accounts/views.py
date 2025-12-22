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
                    print(f"Found HR department with url_name: {dept.url_name}")
            else:
                # If url_name doesn't exist, set a default based on department name
                dept.url_name = dept.name.lower().replace(' ', '-')
                print(f"Set url_name for {dept.name}: {dept.url_name}")

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
                print(f"DEBUG: Stored {len(dept_modules)} modules for department '{dept.name}' with url_name '{dept.url_name}'")
            else:
                dept_url_key = dept.name.lower().replace(' ', '-')
                department_modules[dept_url_key] = dept_modules
                print(f"DEBUG: Stored {len(dept_modules)} modules for department '{dept.name}' with generated key '{dept_url_key}'")

    except Exception as e:
        # If administrator app is not installed or any error occurs
        print(f"Error loading departments and modules: {str(e)}")
        import traceback
        traceback.print_exc()

    print(f"DEBUG: Final department_modules keys: {list(department_modules.keys())}")
    for key, modules in department_modules.items():
        print(f"DEBUG: Department '{key}' has {len(modules)} modules")
        for module in modules:
            print(f"  - Module: {module.name}, URL: {module.url}")

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


# Global Search API
@login_required
@csrf_exempt
def global_search_api(request):
    """
    Global search API endpoint that searches across all modules
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        module_filter = data.get('module', '').strip()
        limit = min(int(data.get('limit', 20)), 50)  # Max 50 results

        if len(query) < 2:
            return JsonResponse({'results': []})

        results = []

        # Search in HR module
        if not module_filter or module_filter == 'hr':
            results.extend(search_hr_data(query, request.user, limit))

        # Search in Inventory module
        if not module_filter or module_filter == 'inventory':
            results.extend(search_inventory_data(query, request.user, limit))

        # Search in Tasks module
        if not module_filter or module_filter == 'tasks':
            results.extend(search_tasks_data(query, request.user, limit))

        # Search in Meetings module
        if not module_filter or module_filter == 'meetings':
            results.extend(search_meetings_data(query, request.user, limit))

        # Search in Purchase Orders module
        if not module_filter or module_filter == 'purchase_orders':
            results.extend(search_purchase_orders_data(query, request.user, limit))

        # Sort results by relevance
        results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)[:limit]

        return JsonResponse({'results': results})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def search_hr_data(query, user, limit):
    """Search in HR module data"""
    results = []

    try:
        # Import models from new apps
        from apps.hr.employees.models import Employee
        from org.models import Department

        # Search employees
        employees = Employee.objects.filter(
            Q(first_name__icontains=query) |
            Q(second_name__icontains=query) |
            Q(third_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(emp_code__icontains=query)
        ).filter(emp_status='Active')[:limit//2]

        for emp in employees:
            # Create full name
            full_name = f"{emp.first_name} {emp.second_name or ''} {emp.third_name or ''} {emp.last_name or ''}".strip()

            results.append({
                'module': 'hr',
                'type': 'employee',
                'title': full_name,
                'description': f'موظف - {emp.dept.dept_name if emp.dept else "بدون قسم"}',
                'url': f'/employees/list/#employee-{emp.emp_id}',
                'icon': 'fas fa-user',
                'meta': [
                    f'الكود: {emp.emp_code}',
                    f'القسم: {emp.dept.dept_name if emp.dept else "غير محدد"}'
                ],
                'score': calculate_relevance_score(query, full_name)
            })

        # Search departments
        departments = Department.objects.filter(
            Q(dept_name__icontains=query)
        ).filter(is_active=True)[:limit//2]

        for dept in departments:
            results.append({
                'module': 'hr',
                'type': 'department',
                'title': dept.dept_name,
                'description': f'قسم - {dept.branch.branch_name if dept.branch else "بدون فرع"}',
                'url': f'/org/#department-{dept.dept_id}',
                'icon': 'fas fa-building',
                'meta': [
                    f'المعرف: {dept.dept_id}',
                    f'الفرع: {dept.branch.branch_name if dept.branch else "غير محدد"}'
                ],
                'score': calculate_relevance_score(query, dept.dept_name)
            })

    except Exception as e:
        print(f"Error searching HR data: {e}")

    return results


def search_inventory_data(query, user, limit):
    """Search in Inventory module data"""
    results = []

    try:
        from apps.inventory.models import Product

        # Search products
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(product_id__icontains=query)
        )[:limit]

        for product in products:
            results.append({
                'module': 'inventory',
                'type': 'product',
                'title': product.name,
                'description': f'منتج - {getattr(product, "category", "بدون تصنيف")}',
                'url': f'/inventory/products/{product.product_id}/',
                'icon': 'fas fa-box',
                'meta': [
                    f'الكود: {product.product_id}',
                    f'الكمية: {getattr(product, "quantity", "غير محدد")}'
                ],
                'score': calculate_relevance_score(query, product.name)
            })

    except Exception as e:
        print(f"Error searching inventory data: {e}")

    return results


def search_tasks_data(query, user, limit):
    """Search in Tasks module data"""
    results = []

    try:
        # Search tasks accessible to user
        if user.is_superuser:
            tasks = Task.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )[:limit]
        else:
            tasks = Task.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            ).filter(
                Q(assigned_to=user) |
                Q(created_by=user)
            )[:limit]

        for task in tasks:
            results.append({
                'module': 'tasks',
                'type': 'task',
                'title': task.title,
                'description': task.description[:100] + '...' if len(task.description) > 100 else task.description,
                'url': f'/tasks/{task.id}/',
                'icon': 'fas fa-tasks',
                'meta': [
                    f'الحالة: {task.get_status_display()}',
                    f'الأولوية: {task.get_priority_display()}'
                ],
                'score': calculate_relevance_score(query, task.title)
            })

    except Exception as e:
        print(f"Error searching tasks data: {e}")

    return results


def search_meetings_data(query, user, limit):
    """Search in Meetings module data"""
    results = []

    try:
        # Search meetings
        meetings = Meeting.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )[:limit]

        for meeting in meetings:
            results.append({
                'module': 'meetings',
                'type': 'meeting',
                'title': meeting.title,
                'description': f'اجتماع - {getattr(meeting, "location", "")}',
                'url': f'/meetings/{meeting.id}/',
                'icon': 'fas fa-calendar-alt',
                'meta': [
                    f'التاريخ: {meeting.date_time.strftime("%Y-%m-%d") if hasattr(meeting, "date_time") else "غير محدد"}',
                    f'المكان: {getattr(meeting, "location", "غير محدد")}'
                ],
                'score': calculate_relevance_score(query, meeting.title)
            })

    except Exception as e:
        print(f"Error searching meetings data: {e}")

    return results


def search_purchase_orders_data(query, user, limit):
    """Search in Purchase Orders module data"""
    results = []

    try:
        from apps.procurement.purchase_orders.models import PurchaseRequest

        # Search purchase requests
        requests = PurchaseRequest.objects.filter(
            Q(description__icontains=query)
        )[:limit]

        for req in requests:
            results.append({
                'module': 'purchase_orders',
                'type': 'purchase_request',
                'title': f'طلب شراء #{req.id}',
                'description': req.description[:100] + '...' if len(req.description) > 100 else req.description,
                'url': f'/purchase/requests/{req.id}/',
                'icon': 'fas fa-shopping-cart',
                'meta': [
                    f'الحالة: {getattr(req, "status", "غير محدد")}',
                    f'التاريخ: {req.created_at.strftime("%Y-%m-%d") if hasattr(req, "created_at") else "غير محدد"}'
                ],
                'score': calculate_relevance_score(query, req.description)
            })

    except Exception as e:
        print(f"Error searching purchase orders data: {e}")

    return results


def calculate_relevance_score(query, text):
    """Calculate relevance score for search results"""
    if not query or not text:
        return 0

    query_lower = query.lower()
    text_lower = text.lower()

    # Exact match gets highest score
    if query_lower == text_lower:
        return 100

    # Starts with query gets high score
    if text_lower.startswith(query_lower):
        return 80

    # Contains query gets medium score
    if query_lower in text_lower:
        return 60

    # Word match gets lower score
    query_words = query_lower.split()
    text_words = text_lower.split()

    matches = sum(1 for word in query_words if any(word in text_word for text_word in text_words))
    if matches > 0:
        return 40 + (matches * 10)

    return 0
