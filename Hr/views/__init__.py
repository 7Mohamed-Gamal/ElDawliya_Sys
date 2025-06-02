from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from Hr.models.salary_models import PayrollPeriod, PayrollEntry, PayrollItemDetail, SalaryItem
from Hr.models.employee_model import Employee
from Hr.forms.salary_forms import PayrollPeriodForm
from Hr.models.attendance_models import AttendanceRule, EmployeeAttendanceRule
from Hr.forms.attendance_forms import AttendanceRuleForm, EmployeeAttendanceRuleForm, EmployeeAttendanceRuleBulkForm

# استيراد جميع الوظائف من وحداتها المحددة
from Hr.views.employee_views import (
    dashboard, employee_list, employee_create, employee_detail,
    employee_edit, employee_delete, employee_search, employee_print,
    employee_detail_view
)

from Hr.views.department_views_updated import (
    department_list, department_detail, department_create,
    department_edit, department_delete, department_employee_list,
    department_performance
)

from Hr.views.job_views import (
    job_list, job_create, job_detail, job_edit, job_delete,
    get_next_job_code
)

from Hr.views.salary_views import (
    salary_item_list, salary_item_create, salary_item_edit, salary_item_delete,
    employee_salary_item_list, employee_salary_item_create, 
    employee_salary_item_bulk_create, employee_salary_item_edit,
    employee_salary_item_delete, payroll_calculate
)

from Hr.views.car_views import (
    car_list, car_create, car_detail, car_edit, car_delete
)

from Hr.views.pickup_point_views import (
    pickup_point_list, pickup_point_create, pickup_point_detail,
    pickup_point_edit, pickup_point_delete
)

from Hr.views.insurance_views import (
    insurance_job_list, insurance_job_create, insurance_job_detail,
    insurance_job_edit, insurance_job_delete
)

from Hr.views.task_views import (
    employee_task_list, employee_task_create, employee_task_detail,
    employee_task_edit, employee_task_delete, task_step_toggle, task_step_delete
)

from Hr.views.note_views import (
    employee_note_list, employee_note_create, employee_note_detail,
    employee_note_edit, employee_note_delete
)

from Hr.views.file_views import (
    employee_file_list, employee_file_create, employee_file_detail,
    employee_file_edit, employee_file_delete
)

from Hr.views.hr_task_views import (
    hr_task_list, hr_task_create, hr_task_detail,
    hr_task_edit, hr_task_delete
)

from Hr.views.leave_views import (
    leave_type_list, leave_type_create, leave_type_edit,
    employee_leave_list, employee_leave_create, employee_leave_detail,
    employee_leave_edit, employee_leave_approve
)

@login_required
def payroll_period_list(request):
    """عرض قائمة فترات الرواتب"""
    # Get all periods ordered by most recent first
    periods = PayrollPeriod.objects.all().order_by('-period')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        periods = periods.filter(status=status)
        
    context = {
        'payroll_periods': periods,
        'page_title': 'فترات الرواتب'
    }
    
    return render(request, 'Hr/payrolls/payroll_period_list.html', context)

@login_required
def payroll_period_create(request):
    """إنشاء فترة راتب جديدة"""
    if request.method == 'POST':
        form = PayrollPeriodForm(request.POST)
        if form.is_valid():
            period = form.save(commit=False)
            period.created_by = request.user
            period.save()
            messages.success(request, 'تم إنشاء فترة الراتب بنجاح')
            return redirect('Hr:payroll_period_list')
    else:
        form = PayrollPeriodForm()
    
    context = {
        'form': form,
        'title': 'إنشاء فترة راتب جديدة'
    }
    
    return render(request, 'Hr/payrolls/payroll_period_form.html', context)

@login_required
def payroll_period_edit(request, pk):
    """تعديل فترة راتب"""
    period = get_object_or_404(PayrollPeriod, pk=pk)
    
    if request.method == 'POST':
        form = PayrollPeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث فترة الراتب بنجاح')
            return redirect('Hr:payroll_period_list')
    else:
        form = PayrollPeriodForm(instance=period)
    
    context = {
        'form': form,
        'period': period,
        'title': 'تعديل فترة راتب'
    }
    
    return render(request, 'Hr/payrolls/payroll_period_form.html', context)

@login_required
def payroll_period_delete(request, pk):
    """حذف فترة راتب"""
    period = get_object_or_404(PayrollPeriod, pk=pk)
    
    if request.method == 'POST':
        try:
            period.delete()
            messages.success(request, 'تم حذف فترة الراتب بنجاح')
        except Exception as e:
            messages.error(request, 'لا يمكن حذف فترة الراتب. قد تكون مرتبطة ببيانات أخرى.')
        return redirect('Hr:payroll_period_list')
    
    context = {
        'period': period,
        'title': 'حذف فترة راتب'
    }
    
    return render(request, 'Hr/payrolls/payroll_period_confirm_delete.html', context)

@login_required
def payroll_entry_list(request):
    """عرض قائمة سجلات الرواتب"""
    # Get filters from request
    period_id = request.GET.get('payroll_period')
    employee_id = request.GET.get('employee')
    
    # Base queryset
    entries = PayrollEntry.objects.select_related('employee', 'period').all()
    
    # Apply filters
    if period_id:
        entries = entries.filter(period_id=period_id)
    if employee_id:
        entries = entries.filter(employee_id=employee_id)
        
    # Get periods and employees for filter dropdowns
    payroll_periods = PayrollPeriod.objects.all().order_by('-period')
    employees = Employee.objects.filter(working_condition='سارى').order_by('emp_full_name')
    
    context = {
        'payroll_entries': entries,
        'payroll_periods': payroll_periods,
        'employees': employees,
        'selected_period': period_id,
        'selected_employee': employee_id,
        'page_title': 'سجلات الرواتب'
    }
    
    return render(request, 'Hr/payrolls/payroll_entry_list.html', context)

@login_required
def payroll_entry_detail(request, pk):
    """عرض تفاصيل سجل راتب"""
    entry = get_object_or_404(PayrollEntry.objects.select_related('employee', 'period'), pk=pk)
    
    # Get all salary items for this entry
    payroll_items = PayrollItemDetail.objects.filter(payroll_entry=entry).select_related('salary_item')
    
    context = {
        'payroll_entry': entry,
        'payroll_items': payroll_items,
        'page_title': f'تفاصيل راتب {entry.employee.emp_full_name}'
    }
    
    return render(request, 'Hr/payrolls/payroll_entry_detail.html', context)

@login_required
def payroll_entry_print(request, pk):
    """طباعة قسيمة راتب"""
    entry = get_object_or_404(PayrollEntry.objects.select_related('employee', 'period'), pk=pk)
    payroll_items = PayrollItemDetail.objects.filter(payroll_entry=entry).select_related('salary_item')
    
    context = {
        'payroll_entry': entry,
        'payroll_items': payroll_items,
        'page_title': f'قسيمة راتب {entry.employee.emp_full_name}'
    }
    
    return render(request, 'Hr/payrolls/payroll_entry_print.html', context)

@login_required
def payroll_entry_approve(request, pk):
    """اعتماد سجل راتب"""
    entry = get_object_or_404(PayrollEntry.objects.select_related('employee', 'period'), pk=pk)
    
    if entry.status != 'pending':
        messages.error(request, 'لا يمكن اعتماد سجل راتب غير معلق')
        return redirect('Hr:payroll_entry_detail', pk=entry.pk)
    
    entry.status = 'approved'
    entry.approved_by = request.user
    entry.approval_date = timezone.now()
    entry.save()
    
    messages.success(request, f'تم اعتماد راتب {entry.employee.emp_full_name} بنجاح')
    return redirect('Hr:payroll_entry_detail', pk=entry.pk)

@login_required 
def payroll_entry_reject(request, pk):
    """رفض سجل راتب"""
    entry = get_object_or_404(PayrollEntry.objects.select_related('employee', 'period'), pk=pk)
    
    if entry.status != 'pending':
        messages.error(request, 'لا يمكن رفض سجل راتب غير معلق')
        return redirect('Hr:payroll_entry_detail', pk=entry.pk)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason')
        if not rejection_reason:
            messages.error(request, 'يجب إدخال سبب الرفض')
            return redirect('Hr:payroll_entry_reject', pk=entry.pk)
            
        entry.status = 'rejected'
        entry.rejection_reason = rejection_reason
        entry.approved_by = request.user
        entry.approval_date = timezone.now()
        entry.save()
        
        messages.success(request, f'تم رفض راتب {entry.employee.emp_full_name}')
        return redirect('Hr:payroll_entry_detail', pk=entry.pk)
    
    context = {
        'payroll_entry': entry,
        'page_title': f'رفض راتب {entry.employee.emp_full_name}'
    }
    
    return render(request, 'Hr/payrolls/payroll_entry_reject.html', context)

@login_required
def attendance_rule_list(request):
    """عرض قائمة قواعد الحضور"""
    attendance_rules = AttendanceRule.objects.all()
    
    context = {
        'attendance_rules': attendance_rules,
        'page_title': 'قواعد الحضور'
    }
    
    return render(request, 'Hr/attendance/attendance_rule_list.html', context)

@login_required
def attendance_rule_create(request):
    """إنشاء قاعدة حضور جديدة"""
    if request.method == 'POST':
        form = AttendanceRuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء قاعدة الحضور بنجاح')
            return redirect('Hr:attendance_rule_list')
    else:
        form = AttendanceRuleForm()
    
    context = {
        'form': form,
        'page_title': 'إنشاء قاعدة حضور'
    }
    
    return render(request, 'Hr/attendance/attendance_rule_form.html', context)

@login_required
def attendance_rule_edit(request, pk):
    """تعديل قاعدة حضور"""
    rule = get_object_or_404(AttendanceRule, pk=pk)
    
    if request.method == 'POST':
        form = AttendanceRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث قاعدة الحضور بنجاح')
            return redirect('Hr:attendance_rule_list')
    else:
        form = AttendanceRuleForm(instance=rule)
    
    context = {
        'form': form,
        'rule': rule,
        'page_title': 'تعديل قاعدة حضور'
    }
    
    return render(request, 'Hr/attendance/attendance_rule_form.html', context)

@login_required
def attendance_rule_delete(request, pk):
    """حذف قاعدة حضور"""
    rule = get_object_or_404(AttendanceRule, pk=pk)
    
    if request.method == 'POST':
        try:
            rule.delete()
            messages.success(request, 'تم حذف قاعدة الحضور بنجاح')
        except Exception as e:
            messages.error(request, 'لا يمكن حذف قاعدة الحضور. قد تكون مرتبطة ببيانات أخرى.')
        return redirect('Hr:attendance_rule_list')
    
    context = {
        'attendance_rule': rule,
        'page_title': 'حذف قاعدة حضور'
    }
    
    return render(request, 'Hr/attendance/attendance_rule_confirm_delete.html', context)

@login_required
def employee_attendance_rule_list(request):
    """عرض قائمة قواعد حضور الموظفين"""
    # Get the employee ID from request
    employee_id = request.GET.get('employee')
    
    # Base queryset for employee attendance rules
    rules = EmployeeAttendanceRule.objects.select_related('employee', 'attendance_rule').all()
    
    # Filter by employee if provided
    if employee_id:
        rules = rules.filter(employee_id=employee_id)
        
    # Get employees for filter dropdown
    employees = Employee.objects.filter(working_condition='سارى').order_by('emp_full_name')
    
    context = {
        'employee_attendance_rules': rules,
        'employees': employees,
        'selected_employee': employee_id,
        'page_title': 'قواعد حضور الموظفين'
    }
    
    return render(request, 'Hr/attendance/employee_attendance_rule_list.html', context)

@login_required
def employee_attendance_rule_create(request):
    """إنشاء قاعدة حضور جديدة لموظف"""
    if request.method == 'POST':
        form = EmployeeAttendanceRuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء قاعدة الحضور للموظف بنجاح')
            return redirect('Hr:employee_attendance_rule_list')
    else:
        form = EmployeeAttendanceRuleForm()
    
    context = {
        'form': form,
        'page_title': 'إنشاء قاعدة حضور لموظف'
    }
    
    return render(request, 'Hr/attendance/employee_attendance_rule_form.html', context)

@login_required
def employee_attendance_rule_edit(request, pk):
    """تعديل قاعدة حضور لموظف"""
    rule = get_object_or_404(EmployeeAttendanceRule, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeAttendanceRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث قاعدة الحضور للموظف بنجاح')
            return redirect('Hr:employee_attendance_rule_list')
    else:
        form = EmployeeAttendanceRuleForm(instance=rule)
    
    context = {
        'form': form,
        'rule': rule,
        'page_title': 'تعديل قاعدة حضور لموظف'
    }
    
    return render(request, 'Hr/attendance/employee_attendance_rule_form.html', context)

@login_required
def employee_attendance_rule_delete(request, pk):
    """حذف قاعدة حضور لموظف"""
    rule = get_object_or_404(EmployeeAttendanceRule, pk=pk)
    
    if request.method == 'POST':
        try:
            rule.delete()
            messages.success(request, 'تم حذف قاعدة الحضور للموظف بنجاح')
        except Exception as e:
            messages.error(request, 'لا يمكن حذف قاعدة الحضور للموظف. قد تكون مرتبطة ببيانات أخرى.')
        return redirect('Hr:employee_attendance_rule_list')
    
    context = {
        'rule': rule,
        'page_title': 'حذف قاعدة حضور لموظف'
    }
    
    return render(request, 'Hr/attendance/employee_attendance_rule_confirm_delete.html', context)

@login_required
def employee_attendance_rule_bulk_create(request):
    """إنشاء قواعد حضور متعددة للموظفين"""
    if request.method == 'POST':
        form = EmployeeAttendanceRuleBulkForm(request.POST)
        if form.is_valid():
            employees = form.cleaned_data['employees']
            attendance_rule = form.cleaned_data['attendance_rule']
            effective_date = form.cleaned_data['effective_date']
            end_date = form.cleaned_data['end_date']
            is_active = form.cleaned_data['is_active']
            
            # Create rules for each selected employee
            for employee in employees:
                EmployeeAttendanceRule.objects.create(
                    employee=employee,
                    attendance_rule=attendance_rule,
                    effective_date=effective_date,
                    end_date=end_date,
                    is_active=is_active
                )
            
            messages.success(request, 'تم إنشاء قواعد الحضور للموظفين المحددين بنجاح')
            return redirect('Hr:employee_attendance_rule_list')
    else:
        form = EmployeeAttendanceRuleBulkForm()
    
    context = {
        'form': form,
        'page_title': 'إنشاء قواعد حضور متعددة'
    }
    
    return render(request, 'Hr/attendance/employee_attendance_rule_bulk_form.html', context)

def update_data(request):
    """تحديث بيانات الموظفين"""
    # Placeholder implementation for updating employee data
    return JsonResponse({'status': 'success', 'message': 'تم تحديث البيانات بنجاح'})

# تصدير جميع الوظائف
__all__ = [
    'dashboard', 'employee_list', 'employee_create', 'employee_detail',
    'employee_edit', 'employee_delete', 'employee_search', 'employee_print',
    'employee_detail_view',
    'department_list', 'department_detail', 'department_create',
    'department_edit', 'department_delete', 'department_employee_list',
    'department_performance',
    'job_list', 'job_create', 'job_detail', 'job_edit', 'job_delete',
    'get_next_job_code',
    'salary_item_list', 'salary_item_create', 'salary_item_edit', 'salary_item_delete',
    'employee_salary_item_list', 'employee_salary_item_create',
    'employee_salary_item_bulk_create', 'employee_salary_item_edit',
    'employee_salary_item_delete', 'payroll_calculate',
    'car_list', 'car_create', 'car_detail', 'car_edit', 'car_delete',
    'pickup_point_list', 'pickup_point_create', 'pickup_point_detail',
    'pickup_point_edit', 'pickup_point_delete',
    'insurance_job_list', 'insurance_job_create', 'insurance_job_detail',
    'insurance_job_edit', 'insurance_job_delete',
    'employee_task_list', 'employee_task_create', 'employee_task_detail',
    'employee_task_edit', 'employee_task_delete', 'task_step_toggle', 'task_step_delete',
    'employee_note_list', 'employee_note_create', 'employee_note_detail',
    'employee_note_edit', 'employee_note_delete',
    'employee_file_list', 'employee_file_create', 'employee_file_detail',
    'employee_file_edit', 'employee_file_delete',
    'hr_task_list', 'hr_task_create', 'hr_task_detail',
    'hr_task_edit', 'hr_task_delete',
    'leave_type_list', 'leave_type_create', 'leave_type_edit',
    'employee_leave_list', 'employee_leave_create', 'employee_leave_detail',
    'employee_leave_edit', 'employee_leave_approve',
    'payroll_period_list', 'payroll_period_create', 'payroll_period_edit', 'payroll_period_delete',
    'payroll_entry_list', 'payroll_entry_detail', 'payroll_entry_print',
    'payroll_entry_approve', 'payroll_entry_reject',
    'attendance_rule_list', 'attendance_rule_create', 'attendance_rule_edit', 'attendance_rule_delete',
    'employee_attendance_rule_list', 'employee_attendance_rule_create', 'employee_attendance_rule_edit',
    'employee_attendance_rule_delete', 'employee_attendance_rule_bulk_create'
]
