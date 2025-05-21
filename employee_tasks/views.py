from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse
from datetime import datetime, timedelta

from .models import TaskCategory, EmployeeTask, TaskStep, TaskReminder
from .forms import TaskCategoryForm, EmployeeTaskForm, TaskStepForm, TaskReminderForm, TaskFilterForm
from .decorators import can_access_task, employee_tasks_module_permission_required

# Dashboard Views
@login_required
@permission_required('employee_tasks.view_employeetask', login_url='accounts:access_denied')
def dashboard(request):
    """
    عرض لوحة تحكم مهام الموظفين
    """
    user = request.user
    is_superuser = user.is_superuser

    # الإحصائيات العامة
    if is_superuser:
        # المشرف يرى جميع المهام
        total_tasks = EmployeeTask.objects.count()
        pending_tasks = EmployeeTask.objects.filter(status='pending').count()
        in_progress_tasks = EmployeeTask.objects.filter(status='in_progress').count()
        completed_tasks = EmployeeTask.objects.filter(status='completed').count()

        # المهام المتأخرة
        today = timezone.now().date()
        overdue_tasks = EmployeeTask.objects.filter(
            due_date__lt=today,
            status__in=['pending', 'in_progress']
        ).count()

        # المهام الحديثة
        recent_tasks = EmployeeTask.objects.order_by('-created_at')[:5]

        # المهام القادمة
        upcoming_tasks = EmployeeTask.objects.filter(
            due_date__gte=today,
            status__in=['pending', 'in_progress']
        ).order_by('due_date')[:5]

    else:
        # المستخدم العادي يرى المهام الخاصة به فقط
        total_tasks = EmployeeTask.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        ).count()

        pending_tasks = EmployeeTask.objects.filter(
            Q(created_by=user) | Q(assigned_to=user),
            status='pending'
        ).count()

        in_progress_tasks = EmployeeTask.objects.filter(
            Q(created_by=user) | Q(assigned_to=user),
            status='in_progress'
        ).count()

        completed_tasks = EmployeeTask.objects.filter(
            Q(created_by=user) | Q(assigned_to=user),
            status='completed'
        ).count()

        # المهام المتأخرة
        today = timezone.now().date()
        overdue_tasks = EmployeeTask.objects.filter(
            Q(created_by=user) | Q(assigned_to=user),
            due_date__lt=today,
            status__in=['pending', 'in_progress']
        ).count()

        # المهام الحديثة
        recent_tasks = EmployeeTask.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        ).order_by('-created_at')[:5]

        # المهام القادمة
        upcoming_tasks = EmployeeTask.objects.filter(
            Q(created_by=user) | Q(assigned_to=user),
            due_date__gte=today,
            status__in=['pending', 'in_progress']
        ).order_by('due_date')[:5]

    # تصنيفات المهام
    categories = TaskCategory.objects.annotate(
        task_count=Count('tasks')
    ).order_by('-task_count')[:5]

    context = {
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'recent_tasks': recent_tasks,
        'upcoming_tasks': upcoming_tasks,
        'categories': categories,
    }

    return render(request, 'employee_tasks/dashboard.html', context)

# Task List Views
@login_required
@permission_required('employee_tasks.view_employeetask', login_url='accounts:access_denied')
def task_list(request):
    """
    عرض قائمة المهام
    """
    user = request.user
    is_superuser = user.is_superuser

    # تصفية المهام
    filter_form = TaskFilterForm(request.GET)

    # البحث الأساسي
    if is_superuser:
        tasks = EmployeeTask.objects.all()
    else:
        tasks = EmployeeTask.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        )

    # تطبيق التصفية إذا تم تقديم النموذج
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        category = filter_form.cleaned_data.get('category')
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        search = filter_form.cleaned_data.get('search')

        if status:
            tasks = tasks.filter(status=status)

        if priority:
            tasks = tasks.filter(priority=priority)

        if category:
            tasks = tasks.filter(category=category)

        if start_date:
            tasks = tasks.filter(start_date__gte=start_date)

        if end_date:
            tasks = tasks.filter(due_date__lte=end_date)

        if search:
            tasks = tasks.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

    # ترتيب المهام
    tasks = tasks.order_by('-created_at')

    context = {
        'tasks': tasks,
        'filter_form': filter_form,
    }

    return render(request, 'employee_tasks/task_list.html', context)

@login_required
@permission_required('employee_tasks.view_employeetask', login_url='accounts:access_denied')
def my_tasks(request):
    """
    عرض مهام المستخدم الحالي
    """
    user = request.user

    # تصفية المهام
    filter_form = TaskFilterForm(request.GET)

    # البحث الأساسي (المهام التي أنشأها المستخدم فقط)
    tasks = EmployeeTask.objects.filter(created_by=user)

    # تطبيق التصفية إذا تم تقديم النموذج
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        category = filter_form.cleaned_data.get('category')
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        search = filter_form.cleaned_data.get('search')

        if status:
            tasks = tasks.filter(status=status)

        if priority:
            tasks = tasks.filter(priority=priority)

        if category:
            tasks = tasks.filter(category=category)

        if start_date:
            tasks = tasks.filter(start_date__gte=start_date)

        if end_date:
            tasks = tasks.filter(due_date__lte=end_date)

        if search:
            tasks = tasks.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

    # ترتيب المهام
    tasks = tasks.order_by('-created_at')

    context = {
        'tasks': tasks,
        'filter_form': filter_form,
        'is_my_tasks': True,
    }

    return render(request, 'employee_tasks/task_list.html', context)

@login_required
@permission_required('employee_tasks.view_employeetask', login_url='accounts:access_denied')
def assigned_tasks(request):
    """
    عرض المهام المسندة إلى المستخدم الحالي
    """
    user = request.user

    # تصفية المهام
    filter_form = TaskFilterForm(request.GET)

    # البحث الأساسي (المهام المسندة إلى المستخدم فقط)
    tasks = EmployeeTask.objects.filter(assigned_to=user)

    # تطبيق التصفية إذا تم تقديم النموذج
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        category = filter_form.cleaned_data.get('category')
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        search = filter_form.cleaned_data.get('search')

        if status:
            tasks = tasks.filter(status=status)

        if priority:
            tasks = tasks.filter(priority=priority)

        if category:
            tasks = tasks.filter(category=category)

        if start_date:
            tasks = tasks.filter(start_date__gte=start_date)

        if end_date:
            tasks = tasks.filter(due_date__lte=end_date)

        if search:
            tasks = tasks.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

    # ترتيب المهام
    tasks = tasks.order_by('-created_at')

    context = {
        'tasks': tasks,
        'filter_form': filter_form,
        'is_assigned_tasks': True,
    }

    return render(request, 'employee_tasks/task_list.html', context)

# Task Detail Views
@login_required
def task_detail(request, pk):
    """
    عرض تفاصيل المهمة
    """
    task = get_object_or_404(EmployeeTask, pk=pk)
    if not (request.user.is_superuser or request.user == task.created_by or request.user == task.assigned_to):
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه المهمة")
        return redirect('employee_tasks:dashboard')

    # الحصول على خطوات المهمة
    steps = task.steps.all().order_by('created_at')

    # الحصول على تذكيرات المهمة
    reminders = task.reminders.all().order_by('reminder_date')

    # نموذج إضافة خطوة جديدة
    if request.method == 'POST' and 'add_step' in request.POST:
        step_form = TaskStepForm(request.POST, user=request.user, task=task)
        if step_form.is_valid():
            step = step_form.save()
            messages.success(request, "تمت إضافة الخطوة بنجاح")
            return redirect('employee_tasks:task_detail', pk=task.pk)
    else:
        step_form = TaskStepForm(user=request.user, task=task)

    # نموذج إضافة تذكير جديد
    if request.method == 'POST' and 'add_reminder' in request.POST:
        reminder_form = TaskReminderForm(request.POST, task=task)
        if reminder_form.is_valid():
            reminder = reminder_form.save()
            messages.success(request, "تم إضافة التذكير بنجاح")
            return redirect('employee_tasks:task_detail', pk=task.pk)
    else:
        reminder_form = TaskReminderForm(task=task)

    context = {
        'task': task,
        'steps': steps,
        'reminders': reminders,
        'step_form': step_form,
        'reminder_form': reminder_form,
    }

    return render(request, 'employee_tasks/task_detail.html', context)

# Task Create/Edit Views
@login_required
@permission_required('employee_tasks.add_employeetask', login_url='accounts:access_denied')
def task_create(request):
    """
    إنشاء مهمة جديدة
    """
    if request.method == 'POST':
        form = EmployeeTaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, "تم إنشاء المهمة بنجاح")
            return redirect('employee_tasks:task_detail', pk=task.pk)
    else:
        form = EmployeeTaskForm(user=request.user)

    context = {
        'form': form,
        'is_create': True,
    }

    return render(request, 'employee_tasks/task_form.html', context)

@login_required
def task_edit(request, pk):
    """
    تعديل مهمة موجودة
    """
    task = get_object_or_404(EmployeeTask, pk=pk)
    if not (request.user.is_superuser or request.user == task.created_by):
        messages.error(request, "ليس لديك صلاحية لتعديل هذه المهمة")
        return redirect('employee_tasks:dashboard')

    if request.method == 'POST':
        form = EmployeeTaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            task = form.save()
            messages.success(request, "تم تحديث المهمة بنجاح")
            return redirect('employee_tasks:task_detail', pk=task.pk)
    else:
        form = EmployeeTaskForm(instance=task, user=request.user)

    context = {
        'form': form,
        'task': task,
        'is_edit': True,
    }

    return render(request, 'employee_tasks/task_form.html', context)

@login_required
def task_delete(request, pk):
    """
    حذف مهمة
    """
    task = get_object_or_404(EmployeeTask, pk=pk)
    if not (request.user.is_superuser or request.user == task.created_by):
        messages.error(request, "ليس لديك صلاحية لحذف هذه المهمة")
        return redirect('employee_tasks:dashboard')

    if request.method == 'POST':
        task.delete()
        messages.success(request, "تم حذف المهمة بنجاح")
        return redirect('employee_tasks:task_list')

    context = {
        'task': task,
    }

    return render(request, 'employee_tasks/task_confirm_delete.html', context)

# Task Step Views
@login_required
@can_access_task
def step_edit(request, pk, step_id, task=None):
    """
    تعديل خطوة مهمة
    """
    # المهمة تم تمريرها من المزخرف can_access_task
    task = task

    # الحصول على الخطوة
    step = get_object_or_404(TaskStep, pk=step_id, task=task)

    if request.method == 'POST':
        form = TaskStepForm(request.POST, instance=step, user=request.user, task=task)
        if form.is_valid():
            step = form.save()
            messages.success(request, "تم تحديث الخطوة بنجاح")
            return redirect('employee_tasks:task_detail', pk=task.pk)
    else:
        form = TaskStepForm(instance=step, user=request.user, task=task)

    context = {
        'form': form,
        'task': task,
        'step': step,
    }

    return render(request, 'employee_tasks/step_form.html', context)

@login_required
@can_access_task
def step_delete(request, pk, step_id, task=None):
    """
    حذف خطوة مهمة
    """
    # المهمة تم تمريرها من المزخرف can_access_task
    task = task

    # الحصول على الخطوة
    step = get_object_or_404(TaskStep, pk=step_id, task=task)

    if request.method == 'POST':
        step.delete()
        messages.success(request, "تم حذف الخطوة بنجاح")
        return redirect('employee_tasks:task_detail', pk=task.pk)

    context = {
        'task': task,
        'step': step,
    }

    return render(request, 'employee_tasks/step_confirm_delete.html', context)

@login_required
@can_access_task
def toggle_step_status(request, pk, step_id, task=None):
    """
    تبديل حالة خطوة مهمة (مكتملة/غير مكتملة)
    """
    # المهمة تم تمريرها من المزخرف can_access_task
    task = task

    # الحصول على الخطوة
    step = get_object_or_404(TaskStep, pk=step_id, task=task)

    # تبديل الحالة
    step.completed = not step.completed
    step.save()

    # إذا كان طلب AJAX، أعد استجابة JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'completed': step.completed,
            'completion_date': step.completion_date.strftime('%Y-%m-%d') if step.completion_date else None,
        })

    # وإلا، أعد توجيه إلى صفحة تفاصيل المهمة
    messages.success(request, "تم تحديث حالة الخطوة بنجاح")
    return redirect('employee_tasks:task_detail', pk=task.pk)

# Task Reminder Views
@login_required
@can_access_task
def reminder_delete(request, pk, reminder_id, task=None):
    """
    حذف تذكير مهمة
    """
    # المهمة تم تمريرها من المزخرف can_access_task
    task = task

    # الحصول على التذكير
    reminder = get_object_or_404(TaskReminder, pk=reminder_id, task=task)

    if request.method == 'POST':
        reminder.delete()
        messages.success(request, "تم حذف التذكير بنجاح")
        return redirect('employee_tasks:task_detail', pk=task.pk)

    context = {
        'task': task,
        'reminder': reminder,
    }

    return render(request, 'employee_tasks/reminder_confirm_delete.html', context)

# Task Category Views
@login_required
@employee_tasks_module_permission_required('categories', 'view')
def category_list(request):
    """
    عرض قائمة تصنيفات المهام
    """
    categories = TaskCategory.objects.all().order_by('name')

    context = {
        'categories': categories,
    }

    return render(request, 'employee_tasks/category_list.html', context)

@login_required
@employee_tasks_module_permission_required('categories', 'add')
def category_create(request):
    """
    إنشاء تصنيف مهام جديد
    """
    if request.method == 'POST':
        form = TaskCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, "تم إنشاء التصنيف بنجاح")
            return redirect('employee_tasks:category_list')
    else:
        form = TaskCategoryForm()

    context = {
        'form': form,
        'is_create': True,
    }

    return render(request, 'employee_tasks/category_form.html', context)

@login_required
@employee_tasks_module_permission_required('categories', 'change')
def category_edit(request, pk):
    """
    تعديل تصنيف مهام موجود
    """
    category = get_object_or_404(TaskCategory, pk=pk)

    if request.method == 'POST':
        form = TaskCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, "تم تحديث التصنيف بنجاح")
            return redirect('employee_tasks:category_list')
    else:
        form = TaskCategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
        'is_edit': True,
    }

    return render(request, 'employee_tasks/category_form.html', context)

@login_required
@employee_tasks_module_permission_required('categories', 'delete')
def category_delete(request, pk):
    """
    حذف تصنيف مهام
    """
    category = get_object_or_404(TaskCategory, pk=pk)

    if request.method == 'POST':
        category.delete()
        messages.success(request, "تم حذف التصنيف بنجاح")
        return redirect('employee_tasks:category_list')

    context = {
        'category': category,
    }

    return render(request, 'employee_tasks/category_confirm_delete.html', context)

# Calendar View
@login_required
@permission_required('employee_tasks.view_employeetask', login_url='accounts:access_denied')
def calendar(request):
    """
    عرض تقويم المهام
    """
    user = request.user
    is_superuser = user.is_superuser

    # الحصول على المهام
    if is_superuser:
        tasks = EmployeeTask.objects.all()
    else:
        tasks = EmployeeTask.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        )

    context = {
        'tasks': tasks,
    }

    return render(request, 'employee_tasks/calendar.html', context)

# Analytics View
@login_required
@permission_required('employee_tasks.view_employeetask', login_url='accounts:access_denied')
def analytics(request):
    """
    عرض تحليلات المهام
    """
    user = request.user
    is_superuser = user.is_superuser

    # الحصول على المهام
    if is_superuser:
        tasks = EmployeeTask.objects.all()
    else:
        tasks = EmployeeTask.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        )

    # إحصائيات حسب الحالة
    status_stats = {
        'pending': tasks.filter(status='pending').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'completed': tasks.filter(status='completed').count(),
        'cancelled': tasks.filter(status='cancelled').count(),
        'deferred': tasks.filter(status='deferred').count(),
    }

    # إحصائيات حسب الأولوية
    priority_stats = {
        'low': tasks.filter(priority='low').count(),
        'medium': tasks.filter(priority='medium').count(),
        'high': tasks.filter(priority='high').count(),
        'urgent': tasks.filter(priority='urgent').count(),
    }

    # إحصائيات حسب التصنيف
    categories = TaskCategory.objects.all()
    category_stats = {}
    for category in categories:
        category_stats[category.name] = tasks.filter(category=category).count()

    # إحصائيات حسب الشهر
    today = timezone.now().date()
    six_months_ago = today - timedelta(days=180)
    monthly_tasks = {}

    for i in range(6):
        month_date = today - timedelta(days=30 * i)
        month_name = month_date.strftime('%B %Y')
        month_start = month_date.replace(day=1)
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)

        monthly_tasks[month_name] = {
            'created': tasks.filter(created_at__date__gte=month_start, created_at__date__lte=month_end).count(),
            'completed': tasks.filter(completion_date__gte=month_start, completion_date__lte=month_end).count(),
        }

    context = {
        'status_stats': status_stats,
        'priority_stats': priority_stats,
        'category_stats': category_stats,
        'monthly_tasks': monthly_tasks,
    }

    return render(request, 'employee_tasks/analytics.html', context)

# API Views for AJAX
@login_required
def update_task_status(request, pk):
    """
    تحديث حالة المهمة عبر AJAX
    """
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        task = EmployeeTask.objects.get(pk=pk)

        # التحقق من الصلاحيات
        user = request.user
        if not (user.is_superuser or user == task.created_by or user == task.assigned_to):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        # تحديث الحالة
        status = request.POST.get('status')
        if status and status in dict(EmployeeTask.STATUS_CHOICES).keys():
            task.status = status
            task.save()

            return JsonResponse({
                'success': True,
                'status': status,
                'status_display': dict(EmployeeTask.STATUS_CHOICES)[status],
                'completion_date': task.completion_date.strftime('%Y-%m-%d') if task.completion_date else None,
            })
        else:
            return JsonResponse({'error': 'Invalid status'}, status=400)

    except EmployeeTask.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

@login_required
def update_task_progress(request, pk):
    """
    تحديث نسبة إنجاز المهمة عبر AJAX
    """
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        task = EmployeeTask.objects.get(pk=pk)

        # التحقق من الصلاحيات
        user = request.user
        if not (user.is_superuser or user == task.created_by or user == task.assigned_to):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        # تحديث نسبة الإنجاز
        progress = request.POST.get('progress')
        try:
            progress = int(progress)
            if 0 <= progress <= 100:
                task.progress = progress

                # إذا كانت نسبة الإنجاز 100%، قم بتعيين الحالة إلى مكتملة
                if progress == 100 and task.status != 'completed':
                    task.status = 'completed'

                task.save()

                return JsonResponse({
                    'success': True,
                    'progress': progress,
                    'status': task.status,
                    'status_display': dict(EmployeeTask.STATUS_CHOICES)[task.status],
                    'completion_date': task.completion_date.strftime('%Y-%m-%d') if task.completion_date else None,
                })
            else:
                return JsonResponse({'error': 'Progress must be between 0 and 100'}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid progress value'}, status=400)

    except EmployeeTask.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)
