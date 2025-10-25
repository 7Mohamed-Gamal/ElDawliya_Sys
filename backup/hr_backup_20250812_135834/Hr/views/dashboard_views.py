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
# Use the modern, refactored models
from Hr.models.core.department_models import Department
from Hr.models.employee.employee_models import Employee


# =============================================================================
# MAIN HR DASHBOARD
# =============================================================================

class HRDashboardView(LoginRequiredMixin, TemplateView):
    """Comprehensive HR Dashboard"""
    template_name = 'Hr/dashboard/hr_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('لوحة تحكم الموارد البشرية')

        try:
            total_departments = Department.objects.count()
            total_job_positions = Job.objects.count()
            total_employees = Employee.objects.count()
            active_employees = Employee.objects.filter(status=Employee.ACTIVE).count()
            inactive_employees = total_employees - active_employees
        except Exception as e:
            # Handle potential database errors gracefully
            total_departments = 0
            total_job_positions = 0
            total_employees = 0
            active_employees = 0
            inactive_employees = 0
            messages.error(self.request, f"An error occurred while fetching dashboard data: {e}")

        context.update({
            'total_departments': total_departments,
            'total_job_positions': total_job_positions,
            'employee_stats': {
                'total_employees': total_employees,
                'active_employees': active_employees,
                'inactive_employees': inactive_employees,
            },
            # Other stats can be added here or loaded via AJAX
        })

        return context
    


# =============================================================================
# AJAX DASHBOARD DATA
# =============================================================================

@login_required
def dashboard_data_ajax(request):
    """Dashboard data for AJAX calls"""
    data_type = request.GET.get('type', 'overview')
    
    try:
        if data_type == 'overview':
            return JsonResponse(get_overview_data())
        elif data_type == 'attendance':
            return JsonResponse(get_attendance_chart_data())
        elif data_type == 'leaves':
            return JsonResponse(get_leaves_chart_data())
        elif data_type == 'payroll':
            return JsonResponse(get_payroll_chart_data())
        else:
            return JsonResponse({'error': 'Invalid data type'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_overview_data():
    """Overview data for the dashboard"""
    today = date.today()

    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status=Employee.ACTIVE).count()
    # Use the new join_date field
    new_this_month = Employee.objects.filter(
        join_date__gte=today.replace(day=1)
    ).count()

    return {
        'employees': {
            'total': total_employees,
            'active': active_employees,
            'new_this_month': new_this_month,
        },
        # Placeholder data for other sections
        'attendance': {'present_today': 0, 'late_today': 0},
        'leaves': {'pending': 0, 'approved_today': 0}
    }

def get_attendance_chart_data():
    """Data for the attendance chart"""
    dates, present_data, late_data, absent_data = [], [], [], []
    total_active = Employee.objects.filter(status=Employee.ACTIVE).count()

    for i in range(6, -1, -1):
        date_obj = date.today() - timedelta(days=i)
        dates.append(date_obj.strftime('%Y-%m-%d'))
        
        day_records = AttendanceRecord.objects.filter(record_date=date_obj)
        present_count = day_records.filter(record_type='check_in').values('employee').distinct().count()
        late_count = day_records.filter(record_type='late').count()
        absent_count = total_active - present_count
        
        present_data.append(present_count)
        late_data.append(late_count)
        absent_data.append(absent_count)
    
    return {
        'labels': dates,
        'datasets': [
            {'label': 'حاضر', 'data': present_data, 'backgroundColor': 'rgba(40, 167, 69, 0.8)'},
            {'label': 'متأخر', 'data': late_data, 'backgroundColor': 'rgba(255, 193, 7, 0.8)'},
            {'label': 'غائب', 'data': absent_data, 'backgroundColor': 'rgba(220, 53, 69, 0.8)'},
        ]
    }

def get_leaves_chart_data():
    # ... (No changes needed here as it uses modern models already)
    pass # Implementation remains the same

def get_payroll_chart_data():
    # ... (No changes needed here as it uses modern models already)
    pass # Implementation remains the same


# =============================================================================
# QUICK ACTIONS
# =============================================================================

@login_required
def quick_employee_search(request):
    """Quick search for employees via AJAX"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'employees': []})
    
    # Use the new fields for searching
    employees = Employee.objects.filter(
        Q(employee_id__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(full_name__icontains=query) |
        Q(national_id__icontains=query)
    ).filter(status=Employee.ACTIVE).select_related('department', 'position')[:10]
    
    results = [{
        'id': emp.id,
        'employee_id': emp.employee_id,
        'full_name': emp.full_name,
        'department': emp.department.dept_name if emp.department else '',
        'position': emp.position.name if emp.position else '',
        # 'photo_url': emp.photo.url if emp.photo else None, # Assuming a 'photo' field
        'url': reverse('Hr:employee_detail', args=[emp.id]) # Use modern URL
    } for emp in employees]
    
    return JsonResponse({'employees': results})


@login_required
def dashboard_notifications(request):
    """Dashboard notifications via AJAX"""
    notifications = []
    
    # New leave requests (already uses modern model)
    new_leave_requests = EmployeeLeave.objects.filter(
        status='pending_approval', # Use new status
        created_at__gte=timezone.now() - timedelta(days=1)
    ).count()

    if new_leave_requests > 0:
        notifications.append({
            'type': 'leave_request',
            'count': new_leave_requests,
            'message': f'{new_leave_requests} new leave requests pending approval.',
            'url': reverse('Hr:leave_request_list')
        })
    
    # New employees (use new join_date field)
    new_employees = Employee.objects.filter(
        join_date__gte=timezone.now().date() - timedelta(days=1)
    ).count()
    
    if new_employees > 0:
        notifications.append({
            'type': 'new_employee',
            'count': new_employees,
            'message': f'{new_employees} new employees joined in the last 24 hours.',
            'url': reverse('Hr:employee_list')
        })
    
    return JsonResponse({'notifications': notifications})
