from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Meeting, Attendee, MeetingTask
import json
from .forms import MeetingForm, MeetingTaskStepForm, MeetingTaskStatusForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q

User = get_user_model()

@login_required
def dashboard(request):
    """عرض لوحة تحكم الاجتماعات"""
    # تصفية الاجتماعات حسب صلاحية الوصول للمستخدم
    if request.user.is_superuser:
        # المدير العام يرى جميع الاجتماعات
        accessible_meetings = Meeting.objects.all()
    else:
        # المستخدمون العاديون يرون فقط الاجتماعات التي أنشؤوها أو مدعوون إليها
        accessible_meetings = Meeting.objects.filter(
            Q(created_by=request.user) | Q(attendees__user=request.user)
        ).distinct()

    # إحصائيات الاجتماعات
    total_meetings = accessible_meetings.count()

    # اجتماعات اليوم
    today = timezone.now().date()
    today_meetings = accessible_meetings.filter(date__date=today)
    today_meetings_count = today_meetings.count()

    # اجتماعات الأسبوع
    week_start = today
    week_end = today + timedelta(days=6)
    week_meetings = accessible_meetings.filter(date__date__gte=week_start, date__date__lte=week_end).count()

    # الاجتماعات المكتملة
    completed_meetings = accessible_meetings.filter(status='completed').count()

    # الاجتماعات القادمة (من اليوم فصاعدًا، بما في ذلك الاجتماعات قيد الانتظار)
    upcoming_meetings = accessible_meetings.filter(
        date__date__gte=today,
    ).order_by('date')[:5]

    # عدد الاجتماعات القادمة (مع التركيز على الاجتماعات قيد الانتظار)
    upcoming_meetings_count = accessible_meetings.filter(
        date__date__gte=today,
        status='pending'
    ).count()
    
    context = {
        'total_meetings': total_meetings,
        'today_meetings': today_meetings_count,
        'today_meetings_list': today_meetings[:5],
        'week_meetings': week_meetings,
        'completed_meetings': completed_meetings,
        'upcoming_meetings': upcoming_meetings,
        'upcoming_meetings_count': upcoming_meetings_count,
        'today': today,
    }
    return render(request, 'meetings/dashboard.html', context)

@login_required
def meeting_list(request):
    # تصفية الاجتماعات حسب صلاحية الوصول للمستخدم
    if request.user.is_superuser:
        # المدير العام يرى جميع الاجتماعات
        meetings = Meeting.objects.all().order_by('-date')
    else:
        # المستخدمون العاديون يرون فقط الاجتماعات التي أنشؤوها أو مدعوون إليها
        meetings = Meeting.objects.filter(
            Q(created_by=request.user) | Q(attendees__user=request.user)
        ).distinct().order_by('-date')

    # تطبيق عوامل التصفية
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')
    search = request.GET.get('search')

    if date_from:
        meetings = meetings.filter(date__date__gte=date_from)

    if date_to:
        meetings = meetings.filter(date__date__lte=date_to)

    if status:
        meetings = meetings.filter(status=status)

    if search:
        meetings = meetings.filter(
            Q(title__icontains=search) | Q(topic__icontains=search)
        )

    # إضافة معلومات الحضور لكل اجتماع لتحديد إمكانية الوصول
    meetings_with_access = []
    for meeting in meetings:
        # التحقق من إمكانية الوصول للمستخدم الحالي
        user_can_access = (
            request.user.is_superuser or
            meeting.attendees.filter(user=request.user).exists() or
            meeting.created_by == request.user
        )
        meeting.user_can_access = user_can_access
        meetings_with_access.append(meeting)

    return render(request, 'meetings/meeting_list.html', {
        'meetings': meetings_with_access,
        'date_from': date_from,
        'date_to': date_to,
        'status': status,
        'search': search
    })

@login_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)

    # التحقق من صلاحية الوصول - فقط المدير العام أو الحضور أو منشئ الاجتماع
    if not (request.user.is_superuser or
            meeting.attendees.filter(user=request.user).exists() or
            meeting.created_by == request.user):
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذا الاجتماع")
        return redirect('meetings:list')
    
    # حساب إحصائيات المهام
    total_tasks = meeting.meeting_tasks.count()
    completed_count = meeting.meeting_tasks.filter(status='completed').count()
    in_progress_count = meeting.meeting_tasks.filter(status='in_progress').count()
    
    # حساب النسب المئوية للمهام
    completed_percent = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
    in_progress_percent = (in_progress_count / total_tasks * 100) if total_tasks > 0 else 0
    pending_percent = 100 - completed_percent - in_progress_percent
    
    # الحصول على قائمة المستخدمين المتاحين لإضافتهم (غير موجودين بالفعل في قائمة الحضور)
    existing_attendee_ids = meeting.attendees.values_list('user_id', flat=True)
    available_users = User.objects.exclude(id__in=existing_attendee_ids)
    
    # مع عدد المهام المخصصة لكل حضور
    attendee_task_counts = []
    for attendee in meeting.attendees.all():
        task_count = meeting.meeting_tasks.filter(assigned_to=attendee.user).count()
        attendee_task_counts.append({
            'attendee': attendee,
            'task_count': task_count
        })
    
    context = {
        'meeting': meeting,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'completed_percent': completed_percent,
        'in_progress_percent': in_progress_percent,
        'pending_percent': pending_percent,
        'available_users': available_users,
        'attendee_task_counts': attendee_task_counts
    }
    return render(request, 'meetings/meeting_detail.html', context)

@login_required
@permission_required('meetings.add_meeting', login_url='accounts:access_denied')
def meeting_create(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.save()
            
            # حفظ الحضور المحددين
            attendees = form.cleaned_data.get('attendees', [])
            for user in attendees:
                Attendee.objects.create(meeting=meeting, user=user)
            
            # معالجة المهام
            tasks_text = form.cleaned_data.get('tasks', '')
            if tasks_text:
                task_lines = [line.strip() for line in tasks_text.split('\n') if line.strip()]
                
                # معالجة تعيينات المهام
                task_assignments = {}
                task_assignments_text = form.cleaned_data.get('task_assignments', '')
                if task_assignments_text:
                    try:
                        task_assignments = json.loads(task_assignments_text)
                    except json.JSONDecodeError:
                        # إذا كان هناك خطأ في تحليل البيانات، تجاهل
                        pass
                
                # إنشاء المهام
                for i, task_description in enumerate(task_lines):
                    task_id = f"task-{i}"
                    task = MeetingTask(meeting=meeting, description=task_description)
                    
                    # إذا كانت المهمة معينة لشخص، أضف المستخدم وغير الحالة إلى قيد التنفيذ
                    if task_id in task_assignments and task_assignments[task_id]:
                        try:
                            assigned_to_id = task_assignments[task_id]
                            assigned_to = User.objects.get(id=assigned_to_id)
                            task.assigned_to = assigned_to
                            task.status = 'in_progress'
                            # إضافة تاريخ انتهاء افتراضي (بعد أسبوع من تاريخ الاجتماع)
                            task.end_date = meeting.date.date() + timedelta(days=7)
                        except User.DoesNotExist:
                            pass
                    
                    task.save()
            
            messages.success(request, "تم إنشاء الاجتماع بنجاح")
            return redirect('meetings:detail', pk=meeting.pk)
    else:
        form = MeetingForm()
    
    context = {
        'form': form, 
        'edit': False, 
        'select2_enabled': True,  # لتفعيل القائمة المنسدلة
    }
    return render(request, 'meetings/meeting_form.html', context)

@login_required
@permission_required('meetings.change_meeting', login_url='accounts:access_denied')
def meeting_edit(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            # حفظ بيانات الاجتماع
            form.save()
            
            # حفظ الحضور المحددين - أولا نحذف الحضور القدامى
            meeting.attendees.all().delete()
            attendees = form.cleaned_data.get('attendees', [])
            for user in attendees:
                Attendee.objects.create(meeting=meeting, user=user)
            
            # معالجة المهام - أولا نحذف المهام القديمة
            meeting.meeting_tasks.all().delete()
            
            # ثم نضيف المهام الجديدة
            tasks_text = form.cleaned_data.get('tasks', '')
            if tasks_text:
                task_lines = [line.strip() for line in tasks_text.split('\n') if line.strip()]
                
                # معالجة تعيينات المهام
                task_assignments = {}
                task_assignments_text = form.cleaned_data.get('task_assignments', '')
                if task_assignments_text:
                    try:
                        task_assignments = json.loads(task_assignments_text)
                    except json.JSONDecodeError:
                        # إذا كان هناك خطأ في تحليل البيانات، تجاهل
                        pass
                
                # إنشاء المهام
                for i, task_description in enumerate(task_lines):
                    task_id = f"task-{i}"
                    task = MeetingTask(meeting=meeting, description=task_description)
                    
                    # إذا كانت المهمة معينة لشخص، أضف المستخدم وغير الحالة إلى قيد التنفيذ
                    if task_id in task_assignments and task_assignments[task_id]:
                        try:
                            assigned_to_id = task_assignments[task_id]
                            assigned_to = User.objects.get(id=assigned_to_id)
                            task.assigned_to = assigned_to
                            task.status = 'in_progress'
                            # إضافة تاريخ انتهاء افتراضي (بعد أسبوع من تاريخ الاجتماع)
                            task.end_date = meeting.date.date() + timedelta(days=7)
                        except User.DoesNotExist:
                            pass
                    
                    task.save()
            
            messages.success(request, "تم تحديث الاجتماع بنجاح")
            return redirect('meetings:detail', pk=meeting.pk)
    else:
        # إعداد البيانات الحالية للنموذج
        form = MeetingForm(instance=meeting)
        
        # تحديد الحضور المحددين مسبقاً
        current_attendees = meeting.attendees.values_list('user_id', flat=True)
        if current_attendees.exists():
            form.initial['attendees'] = list(current_attendees)
        
        # إعداد المهام الحالية
        tasks = meeting.meeting_tasks.all()
        if tasks.exists():
            # تجميع وصف المهام
            tasks_text = "\n".join([task.description for task in tasks])
            form.initial['tasks'] = tasks_text
            
            # تجميع تعيينات المهام
            task_assignments = {}
            for i, task in enumerate(tasks):
                if task.assigned_to:
                    task_assignments[f"task-{i}"] = str(task.assigned_to.id)
            
            if task_assignments:
                form.initial['task_assignments'] = json.dumps(task_assignments)
    
    context = {
        'form': form, 
        'edit': True, 
        'meeting': meeting, 
        'select2_enabled': True,  # لتفعيل القائمة المنسدلة
    }
    return render(request, 'meetings/meeting_form.html', context)

@login_required
@permission_required('meetings.delete_meeting', login_url='accounts:access_denied')
def meeting_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        meeting.delete()
        messages.success(request, "تم حذف الاجتماع بنجاح")
        return redirect('meetings:list')
    return redirect('meetings:detail', pk=meeting.pk)

@login_required
@permission_required('meetings.add_attendee', login_url='accounts:access_denied')
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
@permission_required('meetings.delete_attendee', login_url='accounts:access_denied')
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
@permission_required('meetings.view_meeting', login_url='accounts:access_denied')
def calendar_view(request):
    """عرض تقويم الاجتماعات"""
    meetings = Meeting.objects.all()
    return render(request, 'meetings/calendar.html', {'meetings': meetings})

@login_required
def meeting_task_detail(request, task_id):
    """عرض تفاصيل مهمة الاجتماع مع إمكانية التحديث"""
    # الحصول على المهمة بواسطة المعرف
    task = get_object_or_404(MeetingTask, pk=task_id)

    # التحقق من صلاحية الوصول - فقط المدير العام أو المكلف بالمهمة
    if not (request.user.is_superuser or request.user == task.assigned_to):
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه المهمة")
        return redirect('meetings:detail', pk=task.meeting.pk)

    # الحصول على بيانات الاجتماع المرتبط
    meeting = task.meeting

    # معالجة إضافة خطوة جديدة
    step_form = None
    status_form = None

    if request.method == 'POST':
        if 'add_step' in request.POST:
            step_form = MeetingTaskStepForm(request.POST, meeting_task=task, user=request.user)
            if step_form.is_valid():
                step_form.save()
                messages.success(request, "تم إضافة الخطوة بنجاح")
                return redirect('meetings:task_detail', task_id=task.id)
        elif 'update_status' in request.POST:
            status_form = MeetingTaskStatusForm(request.POST, instance=task)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, "تم تحديث حالة المهمة بنجاح")
                return redirect('meetings:task_detail', task_id=task.id)

    # إنشاء النماذج للعرض
    if not step_form:
        step_form = MeetingTaskStepForm(meeting_task=task, user=request.user)
    if not status_form:
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

    # إحصائيات الخطوات
    steps_stats = None
    if steps.exists():
        completed_steps = steps.filter(completed=True).count()
        total_steps = steps.count()
        progress_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        steps_stats = {
            'completed': completed_steps,
            'total': total_steps,
            'progress_percentage': round(progress_percentage, 1)
        }

    context = {
        'task': task,
        'meeting': meeting,
        'step_form': step_form,
        'status_form': status_form,
        'steps': steps,
        'related_tasks': related_tasks,
        'meeting_tasks_stats': meeting_tasks_stats,
        'steps_stats': steps_stats,
        'is_meeting_task': True,
    }
    return render(request, 'meetings/meeting_task_detail.html', context)

@login_required
@permission_required('meetings.view_report', login_url='accounts:access_denied')
def reports(request):
    """عرض تقارير الاجتماعات"""
    # استخلاص معايير التصفية
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')
    creator = request.GET.get('creator')
    
    # تطبيق معايير التصفية على الاستعلام
    meetings = Meeting.objects.all()
    
    if date_from:
        meetings = meetings.filter(date__date__gte=date_from)
    
    if date_to:
        meetings = meetings.filter(date__date__lte=date_to)
        
    if status:
        meetings = meetings.filter(status=status)
        
    if creator:
        meetings = meetings.filter(created_by_id=creator)
    
    # إحصائيات حالة الاجتماعات
    pending_count = meetings.filter(status='pending').count()
    completed_count = meetings.filter(status='completed').count()
    cancelled_count = meetings.filter(status='cancelled').count()
    
    # بيانات الاجتماعات حسب الشهر
    monthly_data = []
    months_ar = [
        'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
    ]
    
    # الحصول على الأشهر التي تحتوي على اجتماعات
    meeting_months = meetings.dates('date', 'month')
    
    for month in meeting_months:
        month_count = meetings.filter(date__year=month.year, date__month=month.month).count()
        month_name = f"{months_ar[month.month - 1]} {month.year}"
        monthly_data.append({
            'month_name': month_name,
            'count': month_count
        })
    
    # حساب متوسط المهام والحضور لكل اجتماع
    avg_tasks = meetings.annotate(tasks_count=Count('meeting_tasks')).aggregate(avg=Avg('tasks_count'))['avg'] or 0
    avg_attendees = meetings.annotate(attendees_count=Count('attendees')).aggregate(avg=Avg('attendees_count'))['avg'] or 0
    
    # إضافة عدد المهام المكتملة لكل اجتماع
    meeting_list = []
    for meeting in meetings:
        # حساب عدد المهام المكتملة
        meeting.completed_tasks_count = meeting.meeting_tasks.filter(status='completed').count()
        meeting_list.append(meeting)
    
    # الحصول على قائمة المستخدمين للفلتر
    users = User.objects.all()
    
    # التاريخ الحالي للطباعة
    now = timezone.now()
    
    context = {
        'meetings': meeting_list,
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
