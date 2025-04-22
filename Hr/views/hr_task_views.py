from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from Hr.models.hr_task_models import HrTask
from Hr.forms.hr_task_forms import HrTaskForm

@login_required
def hr_task_list(request):
    """عرض قائمة مهام قسم الموارد البشرية"""
    # Filter tasks based on query parameters
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    task_type = request.GET.get('task_type')
    assigned_to = request.GET.get('assigned_to')
    
    tasks = HrTask.objects.all()
    
    if status:
        tasks = tasks.filter(status=status)
    
    if priority:
        tasks = tasks.filter(priority=priority)
    
    if task_type:
        tasks = tasks.filter(task_type=task_type)
    
    if assigned_to:
        tasks = tasks.filter(assigned_to_id=assigned_to)
    
    # Default ordering
    tasks = tasks.order_by('-due_date', 'priority')
    
    # Stats
    pending_tasks = HrTask.objects.filter(status='pending').count()
    in_progress_tasks = HrTask.objects.filter(status='in_progress').count()
    completed_tasks = HrTask.objects.filter(status='completed').count()
    overdue_tasks = HrTask.objects.filter(due_date__lt=timezone.now().date(), status__in=['pending', 'in_progress']).count()
    
    # Get tasks that need reminders
    today = timezone.now().date()
    reminder_tasks = HrTask.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__gte=today
    ).exclude(status='completed')
    
    reminder_tasks_list = []
    for task in reminder_tasks:
        days_until_due = (task.due_date - today).days
        if days_until_due <= task.reminder_days:
            reminder_tasks_list.append({
                'task': task,
                'days_left': days_until_due
            })
    
    context = {
        'tasks': tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'reminder_tasks': reminder_tasks_list,
        'title': 'مهام قسم الموارد البشرية'
    }
    
    return render(request, 'Hr/hr_tasks/list.html', context)

@login_required
def hr_task_create(request):
    """إنشاء مهمة جديدة لقسم الموارد البشرية"""
    if request.method == 'POST':
        form = HrTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, 'تم إنشاء المهمة بنجاح')
            return redirect('Hr:hr_tasks:list')
    else:
        form = HrTaskForm()
    
    context = {
        'form': form,
        'title': 'إنشاء مهمة جديدة'
    }
    
    return render(request, 'Hr/hr_tasks/create.html', context)

@login_required
def hr_task_detail(request, pk):
    """عرض تفاصيل مهمة"""
    task = get_object_or_404(HrTask, pk=pk)
    
    # Calculate days left until due
    today = timezone.now().date()
    days_left = (task.due_date - today).days if task.due_date >= today else 0
    
    # Check if task is overdue
    is_overdue = task.due_date < today and task.status != 'completed'
    
    context = {
        'task': task,
        'days_left': days_left,
        'is_overdue': is_overdue,
        'title': f'تفاصيل المهمة: {task.title}'
    }
    
    return render(request, 'Hr/hr_tasks/detail.html', context)

@login_required
def hr_task_edit(request, pk):
    """تعديل مهمة"""
    task = get_object_or_404(HrTask, pk=pk)
    
    if request.method == 'POST':
        form = HrTaskForm(request.POST, instance=task)
        if form.is_valid():
            # Check if status changed to completed
            if form.cleaned_data['status'] == 'completed' and task.status != 'completed':
                task = form.save(commit=False)
                task.completion_date = timezone.now().date()
                task.save()
            else:
                form.save()
            
            messages.success(request, 'تم تعديل المهمة بنجاح')
            return redirect('Hr:hr_tasks:detail', pk=task.pk)
    else:
        form = HrTaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'title': f'تعديل المهمة: {task.title}'
    }
    
    return render(request, 'Hr/hr_tasks/edit.html', context)

@login_required
def hr_task_delete(request, pk):
    """حذف مهمة"""
    task = get_object_or_404(HrTask, pk=pk)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'تم حذف المهمة بنجاح')
        return redirect('Hr:hr_tasks:list')
    
    context = {
        'task': task,
        'title': f'حذف المهمة: {task.title}'
    }
    
    return render(request, 'Hr/hr_tasks/delete.html', context)
