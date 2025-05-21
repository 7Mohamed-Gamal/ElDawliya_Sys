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
from ..utils.permissions import require_report_permission, require_export_permission

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
    reports = []
    
    # Only show reports the user has permission to view
    if request.user.has_perm('Hr.view_employee') or request.user.is_superuser:
        reports.append({
            'id': 'employees',
            'name': 'تقرير الموظفين',
            'description': 'تقرير تفصيلي عن بيانات الموظفين',
            'icon': 'fas fa-users'
        })

    if request.user.has_perm('Hr.view_employeeleave') or request.user.is_superuser:
        reports.append({
            'id': 'leaves',
            'name': 'تقرير الإجازات',
            'description': 'تقرير عن إجازات الموظفين',
            'icon': 'fas fa-calendar-alt'
        })

    if request.user.has_perm('Hr.view_attendance') or request.user.is_superuser:
        reports.append({
            'id': 'attendance',
            'name': 'تقرير الحضور والانصراف',
            'description': 'تقرير عن حضور وانصراف الموظفين',
            'icon': 'fas fa-clock'
        })

    if request.user.has_perm('Hr.view_employeetask') or request.user.is_superuser:
        reports.append({
            'id': 'tasks',
            'name': 'تقرير المهام',
            'description': 'تقرير عن مهام الموظفين',
            'icon': 'fas fa-tasks'
        })

    if request.user.has_perm('Hr.view_hrtask') or request.user.is_superuser:
        reports.append({
            'id': 'hr_tasks',
            'name': 'تقرير مهام الموارد البشرية',
            'description': 'تقرير عن مهام قسم الموارد البشرية',
            'icon': 'fas fa-clipboard-list'
        })

    if request.user.has_perm('Hr.view_payroll') or request.user.is_superuser:
        reports.append({
            'id': 'payroll',
            'name': 'تقرير الرواتب',
            'description': 'تقرير عن رواتب الموظفين',
            'icon': 'fas fa-money-bill-wave'
        })

    if request.user.has_perm('Hr.view_insurance') or request.user.is_superuser:
        reports.append({
            'id': 'insurance',
            'name': 'تقرير التأمينات',
            'description': 'تقرير عن تأمينات الموظفين',
            'icon': 'fas fa-shield-alt'
        })

    context = {
        'reports': reports,
        'title': 'التقارير'
    }

    return render(request, 'Hr/reports/list.html', context)

@login_required
def report_detail(request, report_type):
    """عرض تفاصيل تقرير محدد"""
    # Check permissions before redirecting to specific reports
    if report_type == 'employees':
        if not request.user.has_perm('Hr.view_employee') and not request.user.is_superuser:
            return redirect('accounts:access_denied')
        return employee_report(request)
    elif report_type == 'leaves':
        if not request.user.has_perm('Hr.view_employeeleave') and not request.user.is_superuser:
            return redirect('accounts:access_denied')
        return leave_report(request)
    elif report_type == 'attendance':
        if not request.user.has_perm('Hr.view_attendance') and not request.user.is_superuser:
            return redirect('accounts:access_denied')
        return attendance_report(request)
    elif report_type == 'tasks':
        if not request.user.has_perm('Hr.view_employeetask') and not request.user.is_superuser:
            return redirect('accounts:access_denied')
        return task_report(request)
    elif report_type == 'hr_tasks':
        if not request.user.has_perm('Hr.view_hrtask') and not request.user.is_superuser:
            return redirect('accounts:access_denied')
        return hr_task_report(request)
    elif report_type == 'payroll':
        if not request.user.has_perm('Hr.view_payroll') and not request.user.is_superuser:
            return redirect('accounts:access_denied')
        return payroll_report(request)
    elif report_type == 'insurance':
        if not request.user.has_perm('Hr.view_insurance') and not request.user.is_superuser:
            return redirect('accounts:access_denied')
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

@login_required
@permission_required('Hr.view_employeeleave', login_url='accounts:access_denied')
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

    # Export if requested and user has permission
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel'] and (
        request.user.has_perm('Hr.export_leave_data') or 
        request.user.is_superuser
    ):
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

@login_required
@permission_required('Hr.view_employeetask', login_url='accounts:access_denied')
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

    # Export if requested and user has permission
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel'] and (
        request.user.has_perm('Hr.export_task_data') or 
        request.user.is_superuser
    ):
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

@login_required
@permission_required('Hr.view_hrtask', login_url='accounts:access_denied')
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

    # Export if requested and user has permission
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel'] and (
        request.user.has_perm('Hr.export_hrtask_data') or 
        request.user.is_superuser
    ):
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

@login_required
@permission_required('Hr.view_insurance', login_url='accounts:access_denied')
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

    # Export if requested and user has permission
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel'] and (
        request.user.has_perm('Hr.export_insurance_data') or 
        request.user.is_superuser
    ):
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
@permission_required('Hr.view_payroll', login_url='accounts:access_denied')
def monthly_salary_report(request):
    """تقرير الرواتب الشهري"""
    if not request.user.has_perm('Hr.view_payroll') and not request.user.is_superuser:
        return redirect('accounts:access_denied')

    # Process export requests
    if request.GET.get('export') and (request.user.has_perm('Hr.export_payroll_data') or request.user.is_superuser):
        export_format = request.GET.get('export')
        if export_format == 'excel':
            return export_salary_report_excel(request)
        elif export_format == 'csv':
            return export_salary_report_csv(request)

    # Filter parameters
    selected_period = request.GET.get('period')
    selected_department = request.GET.get('department')

    # Base queryset
    salary_entries = PayrollEntry.objects.select_related('employee', 'employee__department').all()

    # Apply filters
    if selected_period:
        salary_entries = salary_entries.filter(period_id=selected_period)
    if selected_department:
        salary_entries = salary_entries.filter(employee__department__dept_code=selected_department)

    # Calculate totals
    total_basic = salary_entries.aggregate(Sum('basic_salary'))['basic_salary__sum'] or 0
    total_allowances = salary_entries.aggregate(Sum('total_allowances'))['total_allowances__sum'] or 0
    total_deductions = salary_entries.aggregate(Sum('total_deductions'))['total_deductions__sum'] or 0
    total_salary = total_basic + total_allowances - total_deductions

    context = {
        'periods': PayrollPeriod.objects.all(),
        'departments': Department.objects.all(),
        'selected_period': selected_period,
        'selected_department': selected_department,
        'entries': salary_entries,
        'total_basic': total_basic,
        'total_allowances': total_allowances,
        'total_deductions': total_deductions,
        'total_salary': total_salary,
    }

    return render(request, 'Hr/reports/monthly_salary_report.html', context)

@login_required
@permission_required('Hr.view_payroll_reports', login_url='accounts:access_denied')
def export_salary_report_excel(request):
    """Export salary report to Excel"""
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('تقرير الرواتب')

    # Sheet header
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [
        'الموظف', 'القسم', 'الراتب الأساسي', 'البدلات',
        'الخصومات', 'صافي الراتب', 'تاريخ الحساب'
    ]

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    # Sheet body
    font_style = xlwt.XFStyle()

    # Get filtered data
    selected_period = request.GET.get('period')
    selected_department = request.GET.get('department')

    entries = PayrollEntry.objects.select_related('employee', 'employee__department').all()

    if selected_period:
        entries = entries.filter(period_id=selected_period)
    if selected_department:
        entries = entries.filter(employee__department__dept_code=selected_department)

    for entry in entries:
        row_num += 1
        row = [
            entry.employee.emp_full_name if entry.employee else '',
            entry.employee.department.dept_name if entry.employee and entry.employee.department else '',
            str(entry.basic_salary or 0),
            str(entry.total_allowances or 0),
            str(entry.total_deductions or 0),
            str((entry.basic_salary or 0) + (entry.total_allowances or 0) - (entry.total_deductions or 0)),
            entry.calculation_date.strftime('%Y-%m-%d') if entry.calculation_date else ''
        ]
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="salary_report.xls"'
    wb.save(response)
    return response

@login_required
@permission_required('Hr.view_payroll_reports', login_url='accounts:access_denied')
def export_salary_report_csv(request):
    """Export salary report to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="salary_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'الموظف', 'القسم', 'الراتب الأساسي', 'البدلات',
        'الخصومات', 'صافي الراتب', 'تاريخ الحساب'
    ])

    # Get filtered data
    selected_period = request.GET.get('period')
    selected_department = request.GET.get('department')

    entries = PayrollEntry.objects.select_related('employee', 'employee__department').all()

    if selected_period:
        entries = entries.filter(period_id=selected_period)
    if selected_department:
        entries = entries.filter(employee__department__dept_code=selected_department)

    for entry in entries:
        writer.writerow([
            entry.employee.emp_full_name if entry.employee else '',
            entry.employee.department.dept_name if entry.employee and entry.employee.department else '',
            str(entry.basic_salary or 0),
            str(entry.total_allowances or 0),
            str(entry.total_deductions or 0),
            str((entry.basic_salary or 0) + (entry.total_allowances or 0) - (entry.total_deductions or 0)),
            entry.calculation_date.strftime('%Y-%m-%d') if entry.calculation_date else ''
        ])

    return response

def check_report_permissions(user, report_type):
    """Helper function to check if user has required permissions for a report type"""
    permission_map = {
        'salary': 'Hr.view_payroll_reports',
        'attendance': 'Hr.view_attendance_reports',
        'leave': 'Hr.view_leave_reports',
        'task': 'Hr.view_task_reports',
        'employee': 'Hr.view_employee_reports'
    }
    
    if report_type not in permission_map:
        return False
        
    return user.has_perm(permission_map[report_type])

def has_export_permission(user, report_type):
    """Check if user has permission to export a specific report type"""
    export_permission_map = {
        'salary': 'Hr.export_payroll_reports',
        'attendance': 'Hr.export_attendance_reports',
        'leave': 'Hr.export_leave_reports',
        'task': 'Hr.export_task_reports',
        'employee': 'Hr.export_employee_reports'
    }
    
    if report_type not in export_permission_map:
        return False
        
    return user.has_perm(export_permission_map[report_type])

@login_required
def attendance_report_view(request):
    if not check_report_permissions(request.user, 'attendance'):
        return redirect('accounts:access_denied')
        
    # Filter parameters
    employee_id = request.GET.get('employee')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Base queryset
    attendance_data = AttendanceSummary.objects.all()

    # Apply filters
    if employee_id:
        attendance_data = attendance_data.filter(employee_id=employee_id)

    if status:
        attendance_data = attendance_data.filter(status=status)

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            attendance_data = attendance_data.filter(date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            attendance_data = attendance_data.filter(date__lte=date_to)
        except ValueError:
            pass

    # Export if requested
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel']:
        return export_attendance_data(attendance_data, export_format)

    context = {
        'attendance_data': attendance_data,
        'can_export': has_export_permission(request.user, 'attendance'),
        'employees': Employee.objects.all(),
        'statuses': AttendanceSummary.STATUS_CHOICES,
        'selected_employee': employee_id,
        'selected_status': status,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'title': 'تقرير الحضور والانصراف'
    }
    return render(request, 'Hr/reports/attendance_report.html', context)

@login_required
def leave_report_view(request):
    if not check_report_permissions(request.user, 'leave'):
        return redirect('accounts:access_denied')
        
    # Filter parameters
    employee_id = request.GET.get('employee')
    leave_type_id = request.GET.get('leave_type')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Base queryset
    leave_data = EmployeeLeave.objects.all()

    # Apply filters
    if employee_id:
        leave_data = leave_data.filter(employee_id=employee_id)

    if leave_type_id:
        leave_data = leave_data.filter(leave_type_id=leave_type_id)

    if status:
        leave_data = leave_data.filter(status=status)

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            leave_data = leave_data.filter(start_date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            leave_data = leave_data.filter(end_date__lte=date_to)
        except ValueError:
            pass

    # Export if requested and user has permission
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel'] and (
        request.user.has_perm('Hr.export_leave_data') or 
        request.user.is_superuser
    ):
        return export_leave_data(leave_data, export_format)

    # Prepare context for template
    from Hr.models.leave_models import LeaveType

    context = {
        'leave_data': leave_data,
        'can_export': has_export_permission(request.user, 'leave'),
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

@login_required
def employee_report_view(request):
    if not check_report_permissions(request.user, 'employee'):
        return redirect('accounts:access_denied')
        
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
        'can_export': has_export_permission(request.user, 'employee'),
        'can_view_salary': has_report_permission(request.user, 'salary'),
        'departments': Department.objects.all(),
        'employee': Employee,  # Pass the Employee model to access WORKING_CONDITION_CHOICES
        'selected_department': department_id,
        'selected_working_condition': working_condition,
        'title': 'تقرير الموظفين'
    }

    return render(request, 'Hr/reports/employee_report.html', context)

@login_required
def task_report_view(request):
    if not check_report_permissions(request.user, 'task'):
        return redirect('accounts:access_denied')
        
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

    # Export if requested and user has permission
    export_format = request.GET.get('export')
    if export_format in ['csv', 'excel'] and (
        request.user.has_perm('Hr.export_task_data') or 
        request.user.is_superuser
    ):
        return export_task_data(tasks, export_format)

    # Prepare context for template
    context = {
        'tasks': tasks,
        'can_export': has_export_permission(request.user, 'task'),
        'can_edit': has_edit_permission(request.user, 'task'),
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

@login_required
def export_report(request, report_type):
    if not has_export_permission(request.user, report_type):
        return redirect('accounts:access_denied')
        
    if report_type == 'salary':
        return export_salary_report(request)
    elif report_type == 'attendance':
        return export_attendance_report(request)
    elif report_type == 'leave':
        return export_leave_report(request)
    elif report_type == 'task':
        return export_task_report(request)
    else:
        raise Http404('Report type not found')
