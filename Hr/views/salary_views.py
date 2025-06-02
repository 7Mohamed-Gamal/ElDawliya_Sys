from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone

from Hr.models.salary_models import (
    SalaryItem, EmployeeSalaryItem, PayrollPeriod, 
    PayrollEntry, PayrollItemDetail
)
from Hr.forms.salary_forms import (
    SalaryItemForm, EmployeeSalaryItemForm, EmployeeSalaryItemBulkForm,
    PayrollPeriodForm, PayrollCalculationForm
)
from Hr.decorators import hr_module_permission_required

@login_required
@hr_module_permission_required('payroll', 'view')
def salary_item_list(request):
    """عرض قائمة بنود الرواتب"""
    salary_items = SalaryItem.objects.all().order_by('item_code')
    
    context = {
        'salary_items': salary_items,
        'title': 'بنود الرواتب'
    }
    
    return render(request, 'Hr/salary/item_list.html', context)

@login_required
@hr_module_permission_required('payroll', 'add')
def salary_item_create(request):
    """إنشاء بند راتب جديد"""
    if request.method == 'POST':
        form = SalaryItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء بند الراتب بنجاح')
            return redirect('Hr:salary_item_list')
    else:
        form = SalaryItemForm()
    
    context = {
        'form': form,
        'title': 'إنشاء بند راتب'
    }
    
    return render(request, 'Hr/salary/item_form.html', context)

@login_required
@hr_module_permission_required('payroll', 'edit')
def salary_item_edit(request, pk):
    """تعديل بند راتب"""
    salary_item = get_object_or_404(SalaryItem, pk=pk)
    
    if request.method == 'POST':
        form = SalaryItemForm(request.POST, instance=salary_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بند الراتب بنجاح')
            return redirect('Hr:salary_item_list')
    else:
        form = SalaryItemForm(instance=salary_item)
    
    context = {
        'form': form,
        'salary_item': salary_item,
        'title': f'تعديل بند الراتب: {salary_item.name}'
    }
    
    return render(request, 'Hr/salary/item_form.html', context)

@login_required
@hr_module_permission_required('payroll', 'delete')
def salary_item_delete(request, pk):
    """حذف بند راتب"""
    salary_item = get_object_or_404(SalaryItem, pk=pk)
    
    if request.method == 'POST':
        salary_item.delete()
        messages.success(request, 'تم حذف بند الراتب بنجاح')
        return redirect('Hr:salary_item_list')
    
    context = {
        'salary_item': salary_item,
        'title': f'حذف بند الراتب: {salary_item.name}'
    }
    
    return render(request, 'Hr/salary/item_delete.html', context)

@login_required
@hr_module_permission_required('payroll', 'view')
def employee_salary_item_list(request):
    """عرض قائمة بنود رواتب الموظفين"""
    salary_items = EmployeeSalaryItem.objects.select_related('employee', 'salary_item').all()
    
    # Group by employee
    employees_salary_items = {}
    for item in salary_items:
        if item.employee_id not in employees_salary_items:
            employees_salary_items[item.employee_id] = {
                'employee': item.employee,
                'items': [],
                'total': 0
            }
        employees_salary_items[item.employee_id]['items'].append(item)
        employees_salary_items[item.employee_id]['total'] += item.amount
    
    context = {
        'employees_salary_items': employees_salary_items,
        'title': 'بنود رواتب الموظفين'
    }
    
    return render(request, 'Hr/salary/employee_item_list.html', context)

@login_required
@hr_module_permission_required('payroll', 'add')
def employee_salary_item_create(request):
    """إنشاء بند راتب جديد لموظف"""
    if request.method == 'POST':
        form = EmployeeSalaryItemForm(request.POST)
        if form.is_valid():
            salary_item = form.save()
            messages.success(request, 'تم إضافة بند الراتب للموظف بنجاح')
            return redirect('Hr:employee_salary_item_list')
    else:
        form = EmployeeSalaryItemForm()
    
    context = {
        'form': form,
        'title': 'إضافة بند راتب لموظف'
    }
    
    return render(request, 'Hr/salary/employee_item_form.html', context)

@login_required
@hr_module_permission_required('payroll', 'add')
def employee_salary_item_bulk_create(request):
    """إنشاء بنود رواتب للموظفين بالجملة"""
    if request.method == 'POST':
        form = EmployeeSalaryItemBulkForm(request.POST)
        if form.is_valid():
            salary_item = form.cleaned_data['salary_item']
            amount = form.cleaned_data['amount']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            employees = form.cleaned_data['employees']
            
            created_items = []
            for employee in employees:
                item = EmployeeSalaryItem.objects.create(
                    employee=employee,
                    salary_item=salary_item,
                    amount=amount,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=True
                )
                created_items.append(item)
            
            messages.success(
                request, 
                f'تم إضافة بند الراتب لعدد {len(created_items)} موظف بنجاح'
            )
            return redirect('Hr:employee_salary_item_list')
    else:
        form = EmployeeSalaryItemBulkForm()
    
    context = {
        'form': form,
        'title': 'إضافة بنود رواتب للموظفين'
    }
    
    return render(request, 'Hr/salary/employee_item_bulk_form.html', context)

@login_required
@hr_module_permission_required('payroll', 'edit')
def employee_salary_item_edit(request, pk):
    """تعديل بند راتب موظف"""
    salary_item = get_object_or_404(EmployeeSalaryItem, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeSalaryItemForm(request.POST, instance=salary_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بند الراتب للموظف بنجاح')
            return redirect('Hr:employee_salary_item_list')
    else:
        form = EmployeeSalaryItemForm(instance=salary_item)
    
    context = {
        'form': form,
        'salary_item': salary_item,
        'title': f'تعديل بند راتب: {salary_item.employee} - {salary_item.salary_item}'
    }
    
    return render(request, 'Hr/salary/employee_item_form.html', context)

@login_required
@hr_module_permission_required('payroll', 'delete')
def employee_salary_item_delete(request, pk):
    """حذف بند راتب موظف"""
    salary_item = get_object_or_404(EmployeeSalaryItem, pk=pk)
    
    if request.method == 'POST':
        salary_item.delete()
        messages.success(request, 'تم حذف بند الراتب للموظف بنجاح')
        return redirect('Hr:employee_salary_item_list')
    
    context = {
        'salary_item': salary_item,
        'title': f'حذف بند راتب: {salary_item.employee} - {salary_item.salary_item}'
    }
    
    return render(request, 'Hr/salary/employee_item_delete.html', context)

@login_required
@hr_module_permission_required('payroll', 'calculate')
def payroll_calculate(request):
    """حساب الرواتب"""
    if request.method == 'POST':
        form = PayrollCalculationForm(request.POST)
        if form.is_valid():
            period = form.cleaned_data['period']
            
            # Create payroll entries for all active employees
            created_entries = []
            for emp_salary in EmployeeSalaryItem.objects.filter(
                employee__is_active=True
            ).select_related('employee', 'salary_item'):
                entry, created = PayrollEntry.objects.get_or_create(
                    employee=emp_salary.employee,
                    period=period,
                    defaults={
                        'total_amount': emp_salary.amount,
                        'status': 'pending'
                    }
                )
                
                if created:
                    # Create payroll item details
                    PayrollItemDetail.objects.create(
                        payroll_entry=entry,
                        salary_item=emp_salary.salary_item,
                        amount=emp_salary.amount
                    )
                    created_entries.append(entry)
            
            messages.success(
                request, 
                f'تم حساب الرواتب بنجاح لعدد {len(created_entries)} موظف'
            )
            return redirect('Hr:payroll_entry_list')
    else:
        form = PayrollCalculationForm()
    
    context = {
        'form': form,
        'title': 'حساب الرواتب'
    }
    
    return render(request, 'Hr/salary/calculate.html', context)

@login_required
@hr_module_permission_required('payroll', 'view')
def payroll_period_list(request):
    """Displays a list of payroll periods."""
    payroll_periods = PayrollPeriod.objects.all().order_by('-start_date')
    context = {
        'payroll_periods': payroll_periods,
        'title': 'فترات الرواتب'
    }
    return render(request, 'Hr/salary/payroll_period_list.html', context)

@login_required
@hr_module_permission_required('payroll', 'add')
def payroll_period_create(request):
    """Handles the creation of new payroll periods."""
    if request.method == 'POST':
        form = PayrollPeriodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء فترة الراتب بنجاح')
            return redirect('Hr:payroll_period_list')
    else:
        form = PayrollPeriodForm()
    context = {
        'form': form,
        'title': 'إنشاء فترة راتب'
    }
    return render(request, 'Hr/salary/payroll_period_form.html', context)

@login_required
@hr_module_permission_required('payroll', 'edit')
def payroll_period_edit(request, pk):
    """Handles editing existing payroll periods."""
    payroll_period = get_object_or_404(PayrollPeriod, pk=pk)
    if request.method == 'POST':
        form = PayrollPeriodForm(request.POST, instance=payroll_period)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث فترة الراتب بنجاح')
            return redirect('Hr:payroll_period_list')
    else:
        form = PayrollPeriodForm(instance=payroll_period)
    context = {
        'form': form,
        'payroll_period': payroll_period,
        'title': f'تعديل فترة الراتب: {payroll_period}'
    }
    return render(request, 'Hr/salary/payroll_period_form.html', context)

@login_required
@hr_module_permission_required('payroll', 'delete')
def payroll_period_delete(request, pk):
    """Handles deleting payroll periods."""
    payroll_period = get_object_or_404(PayrollPeriod, pk=pk)
    if request.method == 'POST':
        payroll_period.delete()
        messages.success(request, 'تم حذف فترة الراتب بنجاح')
        return redirect('Hr:payroll_period_list')
    context = {
        'payroll_period': payroll_period,
        'title': f'حذف فترة الراتب: {payroll_period}'
    }
    return render(request, 'Hr/salary/payroll_period_confirm_delete.html', context)

@login_required
@hr_module_permission_required('payroll', 'view')
def payroll_entry_list(request):
    """عرض قائمة إدخالات الرواتب"""
    payroll_entries = PayrollEntry.objects.select_related('employee', 'period').all()

    context = {
        'payroll_entries': payroll_entries,
        'title': 'إدخالات الرواتب'
    }

    return render(request, 'Hr/salary/payroll_entry_list.html', context)

@login_required
@hr_module_permission_required('payroll', 'view')
def payroll_entry_detail(request, pk):
    """عرض تفاصيل إدخال الرواتب"""
    payroll_entry = get_object_or_404(PayrollEntry, pk=pk)
    payroll_item_details = PayrollItemDetail.objects.filter(payroll_entry=payroll_entry).select_related('salary_item')

    context = {
        'payroll_entry': payroll_entry,
        'payroll_item_details': payroll_item_details,
        'title': f'تفاصيل إدخال الرواتب: {payroll_entry.employee}'
    }

    return render(request, 'Hr/salary/payroll_entry_detail.html', context)

@login_required
@hr_module_permission_required('payroll', 'approve')
def payroll_entry_approve(request, pk):
    """الموافقة على إدخال الرواتب"""
    payroll_entry = get_object_or_404(PayrollEntry, pk=pk)

    if request.method == 'POST':
        payroll_entry.status = 'approved'
        payroll_entry.save()
        messages.success(request, f'تمت الموافقة على إدخال الرواتب للموظف {payroll_entry.employee}')
        return redirect('Hr:payroll_entry_list')

    context = {
        'payroll_entry': payroll_entry,
        'title': f'الموافقة على إدخال الرواتب: {payroll_entry.employee}'
    }

    return render(request, 'Hr/salary/payroll_entry_approve.html', context)

@login_required
@hr_module_permission_required('payroll', 'reject')
def payroll_entry_reject(request, pk):
    """رفض إدخال الرواتب"""
    payroll_entry = get_object_or_404(PayrollEntry, pk=pk)

    if request.method == 'POST':
        payroll_entry.status = 'rejected'
        payroll_entry.save()
        messages.success(request, f'تم رفض إدخال الرواتب للموظف {payroll_entry.employee}')
        return redirect('Hr:payroll_entry_list')

    context = {
        'payroll_entry': payroll_entry,
        'title': f'رفض إدخال الرواتب: {payroll_entry.employee}'
    }

    return render(request, 'Hr/salary/payroll_entry_reject.html', context)