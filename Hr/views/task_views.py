from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from Hr.models.task_models import EmployeeTask
from Hr.forms.task_forms import EmployeeTaskForm

@login_required
def employee_task_list(request):
    """عرض قائمة مهام الموظفين"""
    # Filter tasks based on query parameters
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    employee_id = request.GET.get('employee')
    
    tasks = EmployeeTask.objects.all()
    
    if status:
        tasks = tasks.filter(status=status)
    
    if priority:
        tasks = tasks.filter(priority=priority)
    
    if employee_id:
        tasks = tasks.filter(employee_id=employee_id)
    
    # Default ordering
    tasks = tasks.order_by('-due_date', 'priority')
    
    # Stats
    pending_tasks = EmployeeTask.objects.filter(status='pending').count()
    in_progress_tasks = EmployeeTask.objects.filter(status='in_progress').count()
    completed_tasks = EmployeeTask.objects.filter(status='completed').count()
    overdue_tasks = EmployeeTask.objects.filter(due_date__lt=timezone.now().date(), status__in=['pending', 'in_progress']).count()
    
    context = {
        'tasks': tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'title': 'مهام الموظفين'
    }
    
    return render(request, 'Hr/tasks/list.html', context)

@login_required
def employee_task_create(request):
    """إنشاء مهمة جديدة للموظف"""
    if request.method == 'POST':
        form = EmployeeTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            messages.success(request, 'تم إنشاء المهمة بنجاح')
            return redirect('Hr:tasks:list')
    else:
        form = EmployeeTaskForm()
    
    context = {
        'form': form,
        'title': 'إنشاء مهمة جديدة'
    }
    
    return render(request, 'Hr/tasks/create.html', context)

@login_required
def employee_task_detail(request, pk):
    """عرض تفاصيل مهمة"""
    task = get_object_or_404(EmployeeTask, pk=pk)
    
    context = {
        'task': task,
        'title': f'تفاصيل المهمة: {task.title}'
    }
    
    return render(request, 'Hr/tasks/detail.html', context)

@login_required
def employee_task_edit(request, pk):
    """تعديل مهمة"""
    task = get_object_or_404(EmployeeTask, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeTaskForm(request.POST, instance=task)
        if form.is_valid():
            # Check if status changed to completed
            if form.cleaned_data['status'] == 'completed' and task.status != 'completed':
                task = form.save(commit=False)
                task.completion_date = timezone.now().date()
                task.save()
            else:
                form.save()
            
            messages.success(request, 'تم تعديل المهمة بنجاح')
            return redirect('Hr:tasks:detail', pk=task.pk)
    else:
        form = EmployeeTaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'title': f'تعديل المهمة: {task.title}'
    }
    
    return render(request, 'Hr/tasks/edit.html', context)

@login_required
def employee_task_delete(request, pk):
    """حذف مهمة"""
    task = get_object_or_404(EmployeeTask, pk=pk)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'تم حذف المهمة بنجاح')
        return redirect('Hr:tasks:list')
    
    context = {
        'task': task,
        'title': f'حذف المهمة: {task.title}'
    }
    
    return render(request, 'Hr/tasks/delete.html', context)
