from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse  # مستخدم في بعض الوظائف
from .models import Meeting, Attendee
from .forms import MeetingForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q  # مستخدم في وظيفة reports

User = get_user_model()  # Get the custom user model

@login_required
@permission_required('meetings.view_meeting', raise_exception=True)
def dashboard(request):
    """عرض لوحة تحكم الاجتماعات"""
    # إحصائيات الاجتماعات
    total_meetings = Meeting.objects.count()

    # اجتماعات اليوم
    today = timezone.now().date()
    today_meetings = Meeting.objects.filter(date=today)
    today_meetings_count = today_meetings.count()

    # اجتماعات الأسبوع
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_meetings = Meeting.objects.filter(date__range=[week_start, week_end]).count()

    # اجتماعات مكتملة
    completed_meetings = Meeting.objects.filter(status='completed').count()

    # الاجتماعات القادمة
    upcoming_meetings = Meeting.objects.filter(
        date__gte=today
    ).order_by('date')[:5]

    context = {
        'total_meetings': total_meetings,
        'today_meetings': today_meetings_count,
        'today_meetings_list': today_meetings[:5],  # أول 5 اجتماعات فقط للعرض
        'week_meetings': week_meetings,
        'completed_meetings': completed_meetings,
        'upcoming_meetings': upcoming_meetings,
    }

    return render(request, 'meetings/dashboard.html', context)

@login_required
@permission_required('meetings.view_meeting', raise_exception=True)
def meeting_list(request):
    meetings = Meeting.objects.all()

    # Apply filters
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    status = request.GET.get('status', '')

    if search_query:
        meetings = meetings.filter(title__icontains=search_query) | meetings.filter(topic__icontains=search_query)

    if date_from:
        meetings = meetings.filter(date__date__gte=date_from)

    if date_to:
        meetings = meetings.filter(date__date__lte=date_to)

    if status:
        meetings = meetings.filter(status=status)

    # Order by date
    meetings = meetings.order_by('-date')

    return render(request, 'meetings/meeting_list.html', {'meetings': meetings})

@login_required
@permission_required('meetings.view_meeting', raise_exception=True)
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

    # Get task count for each attendee
    # Import Task model
    from tasks.models import Task

    # Get all attendees with their task counts
    attendee_task_counts = []
    for attendee in meeting.attendees.all():
        task_count = Task.objects.filter(meeting=meeting, assigned_to=attendee.user).count()
        attendee.task_count = task_count
        attendee_task_counts.append({'attendee': attendee, 'task_count': task_count})

    context = {
        'meeting': meeting,
        'available_users': available_users,
        'completed_count': completed_tasks,
        'in_progress_count': in_progress_tasks,
        'completed_percent': completed_percent,
        'in_progress_percent': in_progress_percent,
        'pending_percent': pending_percent,
        'attendee_task_counts': attendee_task_counts,
    }

    return render(request, 'meetings/meeting_detail.html', context)

@login_required
@permission_required('meetings.add_meeting', raise_exception=True)
def meeting_create(request):
    if request.method == 'POST':
        # Debug: Print POST data
        print("POST data:", request.POST)

        form = MeetingForm(request.POST)
        if form.is_valid():
            # Debug: Print form cleaned data
            print("Form is valid. Cleaned data:", form.cleaned_data)

            try:
                # Save the meeting
                meeting = form.save(commit=False)
                meeting.created_by = request.user
                meeting.save()

                # Debug: Print meeting ID
                print("Meeting saved with ID:", meeting.id)

                # Save many-to-many fields (including attendees)
                form.save_m2m()

                # Get the selected attendees and create Attendee objects
                selected_attendees = form.cleaned_data.get('attendees', [])
                print("Selected attendees:", [user.username for user in selected_attendees])

                for user in selected_attendees:
                    Attendee.objects.get_or_create(meeting=meeting, user=user)

                # Process tasks if any
                tasks_text = form.cleaned_data.get('tasks', '')

                # Try to get task_assignments directly from POST data if not in cleaned_data
                task_assignments_json = form.cleaned_data.get('task_assignments', '')
                if not task_assignments_json:
                    task_assignments_json = request.POST.get('task_assignments', '')

                # Debug: Print task data
                print("Tasks text:", tasks_text)
                print("Task assignments JSON:", task_assignments_json)
                print("POST task_assignments:", request.POST.get('task_assignments', ''))

                # Process tasks if there are any, even without assignments
                if tasks_text and tasks_text.strip():
                    from tasks.models import Task
                    import json

                    # Split by new lines and filter out empty lines
                    task_descriptions = [task.strip() for task in tasks_text.split('\n') if task.strip()]
                    print("Task descriptions:", task_descriptions)

                    # Create tasks for each description
                    from datetime import datetime, timedelta

                    # Set default dates (start date = now, end date = 7 days from now)
                    now = datetime.now()
                    end_date = now + timedelta(days=7)

                    # Parse task assignments
                    task_assignments = {}
                    if task_assignments_json:
                        try:
                            task_assignments = json.loads(task_assignments_json)
                            print("Parsed task assignments:", task_assignments)
                        except json.JSONDecodeError as e:
                            # If JSON parsing fails, log the error and continue with default assignments
                            print(f"Error parsing task assignments: {e}")
                            print(f"Raw JSON: {task_assignments_json}")
                    else:
                        print("No task assignments JSON provided")

                    # Create tasks with assignments
                    try:
                        for index, description in enumerate(task_descriptions):
                            if not description.strip():
                                continue

                            task_id = f"task-{index}"
                            assigned_user_id = task_assignments.get(task_id)
                            print(f"Task {index}: '{description}', Assignment ID: {assigned_user_id}")

                            # Default to meeting creator if no assignment
                            assigned_to = request.user

                            # If task is assigned to an attendee
                            if assigned_user_id:
                                try:
                                    assigned_to = User.objects.get(id=assigned_user_id)
                                    print(f"Assigned to user: {assigned_to.username}")
                                except User.DoesNotExist:
                                    # If user doesn't exist, log the error and use default
                                    print(f"User with ID {assigned_user_id} not found, defaulting to {request.user.username}")

                            task = Task.objects.create(
                                description=description,
                                meeting=meeting,
                                created_by=request.user,
                                assigned_to=assigned_to,
                                status='pending',
                                start_date=now,
                                end_date=end_date
                            )
                            print(f"Created task with ID: {task.id}")
                    except Exception as e:
                        print(f"Error creating tasks: {str(e)}")
                        messages.error(request, f"حدث خطأ أثناء إنشاء المهام: {str(e)}")
                        # Continue execution - don't return here so the meeting is still saved

                messages.success(request, "تم إنشاء الاجتماع والمهام المرتبطة بنجاح")
                return redirect('meetings:detail', pk=meeting.pk)

            except Exception as e:
                # Debug: Print any exceptions
                print("Exception saving meeting:", str(e))
                messages.error(request, f"حدث خطأ أثناء حفظ الاجتماع: {str(e)}")
                return render(request, 'meetings/meeting_form.html', {
                    'form': form,
                    'edit': False,
                    'select2_enabled': True
                })
        else:
            # Debug: Print form errors
            print("Form is invalid. Errors:", form.errors)
            print("Non-field errors:", form.non_field_errors())

            # Return the form with errors
            return render(request, 'meetings/meeting_form.html', {
                'form': form,
                'edit': False,
                'select2_enabled': True
            })
    else:
        form = MeetingForm()

    return render(request, 'meetings/meeting_form.html', {
        'form': form,
        'edit': False,
        'select2_enabled': True  # Flag to load select2 library
    })

@login_required
@permission_required('meetings.change_meeting', raise_exception=True)
def meeting_edit(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    print(f"Editing meeting with ID: {meeting.id}, Title: {meeting.title}")

    # Get existing attendees for initial form data
    existing_attendees = User.objects.filter(attendees__meeting=meeting)
    print(f"Existing attendees: {[user.username for user in existing_attendees]}")

    if request.method == 'POST':
        print("POST data:", request.POST)

        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            print("Form is valid. Cleaned data:", form.cleaned_data)

            try:
                # Save the meeting
                form.save()
                print(f"Meeting updated: {meeting.id}")

                # Update attendees
                selected_attendees = form.cleaned_data.get('attendees', [])
                print(f"Selected attendees: {[user.username for user in selected_attendees]}")

                # Remove attendees that are no longer selected
                removed = Attendee.objects.filter(meeting=meeting).exclude(user__in=selected_attendees)
                print(f"Removing attendees: {[a.user.username for a in removed]}")
                removed.delete()

                # Add new attendees
                for user in selected_attendees:
                    created = Attendee.objects.get_or_create(meeting=meeting, user=user)
                    if created[1]:  # If created is True
                        print(f"Added new attendee: {user.username}")

                # Process tasks if any
                tasks_text = form.cleaned_data.get('tasks', '')

                # Try to get task_assignments directly from POST data if not in cleaned_data
                task_assignments_json = form.cleaned_data.get('task_assignments', '')
                if not task_assignments_json:
                    task_assignments_json = request.POST.get('task_assignments', '')

                # Debug: Print task data
                print("Tasks text:", tasks_text)
                print("Task assignments JSON:", task_assignments_json)
                print("POST task_assignments:", request.POST.get('task_assignments', ''))

                # Process tasks if there are any, even without assignments
                if tasks_text and tasks_text.strip():
                    from tasks.models import Task
                    import json

                    # Split by new lines and filter out empty lines
                    task_descriptions = [task.strip() for task in tasks_text.split('\n') if task.strip()]
                    print("Task descriptions:", task_descriptions)

                    # Create tasks for each description
                    from datetime import datetime, timedelta

                    # Set default dates (start date = now, end date = 7 days from now)
                    now = datetime.now()
                    end_date = now + timedelta(days=7)

                    # Parse task assignments
                    task_assignments = {}
                    if task_assignments_json:
                        try:
                            task_assignments = json.loads(task_assignments_json)
                            print("Parsed task assignments:", task_assignments)
                        except json.JSONDecodeError as e:
                            # If JSON parsing fails, log the error and continue with default assignments
                            print(f"Error parsing task assignments: {e}")
                            print(f"Raw JSON: {task_assignments_json}")
                    else:
                        print("No task assignments JSON provided")

                    # Create tasks with assignments
                    try:
                        for index, description in enumerate(task_descriptions):
                            if not description.strip():
                                continue

                            task_id = f"task-{index}"
                            assigned_user_id = task_assignments.get(task_id)
                            print(f"Task {index}: '{description}', Assignment ID: {assigned_user_id}")

                            # Default to meeting creator if no assignment
                            assigned_to = request.user

                            # If task is assigned to an attendee
                            if assigned_user_id:
                                try:
                                    assigned_to = User.objects.get(id=assigned_user_id)
                                    print(f"Assigned to user: {assigned_to.username}")
                                except User.DoesNotExist:
                                    # If user doesn't exist, log the error and use default
                                    print(f"User with ID {assigned_user_id} not found, defaulting to {request.user.username}")

                            task = Task.objects.create(
                                description=description,
                                meeting=meeting,
                                created_by=request.user,
                                assigned_to=assigned_to,
                                status='pending',
                                start_date=now,
                                end_date=end_date
                            )
                            print(f"Created task with ID: {task.id}")
                    except Exception as e:
                        print(f"Error creating tasks: {str(e)}")
                        messages.error(request, f"حدث خطأ أثناء إنشاء المهام: {str(e)}")
                        # Continue execution - don't return here so the meeting is still saved

                messages.success(request, "تم تحديث الاجتماع بنجاح")
                return redirect('meetings:detail', pk=meeting.pk)

            except Exception as e:
                print(f"Error updating meeting: {str(e)}")
                messages.error(request, f"حدث خطأ أثناء تحديث الاجتماع: {str(e)}")
                return render(request, 'meetings/meeting_form.html', {
                    'form': form,
                    'edit': True,
                    'meeting': meeting,
                    'select2_enabled': True
                })
        else:
            # Debug: Print form errors
            print("Form is invalid. Errors:", form.errors)
            print("Non-field errors:", form.non_field_errors())

            # Return the form with errors
            return render(request, 'meetings/meeting_form.html', {
                'form': form,
                'edit': True,
                'meeting': meeting,
                'select2_enabled': True
            })
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
@require_permission('delete_meetings')
def meeting_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        meeting.delete()
        messages.success(request, "تم حذف الاجتماع بنجاح")
        return redirect('meetings:list')
    return redirect('meetings:detail', pk=meeting.pk)

@login_required
@require_permission('add_attendees')
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
@require_permission('delete_attendees')
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

@login_required
@require_permission('view_meetings')
def calendar_view(request):
    """عرض تقويم الاجتماعات"""
    meetings = Meeting.objects.all()
    return render(request, 'meetings/calendar.html', {'meetings': meetings})

@login_required
@require_permission('view_reports')
def reports(request):
    """عرض تقارير الاجتماعات"""
    # Apply filters from request parameters
    base_meetings = Meeting.objects.all()

    # Filter by date range if provided
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    status = request.GET.get('status', '')
    creator_id = request.GET.get('creator', '')

    if date_from:
        base_meetings = base_meetings.filter(date__date__gte=date_from)

    if date_to:
        base_meetings = base_meetings.filter(date__date__lte=date_to)

    if status:
        base_meetings = base_meetings.filter(status=status)

    if creator_id:
        base_meetings = base_meetings.filter(created_by_id=creator_id)

    # Get status counts
    pending_count = base_meetings.filter(status='pending').count()
    completed_count = base_meetings.filter(status='completed').count()
    cancelled_count = base_meetings.filter(status='cancelled').count()

    # Calculate monthly distribution
    from django.db.models import Count
    from django.db.models.functions import TruncMonth

    monthly_meetings = base_meetings.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # Format monthly data for chart
    monthly_data = []
    for item in monthly_meetings:
        if item['month']:
            month_name = item['month'].strftime('%B %Y')
            monthly_data.append({
                'month_name': month_name,
                'count': item['count']
            })

    # If no monthly data is found, add some sample data
    if not monthly_data:
        import datetime
        current_month = datetime.datetime.now()
        for i in range(6):
            month = current_month - datetime.timedelta(days=30 * i)
            monthly_data.append({
                'month_name': month.strftime('%B %Y'),
                'count': 0
            })
        monthly_data.reverse()

    # Calculate averages
    from django.db.models import Avg, Count

    # Count tasks per meeting
    from tasks.models import Task

    # Get meetings with related tasks and add completed task counts
    # استخدام Q الذي تم استيراده في بداية الملف

    # Add counts to each meeting
    for meeting in base_meetings:
        meeting.completed_tasks_count = Task.objects.filter(
            meeting=meeting,
            status='completed'
        ).count()

    meetings_with_tasks = base_meetings.annotate(task_count=Count('tasks'))
    avg_tasks = meetings_with_tasks.aggregate(avg=Avg('task_count'))['avg'] or 0

    # Get meetings with attendees
    meetings_with_attendees = base_meetings.annotate(attendee_count=Count('attendees'))
    avg_attendees = meetings_with_attendees.aggregate(avg=Avg('attendee_count'))['avg'] or 0

    # Get all users for the creator filter
    users = User.objects.all()

    # Get current date for report header
    now = timezone.now()

    context = {
        'meetings': base_meetings.order_by('-date'),
        'pending_count': pending_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'monthly_data': monthly_data,
        'avg_tasks': avg_tasks,
        'avg_attendees': avg_attendees,
        'users': users,
        'now': now,
    }

    return render(request, 'meetings/reports.html', context)
