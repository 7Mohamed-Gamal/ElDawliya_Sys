from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, Http404
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg, Case, When, IntegerField
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from datetime import datetime, timedelta
import json
import logging

from .models import Task, TaskStep
from .forms import (
    TaskForm, TaskStepForm, TaskFilterForm,
    BulkTaskUpdateForm, TaskStatusUpdateForm
)
from meetings.models import Meeting
from tasks.decorators import tasks_module_permission_required, can_access_task

# Set up logging
logger = logging.getLogger(__name__)

User = get_user_model()

@login_required
@tasks_module_permission_required('dashboard', 'view')
def dashboard(request):
    """Enhanced unified dashboard with both regular and meeting tasks"""
    from tasks.models import UnifiedTaskManager

    try:
        user = request.user

        # Get unified statistics
        stats = UnifiedTaskManager.get_statistics(user)

        # Calculate completion rate
        completion_rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0

        # Get recent unified tasks
        recent_tasks = UnifiedTaskManager.get_user_tasks(user, include_meeting_tasks=True)

        # Sort by creation date and limit
        recent_tasks.sort(key=lambda x: x.created_at, reverse=True)
        my_recent_tasks = recent_tasks[:8]

        # Get overdue tasks
        overdue_tasks = [task for task in recent_tasks if task.is_overdue]
        overdue_tasks.sort(key=lambda x: x.end_date or timezone.now())
        overdue_tasks_list = overdue_tasks[:5]

        # Priority distribution (only for regular tasks)
        priority_stats = []
        if user.is_superuser:
            priority_stats = Task.objects.values('priority').annotate(
                count=Count('id')
            ).order_by('priority')
        else:
            priority_stats = Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user)
            ).values('priority').annotate(count=Count('id')).order_by('priority')

        # Task type distribution
        task_type_stats = {
            'regular': stats['regular_stats']['total'],
            'meeting': stats['meeting_stats']['total'],
        }

        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_activity = {
            'new_tasks': len([t for t in recent_tasks if t.created_at >= week_ago]),
            'completed_tasks': len([t for t in recent_tasks if t.status == 'completed' and t.updated_at >= week_ago]),
        }

        context = {
            'total_tasks': stats['total'],
            'completed_tasks': stats['completed'],
            'in_progress_tasks': stats['in_progress'],
            'overdue_tasks': stats['overdue'],
            'completion_rate': round(completion_rate, 1),
            'my_recent_tasks': my_recent_tasks,
            'overdue_tasks_list': overdue_tasks_list,
            'priority_stats': priority_stats,
            'task_type_stats': task_type_stats,
            'recent_activity': recent_activity,
            'user_is_superuser': user.is_superuser,
            'regular_stats': stats['regular_stats'],
            'meeting_stats': stats['meeting_stats'],
        }

        return render(request, 'tasks/unified_dashboard.html', context)

    except Exception as e:
        logger.error(f"Error in unified dashboard view: {str(e)}")
        messages.error(request, "حدث خطأ أثناء تحميل لوحة التحكم")
        return render(request, 'tasks/unified_dashboard.html', {
            'total_tasks': 0,
            'completed_tasks': 0,
            'in_progress_tasks': 0,
            'overdue_tasks': 0,
            'completion_rate': 0,
            'my_recent_tasks': [],
            'overdue_tasks_list': [],
            'priority_stats': [],
            'task_type_stats': {'regular': 0, 'meeting': 0},
            'recent_activity': {'new_tasks': 0, 'completed_tasks': 0},
        })

@login_required
@tasks_module_permission_required('tasks', 'add')
@csrf_protect
def task_create(request):
    """Enhanced task creation with better validation and UX"""

    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)

        if form.is_valid():
            try:
                task = form.save(commit=False)
                task.created_by = request.user

                # Ensure non-superusers can only assign tasks to themselves
                if not request.user.is_superuser:
                    task.assigned_to = request.user

                task.save()

                # Log task creation
                logger.info(f"Task created: {task.id} by user {request.user.username}")

                messages.success(request, "تم إنشاء المهمة بنجاح")

                # Redirect based on user preference or default to detail
                next_url = request.GET.get('next')
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect('tasks:detail', pk=task.id)

            except Exception as e:
                logger.error(f"Error creating task: {str(e)}")
                messages.error(request, "حدث خطأ أثناء إنشاء المهمة")
        else:
            messages.error(request, "يرجى تصحيح الأخطاء في النموذج")
    else:
        # Initialize form with default values
        initial_data = {
            'assigned_to': request.user,
            'priority': 'medium',
            'status': 'pending'
        }

        # If creating from meeting, pre-fill meeting field
        meeting_id = request.GET.get('meeting_id')
        if meeting_id:
            try:
                meeting = get_object_or_404(Meeting, pk=meeting_id)
                initial_data['meeting'] = meeting
            except (Meeting.DoesNotExist, ValueError):
                messages.warning(request, "الاجتماع المحدد غير موجود")

        form = TaskForm(initial=initial_data, user=request.user)

    context = {
        'form': form,
        'title': 'إنشاء مهمة جديدة',
        'submit_text': 'إنشاء المهمة',
        'cancel_url': request.GET.get('next', 'tasks:list')
    }

    return render(request, 'tasks/task_form.html', context)

@login_required
@tasks_module_permission_required('tasks', 'view')
def task_list(request):
    """Enhanced unified task list with filtering, pagination, and better performance"""
    from tasks.models import UnifiedTaskManager
    from tasks.forms import UnifiedTaskFilterForm

    try:
        user = request.user

        # Initialize unified filter form
        filter_form = UnifiedTaskFilterForm(request.GET, user=user)

        # Get all unified tasks
        unified_tasks = UnifiedTaskManager.get_user_tasks(user, include_meeting_tasks=True)

        # Apply filters
        if filter_form.is_valid():
            search = filter_form.cleaned_data.get('search')
            task_type = filter_form.cleaned_data.get('task_type')
            status = filter_form.cleaned_data.get('status')
            priority = filter_form.cleaned_data.get('priority')
            assigned_to = filter_form.cleaned_data.get('assigned_to')
            overdue_only = filter_form.cleaned_data.get('overdue_only')
            meeting = filter_form.cleaned_data.get('meeting')

            # Apply search filter
            if search:
                unified_tasks = [
                    task for task in unified_tasks
                    if search.lower() in task.description.lower() or
                    (task.title and search.lower() in task.title.lower())
                ]

            # Apply task type filter
            if task_type:
                unified_tasks = [task for task in unified_tasks if task.task_type == task_type]

            # Apply status filter
            if status:
                unified_tasks = [task for task in unified_tasks if task.status == status]

            # Apply priority filter (only affects regular tasks)
            if priority:
                unified_tasks = [
                    task for task in unified_tasks
                    if task.task_type == 'meeting' or task.priority == priority
                ]

            # Apply assigned_to filter
            if assigned_to:
                unified_tasks = [task for task in unified_tasks if task.assigned_to == assigned_to]

            # Apply overdue filter
            if overdue_only:
                unified_tasks = [task for task in unified_tasks if task.is_overdue]

            # Apply meeting filter
            if meeting:
                unified_tasks = [task for task in unified_tasks if task.meeting == meeting]

        # Sort tasks by priority and due date
        def sort_key(task):
            priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
            priority_val = priority_order.get(task.priority, 4)
            due_date = task.end_date or timezone.now() + timedelta(days=365)
            overdue_penalty = 0 if not task.is_overdue else -1000  # Overdue tasks first
            return (overdue_penalty, priority_val, due_date)

        unified_tasks.sort(key=sort_key)

        # Pagination
        paginator = Paginator(unified_tasks, 20)  # 20 tasks per page
        page = request.GET.get('page')

        try:
            tasks_page = paginator.page(page)
        except PageNotAnInteger:
            tasks_page = paginator.page(1)
        except EmptyPage:
            tasks_page = paginator.page(paginator.num_pages)

        # Get statistics
        stats = UnifiedTaskManager.get_statistics(user)

        # Calculate filtered statistics
        filtered_stats = {
            'total': len(unified_tasks),
            'completed': len([t for t in unified_tasks if t.status == 'completed']),
            'in_progress': len([t for t in unified_tasks if t.status == 'in_progress']),
            'overdue': len([t for t in unified_tasks if t.is_overdue]),
            'regular': len([t for t in unified_tasks if t.task_type == 'regular']),
            'meeting': len([t for t in unified_tasks if t.task_type == 'meeting']),
        }

        context = {
            'tasks': tasks_page,
            'filter_form': filter_form,
            'total_count': stats['total'],
            'in_progress_count': stats['in_progress'],
            'completed_count': stats['completed'],
            'overdue_count': stats['overdue'],
            'filtered_stats': filtered_stats,
            'paginator': paginator,
            'page_obj': tasks_page,
            'is_paginated': paginator.num_pages > 1,
            'user_is_superuser': user.is_superuser,
        }

        return render(request, 'tasks/unified_task_list.html', context)

    except Exception as e:
        logger.error(f"Error in unified task_list view: {str(e)}")
        messages.error(request, "حدث خطأ أثناء تحميل قائمة المهام")
        return render(request, 'tasks/unified_task_list.html', {
            'tasks': [],
            'filter_form': UnifiedTaskFilterForm(user=request.user),
            'total_count': 0,
            'in_progress_count': 0,
            'completed_count': 0,
            'overdue_count': 0,
            'filtered_stats': {'total': 0, 'completed': 0, 'in_progress': 0, 'overdue': 0, 'regular': 0, 'meeting': 0},
        })

def _get_task_statistics(user):
    """Helper function to get task statistics efficiently"""
    from meetings.models import MeetingTask

    if user.is_superuser:
        regular_stats = Task.objects.aggregate(
            total=Count('id'),
            in_progress=Count(Case(When(status='in_progress', then=1), output_field=IntegerField())),
            completed=Count(Case(When(status='completed', then=1), output_field=IntegerField())),
            overdue=Count(Case(
                When(end_date__lt=timezone.now(), status__in=['pending', 'in_progress'], then=1),
                output_field=IntegerField()
            ))
        )
        meeting_stats = MeetingTask.objects.aggregate(
            total=Count('id'),
            in_progress=Count(Case(When(status='in_progress', then=1), output_field=IntegerField())),
            completed=Count(Case(When(status='completed', then=1), output_field=IntegerField())),
            overdue=Count(Case(
                When(end_date__lt=timezone.now().date(), status__in=['pending', 'in_progress'], then=1),
                output_field=IntegerField()
            ))
        )
    else:
        regular_stats = Task.objects.filter(
            Q(assigned_to=user) | Q(created_by=user)
        ).aggregate(
            total=Count('id'),
            in_progress=Count(Case(When(status='in_progress', then=1), output_field=IntegerField())),
            completed=Count(Case(When(status='completed', then=1), output_field=IntegerField())),
            overdue=Count(Case(
                When(end_date__lt=timezone.now(), status__in=['pending', 'in_progress'], then=1),
                output_field=IntegerField()
            ))
        )
        meeting_stats = MeetingTask.objects.filter(assigned_to=user).aggregate(
            total=Count('id'),
            in_progress=Count(Case(When(status='in_progress', then=1), output_field=IntegerField())),
            completed=Count(Case(When(status='completed', then=1), output_field=IntegerField())),
            overdue=Count(Case(
                When(end_date__lt=timezone.now().date(), status__in=['pending', 'in_progress'], then=1),
                output_field=IntegerField()
            ))
        )

    return {
        'total': regular_stats['total'] + meeting_stats['total'],
        'in_progress': regular_stats['in_progress'] + meeting_stats['in_progress'],
        'completed': regular_stats['completed'] + meeting_stats['completed'],
        'overdue': regular_stats['overdue'] + meeting_stats['overdue'],
    }

@login_required
def task_detail(request, pk):
    """
    Enhanced unified task detail view - supports both regular and meeting tasks
    """
    from tasks.models import UnifiedTaskManager
    from tasks.forms import UnifiedTaskStepForm, UnifiedTaskStatusForm, MeetingTaskEditForm

    try:
        # Get unified task using the manager
        unified_task = UnifiedTaskManager.get_task_by_id(str(pk), user=request.user)

        if not unified_task:
            raise Http404("المهمة غير موجودة أو ليس لديك صلاحية لعرضها")

        # Check permissions
        if not unified_task.can_be_viewed_by(request.user):
            return HttpResponseForbidden("ليس لديك صلاحية لعرض هذه المهمة")

        # Get task steps
        steps = unified_task.steps.order_by('-created_at' if unified_task.task_type == 'meeting' else '-date')

        # Initialize forms
        step_form = UnifiedTaskStepForm()
        status_form = UnifiedTaskStatusForm(task_type=unified_task.task_type)
        edit_form = None

        # For meeting tasks, also provide edit form
        if unified_task.task_type == 'meeting':
            edit_form = MeetingTaskEditForm(meeting_task=unified_task.task_instance)

        # Handle POST requests
        if request.method == 'POST':
            if 'add_step' in request.POST:
                step_form = UnifiedTaskStepForm(request.POST)
                if step_form.is_valid():
                    description = step_form.cleaned_data['description']
                    notes = step_form.cleaned_data['notes']
                    completed = step_form.cleaned_data['completed']

                    # Add step using unified interface
                    step = unified_task.add_step(description, notes, request.user)
                    if step:
                        if completed:
                            step.completed = True
                            if hasattr(step, 'completion_date'):
                                step.completion_date = timezone.now()
                            step.save()

                        messages.success(request, "تم إضافة الخطوة بنجاح")
                        return redirect('tasks:detail', pk=pk)
                    else:
                        messages.error(request, "لا يمكنك إضافة خطوات لهذه المهمة")

            elif 'update_status' in request.POST:
                status_form = UnifiedTaskStatusForm(request.POST, task_type=unified_task.task_type)
                if status_form.is_valid():
                    new_status = status_form.cleaned_data['status']
                    if unified_task.update_status(new_status, request.user):
                        messages.success(request, "تم تحديث حالة المهمة بنجاح")
                        return redirect('tasks:detail', pk=pk)
                    else:
                        messages.error(request, "لا يمكنك تحديث حالة هذه المهمة")

            elif 'edit_meeting_task' in request.POST and unified_task.task_type == 'meeting':
                edit_form = MeetingTaskEditForm(request.POST, meeting_task=unified_task.task_instance)
                if edit_form.is_valid() and unified_task.can_be_edited_by(request.user):
                    # Update meeting task
                    task_instance = unified_task.task_instance
                    task_instance.description = edit_form.cleaned_data['description']
                    task_instance.status = edit_form.cleaned_data['status']
                    task_instance.end_date = edit_form.cleaned_data['end_date']
                    task_instance.save()

                    messages.success(request, "تم تحديث المهمة بنجاح")
                    return redirect('tasks:detail', pk=pk)

        # Get related tasks
        related_tasks = []
        if unified_task.meeting:
            # Get other tasks from the same meeting
            if unified_task.task_type == 'meeting':
                from meetings.models import MeetingTask
                related_meeting_tasks = MeetingTask.objects.filter(
                    meeting=unified_task.meeting
                ).exclude(id=unified_task.raw_id)[:3]
                related_tasks.extend([
                    UnifiedTaskManager.get_task_by_id(f"meeting_{t.id}", request.user)
                    for t in related_meeting_tasks
                ])

            # Also get regular tasks from the same meeting
            related_regular_tasks = Task.objects.filter(
                meeting=unified_task.meeting
            )
            if unified_task.task_type == 'regular':
                related_regular_tasks = related_regular_tasks.exclude(id=unified_task.raw_id)

            related_tasks.extend([
                UnifiedTaskManager.get_task_by_id(str(t.id), request.user)
                for t in related_regular_tasks[:3]
            ])

        # Calculate additional statistics
        completed_steps = sum(1 for step in steps if getattr(step, 'completed', False))
        total_steps = len(steps)
        step_completion_rate = (completed_steps / total_steps * 100) if total_steps > 0 else 0

        # Meeting statistics (if applicable)
        meeting_stats = None
        if unified_task.meeting:
            from meetings.models import MeetingTask
            meeting_tasks = MeetingTask.objects.filter(meeting=unified_task.meeting)
            regular_tasks = Task.objects.filter(meeting=unified_task.meeting)

            meeting_stats = {
                'total_meeting_tasks': meeting_tasks.count(),
                'completed_meeting_tasks': meeting_tasks.filter(status='completed').count(),
                'total_regular_tasks': regular_tasks.count(),
                'completed_regular_tasks': regular_tasks.filter(status='completed').count(),
            }

        context = {
            'unified_task': unified_task,
            'task': unified_task.task_instance,  # For backward compatibility
            'steps': steps,
            'step_form': step_form,
            'status_form': status_form,
            'edit_form': edit_form,
            'is_meeting_task': unified_task.task_type == 'meeting',
            'task_type': unified_task.task_type,
            'can_edit': unified_task.can_be_edited_by(request.user),
            'can_view': unified_task.can_be_viewed_by(request.user),
            'completed_steps': completed_steps,
            'total_steps': total_steps,
            'step_completion_rate': round(step_completion_rate, 1),
            'related_tasks': [t for t in related_tasks if t],  # Filter out None values
            'meeting_stats': meeting_stats,
        }

        return render(request, 'tasks/unified_task_detail.html', context)

    except Exception as e:
        logger.error(f"Error in unified task_detail view: {str(e)}")
        messages.error(request, "حدث خطأ أثناء تحميل تفاصيل المهمة")
        return redirect('tasks:list')

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
@require_POST
@csrf_protect
def bulk_task_update(request):
    """Handle bulk task updates"""
    from .forms import BulkTaskUpdateForm

    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'غير مصرح لك بهذا الإجراء'})

    form = BulkTaskUpdateForm(request.POST)
    if form.is_valid():
        try:
            action = form.cleaned_data['action']
            task_ids = form.cleaned_data['task_ids'].split(',')
            task_ids = [int(id.strip()) for id in task_ids if id.strip().isdigit()]

            tasks = Task.objects.filter(id__in=task_ids)
            updated_count = 0

            if action == 'update_status':
                new_status = form.cleaned_data['new_status']
                updated_count = tasks.update(status=new_status)

            elif action == 'update_priority':
                new_priority = form.cleaned_data['new_priority']
                updated_count = tasks.update(priority=new_priority)

            elif action == 'reassign':
                new_assigned_to = form.cleaned_data['new_assigned_to']
                updated_count = tasks.update(assigned_to=new_assigned_to)

            elif action == 'delete':
                updated_count = tasks.count()
                tasks.delete()

            return JsonResponse({
                'success': True,
                'message': f'تم تحديث {updated_count} مهمة بنجاح'
            })

        except Exception as e:
            logger.error(f"Error in bulk update: {str(e)}")
            return JsonResponse({'success': False, 'error': 'حدث خطأ أثناء التحديث'})

    return JsonResponse({'success': False, 'error': 'بيانات غير صحيحة'})

@login_required
def export_tasks(request):
    """Export tasks to CSV"""
    import csv
    from django.http import HttpResponse

    try:
        # Get user's tasks
        if request.user.is_superuser:
            tasks = Task.objects.with_related()
        else:
            tasks = Task.objects.for_user(request.user).with_related()

        # Apply filters if provided
        status = request.GET.get('status')
        if status:
            tasks = tasks.filter(status=status)

        # Create CSV response
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="tasks_export.csv"'

        # Add BOM for proper UTF-8 encoding in Excel
        response.write('\ufeff')

        writer = csv.writer(response)
        writer.writerow([
            'العنوان', 'الوصف', 'المكلف', 'منشئ المهمة', 'الأولوية',
            'الحالة', 'تاريخ البدء', 'تاريخ الانتهاء', 'تاريخ الإنشاء'
        ])

        for task in tasks:
            writer.writerow([
                task.title or '',
                task.description,
                task.assigned_to.username,
                task.created_by.username if task.created_by else '',
                task.get_priority_display(),
                task.get_status_display(),
                task.start_date.strftime('%Y-%m-%d %H:%M') if task.start_date else '',
                task.end_date.strftime('%Y-%m-%d %H:%M') if task.end_date else '',
                task.created_at.strftime('%Y-%m-%d %H:%M') if task.created_at else '',
            ])

        return response

    except Exception as e:
        logger.error(f"Error exporting tasks: {str(e)}")
        messages.error(request, "حدث خطأ أثناء تصدير المهام")
        return redirect('tasks:list')

@login_required
def task_search_api(request):
    """API endpoint for task search"""
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'results': []})

    try:
        # Search in user's accessible tasks
        if request.user.is_superuser:
            tasks = Task.objects.with_related()
        else:
            tasks = Task.objects.for_user(request.user).with_related()

        # Apply search filter
        search_q = Q(title__icontains=query) | Q(description__icontains=query)
        tasks = tasks.filter(search_q)[:10]  # Limit to 10 results

        results = []
        for task in tasks:
            results.append({
                'id': task.id,
                'title': task.get_display_title(),
                'description': task.description[:100] + '...' if len(task.description) > 100 else task.description,
                'status': task.get_status_display(),
                'priority': task.get_priority_display(),
                'assigned_to': task.assigned_to.username,
                'url': task.get_absolute_url(),
                'is_overdue': task.is_overdue,
            })

        return JsonResponse({'results': results})

    except Exception as e:
        logger.error(f"Error in task search: {str(e)}")
        return JsonResponse({'results': [], 'error': 'حدث خطأ في البحث'})

@login_required
def task_stats_api(request):
    """API endpoint for detailed task statistics"""
    try:
        user = request.user
        stats = _get_task_statistics(user)

        # Add more detailed statistics
        if user.is_superuser:
            priority_stats = Task.objects.values('priority').annotate(
                count=Count('id')
            ).order_by('priority')

            status_stats = Task.objects.values('status').annotate(
                count=Count('id')
            ).order_by('status')
        else:
            priority_stats = Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user)
            ).values('priority').annotate(
                count=Count('id')
            ).order_by('priority')

            status_stats = Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user)
            ).values('status').annotate(
                count=Count('id')
            ).order_by('status')

        stats.update({
            'priority_distribution': list(priority_stats),
            'status_distribution': list(status_stats),
        })

        return JsonResponse(stats)

    except Exception as e:
        logger.error(f"Error getting task stats: {str(e)}")
        return JsonResponse({'error': 'حدث خطأ في جلب الإحصائيات'})

@login_required
@tasks_module_permission_required('reports', 'view')
def export_report(request):
    """Export detailed task report to CSV"""
    import csv
    from django.http import HttpResponse
    from django.utils import timezone

    try:
        # Get user's accessible tasks
        if request.user.is_superuser:
            tasks = Task.objects.with_related().order_by('-created_at')
        else:
            tasks = Task.objects.for_user(request.user).with_related().order_by('-created_at')

        # Apply date filters if provided
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date:
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                tasks = tasks.filter(created_at__date__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                tasks = tasks.filter(created_at__date__lte=end_date)
            except ValueError:
                pass

        # Apply status filter if provided
        status = request.GET.get('status')
        if status:
            tasks = tasks.filter(status=status)

        # Apply priority filter if provided
        priority = request.GET.get('priority')
        if priority:
            tasks = tasks.filter(priority=priority)

        # Limit export size for performance
        tasks = tasks[:1000]  # Limit to 1000 tasks

        # Create CSV response
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="tasks_report_{timestamp}.csv"'

        # Add BOM for proper UTF-8 encoding in Excel
        response.write('\ufeff')

        writer = csv.writer(response)

        # Write header row
        writer.writerow([
            'رقم المهمة', 'العنوان', 'الوصف', 'المكلف', 'منشئ المهمة',
            'الأولوية', 'الحالة', 'تاريخ البدء', 'تاريخ الانتهاء',
            'تاريخ الإنشاء', 'آخر تحديث', 'عدد الخطوات', 'نسبة التقدم',
            'متأخرة', 'أيام حتى الانتهاء', 'الاجتماع المرتبط'
        ])

        # Write data rows
        for task in tasks:
            writer.writerow([
                task.id,
                task.title or '',
                task.description,
                task.assigned_to.username,
                task.created_by.username if task.created_by else '',
                task.get_priority_display(),
                task.get_status_display(),
                task.start_date.strftime('%Y-%m-%d %H:%M') if task.start_date else '',
                task.end_date.strftime('%Y-%m-%d %H:%M') if task.end_date else '',
                task.created_at.strftime('%Y-%m-%d %H:%M') if task.created_at else '',
                task.updated_at.strftime('%Y-%m-%d %H:%M') if task.updated_at else '',
                task.steps.count(),
                f"{task.progress_percentage}%",
                'نعم' if task.is_overdue else 'لا',
                task.days_until_due,
                task.meeting.title if task.meeting else ''
            ])

        logger.info(f"Task report exported by user {request.user.username}, {tasks.count()} tasks")
        return response

    except Exception as e:
        logger.error(f"Error exporting task report: {str(e)}")
        messages.error(request, "حدث خطأ أثناء تصدير التقرير")
        return redirect('tasks:reports')

@login_required
@tasks_module_permission_required('reports', 'view')
def task_analytics(request):
    """Display advanced task analytics and charts"""
    from django.db.models import Count, Avg, Q
    from django.utils import timezone
    from datetime import timedelta

    try:
        user = request.user

        # Get base queryset
        if user.is_superuser:
            tasks = Task.objects.all()
        else:
            tasks = Task.objects.for_user(user)

        # Time-based analytics
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)

        # Overall statistics
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        overdue_tasks = tasks.filter(
            end_date__lt=now,
            status__in=['pending', 'in_progress']
        ).count()

        # Completion rate
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Recent activity
        recent_tasks = tasks.filter(created_at__gte=last_30_days).count()
        recent_completed = tasks.filter(
            status='completed',
            updated_at__gte=last_30_days
        ).count()

        # Status distribution
        status_distribution = tasks.values('status').annotate(
            count=Count('id')
        ).order_by('status')

        # Priority distribution
        priority_distribution = tasks.values('priority').annotate(
            count=Count('id')
        ).order_by('priority')

        # User performance (for superusers)
        user_performance = []
        if user.is_superuser:
            from accounts.models import Users_Login_New
            active_users = Users_Login_New.objects.filter(is_active=True)

            for u in active_users:
                user_tasks = tasks.filter(assigned_to=u)
                user_completed = user_tasks.filter(status='completed').count()
                user_total = user_tasks.count()
                user_completion_rate = (user_completed / user_total * 100) if user_total > 0 else 0

                if user_total > 0:  # Only include users with tasks
                    user_performance.append({
                        'user': u,
                        'total_tasks': user_total,
                        'completed_tasks': user_completed,
                        'completion_rate': round(user_completion_rate, 1),
                        'overdue_tasks': user_tasks.filter(
                            end_date__lt=now,
                            status__in=['pending', 'in_progress']
                        ).count()
                    })

            # Sort by completion rate
            user_performance.sort(key=lambda x: x['completion_rate'], reverse=True)

        # Monthly trends (last 6 months)
        monthly_trends = []
        for i in range(6):
            month_start = now.replace(day=1) - timedelta(days=30*i)
            month_end = month_start.replace(day=28) + timedelta(days=4)
            month_end = month_end - timedelta(days=month_end.day)

            month_tasks = tasks.filter(
                created_at__gte=month_start,
                created_at__lte=month_end
            )

            monthly_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'month_name': month_start.strftime('%B %Y'),
                'created': month_tasks.count(),
                'completed': month_tasks.filter(status='completed').count()
            })

        monthly_trends.reverse()  # Show oldest first

        # Average completion time
        completed_tasks_with_time = tasks.filter(
            status='completed',
            created_at__isnull=False,
            updated_at__isnull=False
        )

        avg_completion_days = 0
        if completed_tasks_with_time.exists():
            total_days = sum([
                (task.updated_at - task.created_at).days
                for task in completed_tasks_with_time
            ])
            avg_completion_days = total_days / completed_tasks_with_time.count()

        context = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': round(completion_rate, 1),
            'recent_tasks': recent_tasks,
            'recent_completed': recent_completed,
            'status_distribution': status_distribution,
            'priority_distribution': priority_distribution,
            'user_performance': user_performance[:10],  # Top 10 users
            'monthly_trends': monthly_trends,
            'avg_completion_days': round(avg_completion_days, 1),
            'user_is_superuser': user.is_superuser,
        }

        return render(request, 'tasks/analytics.html', context)

    except Exception as e:
        logger.error(f"Error in task analytics: {str(e)}")
        messages.error(request, "حدث خطأ أثناء تحميل التحليلات")
        return redirect('tasks:reports')

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
