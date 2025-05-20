from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Task, TaskStep
from .forms import TaskForm, TaskStepForm
from meetings.models import Meeting
from tasks.decorators import tasks_module_permission_required

User = get_user_model()

@login_required
@tasks_module_permission_required('dashboard', 'view')
def dashboard(request):
    """عرض لوحة تحكم المهام"""
    # إحصائيات المهام
    total_tasks = Task.objects.count()

    # المهام المكتملة
    completed_tasks = Task.objects.filter(status='completed').count()

    # المهام قيد التنفيذ
    in_progress_tasks = Task.objects.filter(status='in_progress').count()

    # المهام المتأخرة
    today = timezone.now().date()
    overdue_tasks = Task.objects.filter(
        end_date__lt=today,
        status__in=['pending', 'in_progress']
    ).count()

    # مهامي
    my_tasks = Task.objects.filter(
        assigned_to=request.user
    ).order_by('-start_date')[:5]

    # المهام المتأخرة (للعرض)
    overdue_tasks_list = Task.objects.filter(
        end_date__lt=today,
        status__in=['pending', 'in_progress']
    ).order_by('end_date')[:5]

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'overdue_tasks': overdue_tasks,
        'my_tasks': my_tasks,
        'overdue_tasks_list': overdue_tasks_list,
    }

    return render(request, 'tasks/dashboard.html', context)

@login_required
@tasks_module_permission_required('tasks', 'add')
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)

        # If user is not a superuser, set assigned_to to the current user
        if not request.user.is_superuser and 'assigned_to' in request.POST:
            # Create a mutable copy of POST data
            post_data = request.POST.copy()
            post_data['assigned_to'] = request.user.id
            form = TaskForm(post_data)

        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user

            # If user is not a superuser, ensure they can only assign tasks to themselves
            if not request.user.is_superuser:
                task.assigned_to = request.user

            task.save()
            messages.success(request, "تم إنشاء المهمة بنجاح")
            return redirect('tasks:detail', pk=task.id)
    else:
        # For new tasks, default assigned_to to the current user
        form = TaskForm(initial={'assigned_to': request.user})

    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
@tasks_module_permission_required('tasks', 'view')
def task_list(request):
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    # Base query
    tasks = Task.objects.filter(assigned_to=request.user)

    # Apply filters
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if search_query:
        tasks = tasks.filter(description__icontains=search_query)

    # Get task counts for statistics
    total_count = Task.objects.filter(assigned_to=request.user).count()
    in_progress_count = Task.objects.filter(assigned_to=request.user, status='in_progress').count()
    completed_count = Task.objects.filter(assigned_to=request.user, status='completed').count()
    overdue_count = 0  # In a real app, this would check dates

    context = {
        'tasks': tasks,
        'total_count': total_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'overdue_count': overdue_count,
    }

    return render(request, 'tasks/task_list.html', context)

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Get related tasks (same meeting or assigned by same person)
    if task.meeting:
        related_tasks = Task.objects.filter(meeting=task.meeting).exclude(id=task.id)[:5]
    else:
        related_tasks = Task.objects.filter(created_by=task.created_by).exclude(id=task.id)[:5]

    if request.method == 'POST':
        form = TaskStepForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            step.task = task
            step.save()
            messages.success(request, "تم إضافة الخطوة بنجاح")
            return redirect('tasks:detail', pk=pk)
    else:
        form = TaskStepForm()

    context = {
        'task': task,
        'form': form,
        'related_tasks': related_tasks
    }

    return render(request, 'tasks/task_detail.html', context)

@login_required
def update_task_status(request, pk):
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)

        # Check if user is allowed to update this task's status
        # Only superusers or the assigned user can update the task status
        if not (request.user.is_superuser or request.user == task.assigned_to):
            return JsonResponse({
                'success': False,
                'error': 'ليس لديك صلاحية لتحديث حالة هذه المهمة'
            })

        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            if new_status and hasattr(task, 'status'):
                task.status = new_status
                task.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Check if user is allowed to edit this task
    # Only superusers or the assigned user can edit the task
    if not (request.user.is_superuser or request.user == task.assigned_to):
        messages.error(request, "ليس لديك صلاحية لتعديل هذه المهمة")
        return redirect('tasks:detail', pk=task.id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)

        # If user is not a superuser, ensure they can't change the assigned_to field
        if not request.user.is_superuser and 'assigned_to' in request.POST:
            # Get the original assigned_to value
            original_assigned_to = task.assigned_to

            # Check if they're trying to change it
            if str(request.POST.get('assigned_to')) != str(original_assigned_to.id):
                messages.error(request, "ليس لديك صلاحية لتغيير المكلف بالمهمة")
                return redirect('tasks:edit', pk=task.id)

        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث المهمة بنجاح")
            return redirect('tasks:detail', pk=task.id)
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'edit': True,
        'task': task
    })

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Check if user is allowed to delete this task
    # Only superusers can delete tasks
    if not request.user.is_superuser:
        messages.error(request, "ليس لديك صلاحية لحذف هذه المهمة")
        return redirect('tasks:detail', pk=task.id)

    if request.method == 'POST':
        task.delete()
        messages.success(request, "تم حذف المهمة بنجاح")
        return redirect('tasks:list')

    # For GET requests, just redirect to detail page
    return redirect('tasks:detail', pk=pk)

@login_required
def delete_step(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Check if user is allowed to delete steps for this task
    # Only superusers or the assigned user can delete steps
    if not (request.user.is_superuser or request.user == task.assigned_to):
        messages.error(request, "ليس لديك صلاحية لحذف خطوات هذه المهمة")
        return redirect('tasks:detail', pk=task.id)

    if request.method == 'POST':
        step_id = request.POST.get('step_id')
        if step_id:
            step = get_object_or_404(TaskStep, id=step_id, task=task)
            step.delete()
            messages.success(request, "تم حذف الخطوة بنجاح")

    return redirect('tasks:detail', pk=pk)

@login_required
def create_from_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)

    if request.method == 'POST':
        form = TaskForm(request.POST)

        # If user is not a superuser, set assigned_to to the current user
        if not request.user.is_superuser and 'assigned_to' in request.POST:
            # Create a mutable copy of POST data
            post_data = request.POST.copy()
            post_data['assigned_to'] = request.user.id
            form = TaskForm(post_data)

        if form.is_valid():
            task = form.save(commit=False)
            task.meeting = meeting
            task.created_by = request.user

            # If user is not a superuser, ensure they can only assign tasks to themselves
            if not request.user.is_superuser:
                task.assigned_to = request.user

            task.save()
            messages.success(request, "تم إنشاء المهمة بنجاح")
            return redirect('meetings:detail', pk=meeting_id)
    else:
        # For new tasks, default assigned_to to the current user
        form = TaskForm(initial={'meeting': meeting, 'assigned_to': request.user})

    return render(request, 'tasks/task_form.html', {'form': form, 'meeting': meeting})


@login_required
def dashboard_stats(request):
    # Get stats for the current user if not a superuser
    if not request.user.is_superuser:
        stats = {
            'meeting_count': Meeting.objects.filter(attendees__user=request.user).count(),
            'task_count': Task.objects.filter(assigned_to=request.user).count(),
            'completed_task_count': Task.objects.filter(assigned_to=request.user, status='completed').count(),
            'user_count': User.objects.count()
        }
    else:
        # Superusers see all stats
        stats = {
            'meeting_count': Meeting.objects.count(),
            'task_count': Task.objects.count(),
            'completed_task_count': Task.objects.filter(status='completed').count(),
            'user_count': User.objects.count()
        }
    return JsonResponse(stats)

@login_required
@tasks_module_permission_required('tasks', 'view')
def my_tasks(request):
    """عرض مهامي"""
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'tasks/my_tasks.html', {'tasks': tasks})

@login_required
@tasks_module_permission_required('tasks', 'view')
def completed_tasks(request):
    """عرض المهام المكتملة"""
    tasks = Task.objects.filter(status='completed')
    return render(request, 'tasks/completed_tasks.html', {'tasks': tasks})

@login_required
@tasks_module_permission_required('reports', 'view')
def reports(request):
    """عرض تقارير المهام"""
    tasks = Task.objects.all()
    return render(request, 'tasks/reports.html', {'tasks': tasks})
