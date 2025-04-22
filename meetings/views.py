from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Meeting, Attendee
from .forms import MeetingForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

from meetings.decorators import meetings_module_permission_required

User = get_user_model()  # Get the custom user model

@login_required
@meetings_module_permission_required('meetings', 'view')
def meeting_list(request):
    meetings = Meeting.objects.all()
    return render(request, 'meetings/meeting_list.html', {'meetings': meetings})

@login_required
@meetings_module_permission_required('meetings', 'view')
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)

    # Check if user is an attendee or admin
    is_attendee = Attendee.objects.filter(meeting=meeting, user=request.user).exists()
    is_admin = request.user.Role == 'admin'
    is_creator = meeting.created_by == request.user

    # If user is not an attendee, admin, or the creator, redirect to meetings list with error message
    if not (is_attendee or is_admin or is_creator):
        messages.error(request, "لا يمكنك عرض تفاصيل هذا الاجتماع لأنك لست من ضمن الحضور")
        return redirect('meetings:list')

    # Get available users for adding attendees (users who are not attendees already)
    existing_attendees = meeting.attendees.all().values_list('user_id', flat=True)
    available_users = User.objects.exclude(id__in=existing_attendees)

    # Get task completion statistics
    total_tasks = meeting.tasks.count()
    completed_tasks = meeting.tasks.filter(status='completed').count()
    in_progress_tasks = meeting.tasks.filter(status='in_progress').count()
    pending_tasks = meeting.tasks.filter(status='pending').count()

    # Calculate percentages
    completed_percent = 0
    in_progress_percent = 0
    pending_percent = 0

    if total_tasks > 0:
        completed_percent = (completed_tasks / total_tasks) * 100
        in_progress_percent = (in_progress_tasks / total_tasks) * 100
        pending_percent = (pending_tasks / total_tasks) * 100

    context = {
        'meeting': meeting,
        'available_users': available_users,
        'completed_count': completed_tasks,
        'in_progress_count': in_progress_tasks,
        'completed_percent': completed_percent,
        'in_progress_percent': in_progress_percent,
        'pending_percent': pending_percent,
    }

    return render(request, 'meetings/meeting_detail.html', context)

@login_required
@meetings_module_permission_required('meetings', 'add')
def meeting_create(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            # Save the meeting
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.save()

            # Save many-to-many fields (including attendees)
            form.save_m2m()

            # Get the selected attendees and create Attendee objects
            selected_attendees = form.cleaned_data.get('attendees', [])
            for user in selected_attendees:
                Attendee.objects.get_or_create(meeting=meeting, user=user)

            # Process tasks if any
            tasks_text = form.cleaned_data.get('tasks', '')
            if tasks_text:
                from tasks.models import Task

                # Split by new lines and filter out empty lines
                task_descriptions = [task.strip() for task in tasks_text.split('\n') if task.strip()]

                # Create tasks for each description
                from datetime import datetime, timedelta

                # Set default dates (start date = now, end date = 7 days from now)
                now = datetime.now()
                end_date = now + timedelta(days=7)

                for description in task_descriptions:
                    # By default, assign tasks to the meeting creator
                    Task.objects.create(
                        description=description,
                        meeting=meeting,
                        created_by=request.user,
                        assigned_to=request.user,
                        status='pending',
                        start_date=now,
                        end_date=end_date
                    )

            messages.success(request, "تم إنشاء الاجتماع والمهام المرتبطة بنجاح")
            return redirect('meetings:detail', pk=meeting.pk)
    else:
        form = MeetingForm()

    return render(request, 'meetings/meeting_form.html', {
        'form': form,
        'edit': False,
        'select2_enabled': True  # Flag to load select2 library
    })

@login_required
@meetings_module_permission_required('meetings', 'edit')
def meeting_edit(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)

    # Get existing attendees for initial form data
    existing_attendees = User.objects.filter(attendee__meeting=meeting)

    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()

            # Update attendees
            selected_attendees = form.cleaned_data.get('attendees', [])

            # Remove attendees that are no longer selected
            Attendee.objects.filter(meeting=meeting).exclude(user__in=selected_attendees).delete()

            # Add new attendees
            for user in selected_attendees:
                Attendee.objects.get_or_create(meeting=meeting, user=user)

            # Process tasks if any
            tasks_text = form.cleaned_data.get('tasks', '')
            if tasks_text:
                from tasks.models import Task

                # Split by new lines and filter out empty lines
                task_descriptions = [task.strip() for task in tasks_text.split('\n') if task.strip()]

                # Create tasks for each description
                from datetime import datetime, timedelta

                # Set default dates (start date = now, end date = 7 days from now)
                now = datetime.now()
                end_date = now + timedelta(days=7)

                for description in task_descriptions:
                    # By default, assign tasks to the meeting creator
                    Task.objects.create(
                        description=description,
                        meeting=meeting,
                        created_by=request.user,
                        assigned_to=request.user,
                        status='pending',
                        start_date=now,
                        end_date=end_date
                    )

            messages.success(request, "تم تحديث الاجتماع بنجاح")
            return redirect('meetings:detail', pk=meeting.pk)
    else:
        form = MeetingForm(instance=meeting, initial={
            'attendees': existing_attendees,
        })

    return render(request, 'meetings/meeting_form.html', {
        'form': form,
        'edit': True,
        'meeting': meeting,
        'select2_enabled': True
    })

@login_required
@meetings_module_permission_required('meetings', 'delete')
def meeting_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        meeting.delete()
        messages.success(request, "تم حذف الاجتماع بنجاح")
        return redirect('meetings:list')
    return redirect('meetings:detail', pk=meeting.pk)

@login_required
@meetings_module_permission_required('attendees', 'add')
def add_attendee(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        user_id = request.POST.get('user')
        if user_id:
            user = User.objects.get(id=user_id)
            Attendee.objects.create(meeting=meeting, user=user)
            messages.success(request, f"تم إضافة {user.username} إلى قائمة الحضور")
    return redirect('meetings:detail', pk=meeting.pk)

@login_required
@meetings_module_permission_required('attendees', 'delete')
def remove_attendee(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    attendee_id = request.GET.get('attendee_id')
    if attendee_id:
        try:
            attendee = Attendee.objects.get(id=attendee_id, meeting=meeting)
            username = attendee.user.username
            attendee.delete()
            messages.success(request, f"تم إزالة {username} من قائمة الحضور")
        except Attendee.DoesNotExist:
            messages.error(request, "الحضور غير موجود")
    return redirect('meetings:detail', pk=meeting.pk)
