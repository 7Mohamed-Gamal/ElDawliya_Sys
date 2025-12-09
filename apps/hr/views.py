"""
HR System Main Views
==================

Central dashboard and navigation for all HR modules
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
import json

# Import models from all HR apps
try:
    from apps.hr.employees.models import Employee, Department
    from apps.hr.attendance.models import EmployeeAttendance
    from apps.hr.leaves.models import EmployeeLeave
    from apps.hr.payroll.models import PayrollRun, EmployeeSalary
    from loans.models import EmployeeLoan
    from apps.hr.training.models import TrainingCourse
    from apps.hr.evaluations.models import EmployeeEvaluation
    from insurance.models import InsurancePolicy
except ImportError as e:
    # Handle missing apps gracefully
    Employee = None
    Department = None
    EmployeeAttendance = None
    EmployeeLeave = None
    PayrollRun = None
    EmployeeSalary = None
    EmployeeLoan = None
    TrainingCourse = None
    EmployeeEvaluation = None
    InsurancePolicy = None


@login_required
def dashboard(request):
    """لوحة التحكم الرئيسية للموارد البشرية"""

    context = {
        'today': date.today(),
        'now': timezone.now(),
    }

    # Get basic statistics if models are available
    if Employee:
        context.update({
            'total_employees': Employee.objects.filter(emp_status='Active').count(),
            'active_employees': Employee.objects.filter(emp_status='Active').count(),
            'new_employees_this_month': Employee.objects.filter(
                hire_date__gte=date.today().replace(day=1)
            ).count(),
        })

    if EmployeeAttendance:
        # Today's attendance
        today_attendance = EmployeeAttendance.objects.filter(att_date=date.today())
        context.update({
            'present_today': today_attendance.filter(status__in=['Present', 'Late']).count(),
            'late_today': today_attendance.filter(status='Late').count(),
            'absent_today': today_attendance.filter(status='Absent').count(),
        })

        # Calculate attendance rate
        if context.get('total_employees', 0) > 0:
            context['attendance_rate'] = (context.get('present_today', 0) / context['total_employees']) * 100

    if EmployeeLeave:
        # Leave statistics
        context.update({
            'pending_leaves': EmployeeLeave.objects.filter(status='Pending').count(),
            'approved_leaves': EmployeeLeave.objects.filter(
                status='Approved',
                created_at__gte=date.today().replace(day=1)
            ).count(),
            'current_leaves': EmployeeLeave.objects.filter(
                status='Approved',
                start_date__lte=date.today(),
                end_date__gte=date.today()
            ).count(),
        })

    if PayrollRun:
        # Payroll statistics
        active_runs = PayrollRun.objects.filter(status__in=['draft', 'calculating', 'review'])
        context.update({
            'active_payroll_runs': active_runs.count(),
        })

        if EmployeeSalary:
            avg_salary = EmployeeSalary.objects.filter(is_current=True).aggregate(
                avg=Avg('basic_salary')
            )['avg']
            total_payroll = EmployeeSalary.objects.filter(is_current=True).aggregate(
                total=Sum('basic_salary')
            )['total']
            context.update({
                'avg_salary': avg_salary or 0,
                'total_payroll': total_payroll or 0,
            })

    if EmployeeLoan:
        context['active_loans'] = EmployeeLoan.objects.filter(status='Active').count()

    if TrainingCourse:
        context.update({
            'active_trainings': TrainingCourse.objects.filter(status='Active').count(),
            'enrolled_trainees': TrainingCourse.objects.filter(status='Active').aggregate(
                total=Sum('enrolled_count')
            )['total'] or 0,
        })

    if EmployeeEvaluation:
        context.update({
            'pending_evaluations': EmployeeEvaluation.objects.filter(status='Pending').count(),
            'overdue_evaluations': EmployeeEvaluation.objects.filter(
                status='Pending',
                due_date__lt=date.today()
            ).count(),
        })

    # Chart data for attendance trends
    chart_labels = []
    attendance_data = []
    absence_data = []

    if EmployeeAttendance:
        for i in range(7):
            date_check = date.today() - timedelta(days=i)
            chart_labels.append(date_check.strftime('%m/%d'))

            day_attendance = EmployeeAttendance.objects.filter(att_date=date_check)
            attendance_data.append(day_attendance.filter(status__in=['Present', 'Late']).count())
            absence_data.append(day_attendance.filter(status='Absent').count())

    # Reverse to show chronological order
    chart_labels.reverse()
    attendance_data.reverse()
    absence_data.reverse()

    context.update({
        'chart_labels': json.dumps(chart_labels),
        'attendance_data': json.dumps(attendance_data),
        'absence_data': json.dumps(absence_data),
    })

    # Recent activities (mock data for now)
    context['recent_activities'] = [
        {
            'title': 'موظف جديد تم تعيينه',
            'time': timezone.now() - timedelta(hours=2),
            'icon': 'fas fa-user-plus',
            'color': '#10b981'
        },
        {
            'title': 'طلب إجازة جديد',
            'time': timezone.now() - timedelta(hours=4),
            'icon': 'fas fa-calendar-alt',
            'color': '#f59e0b'
        },
        {
            'title': 'تم اعتماد تشغيل الرواتب',
            'time': timezone.now() - timedelta(hours=6),
            'icon': 'fas fa-money-bill',
            'color': '#8b5cf6'
        },
    ]

    # Available reports count
    context.update({
        'available_reports': 12,  # Mock data
        'scheduled_reports': 3,   # Mock data
    })

    return render(request, 'hr/hr_dashboard.html', context)


@login_required
def dashboard_data(request):
    """API endpoint لتحديث بيانات لوحة التحكم"""

    data = {}

    if Employee:
        data['total_employees'] = Employee.objects.filter(emp_status='Active').count()

    if EmployeeAttendance:
        today_attendance = EmployeeAttendance.objects.filter(att_date=date.today())
        data['present_today'] = today_attendance.filter(status__in=['Present', 'Late']).count()

    if EmployeeLeave:
        data['pending_leaves'] = EmployeeLeave.objects.filter(status='Pending').count()

    return JsonResponse(data)


@login_required
def profile(request):
    """صفحة الملف الشخصي"""
    return render(request, 'hr/profile.html')


@login_required
def my_payslips(request):
    """كشوف رواتبي الشخصية"""
    return render(request, 'hr/my_payslips.html')


@login_required
def my_leaves(request):
    """إجازاتي الشخصية"""
    return render(request, 'hr/my_leaves.html')


@login_required
def settings(request):
    """إعدادات النظام"""
    return render(request, 'hr/settings.html')


@login_required
def notifications(request):
    """الإشعارات"""
    return render(request, 'hr/notifications.html')


@login_required
def notifications_count(request):
    """عدد الإشعارات"""
    # Mock data - should be replaced with actual notification logic
    return JsonResponse({'count': 3})


# Module status views
@login_required
def module_status(request):
    """حالة جميع وحدات HR"""

    modules = {
        'employees': {'name': 'الموظفين', 'status': True, 'url': 'employees:list'},
        'attendance': {'name': 'الحضور والانصراف', 'status': True, 'url': 'attendance:dashboard'},
        'leaves': {'name': 'الإجازات', 'status': True, 'url': 'leaves:dashboard'},
        'payrolls': {'name': 'المرتبات', 'status': True, 'url': 'payrolls:dashboard'},
        'loans': {'name': 'القروض', 'status': True, 'url': 'loans:dashboard'},
        'training': {'name': 'التدريب', 'status': True, 'url': 'training:dashboard'},
        'evaluations': {'name': 'التقييمات', 'status': True, 'url': 'evaluations:dashboard'},
        'insurance': {'name': 'التأمين', 'status': True, 'url': 'insurance:dashboard'},
        'banks': {'name': 'البنوك', 'status': True, 'url': 'banks:list'},
    }

    return JsonResponse(modules)
