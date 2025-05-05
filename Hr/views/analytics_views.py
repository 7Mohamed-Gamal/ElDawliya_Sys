from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
import json

from Hr.models.employee_model import Employee
from Hr.models.leave_models import EmployeeLeave
from Hr.models.attendance_models import AttendanceSummary
from Hr.models.salary_models import PayrollEntry

@login_required
def analytics_dashboard(request):
    """عرض لوحة تحليل البيانات"""
    # Employee statistics
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(working_condition='سارى',Insurance_Status='مؤمن عليه').count()
    on_leave_employees = Employee.objects.filter(working_condition='إجازة').count()
    resigned_employees = Employee.objects.filter(working_condition='استقالة').count()
    
    # Insurance statistics
    insured_employees = Employee.objects.filter(insurance_status='مؤمن عليه').count()
    uninsured_employees = Employee.objects.filter(insurance_status='غير مؤمن عليه').count()
    
    # Department distribution
    departments = Employee.objects.values('department__dept_name').annotate(
        count=Count('emp_id')
    ).order_by('-count')
    
    # Gender distribution
    gender_distribution = Employee.objects.values('emp_type').annotate(
        count=Count('emp_id')
    ).order_by('emp_type')
    
    # Age distribution
    age_ranges = {
        '18-25': Q(age__gte=18) & Q(age__lte=25),
        '26-35': Q(age__gte=26) & Q(age__lte=35),
        '36-45': Q(age__gte=36) & Q(age__lte=45),
        '46-55': Q(age__gte=46) & Q(age__lte=55),
        '56+': Q(age__gte=56),
    }
    
    age_distribution = []
    for label, age_range in age_ranges.items():
        count = Employee.objects.filter(age_range).count()
        age_distribution.append({'range': label, 'count': count})
    
    # Attendance statistics for the last 30 days
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    attendance_stats = AttendanceSummary.objects.filter(
        date__gte=thirty_days_ago,
        date__lte=today
    ).values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Leave statistics for the current year
    current_year = today.year
    
    leave_stats = EmployeeLeave.objects.filter(
        start_date__year=current_year
    ).values('leave_type__name').annotate(
        count=Count('id'),
        days=Sum('days_count')
    ).order_by('-days')
    
    # Salary statistics
    salary_stats = PayrollEntry.objects.values('payroll_period__name').annotate(
        total=Sum('total_salary'),
        avg=Avg('total_salary'),
        count=Count('id')
    ).order_by('-payroll_period__end_date')[:5]
    
    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'on_leave_employees': on_leave_employees,
        'resigned_employees': resigned_employees,
        'insured_employees': insured_employees,
        'uninsured_employees': uninsured_employees,
        'departments': departments,
        'gender_distribution': gender_distribution,
        'age_distribution': age_distribution,
        'attendance_stats': attendance_stats,
        'leave_stats': leave_stats,
        'salary_stats': salary_stats,
        'title': 'تحليل البيانات'
    }
    
    return render(request, 'Hr/analytics/dashboard.html', context)

@login_required
def analytics_chart(request, chart_type):
    """عرض رسم بياني محدد"""
    if chart_type == 'departments':
        return department_chart(request)
    elif chart_type == 'gender':
        return gender_chart(request)
    elif chart_type == 'age':
        return age_chart(request)
    elif chart_type == 'attendance':
        return attendance_chart(request)
    elif chart_type == 'leaves':
        return leave_chart(request)
    elif chart_type == 'salary':
        return salary_chart(request)
    else:
        return analytics_dashboard(request)

def department_chart(request):
    """رسم بياني لتوزيع الموظفين حسب الأقسام"""
    departments = Employee.objects.values('department__dept_name').annotate(
        count=Count('emp_id')
    ).order_by('-count')
    
    # Prepare data for chart
    labels = [dept['department__dept_name'] or 'غير محدد' for dept in departments]
    data = [dept['count'] for dept in departments]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'عدد الموظفين',
            'data': data,
            'backgroundColor': [
                '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
                '#5a5c69', '#858796', '#6610f2', '#6f42c1', '#e83e8c'
            ],
        }]
    }
    
    context = {
        'chart_data': json.dumps(chart_data),
        'chart_title': 'توزيع الموظفين حسب الأقسام',
        'chart_type': 'pie',
        'title': 'رسم بياني للأقسام'
    }
    
    return render(request, 'Hr/analytics/chart.html', context)

def gender_chart(request):
    """رسم بياني لتوزيع الموظفين حسب الجنس"""
    gender_distribution = Employee.objects.values('emp_type').annotate(
        count=Count('emp_id')
    ).order_by('emp_type')
    
    # Prepare data for chart
    labels = [gender['emp_type'] or 'غير محدد' for gender in gender_distribution]
    data = [gender['count'] for gender in gender_distribution]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'عدد الموظفين',
            'data': data,
            'backgroundColor': ['#4e73df', '#1cc88a'],
        }]
    }
    
    context = {
        'chart_data': json.dumps(chart_data),
        'chart_title': 'توزيع الموظفين حسب الجنس',
        'chart_type': 'pie',
        'title': 'رسم بياني للجنس'
    }
    
    return render(request, 'Hr/analytics/chart.html', context)

def age_chart(request):
    """رسم بياني لتوزيع الموظفين حسب العمر"""
    age_ranges = {
        '18-25': Q(age__gte=18) & Q(age__lte=25),
        '26-35': Q(age__gte=26) & Q(age__lte=35),
        '36-45': Q(age__gte=36) & Q(age__lte=45),
        '46-55': Q(age__gte=46) & Q(age__lte=55),
        '56+': Q(age__gte=56),
    }
    
    age_distribution = []
    for label, age_range in age_ranges.items():
        count = Employee.objects.filter(age_range).count()
        age_distribution.append({'range': label, 'count': count})
    
    # Prepare data for chart
    labels = [age['range'] for age in age_distribution]
    data = [age['count'] for age in age_distribution]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'عدد الموظفين',
            'data': data,
            'backgroundColor': '#4e73df',
        }]
    }
    
    context = {
        'chart_data': json.dumps(chart_data),
        'chart_title': 'توزيع الموظفين حسب العمر',
        'chart_type': 'bar',
        'title': 'رسم بياني للعمر'
    }
    
    return render(request, 'Hr/analytics/chart.html', context)

def attendance_chart(request):
    """رسم بياني لإحصائيات الحضور"""
    # Get attendance data for the last 30 days
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    attendance_stats = AttendanceSummary.objects.filter(
        date__gte=thirty_days_ago,
        date__lte=today
    ).values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Prepare data for chart
    labels = [att['status'] for att in attendance_stats]
    data = [att['count'] for att in attendance_stats]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'عدد الأيام',
            'data': data,
            'backgroundColor': [
                '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#5a5c69'
            ],
        }]
    }
    
    context = {
        'chart_data': json.dumps(chart_data),
        'chart_title': 'إحصائيات الحضور للثلاثين يوم الماضية',
        'chart_type': 'pie',
        'title': 'رسم بياني للحضور'
    }
    
    return render(request, 'Hr/analytics/chart.html', context)

def leave_chart(request):
    """رسم بياني لإحصائيات الإجازات"""
    # Get leave data for the current year
    current_year = timezone.now().date().year
    
    leave_stats = EmployeeLeave.objects.filter(
        start_date__year=current_year
    ).values('leave_type__name').annotate(
        count=Count('id'),
        days=Sum('days_count')
    ).order_by('-days')
    
    # Prepare data for chart
    labels = [leave['leave_type__name'] or 'غير محدد' for leave in leave_stats]
    data = [leave['days'] for leave in leave_stats]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'عدد أيام الإجازات',
            'data': data,
            'backgroundColor': [
                '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
                '#5a5c69', '#858796', '#6610f2', '#6f42c1', '#e83e8c'
            ],
        }]
    }
    
    context = {
        'chart_data': json.dumps(chart_data),
        'chart_title': f'إحصائيات الإجازات لعام {current_year}',
        'chart_type': 'bar',
        'title': 'رسم بياني للإجازات'
    }
    
    return render(request, 'Hr/analytics/chart.html', context)

def salary_chart(request):
    """رسم بياني لإحصائيات الرواتب"""
    # Get salary data for the last 6 periods
    salary_stats = PayrollEntry.objects.values('payroll_period__name').annotate(
        total=Sum('total_salary')
    ).order_by('-payroll_period__end_date')[:6]
    
    # Prepare data for chart
    labels = [stat['payroll_period__name'] for stat in salary_stats]
    data = [float(stat['total']) for stat in salary_stats]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'إجمالي الرواتب',
            'data': data,
            'backgroundColor': '#4e73df',
            'borderColor': '#4e73df',
            'fill': False
        }]
    }
    
    context = {
        'chart_data': json.dumps(chart_data),
        'chart_title': 'إحصائيات الرواتب',
        'chart_type': 'line',
        'title': 'رسم بياني للرواتب'
    }
    
    return render(request, 'Hr/analytics/chart.html', context)
