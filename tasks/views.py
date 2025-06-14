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
    from meetings.models import MeetingTask

    # إحصائيات المهام (تشمل مهام الاجتماعات)
    regular_total = Task.objects.count()
    meeting_total = MeetingTask.objects.count()
    total_tasks = regular_total + meeting_total

    # المهام المكتملة
    regular_completed = Task.objects.filter(status='completed').count()
    meeting_completed = MeetingTask.objects.filter(status='completed').count()
    completed_tasks = regular_completed + meeting_completed

    # المهام قيد التنفيذ
    regular_in_progress = Task.objects.filter(status='in_progress').count()
    meeting_in_progress = MeetingTask.objects.filter(status='in_progress').count()
    in_progress_tasks = regular_in_progress + meeting_in_progress

    # المهام المتأخرة
    today = timezone.now().date()
    overdue_tasks = Task.objects.filter(
        end_date__lt=today,
        status__in=['pending', 'in_progress']
    ).count()
    # Note: MeetingTask uses end_date as DateField, so we need to handle it differently
    overdue_meeting_tasks = MeetingTask.objects.filter(
        end_date__lt=today,
        status__in=['pending', 'in_progress']
    ).count()
    overdue_tasks += overdue_meeting_tasks

    # مهامي (تشمل مهام الاجتماعات)
    my_regular_tasks = Task.objects.filter(
        assigned_to=request.user
    ).order_by('-start_date')[:3]

    my_meeting_tasks = MeetingTask.objects.filter(
        assigned_to=request.user
    ).order_by('-created_at')[:2]

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
        'my_tasks': my_regular_tasks,
        'my_meeting_tasks': my_meeting_tasks,
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
    from meetings.models import MeetingTask
    from datetime import datetime

    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    # Get regular tasks
    regular_tasks = Task.objects.filter(assigned_to=request.user)

    # Get meeting tasks assigned to the user
    meeting_tasks = MeetingTask.objects.filter(assigned_to=request.user)

    # Apply filters to regular tasks
    if status_filter:
        regular_tasks = regular_tasks.filter(status=status_filter)
        meeting_tasks = meeting_tasks.filter(status=status_filter)
    if search_query:
        regular_tasks = regular_tasks.filter(description__icontains=search_query)
        meeting_tasks = meeting_tasks.filter(description__icontains=search_query)

    # Create unified task list with additional metadata
    unified_tasks = []

    # Add regular tasks
    for task in regular_tasks:
        unified_tasks.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'start_date': task.start_date,
            'end_date': task.end_date,
            'assigned_to': task.assigned_to,
            'created_by': task.created_by,
            'meeting': task.meeting,
            'steps': task.steps,
            'task_type': 'regular',  # Identifier for template
            'get_status_display': task.get_status_display(),
            'original_task': task  # Keep reference to original object
        })

    # Add meeting tasks
    for mtask in meeting_tasks:
        # Convert end_date to datetime for consistency
        end_datetime = None
        if mtask.end_date:
            end_datetime = datetime.combine(mtask.end_date, datetime.min.time())

        unified_tasks.append({
            'id': f"meeting_{mtask.id}",  # Prefix to avoid ID conflicts
            'title': None,  # Meeting tasks don't have titles
            'description': mtask.description,
            'status': mtask.status,
            'start_date': mtask.created_at,  # Use creation time as start
            'end_date': end_datetime,
            'assigned_to': mtask.assigned_to,
            'created_by': None,  # Meeting tasks don't have created_by
            'meeting': mtask.meeting,
            'steps': None,  # Meeting tasks don't have steps
            'task_type': 'meeting',  # Identifier for template
            'get_status_display': dict(MeetingTask.STATUS_CHOICES).get(mtask.status, mtask.status),
            'original_task': mtask  # Keep reference to original object
        })

    # Sort unified tasks by end_date (most recent first)
    unified_tasks.sort(key=lambda x: x['end_date'] or datetime.min, reverse=True)

    # Get task counts for statistics (including both types)
    regular_total = Task.objects.filter(assigned_to=request.user).count()
    meeting_total = MeetingTask.objects.filter(assigned_to=request.user).count()
    total_count = regular_total + meeting_total

    regular_in_progress = Task.objects.filter(assigned_to=request.user, status='in_progress').count()
    meeting_in_progress = MeetingTask.objects.filter(assigned_to=request.user, status='in_progress').count()
    in_progress_count = regular_in_progress + meeting_in_progress

    regular_completed = Task.objects.filter(assigned_to=request.user, status='completed').count()
    meeting_completed = MeetingTask.objects.filter(assigned_to=request.user, status='completed').count()
    completed_count = regular_completed + meeting_completed

    overdue_count = 0  # In a real app, this would check dates

    context = {
        'tasks': unified_tasks,
        'total_count': total_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'overdue_count': overdue_count,
    }

    return render(request, 'tasks/task_list.html', context)

@login_required
def task_detail(request, pk):
    """
    عرض تفاصيل المهمة - يدعم كل من المهام العادية ومهام الاجتماعات
    """
    from meetings.models import MeetingTask, MeetingTaskStep
    from meetings.forms import MeetingTaskStepForm, MeetingTaskStatusForm

    # تحديد نوع المهمة بناءً على المعرف
    is_meeting_task = False
    task = None

    # التحقق من كونها مهمة اجتماع (مع البادئة meeting_)
    if str(pk).startswith('meeting_'):
        meeting_task_id = str(pk).replace('meeting_', '')
        try:
            task = get_object_or_404(MeetingTask, pk=meeting_task_id)
            is_meeting_task = True
        except:
            messages.error(request, "المهمة غير موجودة")
            return redirect('tasks:list')
    else:
        task = get_object_or_404(Task, pk=pk)

    # التحقق من صلاحية الوصول
    if not (request.user.is_superuser or request.user == task.assigned_to or
            (hasattr(task, 'created_by') and request.user == task.created_by)):
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه المهمة")
        return redirect('tasks:list')

    # معالجة إضافة خطوة جديدة
    step_form = None
    status_form = None

    if is_meeting_task:
        # للمهام المرتبطة بالاجتماعات
        if request.method == 'POST' and 'add_step' in request.POST:
            step_form = MeetingTaskStepForm(request.POST, meeting_task=task, user=request.user)
            if step_form.is_valid():
                step_form.save()
                messages.success(request, "تم إضافة الخطوة بنجاح")
                return redirect('tasks:detail', pk=pk)
        else:
            step_form = MeetingTaskStepForm(meeting_task=task, user=request.user)

        # نموذج تحديث الحالة
        if request.method == 'POST' and 'update_status' in request.POST:
            status_form = MeetingTaskStatusForm(request.POST, instance=task)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, "تم تحديث حالة المهمة بنجاح")
                return redirect('tasks:detail', pk=pk)
        else:
            status_form = MeetingTaskStatusForm(instance=task)

        # الحصول على الخطوات
        steps = task.steps.all().order_by('created_at')

        # المهام ذات الصلة من نفس الاجتماع
        related_tasks = MeetingTask.objects.filter(meeting=task.meeting).exclude(id=task.id)[:5]

        # إحصائيات مهام الاجتماع
        meeting_tasks_stats = {
            'total': task.meeting.meeting_tasks.count(),
            'completed': task.meeting.meeting_tasks.filter(status='completed').count(),
            'in_progress': task.meeting.meeting_tasks.filter(status='in_progress').count(),
            'pending': task.meeting.meeting_tasks.filter(status='pending').count(),
        }

        # إحصائيات الخطوات للمهام المرتبطة بالاجتماعات
        steps_stats = None
        if steps.exists():
            completed_steps = steps.filter(completed=True).count() if is_meeting_task else 0
            total_steps = steps.count()
            progress_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0
            steps_stats = {
                'completed': completed_steps,
                'total': total_steps,
                'progress_percentage': round(progress_percentage, 1)
            }

    else:
        # للمهام العادية
        if request.method == 'POST':
            step_form = TaskStepForm(request.POST)
            if step_form.is_valid():
                step = step_form.save(commit=False)
                step.task = task
                step.save()
                messages.success(request, "تم إضافة الخطوة بنجاح")
                return redirect('tasks:detail', pk=pk)
        else:
            step_form = TaskStepForm()

        # الحصول على الخطوات
        steps = task.steps.all().order_by('date')

        # المهام ذات الصلة
        if task.meeting:
            related_tasks = Task.objects.filter(meeting=task.meeting).exclude(id=task.id)[:5]
        elif task.created_by:
            related_tasks = Task.objects.filter(created_by=task.created_by).exclude(id=task.id)[:5]
        else:
            related_tasks = Task.objects.filter(assigned_to=task.assigned_to).exclude(id=task.id)[:5]

        # إحصائيات الخطوات للمهام العادية
        if steps.exists() and not is_meeting_task:
            total_steps = steps.count()
            steps_stats = {
                'completed': 0,  # Regular tasks don't track step completion
                'total': total_steps,
                'progress_percentage': 50 if task.status == 'in_progress' else (100 if task.status == 'completed' else 10)
            }

    context = {
        'task': task,
        'is_meeting_task': is_meeting_task,
        'step_form': step_form,
        'status_form': status_form,
        'steps': steps,
        'related_tasks': related_tasks,
        'task_type': 'meeting' if is_meeting_task else 'regular',
        'steps_stats': steps_stats
    }

    # Add meeting stats for meeting tasks
    if is_meeting_task:
        context['meeting_tasks_stats'] = meeting_tasks_stats

    return render(request, 'tasks/task_detail.html', context)

@login_required
def update_task_status(request, pk):
    if request.method == 'POST':
        from meetings.models import MeetingTask

        # Handle both regular tasks and meeting tasks
        task = None
        is_meeting_task = False

        # Check if it's a meeting task (prefixed with "meeting_")
        if str(pk).startswith('meeting_'):
            meeting_task_id = str(pk).replace('meeting_', '')
            try:
                task = get_object_or_404(MeetingTask, pk=meeting_task_id)
                is_meeting_task = True
            except:
                return JsonResponse({'success': False, 'error': 'مهمة غير موجودة'})
        else:
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
                # Validate status for meeting tasks
                if is_meeting_task:
                    valid_statuses = [choice[0] for choice in MeetingTask.STATUS_CHOICES]
                    if new_status not in valid_statuses:
                        return JsonResponse({'success': False, 'error': 'حالة غير صحيحة'})

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
    from meetings.models import MeetingTask, MeetingTaskStep

    # تحديد نوع المهمة بناءً على المعرف
    is_meeting_task = False
    task = None

    # التحقق من كونها مهمة اجتماع (مع البادئة meeting_)
    if str(pk).startswith('meeting_'):
        meeting_task_id = str(pk).replace('meeting_', '')
        try:
            task = get_object_or_404(MeetingTask, pk=meeting_task_id)
            is_meeting_task = True
        except:
            messages.error(request, "المهمة غير موجودة")
            return redirect('tasks:list')
    else:
        task = get_object_or_404(Task, pk=pk)

    # Check if user is allowed to delete steps for this task
    # Only superusers or the assigned user can delete steps
    if not (request.user.is_superuser or request.user == task.assigned_to):
        messages.error(request, "ليس لديك صلاحية لحذف خطوات هذه المهمة")
        return redirect('tasks:detail', pk=pk)

    if request.method == 'POST':
        step_id = request.POST.get('step_id')
        step_type = request.POST.get('step_type', 'regular')

        if step_id:
            if is_meeting_task or step_type == 'meeting':
                step = get_object_or_404(MeetingTaskStep, id=step_id, meeting_task=task)
            else:
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
    from meetings.models import MeetingTask

    # Get stats for the current user if not a superuser
    if not request.user.is_superuser:
        regular_task_count = Task.objects.filter(assigned_to=request.user).count()
        meeting_task_count = MeetingTask.objects.filter(assigned_to=request.user).count()

        regular_completed = Task.objects.filter(assigned_to=request.user, status='completed').count()
        meeting_completed = MeetingTask.objects.filter(assigned_to=request.user, status='completed').count()

        stats = {
            'meeting_count': Meeting.objects.filter(attendees__user=request.user).count(),
            'task_count': regular_task_count + meeting_task_count,
            'completed_task_count': regular_completed + meeting_completed,
            'user_count': User.objects.count()
        }
    else:
        # Superusers see all stats
        regular_task_count = Task.objects.count()
        meeting_task_count = MeetingTask.objects.count()

        regular_completed = Task.objects.filter(status='completed').count()
        meeting_completed = MeetingTask.objects.filter(status='completed').count()

        stats = {
            'meeting_count': Meeting.objects.count(),
            'task_count': regular_task_count + meeting_task_count,
            'completed_task_count': regular_completed + meeting_completed,
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
