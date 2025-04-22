from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json

from .models import Task, TaskStep
from .forms import TaskForm, TaskStepForm
from meetings.models import Meeting

User = get_user_model()

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, "تم إنشاء المهمة بنجاح")
            return redirect('tasks:detail', pk=task.id)
    else:
        form = TaskForm()
    
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
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
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث المهمة بنجاح")
            return redirect('tasks:detail', pk=task.id)
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'edit': True})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, "تم حذف المهمة بنجاح")
        return redirect('tasks:list')
    
    # For GET requests, just redirect to detail page
    return redirect('tasks:detail', pk=pk)

@login_required
def delete_step(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
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
        if form.is_valid():
            task = form.save(commit=False)
            task.meeting = meeting
            task.created_by = request.user
            task.save()
            messages.success(request, "تم إنشاء المهمة بنجاح")
            return redirect('meetings:detail', pk=meeting_id)
    else:
        form = TaskForm(initial={'meeting': meeting})
    
    return render(request, 'tasks/task_form.html', {'form': form, 'meeting': meeting})


def dashboard_stats(request):
    stats = {
        'meeting_count': Meeting.objects.count(),
        'task_count': Task.objects.count(),
        'completed_task_count': Task.objects.filter(status='completed').count(),
        'user_count': User.objects.count()
    }
    return JsonResponse(stats)
