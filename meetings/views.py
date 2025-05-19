from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Meeting, Attendee
from .forms import MeetingForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q

User = get_user_model()

@login_required
@permission_required('meetings.view_meeting', raise_exception=True)
def dashboard(request):
    """عرض لوحة تحكم الاجتماعات"""
    # إحصائيات الاجتماعات
    total_meetings = Meeting.objects.count()
    today = timezone.now().date()
    today_meetings = Meeting.objects.filter(date=today)
    today_meetings_count = today_meetings.count()
    context = {
        'total_meetings': total_meetings,
        'today_meetings_count': today_meetings_count,
        'today_meetings_list': today_meetings[:5],
    }
    return render(request, 'meetings/dashboard.html', context)

@login_required
@permission_required('meetings.view_meeting', raise_exception=True)
def meeting_list(request):
    meetings = Meeting.objects.all().order_by('-date')
    return render(request, 'meetings/meeting_list.html', {'meetings': meetings})

@login_required
@permission_required('meetings.view_meeting', raise_exception=True)
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    return render(request, 'meetings/meeting_detail.html', {'meeting': meeting})

@login_required
@permission_required('meetings.add_meeting', raise_exception=True)
def meeting_create(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.save()
            form.save_m2m()
            messages.success(request, "تم إنشاء الاجتماع بنجاح")
            return redirect('meetings:detail', pk=meeting.pk)
    else:
        form = MeetingForm()
    return render(request, 'meetings/meeting_form.html', {'form': form, 'edit': False})

@login_required
@permission_required('meetings.change_meeting', raise_exception=True)
def meeting_edit(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث الاجتماع بنجاح")
            return redirect('meetings:detail', pk=meeting.pk)
    else:
        form = MeetingForm(instance=meeting)
    return render(request, 'meetings/meeting_form.html', {'form': form, 'edit': True, 'meeting': meeting})

@login_required
@permission_required('meetings.delete_meeting', raise_exception=True)
def meeting_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        meeting.delete()
        messages.success(request, "تم حذف الاجتماع بنجاح")
        return redirect('meetings:list')
    return redirect('meetings:detail', pk=meeting.pk)

@login_required
@permission_required('meetings.add_attendee', raise_exception=True)
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
@permission_required('meetings.delete_attendee', raise_exception=True)
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
@permission_required('meetings.view_meeting', raise_exception=True)
def calendar_view(request):
    """عرض تقويم الاجتماعات"""
    meetings = Meeting.objects.all()
    return render(request, 'meetings/calendar.html', {'meetings': meetings})

@login_required
@permission_required('meetings.view_report', raise_exception=True)
def reports(request):
    """عرض تقارير الاجتماعات"""
    meetings = Meeting.objects.all()
    context = {
        'meetings': meetings,
    }
    return render(request, 'meetings/reports.html', context)
