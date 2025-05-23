from datetime import datetime, date, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import (
    AttendanceRecord,
    EmployeeAttendanceProfile,
    LeaveBalance,
    LeaveType,
    AttendanceRule,
    WorkSchedule
)
from Hr.models import Employee


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
    """View for attendance dashboard"""
    today = timezone.localtime().date()
    
    # Get today's attendance statistics
    today_stats = AttendanceRecord.objects.filter(date=today).aggregate(
        present=Count('id', filter=Q(record_type='check_in')),
        absent=Count('id', filter=Q(record_type='absent')),
        leave=Count('id', filter=Q(record_type='leave')),
        late=Count('id', filter=Q(record_type='check_in', late_minutes__gt=0))
    )
    
    # Get the user's attendance info if they are an employee
    user_attendance = None
    if hasattr(request.user, 'employee'):
        user_attendance = AttendanceRecord.objects.filter(
            employee=request.user.employee,
            date=today
        ).order_by('-time').first()
    
    # Get employee's work schedule and attendance profile
    work_schedule = None
    attendance_profile = None
    if hasattr(request.user, 'employee'):
        attendance_profile = EmployeeAttendanceProfile.objects.filter(
            employee=request.user.employee
        ).first()
        if attendance_profile:
            work_schedule = attendance_profile.work_schedule
    
    context = {
        'today_stats': today_stats,
        'user_attendance': user_attendance,
        'work_schedule': work_schedule,
        'attendance_profile': attendance_profile,
        'now': timezone.localtime(),
    }
    
    return render(request, 'attendance/dashboard.html', context)
