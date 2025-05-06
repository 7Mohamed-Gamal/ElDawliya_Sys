from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
import csv
from datetime import datetime, timedelta

from Hr.models.employee_model import Employee
from Hr.models.leave_models import EmployeeLeave
from Hr.models.task_models import EmployeeTask
from Hr.models.hr_task_models import HrTask
from Hr.models.salary_models import PayrollEntry
from Hr.models.attendance_models import AttendanceRecord, AttendanceSummary

# Try to import xlwt but make it optional
try:
    import xlwt
    XLWT_INSTALLED = True
except ImportError:
    XLWT_INSTALLED = False

def export_csv(data, filename, headers, row_generator):
    """Generic CSV export function"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    writer = csv.writer(response)
    writer.writerow(headers)
    for item in data:
        writer.writerow(row_generator(item))
    return response

def export_excel(data, filename, headers, row_generator):
    """Generic Excel export function"""
    if not XLWT_INSTALLED:
        return HttpResponse("حزمة xlwt غير مثبتة. يُرجى تثبيت حزمة xlwt باستخدام 'pip install xlwt' ثم إعادة تشغيل الخادم.")

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{filename}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    # Sheet header
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num, column_title in enumerate(headers):
        ws.write(row_num, col_num, column_title, font_style)

    # Sheet body
    font_style = xlwt.XFStyle()

    for item in data:
        row_num += 1
        row = row_generator(item)
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    wb.save(response)
    return response

def export_data(data, export_format, filename, headers, row_generator):
    """Generic export function that handles both CSV and Excel formats"""
    if export_format == 'excel':
        return export_excel(data, filename, headers, row_generator)
    elif export_format == 'csv':
        return export_csv(data, filename, headers, row_generator)
    else:
        return HttpResponse("Unsupported export format")

def export_employee_data(employees, export_format):
    """Export employee data to CSV or Excel"""
    headers = ['رقم الموظف', 'الاسم', 'القسم', 'الوظيفة', 'حالة العمل', 'تاريخ التعيين', 'حالة التأمين']

    def row_generator(employee):
        # Safely get department name
        dept_name = ''
        try:
            if employee.department:
                dept_name = employee.department.dept_name
            # Fallback to dept_name field if department relation fails
            elif employee.dept_name:
                dept_name = employee.dept_name
        except:
            # If department relation fails, use the dept_name field
            dept_name = employee.dept_name or ''

        return [
            employee.emp_id,
            employee.emp_full_name or '',
            dept_name,
            employee.jop_name or '',
            employee.working_condition or '',
            employee.emp_date_hiring.strftime('%Y-%m-%d') if employee.emp_date_hiring else '',
            employee.insurance_status or '',
        ]

    return export_data(employees, export_format, 'employees_report', headers, row_generator)

def export_leave_data(leaves, export_format):
    """Export leave data to CSV or Excel"""
    headers = ['الموظف', 'نوع الإجازة', 'تاريخ البداية', 'تاريخ النهاية', 'عدد الأيام', 'الحالة']

    def row_generator(leave):
        return [
            leave.employee.emp_full_name if leave.employee else '',
            leave.leave_type.name if leave.leave_type else '',
            leave.start_date.strftime('%Y-%m-%d') if leave.start_date else '',
            leave.end_date.strftime('%Y-%m-%d') if leave.end_date else '',
            leave.days_count or '',
            leave.status or '',
        ]

    return export_data(leaves, export_format, 'leaves_report', headers, row_generator)

def export_attendance_data(summaries, export_format):
    """Export attendance data to CSV or Excel"""
    headers = ['الموظف', 'التاريخ', 'وقت الحضور', 'وقت الانصراف', 'الحالة', 'الملاحظات']

    def row_generator(summary):
        return [
            summary.employee.emp_full_name if summary.employee else '',
            summary.date.strftime('%Y-%m-%d') if summary.date else '',
            summary.check_in.strftime('%H:%M') if summary.check_in else '',
            summary.check_out.strftime('%H:%M') if summary.check_out else '',
            summary.status or '',
            summary.notes or '',
        ]

    return export_data(summaries, export_format, 'attendance_report', headers, row_generator)

def export_task_data(tasks, export_format):
    """Export task data to CSV or Excel"""
    headers = ['العنوان', 'الموظف', 'الحالة', 'الأولوية', 'تاريخ البداية', 'تاريخ الاستحقاق', 'نسبة الإنجاز']

    def row_generator(task):
        return [
            task.title or '',
            task.employee.emp_full_name if task.employee else '',
            task.get_status_display() or '',
            task.get_priority_display() or '',
            task.start_date.strftime('%Y-%m-%d') if task.start_date else '',
            task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
            f"{task.progress}%" if task.progress is not None else '',
        ]

    return export_data(tasks, export_format, 'tasks_report', headers, row_generator)

def export_hr_task_data(tasks, export_format):
    """Export HR task data to CSV or Excel"""
    headers = ['العنوان', 'نوع المهمة', 'مسندة إلى', 'الحالة', 'الأولوية', 'تاريخ البداية', 'تاريخ الاستحقاق', 'نسبة الإنجاز']

    def row_generator(task):
        return [
            task.title or '',
            task.get_task_type_display() or '',
            task.assigned_to.get_full_name() if task.assigned_to else '',
            task.get_status_display() or '',
            task.get_priority_display() or '',
            task.start_date.strftime('%Y-%m-%d') if task.start_date else '',
            task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
            f"{task.progress}%" if task.progress is not None else '',
        ]

    return export_data(tasks, export_format, 'hr_tasks_report', headers, row_generator)

def export_payroll_data(entries, export_format):
    """Export payroll data to CSV or Excel"""
    headers = ['الموظف', 'فترة الراتب', 'الراتب الأساسي', 'البدلات', 'الخصومات', 'إجمالي الراتب', 'تاريخ الحساب']

    def row_generator(entry):
        return [
            entry.employee.emp_full_name if entry.employee else '',
            entry.payroll_period.name if entry.payroll_period else '',
            str(entry.basic_salary) if entry.basic_salary else '0',
            str(entry.total_allowances) if entry.total_allowances else '0',
            str(entry.total_deductions) if entry.total_deductions else '0',
            str(entry.total_salary) if entry.total_salary else '0',
            entry.calculation_date.strftime('%Y-%m-%d') if entry.calculation_date else '',
        ]

    return export_data(entries, export_format, 'payroll_report', headers, row_generator)

def export_insurance_data(employees, export_format):
    """Export insurance data to CSV or Excel"""
    headers = ['رقم الموظف', 'الاسم', 'القسم', 'الوظيفة', 'حالة التأمين', 'رقم التأمين', 'تاريخ التأمين']

    def row_generator(employee):
        # Safely get department name
        dept_name = ''
        try:
            if employee.department:
                dept_name = employee.department.dept_name
            # Fallback to dept_name field if department relation fails
            elif employee.dept_name:
                dept_name = employee.dept_name
        except:
            # If department relation fails, use the dept_name field
            dept_name = employee.dept_name or ''

        # Handle insurance_number which might not exist
        insurance_number = ''
        try:
            insurance_number = employee.insurance_number or ''
        except AttributeError:
            # Try number_insurance if insurance_number doesn't exist
            insurance_number = employee.number_insurance or ''

        # Handle insurance_date which might not exist
        insurance_date = ''
        try:
            if hasattr(employee, 'insurance_date') and employee.insurance_date:
                insurance_date = employee.insurance_date.strftime('%Y-%m-%d')
            elif hasattr(employee, 'date_insurance_start') and employee.date_insurance_start:
                insurance_date = employee.date_insurance_start.strftime('%Y-%m-%d')
        except:
            pass

        return [
            employee.emp_id,
            employee.emp_full_name or '',
            dept_name,
            employee.jop_name or '',
            employee.insurance_status or '',
            insurance_number,
            insurance_date,
        ]

    return export_data(employees, export_format, 'insurance_report', headers, row_generator)

@login_required
def report_list(request):
    """عرض قائمة التقارير المتاحة"""
    reports = [
        {
            'id': 'employees',
            'name': 'تقرير الموظفين',
            'description': 'تقرير تفصيلي عن بيانات الموظفين',
            'icon': 'fas fa-users'
        },
        {
            'id': 'leaves',
            'name': 'تقرير الإجازات',
            'description': 'تقرير عن إجازات الموظفين',
            'icon': 'fas fa-calendar-alt'
        },
        {
            'id': 'attendance',
            'name': 'تقرير الحضور والانصراف',
            'description': 'تقرير عن حضور وانصراف الموظفين',
            'icon': 'fas fa-clock'
        },
        {
            'id': 'tasks',
            'name': 'تقرير المهام',
            'description': 'تقرير عن مهام الموظفين',
            'icon': 'fas fa-tasks'
        },
        {
            'id': 'hr_tasks',
            'name': 'تقرير مهام الموارد البشرية',
            'description': 'تقرير عن مهام قسم الموارد البشرية',
            'icon': 'fas fa-clipboard-list'
        },
        {
            'id': 'payroll',
            'name': 'تقرير الرواتب',
            'description': 'تقرير عن رواتب الموظفين',
            'icon': 'fas fa-money-bill-wave'
        },
        {
            'id': 'insurance',
            'name': 'تقرير التأمينات',
            'description': 'تقرير عن تأمينات الموظفين',
            'icon': 'fas fa-shield-alt'
        },
    ]

    context = {
        'reports': reports,
        'title': 'التقارير'
    }

    return render(request, 'Hr/reports/list.html', context)

@login_required
def report_detail(request, report_type):
    """عرض تفاصيل تقرير محدد"""
    if report_type == 'employees':
        return employee_report(request)
    elif report_type == 'leaves':
        return leave_report(request)
    elif report_type == 'attendance':
        return attendance_report(request)
    elif report_type == 'tasks':
        return task_report(request)
    elif report_type == 'hr_tasks':
        return hr_task_report(request)
    elif report_type == 'payroll':
        return payroll_report(request)
    elif report_type == 'insurance':
        return insurance_report(request)
    else:
        return redirect('Hr:reports:list')

def employee_report(request):
    """تقرير الموظفين"""
    # Filter parameters
    department_id = request.GET.get('department')
    working_condition = request.GET.get('working_condition')

    # Base queryset
    employees = Employee.objects.all()

    # Apply filters
    if department_id:
        employees = employees.filter(department_id=department_id)

    if working_condition:
        employees = employees.filter(working_condition=working_condition)

    # Export if requested
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel']:
        return export_employee_data(employees, export_format)

    # Prepare context for template
    from Hr.models.department_models import Department

    context = {
        'employees': employees,
        'departments': Department.objects.all(),
        'employee': Employee,  # Pass the Employee model to access WORKING_CONDITION_CHOICES
        'selected_department': department_id,
        'selected_working_condition': working_condition,
        'title': 'تقرير الموظفين'
    }

    return render(request, 'Hr/reports/employee_report.html', context)

def leave_report(request):
    """تقرير الإجازات"""
    # Filter parameters
    employee_id = request.GET.get('employee')
    leave_type_id = request.GET.get('leave_type')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Base queryset
    leaves = EmployeeLeave.objects.all()

    # Apply filters
    if employee_id:
        leaves = leaves.filter(employee_id=employee_id)

    if leave_type_id:
        leaves = leaves.filter(leave_type_id=leave_type_id)

    if status:
        leaves = leaves.filter(status=status)

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            leaves = leaves.filter(start_date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            leaves = leaves.filter(end_date__lte=date_to)
        except ValueError:
            pass

    # Export if requested
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel']:
        return export_leave_data(leaves, export_format)

    # Prepare context for template
    from Hr.models.leave_models import LeaveType

    context = {
        'leaves': leaves,
        'employees': Employee.objects.all(),
        'leave_types': LeaveType.objects.all(),
        'statuses': EmployeeLeave.STATUS_CHOICES,
        'selected_employee': employee_id,
        'selected_leave_type': leave_type_id,
        'selected_status': status,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'title': 'تقرير الإجازات'
    }

    return render(request, 'Hr/reports/leave_report.html', context)

def attendance_report(request):
    """تقرير الحضور والانصراف"""
    # Filter parameters
    employee_id = request.GET.get('employee')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Base queryset
    summaries = AttendanceSummary.objects.all()

    # Apply filters
    if employee_id:
        summaries = summaries.filter(employee_id=employee_id)

    if status:
        summaries = summaries.filter(status=status)

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            summaries = summaries.filter(date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            summaries = summaries.filter(date__lte=date_to)
        except ValueError:
            pass

    # Export if requested
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel']:
        return export_attendance_data(summaries, export_format)

    # Prepare context for template
    context = {
        'summaries': summaries,
        'employees': Employee.objects.all(),
        'statuses': AttendanceSummary.STATUS_CHOICES,
        'selected_employee': employee_id,
        'selected_status': status,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'title': 'تقرير الحضور والانصراف'
    }

    return render(request, 'Hr/reports/attendance_report.html', context)

def task_report(request):
    """تقرير المهام"""
    # Filter parameters
    employee_id = request.GET.get('employee')
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Base queryset
    tasks = EmployeeTask.objects.all()

    # Apply filters
    if employee_id:
        tasks = tasks.filter(employee_id=employee_id)

    if status:
        tasks = tasks.filter(status=status)

    if priority:
        tasks = tasks.filter(priority=priority)

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            tasks = tasks.filter(start_date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            tasks = tasks.filter(due_date__lte=date_to)
        except ValueError:
            pass

    # Export if requested
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel']:
        return export_task_data(tasks, export_format)

    # Prepare context for template
    context = {
        'tasks': tasks,
        'employees': Employee.objects.all(),
        'statuses': EmployeeTask.STATUS_CHOICES,
        'priorities': EmployeeTask.PRIORITY_CHOICES,
        'selected_employee': employee_id,
        'selected_status': status,
        'selected_priority': priority,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'title': 'تقرير المهام'
    }

    return render(request, 'Hr/reports/task_report.html', context)

def hr_task_report(request):
    """تقرير مهام الموارد البشرية"""
    # Filter parameters
    task_type = request.GET.get('task_type')
    assigned_to = request.GET.get('assigned_to')
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Base queryset
    tasks = HrTask.objects.all()

    # Apply filters
    if task_type:
        tasks = tasks.filter(task_type=task_type)

    if assigned_to:
        tasks = tasks.filter(assigned_to_id=assigned_to)

    if status:
        tasks = tasks.filter(status=status)

    if priority:
        tasks = tasks.filter(priority=priority)

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            tasks = tasks.filter(start_date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            tasks = tasks.filter(due_date__lte=date_to)
        except ValueError:
            pass

    # Export if requested
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel']:
        return export_hr_task_data(tasks, export_format)

    # Prepare context for template
    from django.contrib.auth import get_user_model
    User = get_user_model()

    context = {
        'tasks': tasks,
        'task_types': HrTask.TASK_TYPE_CHOICES,
        'users': User.objects.all(),
        'statuses': HrTask.STATUS_CHOICES,
        'priorities': HrTask.PRIORITY_CHOICES,
        'selected_task_type': task_type,
        'selected_assigned_to': assigned_to,
        'selected_status': status,
        'selected_priority': priority,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'title': 'تقرير مهام الموارد البشرية'
    }

    return render(request, 'Hr/reports/hr_task_report.html', context)

def payroll_report(request):
    """تقرير الرواتب"""
    # Filter parameters
    employee_id = request.GET.get('employee')
    period_id = request.GET.get('period')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Base queryset
    entries = PayrollEntry.objects.all()

    # Apply filters
    if employee_id:
        entries = entries.filter(employee_id=employee_id)

    if period_id:
        entries = entries.filter(payroll_period_id=period_id)

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            entries = entries.filter(calculation_date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            entries = entries.filter(calculation_date__lte=date_to)
        except ValueError:
            pass

    # Export if requested
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel']:
        return export_payroll_data(entries, export_format)

    # Prepare context for template
    from Hr.models.salary_models import PayrollPeriod

    context = {
        'entries': entries,
        'employees': Employee.objects.all(),
        'periods': PayrollPeriod.objects.all(),
        'selected_employee': employee_id,
        'selected_period': period_id,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'title': 'تقرير الرواتب'
    }

    return render(request, 'Hr/reports/payroll_report.html', context)

def insurance_report(request):
    """تقرير التأمينات"""
    # Filter parameters
    department_id = request.GET.get('department')
    insurance_status = request.GET.get('insurance_status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Base queryset
    employees = Employee.objects.all()

    # Apply filters
    if department_id:
        employees = employees.filter(department_id=department_id)

    if insurance_status:
        employees = employees.filter(insurance_status=insurance_status)

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            # Try to use date_insurance_start if insurance_date doesn't exist
            try:
                employees = employees.filter(insurance_date__gte=date_from)
            except:
                employees = employees.filter(date_insurance_start__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            # Try to use date_insurance_start if insurance_date doesn't exist
            try:
                employees = employees.filter(insurance_date__lte=date_to)
            except:
                employees = employees.filter(date_insurance_start__lte=date_to)
        except ValueError:
            pass

    # Export if requested
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel']:
        return export_insurance_data(employees, export_format)

    # Prepare context for template
    from Hr.models.department_models import Department

    # Get insurance statuses from the model's choices
    insurance_statuses = getattr(Employee, 'INSURANCE_STATUSES',
                                getattr(Employee, 'INSURANCE_STATUS_CHOICES', []))

    context = {
        'employees': employees,
        'departments': Department.objects.all(),
        'insurance_statuses': insurance_statuses,
        'selected_department': department_id,
        'selected_insurance_status': insurance_status,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'title': 'تقرير التأمينات'
    }

    return render(request, 'Hr/reports/insurance_report.html', context)

@login_required
def monthly_salary_report(request):
    """تقرير الرواتب الشهري"""
    # Filter parameters
    period_id = request.GET.get('period')
    department_id = request.GET.get('department')

    # Base queryset
    entries = PayrollEntry.objects.all()

    # Apply filters
    if period_id:
        entries = entries.filter(payroll_period_id=period_id)

    if department_id:
        entries = entries.filter(employee__department_id=department_id)

    # Calculate totals
    total_basic = entries.aggregate(Sum('basic_salary'))['basic_salary__sum'] or 0
    total_allowances = entries.aggregate(Sum('total_allowances'))['total_allowances__sum'] or 0
    total_deductions = entries.aggregate(Sum('total_deductions'))['total_deductions__sum'] or 0
    total_salary = entries.aggregate(Sum('total_salary'))['total_salary__sum'] or 0

    # Export if requested
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel']:
        return export_payroll_data(entries, export_format)

    # Prepare context for template
    from Hr.models.salary_models import PayrollPeriod
    from Hr.models.department_models import Department

    context = {
        'entries': entries,
        'periods': PayrollPeriod.objects.all(),
        'departments': Department.objects.all(),
        'selected_period': period_id,
        'selected_department': department_id,
        'total_basic': total_basic,
        'total_allowances': total_allowances,
        'total_deductions': total_deductions,
        'total_salary': total_salary,
        'title': 'تقرير الرواتب الشهري'
    }

    return render(request, 'Hr/reports/monthly_salary_report.html', context)
