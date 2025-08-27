from datetime import datetime, date, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Sum, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import JsonResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.auth.decorators import user_passes_test
from .models import (
    AttendanceRecord,
    EmployeeAttendanceProfile,
    LeaveBalance,
    LeaveType,
    AttendanceRule,
    WorkSchedule,
    EmployeeAttendance,
    AttendanceRules,
    ZKDevice,
    ZKAttendanceRaw,
    EmployeeDeviceMapping,
    AttendanceProcessingLog,
    AttendanceSummary
)
from employees.models import Employee
from .zk_service import (
    ZKDataProcessor,
    test_device_connection,
    manual_sync_device
)


class AttendanceRecordListView(LoginRequiredMixin, ListView):
    """View for listing attendance records"""
    model = AttendanceRecord
    template_name = 'attendance/record_list.html'
    context_object_name = 'records'
    paginate_by = 30

    def get_queryset(self):
        queryset = AttendanceRecord.objects.select_related('employee')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        employee_id = self.request.GET.get('employee')
        record_type = self.request.GET.get('record_type')

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if record_type:
            queryset = queryset.filter(record_type=record_type)

        return queryset.order_by('-date', 'employee__emp_full_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['record_types'] = AttendanceRecord.RECORD_TYPE_CHOICES
        return context


@login_required
def mark_attendance(request):
    """View for marking attendance"""
    if request.method == 'POST':
        employee = get_object_or_404(Employee, user=request.user)
        record_type = request.POST.get('record_type')

        # Check if employee has already marked attendance for today
        today = timezone.localtime().date()
        existing_record = AttendanceRecord.objects.filter(
            employee=employee,
            date=today,
            record_type=record_type
        ).exists()

        if existing_record:
            messages.warning(request, _('لقد قمت بتسجيل الحضور/الانصراف بالفعل اليوم'))
            return redirect('attendance:dashboard')

        # Create new attendance record
        AttendanceRecord.objects.create(
            employee=employee,
            record_type=record_type,
            date=today,
            time=timezone.localtime().time(),
        )

        messages.success(request, _('تم تسجيل الحضور/الانصراف بنجاح'))
        return redirect('attendance:dashboard')

    return render(request, 'attendance/mark_attendance.html', {
        'record_types': AttendanceRecord.RECORD_TYPE_CHOICES
    })


class LeaveBalanceListView(LoginRequiredMixin, ListView):
    """View for listing leave balances"""
    model = LeaveBalance
    template_name = 'attendance/leave_balance_list.html'
    context_object_name = 'balances'

    def get_queryset(self):
        employee_id = self.request.GET.get('employee')
        year = self.request.GET.get('year', date.today().year)

        queryset = LeaveBalance.objects.select_related('employee', 'leave_type')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        return queryset.filter(year=year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['current_year'] = date.today().year
        return context


@login_required
def attendance_dashboard(request):
    """لوحة تحكم الحضور والانصراف"""
    today = timezone.localtime().date()

    # إحصائيات اليوم من جدول EmployeeAttendance
    today_stats = EmployeeAttendance.objects.filter(att_date=today).aggregate(
        present=Count('att_id', filter=Q(status='Present')),
        absent=Count('att_id', filter=Q(status='Absent')),
        leave=Count('att_id', filter=Q(status='Leave')),
        late=Count('att_id', filter=Q(status='Late'))
    )

    # إجمالي عدد الموظفين النشطين
    total_employees = Employee.objects.filter(emp_status='Active').count()

    # حساب النسب المئوية
    if total_employees > 0:
        absence_percentage = round((today_stats['absent'] / total_employees) * 100, 1)
    else:
        absence_percentage = 0

    # متوسط دقائق التأخير
    late_records = EmployeeAttendance.objects.filter(
        att_date=today,
        status='Late'
    )
    avg_late_minutes = 0
    if late_records.exists():
        total_late_minutes = sum([record.calculate_late_minutes() for record in late_records])
        avg_late_minutes = round(total_late_minutes / late_records.count(), 1)

    # حضور المستخدم الحالي إذا كان موظفاً
    user_attendance = None
    if hasattr(request.user, 'employee'):
        user_attendance = EmployeeAttendance.objects.filter(
            emp=request.user.employee,
            att_date=today
        ).first()

    # جدول العمل للموظف
    work_schedule = None
    if hasattr(request.user, 'employee'):
        # البحث عن قاعدة الحضور الافتراضية أو المخصصة للموظف
        default_rule = AttendanceRules.objects.filter(is_default=True).first()
        if default_rule:
            work_schedule = {
                'start_time': default_rule.shift_start,
                'end_time': default_rule.shift_end
            }

    # آخر تسجيلات الحضور
    recent_records = EmployeeAttendance.objects.select_related('emp').filter(
        att_date=today
    ).order_by('-check_in')[:10]

    # إحصائيات الأقسام
    from employees.models import Department
    department_stats = []
    departments = Department.objects.filter(is_active=True)
    
    for dept in departments:
        dept_employees = Employee.objects.filter(department=dept, emp_status='Active')
        dept_attendance = EmployeeAttendance.objects.filter(
            emp__in=dept_employees,
            att_date=today
        ).aggregate(
            present_count=Count('att_id', filter=Q(status='Present')),
            absent_count=Count('att_id', filter=Q(status='Absent')),
            late_count=Count('att_id', filter=Q(status='Late'))
        )
        
        department_stats.append({
            'dept_name': dept.dept_name,
            'total_employees': dept_employees.count(),
            'present_count': dept_attendance['present_count'],
            'absent_count': dept_attendance['absent_count'],
            'late_count': dept_attendance['late_count']
        })

    # بيانات الرسم البياني الأسبوعي
    from datetime import timedelta
    weekly_data = {'present': [], 'absent': [], 'late': []}
    
    for i in range(7):
        day = today - timedelta(days=6-i)
        day_stats = EmployeeAttendance.objects.filter(att_date=day).aggregate(
            present=Count('att_id', filter=Q(status='Present')),
            absent=Count('att_id', filter=Q(status='Absent')),
            late=Count('att_id', filter=Q(status='Late'))
        )
        weekly_data['present'].append(day_stats['present'])
        weekly_data['absent'].append(day_stats['absent'])
        weekly_data['late'].append(day_stats['late'])

    context = {
        'today_stats': today_stats,
        'total_employees': total_employees,
        'absence_percentage': absence_percentage,
        'avg_late_minutes': avg_late_minutes,
        'user_attendance': user_attendance,
        'work_schedule': work_schedule,
        'recent_records': recent_records,
        'department_stats': department_stats,
        'weekly_present_data': weekly_data['present'],
        'weekly_absent_data': weekly_data['absent'],
        'weekly_late_data': weekly_data['late'],
        'now': timezone.localtime(),
    }

    return render(request, 'attendance/dashboard.html', context)


# ==== CRUD for AttendanceRules and EmployeeAttendance (schema-specific) ====
from .models import AttendanceRules, EmployeeAttendance
from .forms import AttendanceRulesForm, EmployeeAttendanceForm

@login_required
def attendance_rules_list(request):
    items = AttendanceRules.objects.all().order_by('rule_name')
    return render(request, 'attendance/rules_list.html', {'items': items})

@login_required
def attendance_rules_create(request):
    if request.method == 'POST':
        form = AttendanceRulesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم إضافة قاعدة حضور'))
            return redirect('attendance:rules_list')
    else:
        form = AttendanceRulesForm()
    return render(request, 'attendance/rules_form.html', {'form': form, 'title': 'إضافة قاعدة حضور'})

@login_required
def attendance_rules_edit(request, pk):
    item = get_object_or_404(AttendanceRules, pk=pk)
    if request.method == 'POST':
        form = AttendanceRulesForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تعديل قاعدة الحضور'))
            return redirect('attendance:rules_list')
    else:
        form = AttendanceRulesForm(instance=item)
    return render(request, 'attendance/rules_form.html', {'form': form, 'title': 'تعديل قاعدة حضور'})

@login_required
def attendance_rules_delete(request, pk):
    item = get_object_or_404(AttendanceRules, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, _('تم حذف قاعدة الحضور'))
        return redirect('attendance:rules_list')
    return render(request, 'attendance/rules_confirm_delete.html', {'item': item})


@login_required
def employee_attendance_list(request):
    items = EmployeeAttendance.objects.select_related('emp', 'rule').order_by('-att_date')
    return render(request, 'attendance/emp_att_list.html', {'items': items})

@login_required
def employee_attendance_create(request):
    if request.method == 'POST':
        form = EmployeeAttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم إضافة سجل حضور'))
            return redirect('attendance:emp_att_list')
    else:
        form = EmployeeAttendanceForm()
    return render(request, 'attendance/emp_att_form.html', {'form': form, 'title': 'إضافة سجل حضور'})

@login_required
def employee_attendance_edit(request, pk):
    item = get_object_or_404(EmployeeAttendance, pk=pk)
    if request.method == 'POST':
        form = EmployeeAttendanceForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تعديل سجل الحضور'))
            return redirect('attendance:emp_att_list')
    else:
        form = EmployeeAttendanceForm(instance=item)
    return render(request, 'attendance/emp_att_form.html', {'form': form, 'title': 'تعديل سجل حضور'})

@login_required
def employee_attendance_delete(request, pk):
    item = get_object_or_404(EmployeeAttendance, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, _('تم حذف سجل الحضور'))
        return redirect('attendance:emp_att_list')
    return render(request, 'attendance/emp_att_confirm_delete.html', {'item': item})

# Additional Views for Attendance Management

@login_required
def dashboard(request):
    """لوحة تحكم الحضور"""
    return attendance_dashboard(request)


@login_required
def record_list(request):
    """قائمة سجلات الحضور"""
    view = AttendanceRecordListView()
    view.request = request
    return view.get(request)


@login_required
def add_record(request):
    """إضافة سجل حضور جديد"""
    from .forms import EmployeeAttendanceForm
    
    if request.method == 'POST':
        form = EmployeeAttendanceForm(request.POST)
        if form.is_valid():
            record = form.save()
            messages.success(request, 'تم إضافة سجل الحضور بنجاح.')
            return redirect('attendance:record_list')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeAttendanceForm()
    
    context = {
        'form': form,
        'title': 'إضافة سجل حضور جديد'
    }
    
    return render(request, 'attendance/record_form.html', context)


@login_required
def record_detail(request, record_id):
    """تفاصيل سجل الحضور"""
    record = get_object_or_404(EmployeeAttendance, att_id=record_id)
    
    context = {
        'record': record,
    }
    
    return render(request, 'attendance/record_detail.html', context)


@login_required
def edit_record(request, record_id):
    """تعديل سجل حضور"""
    record = get_object_or_404(EmployeeAttendance, att_id=record_id)
    
    if request.method == 'POST':
        form = EmployeeAttendanceForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save()
            messages.success(request, 'تم تحديث سجل الحضور بنجاح.')
            return redirect('attendance:record_detail', record_id=record.att_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeAttendanceForm(instance=record)
    
    context = {
        'form': form,
        'record': record,
        'title': 'تعديل سجل الحضور'
    }
    
    return render(request, 'attendance/record_form.html', context)


@login_required
def delete_record(request, record_id):
    """حذف سجل حضور"""
    record = get_object_or_404(EmployeeAttendance, att_id=record_id)
    
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'تم حذف سجل الحضور بنجاح.')
        return redirect('attendance:record_list')
    
    context = {
        'record': record,
    }
    
    return render(request, 'attendance/record_confirm_delete.html', context)


@login_required
def rules_list(request):
    """قائمة قواعد الحضور"""
    return attendance_rules_list(request)


@login_required
def add_rule(request):
    """إضافة قاعدة حضور جديدة"""
    return attendance_rules_create(request)


@login_required
def get_rule(request, rule_id):
    """جلب قاعدة حضور"""
    rule = get_object_or_404(AttendanceRules, rule_id=rule_id)
    
    context = {
        'rule': rule,
    }
    
    return render(request, 'attendance/rule_detail.html', context)


@login_required
def update_rule(request, rule_id):
    """تحديث قاعدة حضور"""
    return attendance_rules_edit(request, rule_id)


@login_required
def delete_rule(request, rule_id):
    """حذف قاعدة حضور"""
    return attendance_rules_delete(request, rule_id)


@login_required
def set_default_rule(request, rule_id):
    """تعيين قاعدة حضور كافتراضية"""
    rule = get_object_or_404(AttendanceRules, rule_id=rule_id)
    
    # إزالة الافتراضية من جميع القواعد
    AttendanceRules.objects.all().update(is_default=False)
    
    # تعيين القاعدة الحالية كافتراضية
    rule.is_default = True
    rule.save()
    
    messages.success(request, f'تم تعيين قاعدة "{rule.rule_name}" كقاعدة افتراضية.')
    return redirect('attendance:rules_list')


@login_required
def reports(request):
    """تقارير الحضور"""
    from django.db.models import Count, Avg
    from datetime import datetime, timedelta
    
    # إحصائيات عامة
    total_records = EmployeeAttendance.objects.count()
    today = date.today()
    this_month = EmployeeAttendance.objects.filter(
        att_date__year=today.year,
        att_date__month=today.month
    ).count()
    
    # إحصائيات الحضور اليومي
    daily_stats = EmployeeAttendance.objects.filter(
        att_date__gte=today - timedelta(days=7)
    ).values('att_date').annotate(
        count=Count('att_id')
    ).order_by('att_date')
    
    # إحصائيات الموظفين
    employee_stats = EmployeeAttendance.objects.values(
        'emp__first_name', 'emp__last_name'
    ).annotate(
        attendance_count=Count('att_id')
    ).order_by('-attendance_count')[:10]
    
    context = {
        'total_records': total_records,
        'this_month': this_month,
        'daily_stats': daily_stats,
        'employee_stats': employee_stats,
    }
    
    return render(request, 'attendance/reports.html', context)


@login_required
def export_attendance(request):
    """تصدير بيانات الحضور"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['الموظف', 'التاريخ', 'وقت الدخول', 'وقت الخروج', 'الحالة'])
    
    records = EmployeeAttendance.objects.select_related('emp').all()
    for record in records:
        writer.writerow([
            f"{record.emp.first_name} {record.emp.last_name}",
            record.att_date,
            record.check_in,
            record.check_out,
            record.status
        ])
    
    return response


@login_required
def monthly_report(request):
    """تقرير شهري للحضور"""
    from django.db.models import Count
    
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # إحصائيات الشهر
    monthly_stats = EmployeeAttendance.objects.filter(
        att_date__year=year,
        att_date__month=month
    ).aggregate(
        total_records=Count('att_id'),
        present_count=Count('att_id', filter=Q(status='Present')),
        absent_count=Count('att_id', filter=Q(status='Absent')),
        late_count=Count('att_id', filter=Q(status='Late'))
    )
    
    # تفاصيل يومية
    daily_details = EmployeeAttendance.objects.filter(
        att_date__year=year,
        att_date__month=month
    ).values('att_date').annotate(
        count=Count('att_id')
    ).order_by('att_date')
    
    context = {
        'year': year,
        'month': month,
        'monthly_stats': monthly_stats,
        'daily_details': daily_details,
    }
    
    return render(request, 'attendance/monthly_report.html', context)


@login_required
def employee_attendance_report(request, emp_id):
    """تقرير حضور موظف محدد"""
    from employees.models import Employee
    
    employee = get_object_or_404(Employee, emp_id=emp_id)
    
    # فترة التقرير
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if not date_from:
        date_from = date.today() - timedelta(days=30)
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if not date_to:
        date_to = date.today()
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # سجلات الحضور
    attendance_records = EmployeeAttendance.objects.filter(
        emp=employee,
        att_date__range=[date_from, date_to]
    ).order_by('att_date')
    
    # إحصائيات
    stats = attendance_records.aggregate(
        total_days=Count('att_id'),
        present_days=Count('att_id', filter=Q(status='Present')),
        absent_days=Count('att_id', filter=Q(status='Absent')),
        late_days=Count('att_id', filter=Q(status='Late'))
    )
    
    context = {
        'employee': employee,
        'attendance_records': attendance_records,
        'stats': stats,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'attendance/employee_report.html', context)


@login_required
def record_attendance(request):
    """تسجيل الحضور"""
    return mark_attendance(request)


@login_required
def check_in(request):
    """تسجيل الدخول"""
    if request.method == 'POST':
        # البحث عن الموظف
        emp_id = request.POST.get('emp_id')
        if not emp_id:
            messages.error(request, 'يرجى تحديد الموظف.')
            return redirect('attendance:dashboard')
        
        employee = get_object_or_404(Employee, emp_id=emp_id)
        today = date.today()
        
        # التحقق من وجود سجل لليوم
        existing_record = EmployeeAttendance.objects.filter(
            emp=employee,
            att_date=today
        ).first()
        
        if existing_record and existing_record.check_in:
            messages.warning(request, 'تم تسجيل الدخول مسبقاً لهذا اليوم.')
            return redirect('attendance:dashboard')
        
        # إنشاء أو تحديث السجل
        if existing_record:
            existing_record.check_in = timezone.now()
            existing_record.status = 'Present'
            existing_record.save()
        else:
            EmployeeAttendance.objects.create(
                emp=employee,
                att_date=today,
                check_in=timezone.now(),
                status='Present'
            )
        
        messages.success(request, f'تم تسجيل دخول {employee.first_name} {employee.last_name} بنجاح.')
        return redirect('attendance:dashboard')
    
    return render(request, 'attendance/check_in.html')


@login_required
def check_out(request):
    """تسجيل الخروج"""
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        if not emp_id:
            messages.error(request, 'يرجى تحديد الموظف.')
            return redirect('attendance:dashboard')
        
        employee = get_object_or_404(Employee, emp_id=emp_id)
        today = date.today()
        
        # البحث عن سجل اليوم
        record = EmployeeAttendance.objects.filter(
            emp=employee,
            att_date=today
        ).first()
        
        if not record or not record.check_in:
            messages.error(request, 'لم يتم تسجيل الدخول لهذا اليوم.')
            return redirect('attendance:dashboard')
        
        if record.check_out:
            messages.warning(request, 'تم تسجيل الخروج مسبقاً لهذا اليوم.')
            return redirect('attendance:dashboard')
        
        # تسجيل الخروج
        record.check_out = timezone.now()
        record.save()
        
        messages.success(request, f'تم تسجيل خروج {employee.first_name} {employee.last_name} بنجاح.')
        return redirect('attendance:dashboard')
    
    return render(request, 'attendance/check_out.html')


@login_required
def profile(request):
    """ملف الحضور الشخصي"""
    # هذه الدالة للموظف لعرض حضوره الشخصي
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'لا يمكن الوصول لهذه الصفحة.')
        return redirect('attendance:dashboard')
    
    employee = request.user.employee
    
    # سجلات الحضور الأخيرة
    recent_records = EmployeeAttendance.objects.filter(
        emp=employee
    ).order_by('-att_date')[:10]
    
    # إحصائيات الشهر الحالي
    today = date.today()
    monthly_stats = EmployeeAttendance.objects.filter(
        emp=employee,
        att_date__year=today.year,
        att_date__month=today.month
    ).aggregate(
        total_days=Count('att_id'),
        present_days=Count('att_id', filter=Q(status='Present')),
        absent_days=Count('att_id', filter=Q(status='Absent')),
        late_days=Count('att_id', filter=Q(status='Late'))
    )
    
    context = {
        'employee': employee,
        'recent_records': recent_records,
        'monthly_stats': monthly_stats,
    }
    
    return render(request, 'attendance/profile.html', context)


@login_required
def my_attendance(request):
    """حضوري الشخصي"""
    return profile(request)


# AJAX Views
from django.http import JsonResponse

@login_required
def get_attendance_status(request, emp_id):
    """جلب حالة حضور الموظف"""
    try:
        employee = Employee.objects.get(emp_id=emp_id)
        today = date.today()
        
        record = EmployeeAttendance.objects.filter(
            emp=employee,
            att_date=today
        ).first()
        
        data = {
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'has_checked_in': bool(record and record.check_in),
            'has_checked_out': bool(record and record.check_out),
            'check_in_time': record.check_in.strftime('%H:%M') if record and record.check_in else None,
            'check_out_time': record.check_out.strftime('%H:%M') if record and record.check_out else None,
            'status': record.status if record else 'غير محدد'
        }
        
        return JsonResponse(data)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'الموظف غير موجود'}, status=404)


@login_required
def calculate_work_hours(request):
    """حساب ساعات العمل"""
    emp_id = request.GET.get('emp_id')
    date_str = request.GET.get('date')
    
    if not emp_id or not date_str:
        return JsonResponse({'error': 'بيانات ناقصة'}, status=400)
    
    try:
        employee = Employee.objects.get(emp_id=emp_id)
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        record = EmployeeAttendance.objects.filter(
            emp=employee,
            att_date=target_date
        ).first()
        
        if record and record.check_in and record.check_out:
            work_duration = record.check_out - record.check_in
            hours = work_duration.total_seconds() / 3600
            
            data = {
                'work_hours': round(hours, 2),
                'work_duration': str(work_duration),
                'check_in': record.check_in.strftime('%H:%M'),
                'check_out': record.check_out.strftime('%H:%M')
            }
        else:
            data = {
                'work_hours': 0,
                'work_duration': '00:00:00',
                'check_in': None,
                'check_out': None
            }
        
        return JsonResponse(data)
    except (Employee.DoesNotExist, ValueError):
        return JsonResponse({'error': 'بيانات غير صحيحة'}, status=400)


@login_required
def attendance_summary(request, emp_id):
    """ملخص حضور الموظف"""
    try:
        employee = Employee.objects.get(emp_id=emp_id)
        
        # الشهر الحالي
        today = date.today()
        monthly_records = EmployeeAttendance.objects.filter(
            emp=employee,
            att_date__year=today.year,
            att_date__month=today.month
        )
        
        summary = monthly_records.aggregate(
            total_days=Count('att_id'),
            present_days=Count('att_id', filter=Q(status='Present')),
            absent_days=Count('att_id', filter=Q(status='Absent')),
            late_days=Count('att_id', filter=Q(status='Late'))
        )
        
        # حساب النسب المئوية
        total = summary['total_days'] or 1
        summary['present_percentage'] = round((summary['present_days'] / total) * 100, 1)
        summary['absent_percentage'] = round((summary['absent_days'] / total) * 100, 1)
        summary['late_percentage'] = round((summary['late_days'] / total) * 100, 1)
        
        return JsonResponse(summary)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'الموظف غير موجود'}, status=404)


# Bulk Operations
@login_required
def bulk_import_attendance(request):
    """استيراد سجلات الحضور بالجملة"""
    if request.method == 'POST':
        # معالجة ملف الاستيراد
        pass
    
    return render(request, 'attendance/bulk_import.html')


@login_required
def bulk_export_attendance(request):
    """تصدير سجلات الحضور بالجملة"""
    return export_attendance(request)


@login_required
def bulk_approve_attendance(request):
    """اعتماد سجلات الحضور بالجملة"""
    if request.method == 'POST':
        record_ids = request.POST.getlist('record_ids')
        if record_ids:
            EmployeeAttendance.objects.filter(
                att_id__in=record_ids
            ).update(status='Approved')
            
            messages.success(request, f'تم اعتماد {len(record_ids)} سجل حضور.')
        else:
            messages.warning(request, 'لم يتم تحديد أي سجلات.')
    
    return redirect('attendance:record_list')


# Time Tracking
@login_required
def time_tracking(request):
    """تتبع الوقت"""
    employees = Employee.objects.filter(emp_status='Active').order_by('first_name')
    
    # سجلات اليوم
    today = date.today()
    today_records = EmployeeAttendance.objects.filter(
        att_date=today
    ).select_related('emp')
    
    context = {
        'employees': employees,
        'today_records': today_records,
        'today': today,
    }
    
    return render(request, 'attendance/time_tracking.html', context)


@login_required
def overtime_records(request):
    """سجلات الوقت الإضافي"""
    # هنا يمكن إضافة منطق حساب الوقت الإضافي
    records = EmployeeAttendance.objects.filter(
        check_in__isnull=False,
        check_out__isnull=False
    ).select_related('emp').order_by('-att_date')
    
    context = {
        'records': records,
    }
    
    return render(request, 'attendance/overtime_records.html', context)


# =============================================================================
# ZK DEVICE MANAGEMENT VIEWS
# =============================================================================

@user_passes_test(lambda u: u.is_superuser)
def zk_devices_list(request):
    """قائمة أجهزة ZK"""
    devices = ZKDevice.objects.all().order_by('device_name')
    
    context = {
        'devices': devices,
    }
    
    return render(request, 'attendance/zk_devices_list.html', context)


@user_passes_test(lambda u: u.is_superuser)
def zk_device_create(request):
    """إضافة جهاز ZK جديد"""
    from .forms import ZKDeviceForm
    
    if request.method == 'POST':
        form = ZKDeviceForm(request.POST)
        if form.is_valid():
            device = form.save()
            messages.success(request, f'تم إضافة جهاز {device.device_name} بنجاح.')
            return redirect('attendance:zk_devices_list')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = ZKDeviceForm()
    
    context = {
        'form': form,
        'title': 'إضافة جهاز ZK جديد'
    }
    
    return render(request, 'attendance/zk_device_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def zk_device_edit(request, device_id):
    """تعديل جهاز ZK"""
    from .forms import ZKDeviceForm
    
    device = get_object_or_404(ZKDevice, device_id=device_id)
    
    if request.method == 'POST':
        form = ZKDeviceForm(request.POST, instance=device)
        if form.is_valid():
            device = form.save()
            messages.success(request, f'تم تحديث جهاز {device.device_name} بنجاح.')
            return redirect('attendance:zk_devices_list')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = ZKDeviceForm(instance=device)
    
    context = {
        'form': form,
        'device': device,
        'title': f'تعديل جهاز {device.device_name}'
    }
    
    return render(request, 'attendance/zk_device_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def zk_device_delete(request, device_id):
    """حذف جهاز ZK"""
    device = get_object_or_404(ZKDevice, device_id=device_id)
    
    if request.method == 'POST':
        device_name = device.device_name
        device.delete()
        messages.success(request, f'تم حذف جهاز {device_name} بنجاح.')
        return redirect('attendance:zk_devices_list')
    
    context = {
        'device': device,
    }
    
    return render(request, 'attendance/zk_device_confirm_delete.html', context)


@user_passes_test(lambda u: u.is_superuser)
def zk_device_test(request, device_id):
    """اختبار الاتصال بجهاز ZK"""
    device = get_object_or_404(ZKDevice, device_id=device_id)
    
    if request.method == 'POST':
        result = test_device_connection(device_id)
        
        if result['connection_status']:
            messages.success(request, f'تم الاتصال بجهاز {device.device_name} بنجاح.')
        else:
            messages.error(request, f'فشل الاتصال بجهاز {device.device_name}: {result.get("error_message", "خطأ غير معروف")}')
        
        return JsonResponse(result)
    
    return JsonResponse({'error': 'طريقة غير صحيحة'}, status=405)


@user_passes_test(lambda u: u.is_superuser)
def zk_device_sync(request, device_id):
    """مزامنة بيانات جهاز ZK"""
    device = get_object_or_404(ZKDevice, device_id=device_id)
    
    if request.method == 'POST':
        days = int(request.POST.get('days', 7))
        result = manual_sync_device(device_id, days)
        
        if result['success']:
            messages.success(
                request,
                f'تم سحب {result["records_fetched"]} سجل من جهاز {device.device_name}. '
                f'تم معالجة {result["records_processed"]} سجل بنجاح.'
            )
        else:
            messages.error(
                request,
                f'فشلت عملية المزامنة: {result.get("error_message", "خطأ غير معروف")}'
            )
        
        return JsonResponse(result)
    
    context = {
        'device': device,
    }
    
    return render(request, 'attendance/zk_device_sync.html', context)


@user_passes_test(lambda u: u.is_superuser)
def zk_device_info(request, device_id):
    """معلومات جهاز ZK"""
    device = get_object_or_404(ZKDevice, device_id=device_id)
    
    # آخر سجلات المعالجة
    recent_logs = AttendanceProcessingLog.objects.filter(
        device=device
    ).order_by('-created_at')[:10]
    
    # إحصائيات الجهاز
    total_raw_records = ZKAttendanceRaw.objects.filter(device=device).count()
    processed_records = ZKAttendanceRaw.objects.filter(
        device=device, 
        is_processed=True
    ).count()
    unprocessed_records = total_raw_records - processed_records
    
    # آخر مزامنة
    last_sync = device.last_sync
    
    context = {
        'device': device,
        'recent_logs': recent_logs,
        'total_raw_records': total_raw_records,
        'processed_records': processed_records,
        'unprocessed_records': unprocessed_records,
        'last_sync': last_sync,
    }
    
    return render(request, 'attendance/zk_device_info.html', context)


@user_passes_test(lambda u: u.is_superuser)
def zk_raw_data(request):
    """البيانات الخام من أجهزة ZK"""
    # التصفية
    device_id = request.GET.get('device')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    processed = request.GET.get('processed')
    
    queryset = ZKAttendanceRaw.objects.select_related('device', 'employee')
    
    if device_id:
        queryset = queryset.filter(device_id=device_id)
    if date_from:
        queryset = queryset.filter(timestamp__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(timestamp__date__lte=date_to)
    if processed == 'true':
        queryset = queryset.filter(is_processed=True)
    elif processed == 'false':
        queryset = queryset.filter(is_processed=False)
    
    queryset = queryset.order_by('-timestamp')
    
    # ترقيم الصفحات
    paginator = Paginator(queryset, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'devices': ZKDevice.objects.all(),
        'current_filters': {
            'device': device_id,
            'date_from': date_from,
            'date_to': date_to,
            'processed': processed,
        }
    }
    
    return render(request, 'attendance/zk_raw_data.html', context)


@user_passes_test(lambda u: u.is_superuser)
def zk_employee_mapping(request):
    """ربط الموظفين بأجهزة ZK"""
    mappings = EmployeeDeviceMapping.objects.select_related(
        'employee', 'device'
    ).order_by('device__device_name', 'employee__emp_code')
    
    context = {
        'mappings': mappings,
    }
    
    return render(request, 'attendance/zk_employee_mapping.html', context)


@user_passes_test(lambda u: u.is_superuser)
def zk_create_mapping(request):
    """إضافة ربط موظف بجهاز ZK"""
    from .forms import EmployeeDeviceMappingForm
    
    if request.method == 'POST':
        form = EmployeeDeviceMappingForm(request.POST)
        if form.is_valid():
            mapping = form.save()
            messages.success(
                request,
                f'تم ربط {mapping.employee.emp_code} بجهاز {mapping.device.device_name} بنجاح.'
            )
            return redirect('attendance:zk_employee_mapping')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeDeviceMappingForm()
    
    context = {
        'form': form,
        'title': 'ربط موظف بجهاز ZK'
    }
    
    return render(request, 'attendance/zk_mapping_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def zk_edit_mapping(request, mapping_id):
    """تعديل ربط موظف بجهاز ZK"""
    from .forms import EmployeeDeviceMappingForm
    
    mapping = get_object_or_404(EmployeeDeviceMapping, mapping_id=mapping_id)
    
    if request.method == 'POST':
        form = EmployeeDeviceMappingForm(request.POST, instance=mapping)
        if form.is_valid():
            mapping = form.save()
            messages.success(request, 'تم تحديث الربط بنجاح.')
            return redirect('attendance:zk_employee_mapping')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeDeviceMappingForm(instance=mapping)
    
    context = {
        'form': form,
        'mapping': mapping,
        'title': 'تعديل ربط الموظف بجهاز ZK'
    }
    
    return render(request, 'attendance/zk_mapping_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def zk_delete_mapping(request, mapping_id):
    """حذف ربط موظف بجهاز ZK"""
    mapping = get_object_or_404(EmployeeDeviceMapping, mapping_id=mapping_id)
    
    if request.method == 'POST':
        mapping.delete()
        messages.success(request, 'تم حذف الربط بنجاح.')
        return redirect('attendance:zk_employee_mapping')
    
    context = {
        'mapping': mapping,
    }
    
    return render(request, 'attendance/zk_mapping_confirm_delete.html', context)


@user_passes_test(lambda u: u.is_superuser)
def zk_sync_all_devices(request):
    """مزامنة جميع أجهزة ZK"""
    if request.method == 'POST':
        try:
            logs = ZKDataProcessor.process_all_devices()
            
            total_fetched = sum(log.records_fetched for log in logs)
            total_processed = sum(log.records_processed for log in logs)
            total_failed = sum(log.records_failed for log in logs)
            
            messages.success(
                request,
                f'تم سحب {total_fetched} سجل من {len(logs)} جهاز. '
                f'تم معالجة {total_processed} سجل بنجاح و {total_failed} سجل فشل.'
            )
            
            return JsonResponse({
                'success': True,
                'devices_processed': len(logs),
                'total_fetched': total_fetched,
                'total_processed': total_processed,
                'total_failed': total_failed
            })
            
        except Exception as e:
            messages.error(request, f'خطأ في المزامنة: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'طريقة غير صحيحة'}, status=405)


@user_passes_test(lambda u: u.is_superuser)
def zk_processing_logs(request):
    """سجلات معالجة أجهزة ZK"""
    logs = AttendanceProcessingLog.objects.select_related('device').order_by('-created_at')
    
    # التصفية
    device_id = request.GET.get('device')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    
    if device_id:
        logs = logs.filter(device_id=device_id)
    if status:
        logs = logs.filter(status=status)
    if date_from:
        logs = logs.filter(process_date__gte=date_from)
    
    # ترقيم الصفحات
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'devices': ZKDevice.objects.all(),
        'current_filters': {
            'device': device_id,
            'status': status,
            'date_from': date_from,
        }
    }
    
    return render(request, 'attendance/zk_processing_logs.html', context)


# AJAX Views for ZK Management
@user_passes_test(lambda u: u.is_superuser)
def ajax_zk_device_status(request, device_id):
    """جلب حالة جهاز ZK عبر AJAX"""
    try:
        device = ZKDevice.objects.get(device_id=device_id)
        
        # فحص الاتصال
        is_online = device.is_online()
        
        # آخر مزامنة
        last_sync = device.last_sync.strftime('%Y-%m-%d %H:%M') if device.last_sync else 'لم يتم'
        
        # عدد السجلات غير المعالجة
        unprocessed_count = ZKAttendanceRaw.objects.filter(
            device=device,
            is_processed=False
        ).count()
        
        data = {
            'device_name': device.device_name,
            'is_online': is_online,
            'status': device.status,
            'last_sync': last_sync,
            'unprocessed_count': unprocessed_count,
            'ip_address': device.ip_address,
            'location': device.location or 'غير محدد'
        }
        
        return JsonResponse(data)
        
    except ZKDevice.DoesNotExist:
        return JsonResponse({'error': 'الجهاز غير موجود'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@user_passes_test(lambda u: u.is_superuser)
def ajax_process_raw_record(request, raw_id):
    """معالجة سجل خام واحد عبر AJAX"""
    try:
        raw_record = ZKAttendanceRaw.objects.get(raw_id=raw_id)
        
        if raw_record.is_processed:
            return JsonResponse({
                'success': False,
                'message': 'السجل تم معالجته مسبقاً'
            })
        
        # معالجة السجل
        ZKDataProcessor._create_attendance_record(raw_record)
        
        return JsonResponse({
            'success': True,
            'message': 'تم معالجة السجل بنجاح'
        })
        
    except ZKAttendanceRaw.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'السجل غير موجود'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في المعالجة: {str(e)}'
        }, status=500)


# Attendance Summary and Analytics
@login_required
def attendance_analytics(request):
    """تحليلات الحضور"""
    from django.db.models import Count, Avg, Sum
    from datetime import timedelta
    
    today = date.today()
    last_30_days = today - timedelta(days=30)
    
    # إحصائيات عامة
    total_employees = Employee.objects.filter(emp_status='Active').count()
    total_attendance_records = EmployeeAttendance.objects.count()
    
    # إحصائيات آخر 30 يوم
    recent_stats = EmployeeAttendance.objects.filter(
        att_date__gte=last_30_days
    ).aggregate(
        total_records=Count('att_id'),
        present_records=Count('att_id', filter=Q(status='Present')),
        absent_records=Count('att_id', filter=Q(status='Absent')),
        late_records=Count('att_id', filter=Q(status='Late'))
    )
    
    # حساب النسب المئوية
    if recent_stats['total_records'] > 0:
        recent_stats['present_rate'] = round(
            (recent_stats['present_records'] / recent_stats['total_records']) * 100, 1
        )
        recent_stats['absent_rate'] = round(
            (recent_stats['absent_records'] / recent_stats['total_records']) * 100, 1
        )
        recent_stats['late_rate'] = round(
            (recent_stats['late_records'] / recent_stats['total_records']) * 100, 1
        )
    else:
        recent_stats.update({
            'present_rate': 0,
            'absent_rate': 0,
            'late_rate': 0
        })
    
    # أفضل الموظفين حضوراً
    top_employees = EmployeeAttendance.objects.filter(
        att_date__gte=last_30_days,
        status='Present'
    ).values(
        'emp__emp_code',
        'emp__first_name',
        'emp__last_name'
    ).annotate(
        attendance_count=Count('att_id')
    ).order_by('-attendance_count')[:10]
    
    # إحصائيات شهرية
    monthly_data = []
    for i in range(6):
        month_start = today.replace(day=1) - timedelta(days=i*30)
        month_end = month_start + timedelta(days=30)
        
        month_stats = EmployeeAttendance.objects.filter(
            att_date__range=[month_start, month_end]
        ).aggregate(
            total=Count('att_id'),
            present=Count('att_id', filter=Q(status='Present')),
            absent=Count('att_id', filter=Q(status='Absent'))
        )
        
        monthly_data.append({
            'month': month_start.strftime('%Y-%m'),
            'total': month_stats['total'],
            'present': month_stats['present'],
            'absent': month_stats['absent']
        })
    
    context = {
        'total_employees': total_employees,
        'total_attendance_records': total_attendance_records,
        'recent_stats': recent_stats,
        'top_employees': top_employees,
        'monthly_data': monthly_data,
        'last_30_days': last_30_days,
    }
    
    return render(request, 'attendance/analytics.html', context)


@login_required
def generate_attendance_summary(request):
    """إنشاء ملخص الحضور الشهري"""
    if request.method == 'POST':
        year = int(request.POST.get('year', date.today().year))
        month = int(request.POST.get('month', date.today().month))
        
        # حذف الملخصات الموجودة لنفس الفترة
        AttendanceSummary.objects.filter(year=year, month=month).delete()
        
        # إنشاء ملخص لكل موظف
        employees = Employee.objects.filter(emp_status='Active')
        created_count = 0
        
        for employee in employees:
            # حساب إحصائيات الموظف للشهر
            monthly_records = EmployeeAttendance.objects.filter(
                emp=employee,
                att_date__year=year,
                att_date__month=month
            )
            
            if monthly_records.exists():
                stats = monthly_records.aggregate(
                    total_days=Count('att_id'),
                    present_days=Count('att_id', filter=Q(status='Present')),
                    absent_days=Count('att_id', filter=Q(status='Absent')),
                    late_days=Count('att_id', filter=Q(status='Late'))
                )
                
                # حساب ساعات العمل ودقائق التأخير
                total_work_hours = 0
                total_late_minutes = 0
                
                for record in monthly_records:
                    if record.check_in and record.check_out:
                        work_duration = record.check_out - record.check_in
                        total_work_hours += work_duration.total_seconds() / 3600
                    
                    total_late_minutes += record.calculate_late_minutes()
                
                # إنشاء الملخص
                AttendanceSummary.objects.create(
                    employee=employee,
                    year=year,
                    month=month,
                    total_work_days=stats['total_days'],
                    present_days=stats['present_days'],
                    absent_days=stats['absent_days'],
                    late_days=stats['late_days'],
                    total_work_hours=round(total_work_hours, 2),
                    late_minutes=total_late_minutes
                )
                
                created_count += 1
        
        messages.success(
            request,
            f'تم إنشاء ملخص الحضور لـ {created_count} موظف للشهر {month}/{year}'
        )
        
        return redirect('attendance:attendance_summaries')
    
    return render(request, 'attendance/generate_summary.html')


@login_required
def attendance_summaries(request):
    """عرض ملخصات الحضور"""
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    summaries = AttendanceSummary.objects.filter(
        year=year,
        month=month
    ).select_related('employee').order_by('employee__emp_code')
    
    context = {
        'summaries': summaries,
        'year': year,
        'month': month,
    }
    
    return render(request, 'attendance/summaries.html', context)
    
    context = {
        'records': records,
    }
    
    return render(request, 'attendance/overtime_records.html', context)


@login_required
def calculate_overtime(request):
    """حساب الوقت الإضافي"""
    if request.method == 'POST':
        # منطق حساب الوقت الإضافي
        pass
    
    return render(request, 'attendance/calculate_overtime.html')