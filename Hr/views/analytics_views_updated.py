from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, F, Q
from django.utils import timezone
from datetime import timedelta, date
from django.db.models.functions import ExtractMonth, ExtractYear, TruncMonth

from Hr.models.employee_model import Employee
from Hr.models.department_models import Department
from Hr.models.leave_models import EmployeeLeave
from Hr.models.task_models import EmployeeTask
from Hr.models.salary_models import PayrollEntry
from Hr.models.attendance_models import AttendanceRecord, AttendanceSummary


@login_required
def analytics_dashboard(request):
    """لوحة التحليلات الرئيسية"""
    today = timezone.now().date()
    
    # إحصائيات الموظفين
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(working_condition='سارى',Insurance_Status='مؤمن عليه').count()
    on_leave_employees = Employee.objects.filter(working_condition='إجازة').count()
    inactive_employees = Employee.objects.exclude(working_condition__in=['سارى', 'غير مؤمن عليه']).count()
    
    # نسب توزيع الموظفين
    if total_employees > 0:
        active_percentage = (active_employees / total_employees) * 100
        on_leave_percentage = (on_leave_employees / total_employees) * 100
        inactive_percentage = (inactive_employees / total_employees) * 100
    else:
        active_percentage = on_leave_percentage = inactive_percentage = 0
    
    # توزيع الموظفين حسب القسم
    departments = Department.objects.annotate(
        employee_count=Count('employees'),
    ).order_by('-employee_count')
    
    departments_data = []
    for dept in departments:
        if total_employees > 0:
            percentage = (dept.employee_count / total_employees) * 100
        else:
            percentage = 0
        
        departments_data.append({
            'dept_code': dept.dept_code,
            'dept_name': dept.dept_name,
            'employee_count': dept.employee_count,
            'percentage': percentage,
        })
    
    # توزيع الموظفين حسب حالة التأمين
    insured_employees = Employee.objects.filter(insurance_status='مؤمن عليه').count()
    uninsured_employees = Employee.objects.filter(insurance_status='غير مؤمن عليه').count()
    
    if total_employees > 0:
        insured_percentage = (insured_employees / total_employees) * 100
        uninsured_percentage = (uninsured_employees / total_employees) * 100
    else:
        insured_percentage = uninsured_percentage = 0
    
    # توزيع الإجازات في الأشهر الأخيرة
    last_6_months = today - timedelta(days=180)
    leaves_by_month = EmployeeLeave.objects.filter(
        start_date__gte=last_6_months
    ).annotate(
        month=TruncMonth('start_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # تنسيق بيانات الإجازات للرسم البياني
    leave_labels = []
    leave_data = []
    
    for entry in leaves_by_month:
        month = entry['month'].strftime('%Y-%m')
        leave_labels.append(month)
        leave_data.append(entry['count'])
    
    # معدل الحضور في الأشهر الأخيرة
    attendance_by_month = AttendanceSummary.objects.filter(
        date__gte=last_6_months
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        present_count=Count('id', filter=Q(status='حاضر')),
        total_count=Count('id'),
    ).order_by('month')
    
    # تنسيق بيانات الحضور للرسم البياني
    attendance_labels = []
    attendance_data = []
    
    for entry in attendance_by_month:
        month = entry['month'].strftime('%Y-%m')
        attendance_labels.append(month)
        
        if entry['total_count'] > 0:
            attendance_rate = (entry['present_count'] / entry['total_count']) * 100
        else:
            attendance_rate = 0
            
        attendance_data.append(attendance_rate)
    
    # حالة المهام
    total_tasks = EmployeeTask.objects.count()
    completed_tasks = EmployeeTask.objects.filter(status='completed').count()
    in_progress_tasks = EmployeeTask.objects.filter(status='in_progress').count()
    pending_tasks = EmployeeTask.objects.filter(status='pending').count()
    
    if total_tasks > 0:
        completed_percentage = (completed_tasks / total_tasks) * 100
        in_progress_percentage = (in_progress_tasks / total_tasks) * 100
        pending_percentage = (pending_tasks / total_tasks) * 100
    else:
        completed_percentage = in_progress_percentage = pending_percentage = 0
    
    # التنبيهات الهامة
    expiring_contracts = Employee.objects.filter(
        contract_expiry_date__isnull=False,
        contract_expiry_date__gte=today,
        contract_expiry_date__lte=today + timedelta(days=30),
    ).order_by('contract_expiry_date')[:5]
    
    expiring_health_cards = Employee.objects.filter(
        health_card_expiry_date__isnull=False,
        health_card_expiry_date__gte=today,
        health_card_expiry_date__lte=today + timedelta(days=30),
    ).order_by('health_card_expiry_date')[:5]
    
    overdue_tasks = EmployeeTask.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=today,
    ).order_by('due_date')[:5]
    
    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'active_percentage': active_percentage,
        'on_leave_employees': on_leave_employees,
        'on_leave_percentage': on_leave_percentage,
        'inactive_employees': inactive_employees,
        'inactive_percentage': inactive_percentage,
        
        'departments_data': departments_data,
        
        'insured_employees': insured_employees,
        'insured_percentage': insured_percentage,
        'uninsured_employees': uninsured_employees,
        'uninsured_percentage': uninsured_percentage,
        
        'leave_labels': leave_labels,
        'leave_data': leave_data,
        
        'attendance_labels': attendance_labels,
        'attendance_data': attendance_data,
        
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completed_percentage': completed_percentage,
        'in_progress_tasks': in_progress_tasks,
        'in_progress_percentage': in_progress_percentage,
        'pending_tasks': pending_tasks,
        'pending_percentage': pending_percentage,
        
        'expiring_contracts': expiring_contracts,
        'expiring_health_cards': expiring_health_cards,
        'overdue_tasks': overdue_tasks,
        
        'title': 'لوحة التحليلات'
    }
    
    return render(request, 'Hr/analytics/dashboard.html', context)


@login_required
def analytics_chart(request, chart_type):
    """عرض مخطط بياني محدد"""
    if chart_type == 'employees_by_department':
        return employees_by_department_chart(request)
    elif chart_type == 'employees_by_status':
        return employees_by_status_chart(request)
    elif chart_type == 'employees_by_insurance':
        return employees_by_insurance_chart(request)
    elif chart_type == 'attendance_over_time':
        return attendance_over_time_chart(request)
    elif chart_type == 'leaves_over_time':
        return leaves_over_time_chart(request)
    elif chart_type == 'tasks_status':
        return tasks_status_chart(request)
    elif chart_type == 'salary_distribution':
        return salary_distribution_chart(request)
    elif chart_type == 'employee_turnover':
        return employee_turnover_chart(request)
    else:
        return JsonResponse({'error': 'نوع المخطط غير موجود'})


@login_required
def employees_by_department_chart(request):
    """مخطط توزيع الموظفين حسب الأقسام"""
    departments = Department.objects.annotate(
        employee_count=Count('employees')
    ).order_by('-employee_count')
    
    label_data = []
    count_data = []
    
    for dept in departments:
        label_data.append(dept.dept_name)
        count_data.append(dept.employee_count)
    
    chart_data = {
        'title': 'توزيع الموظفين حسب الأقسام',
        'type': 'pie',
        'labels': label_data,
        'datasets': [{
            'data': count_data,
            'backgroundColor': generate_colors(len(label_data)),
        }]
    }
    
    return JsonResponse(chart_data)


@login_required
def employees_by_status_chart(request):
    """مخطط توزيع الموظفين حسب حالة العمل"""
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(working_condition='سارى').count()
    on_leave_employees = Employee.objects.filter(working_condition='إجازة').count()
    inactive_employees = Employee.objects.exclude(working_condition__in=['سارى', 'غير مؤمن عليه']).count()
    
    chart_data = {
        'title': 'توزيع الموظفين حسب حالة العمل',
        'type': 'pie',
        'labels': ['سارى', 'إجازة', 'غير نشط'],
        'datasets': [{
            'data': [active_employees, on_leave_employees, inactive_employees],
            'backgroundColor': ['#4CAF50', '#FFC107', '#F44336'],
        }]
    }
    
    return JsonResponse(chart_data)


@login_required
def employees_by_insurance_chart(request):
    """مخطط توزيع الموظفين حسب حالة التأمين"""
    insured_employees = Employee.objects.filter(insurance_status='مؤمن عليه').count()
    uninsured_employees = Employee.objects.filter(insurance_status='غير مؤمن عليه').count()
    
    chart_data = {
        'title': 'توزيع الموظفين حسب حالة التأمين',
        'type': 'pie',
        'labels': ['مؤمن عليه', 'غير مؤمن عليه'],
        'datasets': [{
            'data': [insured_employees, uninsured_employees],
            'backgroundColor': ['#2196F3', '#F44336'],
        }]
    }
    
    return JsonResponse(chart_data)


@login_required
def attendance_over_time_chart(request):
    """مخطط معدل الحضور على مدار الزمن"""
    today = timezone.now().date()
    last_12_months = today - timedelta(days=365)
    
    attendance_by_month = AttendanceSummary.objects.filter(
        date__gte=last_12_months
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        present_count=Count('id', filter=Q(status='حاضر')),
        total_count=Count('id'),
    ).order_by('month')
    
    labels = []
    data = []
    
    for entry in attendance_by_month:
        month = entry['month'].strftime('%Y-%m')
        labels.append(month)
        
        if entry['total_count'] > 0:
            attendance_rate = (entry['present_count'] / entry['total_count']) * 100
        else:
            attendance_rate = 0
            
        data.append(attendance_rate)
    
    chart_data = {
        'title': 'معدل الحضور على مدار الزمن',
        'type': 'line',
        'labels': labels,
        'datasets': [{
            'label': 'معدل الحضور (%)',
            'data': data,
            'borderColor': '#4CAF50',
            'backgroundColor': 'rgba(76, 175, 80, 0.2)',
        }]
    }
    
    return JsonResponse(chart_data)


@login_required
def leaves_over_time_chart(request):
    """مخطط الإجازات على مدار الزمن"""
    today = timezone.now().date()
    last_12_months = today - timedelta(days=365)
    
    leaves_by_month = EmployeeLeave.objects.filter(
        start_date__gte=last_12_months
    ).annotate(
        month=TruncMonth('start_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    labels = []
    data = []
    
    for entry in leaves_by_month:
        month = entry['month'].strftime('%Y-%m')
        labels.append(month)
        data.append(entry['count'])
    
    chart_data = {
        'title': 'الإجازات على مدار الزمن',
        'type': 'bar',
        'labels': labels,
        'datasets': [{
            'label': 'عدد الإجازات',
            'data': data,
            'backgroundColor': '#FFC107',
        }]
    }
    
    return JsonResponse(chart_data)


@login_required
def tasks_status_chart(request):
    """مخطط حالة المهام"""
    completed_tasks = EmployeeTask.objects.filter(status='completed').count()
    in_progress_tasks = EmployeeTask.objects.filter(status='in_progress').count()
    pending_tasks = EmployeeTask.objects.filter(status='pending').count()
    
    chart_data = {
        'title': 'حالة المهام',
        'type': 'pie',
        'labels': ['مكتملة', 'قيد التنفيذ', 'معلقة'],
        'datasets': [{
            'data': [completed_tasks, in_progress_tasks, pending_tasks],
            'backgroundColor': ['#4CAF50', '#2196F3', '#F44336'],
        }]
    }
    
    return JsonResponse(chart_data)


@login_required
def salary_distribution_chart(request):
    """مخطط توزيع الرواتب"""
    # للتبسيط، نستخدم فئات رواتب ثابتة
    salary_buckets = {
        '0-2000': (0, 2000),
        '2001-4000': (2001, 4000),
        '4001-6000': (4001, 6000),
        '6001-8000': (6001, 8000),
        '8001-10000': (8001, 10000),
        '10001+': (10001, float('inf'))
    }
    
    salary_distribution = {}
    for key, (min_val, max_val) in salary_buckets.items():
        if max_val == float('inf'):
            count = Employee.objects.filter(basic_salary__gte=min_val).count()
        else:
            count = Employee.objects.filter(
                basic_salary__gte=min_val,
                basic_salary__lte=max_val
            ).count()
        
        salary_distribution[key] = count
    
    chart_data = {
        'title': 'توزيع الرواتب',
        'type': 'bar',
        'labels': list(salary_distribution.keys()),
        'datasets': [{
            'label': 'عدد الموظفين',
            'data': list(salary_distribution.values()),
            'backgroundColor': '#9C27B0',
        }]
    }
    
    return JsonResponse(chart_data)


# وظائف مساعدة
def generate_colors(n):
    """إنشاء مصفوفة من الألوان العشوائية"""
    colors = [
        '#4CAF50',  # أخضر
        '#2196F3',  # أزرق
        '#F44336',  # أحمر
        '#FFC107',  # أصفر
        '#9C27B0',  # بنفسجي
        '#00BCD4',  # سماوي
        '#FF9800',  # برتقالي
        '#795548',  # بني
        '#607D8B',  # رمادي
        '#E91E63',  # وردي
    ]
    
    result = []
    for i in range(n):
        result.append(colors[i % len(colors)])
    
    return result


@login_required
def employee_turnover_chart(request):
    """مخطط معدل دوران الموظفين"""
    today = timezone.now().date()
    
    # الحصول على السنة الحالية وبداية السنة
    current_year = today.year
    start_of_year = date(current_year, 1, 1)
    
    # البيانات للأشهر المنقضية من السنة الحالية
    months = []
    hires = []
    terminations = []
    
    for month in range(1, 13):
        if date(current_year, month, 1) <= today:
            # تحديد فترة الشهر
            month_start = date(current_year, month, 1)
            if month < 12:
                month_end = date(current_year, month + 1, 1) - timedelta(days=1)
            else:
                month_end = date(current_year, 12, 31)
            
            # الموظفون الجدد في هذا الشهر
            new_hires = Employee.objects.filter(
                emp_date_hiring__gte=month_start,
                emp_date_hiring__lte=month_end
            ).count()
            
            # الموظفون الذين غادروا في هذا الشهر
            # (هذا مجرد مثال، ستحتاج إلى تعديله حسب نموذج البيانات الخاص بك)
            # على سبيل المثال، إذا كان لديك حقل تاريخ المغادرة
            terminated = Employee.objects.filter(
                emp_date_termination__gte=month_start,
                emp_date_termination__lte=month_end
            ).count()
            
            # إضافة البيانات للقوائم
            months.append(month_start.strftime('%Y-%m'))
            hires.append(new_hires)
            terminations.append(terminated)
    
    chart_data = {
        'title': 'معدل دوران الموظفين',
        'type': 'line',
        'labels': months,
        'datasets': [
            {
                'label': 'التعيينات الجديدة',
                'data': hires,
                'borderColor': '#4CAF50',
                'backgroundColor': 'rgba(76, 175, 80, 0.2)',
            },
            {
                'label': 'المغادرون',
                'data': terminations,
                'borderColor': '#F44336',
                'backgroundColor': 'rgba(244, 67, 54, 0.2)',
            }
        ]
    }
    
    return JsonResponse(chart_data)
