from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from Hr.models.task_models import EmployeeTask, TaskStep
from Hr.forms.task_forms import EmployeeTaskForm, TaskStepForm

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
    steps = TaskStep.objects.filter(task_id=pk).order_by('-created_at')

    # إضافة خطوة جديدة
    if request.method == 'POST':
        form = TaskStepForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            step.task_id = task.pk
            step.created_by = request.user
            if step.completed:
                step.completion_date = timezone.now().date()
            step.save()

            # تحديث نسبة الإنجاز للمهمة
            completed_steps = TaskStep.objects.filter(task_id=pk, completed=True).count()
            total_steps = TaskStep.objects.filter(task_id=pk).count()
            if total_steps > 0:
                task.progress = int((completed_steps / total_steps) * 100)
                task.save()

            messages.success(request, 'تم إضافة الخطوة بنجاح')
            return redirect('Hr:tasks:detail', pk=task.pk)
    else:
        form = TaskStepForm()

    context = {
        'task': task,
        'steps': steps,
        'form': form,
        'now': timezone.now(),
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


@login_required
def task_step_toggle(request, task_pk, step_pk):
    """تغيير حالة خطوة المهمة (مكتملة/غير مكتملة)"""
    step = get_object_or_404(TaskStep, pk=step_pk, task_id=task_pk)

    # تغيير حالة الخطوة
    step.completed = not step.completed
    if step.completed:
        step.completion_date = timezone.now().date()
    else:
        step.completion_date = None
    step.save()

    # تحديث نسبة الإنجاز للمهمة
    task = get_object_or_404(EmployeeTask, pk=task_pk)
    completed_steps = TaskStep.objects.filter(task_id=task_pk, completed=True).count()
    total_steps = TaskStep.objects.filter(task_id=task_pk).count()
    if total_steps > 0:
        task.progress = int((completed_steps / total_steps) * 100)
        task.save()

    # إذا كان الطلب من AJAX، أرجع استجابة JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'completed': step.completed,
            'task_progress': task.progress
        })

    # وإلا أعد توجيه المستخدم إلى صفحة تفاصيل المهمة
    messages.success(request, 'تم تحديث حالة الخطوة بنجاح')
    return redirect('Hr:tasks:detail', pk=task_pk)


@login_required
def task_step_delete(request, task_pk, step_pk):
    """حذف خطوة المهمة"""
    step = get_object_or_404(TaskStep, pk=step_pk, task_id=task_pk)
    task = get_object_or_404(EmployeeTask, pk=task_pk)

    step.delete()

    # تحديث نسبة الإنجاز للمهمة
    completed_steps = TaskStep.objects.filter(task_id=task_pk, completed=True).count()
    total_steps = TaskStep.objects.filter(task_id=task_pk).count()
    if total_steps > 0:
        task.progress = int((completed_steps / total_steps) * 100)
    else:
        task.progress = 0
    task.save()

    # إذا كان الطلب من AJAX، أرجع استجابة JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'task_progress': task.progress
        })

    # وإلا أعد توجيه المستخدم إلى صفحة تفاصيل المهمة
    messages.success(request, 'تم حذف الخطوة بنجاح')
    return redirect('Hr:tasks:detail', pk=task_pk)
