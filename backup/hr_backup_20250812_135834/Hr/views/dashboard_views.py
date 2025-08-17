# =============================================================================
# ElDawliya HR Management System - Dashboard Views
# =============================================================================
# Comprehensive HR dashboard with statistics and KPIs
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum, Avg, F, Case, When, IntegerField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date, timedelta, datetime
from decimal import Decimal
import json

from Hr.models import (
    Job,
    AttendanceRecord, LeaveType, EmployeeLeave,
    PayrollPeriod, PayrollEntry, SalaryItem
)
# Use the legacy models that match the existing database tables
from Hr.models.legacy.legacy_models import LegacyDepartment as Department
from Hr.models.legacy_employee import LegacyEmployee as Employee


# =============================================================================
# MAIN HR DASHBOARD
# =============================================================================

class HRDashboardView(LoginRequiredMixin, TemplateView):
    """لوحة تحكم الموارد البشرية الشاملة"""
    template_name = 'Hr/dashboard/hr_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('لوحة تحكم الموارد البشرية')

        # إضافة بيانات مبسطة وآمنة
        try:
            total_departments = Department.objects.count()
        except:
            total_departments = 0

        try:
            total_job_positions = Job.objects.count()
        except:
            total_job_positions = 0

        try:
            total_employees = Employee.objects.count()
            active_employees = Employee.objects.filter(working_condition='سارى').count()
            inactive_employees = Employee.objects.exclude(working_condition='سارى').count()
        except:
            total_employees = 0
            active_employees = 0
            inactive_employees = 0

        context.update({
            # إحصائيات عامة
            'total_companies': 1,
            'total_departments': total_departments,
            'total_job_positions': total_job_positions,

            # إحصائيات الموظفين
            'employee_stats': {
                'total_employees': total_employees,
                'active_employees': active_employees,
                'inactive_employees': inactive_employees,
            },

            # إحصائيات الحضور
            'attendance_today': {
                'total_records': 0,  # Will be updated when AttendanceRecord model is available
                'present_employees': 0,
                'absent_employees': 0,
            },

            # إحصائيات الإجازات
            'leave_stats': {
                'total_requests': 0,  # Will be updated when EmployeeLeave model is available
                'pending_requests': 0,
                'approved_requests': 0,
            },

            # إحصائيات الرواتب
            'payroll_stats': {
                'total_periods': 0,  # Will be updated when PayrollPeriod model is available
                'latest_period': None,
            },

            # بيانات حديثة
            'recent_employees': [],  # Will be updated when models are available
            'recent_leave_requests': [],

            # تنبيهات
            'alerts': []
        })

        return context
    



# =============================================================================
# AJAX DASHBOARD DATA
# =============================================================================

@login_required
def dashboard_data_ajax(request):
    """بيانات لوحة التحكم - AJAX"""
    data_type = request.GET.get('type', 'overview')
    
    if data_type == 'overview':
        return JsonResponse(get_overview_data())
    elif data_type == 'attendance':
        return JsonResponse(get_attendance_chart_data())
    elif data_type == 'leaves':
        return JsonResponse(get_leaves_chart_data())
    elif data_type == 'payroll':
        return JsonResponse(get_payroll_chart_data())
    else:
        return JsonResponse({'error': 'نوع البيانات غير صحيح'})


def get_overview_data():
    """بيانات نظرة عامة"""
    today = date.today()

    try:
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(working_condition='سارى').count()
        new_this_month = Employee.objects.filter(
            emp_date_hiring__gte=today.replace(day=1)
        ).count()
    except:
        total_employees = 0
        active_employees = 0
        new_this_month = 0

    return {
        'employees': {
            'total': total_employees,
            'active': active_employees,
            'new_this_month': new_this_month,
        },
        'attendance': {
            'present_today': 0,  # Will be updated when AttendanceRecord model is available
            'late_today': 0,
        },
        'leaves': {
            'pending': 0,  # Will be updated when EmployeeLeave model is available
            'approved_today': 0,
        }
    }


def get_attendance_chart_data():
    """بيانات مخطط الحضور"""
    # آخر 7 أيام
    dates = []
    present_data = []
    late_data = []
    absent_data = []
    
    for i in range(6, -1, -1):
        date_obj = date.today() - timedelta(days=i)
        dates.append(date_obj.strftime('%Y-%m-%d'))
        
        day_records = AttendanceRecord.objects.filter(record_date=date_obj)

        present_count = day_records.filter(
            record_type='check_in'
        ).values('employee').distinct().count()

        late_count = day_records.filter(record_type='late').count()
        
        # حساب الغائبين
        total_active = Employee.objects.filter(working_condition='سارى').count()
        absent_count = total_active - present_count
        
        present_data.append(present_count)
        late_data.append(late_count)
        absent_data.append(absent_count)
    
    return {
        'labels': dates,
        'datasets': [
            {
                'label': 'حاضر',
                'data': present_data,
                'backgroundColor': 'rgba(40, 167, 69, 0.8)',
            },
            {
                'label': 'متأخر',
                'data': late_data,
                'backgroundColor': 'rgba(255, 193, 7, 0.8)',
            },
            {
                'label': 'غائب',
                'data': absent_data,
                'backgroundColor': 'rgba(220, 53, 69, 0.8)',
            }
        ]
    }


def get_leaves_chart_data():
    """بيانات مخطط الإجازات"""
    # إحصائيات أنواع الإجازات
    leave_types = LeaveType.objects.filter(is_active=True)
    
    labels = []
    data = []
    colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
    ]
    
    for i, leave_type in enumerate(leave_types):
        count = EmployeeLeave.objects.filter(
            leave_type=leave_type,
            status='approved',
            start_date__year=date.today().year
        ).count()

        if count > 0:
            labels.append(leave_type.name)
            data.append(count)
    
    return {
        'labels': labels,
        'datasets': [{
            'data': data,
            'backgroundColor': colors[:len(data)],
        }]
    }


def get_payroll_chart_data():
    """بيانات مخطط الرواتب"""
    # آخر 6 أشهر
    months = []
    amounts = []
    
    for i in range(5, -1, -1):
        month_date = date.today().replace(day=1) - timedelta(days=i*30)
        months.append(month_date.strftime('%Y-%m'))
        
        # البحث عن فترة الراتب لهذا الشهر
        period = PayrollPeriod.objects.filter(
            start_date__year=month_date.year,
            start_date__month=month_date.month
        ).first()
        
        if period:
            total_amount = period.payroll_entries.aggregate(
                total=Sum('net_salary')
            )['total'] or 0
            amounts.append(float(total_amount))
        else:
            amounts.append(0)
    
    return {
        'labels': months,
        'datasets': [{
            'label': 'إجمالي الرواتب',
            'data': amounts,
            'borderColor': 'rgba(54, 162, 235, 1)',
            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            'fill': True,
        }]
    }


# =============================================================================
# QUICK ACTIONS
# =============================================================================

@login_required
def quick_employee_search(request):
    """البحث السريع عن الموظفين"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'employees': []})
    
    employees = Employee.objects.filter(
        Q(emp_id__icontains=query) |
        Q(emp_first_name__icontains=query) |
        Q(emp_second_name__icontains=query) |
        Q(emp_full_name__icontains=query)
    ).filter(working_condition='سارى')[:10]
    
    results = [
        {
            'id': emp.emp_id,
            'employee_number': emp.emp_id,
            'full_name': emp.emp_full_name,
            'department': emp.department.dept_name if emp.department else '',
            'job_position': emp.jop_name if emp.jop_name else '',
            'photo_url': emp.emp_image.url if emp.emp_image else None,
            'url': f'/hr/employees/{emp.emp_id}/'
        }
        for emp in employees
    ]
    
    return JsonResponse({'employees': results})


@login_required
def dashboard_notifications(request):
    """إشعارات لوحة التحكم"""
    notifications = []
    
    # طلبات الإجازة الجديدة
    new_leave_requests = EmployeeLeave.objects.filter(
        status='pending',
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()

    if new_leave_requests > 0:
        notifications.append({
            'type': 'leave_request',
            'count': new_leave_requests,
            'message': f'طلب إجازة جديد' if new_leave_requests == 1 else f'{new_leave_requests} طلبات إجازة جديدة',
            'url': '/hr/leave/'
        })
    
    # موظفين جدد
    new_employees = Employee.objects.filter(
        emp_date_hiring__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    if new_employees > 0:
        notifications.append({
            'type': 'new_employee',
            'count': new_employees,
            'message': f'موظف جديد' if new_employees == 1 else f'{new_employees} موظفين جدد',
            'url': '/hr/employees/'
        })
    
    return JsonResponse({'notifications': notifications})
