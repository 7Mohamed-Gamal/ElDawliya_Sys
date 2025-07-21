"""
Working Salary Views
These views provide actual implementation for salary/payroll management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

# Import models that exist
try:
    from Hr.models.salary_models import (
        HrSalaryItem as SalaryItem, 
        HrEmployeeSalaryItem as EmployeeSalaryItem, 
        HrPayrollPeriod as PayrollPeriod,
        HrPayrollEntry as PayrollEntry
    )
    SALARY_MODELS_AVAILABLE = True
except ImportError:
    SALARY_MODELS_AVAILABLE = False
    SalaryItem = EmployeeSalaryItem = PayrollPeriod = PayrollEntry = None

# Import legacy employee model
from Hr.models.legacy_employee import LegacyEmployee as Employee

# Import forms
try:
    from Hr.forms.salary_forms import (
        SalaryItemForm, EmployeeSalaryItemForm, EmployeeSalaryItemBulkForm,
        PayrollPeriodForm, PayrollCalculationForm
    )
    SALARY_FORMS_AVAILABLE = True
except ImportError:
    SALARY_FORMS_AVAILABLE = False


def render_under_construction(request, title):
    """Helper function to render under construction page"""
    return render(request, 'Hr/under_construction.html', {'title': title})


# =============================================================================
# SALARY ITEM VIEWS
# =============================================================================

@login_required
def salary_item_list(request):
    """عرض قائمة بنود الرواتب"""
    if not SALARY_MODELS_AVAILABLE:
        return render_under_construction(request, 'قائمة بنود الرواتب')
    
    try:
        salary_items = SalaryItem.objects.all().order_by('item_code')
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            salary_items = salary_items.filter(
                Q(name__icontains=search_query) |
                Q(item_code__icontains=search_query)
            )
        
        # Filter by type
        item_type = request.GET.get('type', '')
        if item_type:
            salary_items = salary_items.filter(type=item_type)
        
        # Pagination
        paginator = Paginator(salary_items, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'salary_items': page_obj,
            'search_query': search_query,
            'selected_type': item_type,
            'title': 'بنود الرواتب',
            'total_items': salary_items.count()
        }
        
        return render(request, 'Hr/salary/item_list.html', context)
        
    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض بنود الرواتب: {str(e)}')
        return render(request, 'Hr/salary/item_list.html', {
            'salary_items': [],
            'title': 'بنود الرواتب',
            'error': str(e)
        })


@login_required
def salary_item_create(request):
    """إنشاء بند راتب جديد"""
    if not SALARY_MODELS_AVAILABLE or not SALARY_FORMS_AVAILABLE:
        return render_under_construction(request, 'إنشاء بند راتب')
    
    if request.method == 'POST':
        form = SalaryItemForm(request.POST)
        if form.is_valid():
            try:
                salary_item = form.save()
                messages.success(request, f'تم إنشاء بند الراتب "{salary_item.name}" بنجاح')
                return redirect('Hr:salaries:salary_item_list')
            except Exception as e:
                messages.error(request, f'حدث خطأ في إنشاء بند الراتب: {str(e)}')
    else:
        form = SalaryItemForm()
    
    context = {
        'form': form,
        'title': 'إنشاء بند راتب جديد',
        'is_edit': False
    }
    
    return render(request, 'Hr/salary/item_form.html', context)


@login_required
def salary_item_edit(request, pk):
    """تعديل بند راتب"""
    if not SALARY_MODELS_AVAILABLE or not SALARY_FORMS_AVAILABLE:
        return render_under_construction(request, 'تعديل بند راتب')
    
    salary_item = get_object_or_404(SalaryItem, pk=pk)
    
    if request.method == 'POST':
        form = SalaryItemForm(request.POST, instance=salary_item)
        if form.is_valid():
            try:
                salary_item = form.save()
                messages.success(request, f'تم تحديث بند الراتب "{salary_item.name}" بنجاح')
                return redirect('Hr:salaries:salary_item_list')
            except Exception as e:
                messages.error(request, f'حدث خطأ في تحديث بند الراتب: {str(e)}')
    else:
        form = SalaryItemForm(instance=salary_item)
    
    context = {
        'form': form,
        'salary_item': salary_item,
        'title': f'تعديل بند الراتب: {salary_item.name}',
        'is_edit': True
    }
    
    return render(request, 'Hr/salary/item_form.html', context)


@login_required
def salary_item_delete(request, pk):
    """حذف بند راتب"""
    if not SALARY_MODELS_AVAILABLE:
        return render_under_construction(request, 'حذف بند راتب')
    
    salary_item = get_object_or_404(SalaryItem, pk=pk)
    
    if request.method == 'POST':
        try:
            # Check if item is used by employees
            if EmployeeSalaryItem and EmployeeSalaryItem.objects.filter(salary_item=salary_item).exists():
                messages.error(request, 'لا يمكن حذف بند الراتب لأنه مرتبط بموظفين')
                return redirect('Hr:salaries:salary_item_list')
            
            item_name = salary_item.name
            salary_item.delete()
            messages.success(request, f'تم حذف بند الراتب "{item_name}" بنجاح')
            return redirect('Hr:salaries:salary_item_list')
            
        except Exception as e:
            messages.error(request, f'حدث خطأ في حذف بند الراتب: {str(e)}')
            return redirect('Hr:salaries:salary_item_list')
    
    context = {
        'salary_item': salary_item,
        'title': f'حذف بند الراتب: {salary_item.name}'
    }
    
    return render(request, 'Hr/salary/item_delete.html', context)


# =============================================================================
# EMPLOYEE SALARY ITEM VIEWS
# =============================================================================

@login_required
def employee_salary_item_list(request, emp_id):
    """عرض بنود راتب موظف"""
    if not SALARY_MODELS_AVAILABLE:
        return render_under_construction(request, 'بنود راتب الموظف')
    
    try:
        employee = get_object_or_404(Employee, emp_id=emp_id)
        
        if EmployeeSalaryItem:
            employee_items = EmployeeSalaryItem.objects.filter(
                employee_id=emp_id
            ).select_related('salary_item').order_by('salary_item__type', 'salary_item__name')
        else:
            employee_items = []
        
        # Calculate totals
        total_additions = sum(item.amount for item in employee_items if item.salary_item.type == 'addition')
        total_deductions = sum(item.amount for item in employee_items if item.salary_item.type == 'deduction')
        net_salary = total_additions - total_deductions
        
        context = {
            'employee': employee,
            'employee_items': employee_items,
            'total_additions': total_additions,
            'total_deductions': total_deductions,
            'net_salary': net_salary,
            'title': f'بنود راتب الموظف: {employee.emp_name}'
        }
        
        return render(request, 'Hr/salary/employee_items.html', context)
        
    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض بنود راتب الموظف: {str(e)}')
        return redirect('Hr:employees:list')


@login_required
def employee_salary_item_create(request, emp_id):
    """إضافة بند راتب لموظف"""
    if not SALARY_MODELS_AVAILABLE or not SALARY_FORMS_AVAILABLE:
        return render_under_construction(request, 'إضافة بند راتب للموظف')
    
    employee = get_object_or_404(Employee, emp_id=emp_id)
    
    if request.method == 'POST':
        form = EmployeeSalaryItemForm(request.POST)
        if form.is_valid():
            try:
                employee_item = form.save(commit=False)
                employee_item.employee_id = emp_id
                employee_item.save()
                messages.success(request, 'تم إضافة بند الراتب للموظف بنجاح')
                return redirect('Hr:salaries:employee_salary_item_list', emp_id=emp_id)
            except Exception as e:
                messages.error(request, f'حدث خطأ في إضافة بند الراتب: {str(e)}')
    else:
        form = EmployeeSalaryItemForm()
    
    context = {
        'form': form,
        'employee': employee,
        'title': f'إضافة بند راتب للموظف: {employee.emp_name}',
        'is_edit': False
    }
    
    return render(request, 'Hr/salary/employee_item_form.html', context)


@login_required
def employee_salary_item_bulk_create(request):
    """إضافة بند راتب لعدة موظفين"""
    if not SALARY_MODELS_AVAILABLE or not SALARY_FORMS_AVAILABLE:
        return render_under_construction(request, 'إضافة بند راتب لعدة موظفين')
    
    if request.method == 'POST':
        form = EmployeeSalaryItemBulkForm(request.POST)
        if form.is_valid():
            try:
                # Process bulk creation
                created_count = form.save()
                messages.success(request, f'تم إضافة بند الراتب لـ {created_count} موظف بنجاح')
                return redirect('Hr:salaries:salary_item_list')
            except Exception as e:
                messages.error(request, f'حدث خطأ في إضافة بند الراتب: {str(e)}')
    else:
        form = EmployeeSalaryItemBulkForm()
    
    context = {
        'form': form,
        'title': 'إضافة بند راتب لعدة موظفين'
    }
    
    return render(request, 'Hr/salary/bulk_create_form.html', context)


@login_required
def employee_salary_item_edit(request, pk):
    """تعديل بند راتب موظف"""
    if not SALARY_MODELS_AVAILABLE or not SALARY_FORMS_AVAILABLE:
        return render_under_construction(request, 'تعديل بند راتب موظف')
    
    employee_item = get_object_or_404(EmployeeSalaryItem, pk=pk)
    employee = get_object_or_404(Employee, emp_id=employee_item.employee_id)
    
    if request.method == 'POST':
        form = EmployeeSalaryItemForm(request.POST, instance=employee_item)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'تم تحديث بند الراتب بنجاح')
                return redirect('Hr:salaries:employee_salary_item_list', emp_id=employee.emp_id)
            except Exception as e:
                messages.error(request, f'حدث خطأ في تحديث بند الراتب: {str(e)}')
    else:
        form = EmployeeSalaryItemForm(instance=employee_item)
    
    context = {
        'form': form,
        'employee': employee,
        'employee_item': employee_item,
        'title': f'تعديل بند راتب الموظف: {employee.emp_name}',
        'is_edit': True
    }
    
    return render(request, 'Hr/salary/employee_item_form.html', context)


@login_required
def employee_salary_item_delete(request, pk):
    """حذف بند راتب موظف"""
    if not SALARY_MODELS_AVAILABLE:
        return render_under_construction(request, 'حذف بند راتب موظف')
    
    employee_item = get_object_or_404(EmployeeSalaryItem, pk=pk)
    employee = get_object_or_404(Employee, emp_id=employee_item.employee_id)
    
    if request.method == 'POST':
        try:
            employee_item.delete()
            messages.success(request, 'تم حذف بند الراتب بنجاح')
            return redirect('Hr:salaries:employee_salary_item_list', emp_id=employee.emp_id)
        except Exception as e:
            messages.error(request, f'حدث خطأ في حذف بند الراتب: {str(e)}')
            return redirect('Hr:salaries:employee_salary_item_list', emp_id=employee.emp_id)
    
    context = {
        'employee': employee,
        'employee_item': employee_item,
        'title': f'حذف بند راتب الموظف: {employee.emp_name}'
    }
    
    return render(request, 'Hr/salary/employee_item_delete.html', context)


# =============================================================================
# PAYROLL CALCULATION VIEWS
# =============================================================================

@login_required
def payroll_calculate(request):
    """حساب كشف الرواتب"""
    if not SALARY_MODELS_AVAILABLE:
        return render_under_construction(request, 'حساب كشف الرواتب')

    if request.method == 'POST':
        if not SALARY_FORMS_AVAILABLE:
            messages.error(request, 'نماذج الرواتب غير متاحة حالياً')
            return redirect('Hr:dashboard')

        form = PayrollCalculationForm(request.POST)
        if form.is_valid():
            try:
                # Get calculation parameters
                period_id = form.cleaned_data.get('period_id')
                department_id = form.cleaned_data.get('department_id')

                # Get employees to calculate
                employees = Employee.objects.filter(working_condition='سارى')
                if department_id:
                    employees = employees.filter(department_id=department_id)

                calculated_count = 0
                total_amount = Decimal('0.00')

                for employee in employees:
                    # Calculate employee salary
                    if EmployeeSalaryItem:
                        employee_items = EmployeeSalaryItem.objects.filter(
                            employee_id=employee.emp_id
                        ).select_related('salary_item')

                        additions = sum(
                            item.amount for item in employee_items
                            if item.salary_item.type == 'addition'
                        )
                        deductions = sum(
                            item.amount for item in employee_items
                            if item.salary_item.type == 'deduction'
                        )
                        net_salary = additions - deductions

                        if net_salary > 0:
                            calculated_count += 1
                            total_amount += net_salary

                messages.success(request,
                    f'تم حساب الرواتب لـ {calculated_count} موظف بإجمالي {total_amount:,.2f}')

                # Redirect to payroll list or results page
                return redirect('Hr:salaries:payroll_period_list')

            except Exception as e:
                messages.error(request, f'حدث خطأ في حساب الرواتب: {str(e)}')
    else:
        form = PayrollCalculationForm() if SALARY_FORMS_AVAILABLE else None

    # Get summary data
    try:
        total_employees = Employee.objects.filter(working_condition='سارى').count()

        if EmployeeSalaryItem:
            employees_with_salary = EmployeeSalaryItem.objects.values('employee_id').distinct().count()
        else:
            employees_with_salary = 0

        context = {
            'form': form,
            'total_employees': total_employees,
            'employees_with_salary': employees_with_salary,
            'employees_without_salary': total_employees - employees_with_salary,
            'title': 'حساب كشف الرواتب'
        }

    except Exception as e:
        context = {
            'form': form,
            'title': 'حساب كشف الرواتب',
            'error': str(e)
        }

    return render(request, 'Hr/salary/payroll_calculate.html', context)


# =============================================================================
# PAYROLL PERIOD VIEWS
# =============================================================================

@login_required
def payroll_period_list(request):
    """عرض قائمة فترات الرواتب"""
    if not SALARY_MODELS_AVAILABLE:
        return render_under_construction(request, 'فترات الرواتب')

    try:
        if PayrollPeriod:
            periods = PayrollPeriod.objects.all().order_by('-start_date')
        else:
            periods = []

        # Pagination
        paginator = Paginator(periods, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'periods': page_obj,
            'title': 'فترات الرواتب'
        }

        return render(request, 'Hr/salary/period_list.html', context)

    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض فترات الرواتب: {str(e)}')
        return render(request, 'Hr/salary/period_list.html', {
            'periods': [],
            'title': 'فترات الرواتب',
            'error': str(e)
        })


@login_required
def payroll_period_create(request):
    """إنشاء فترة راتب جديدة"""
    if not SALARY_MODELS_AVAILABLE or not SALARY_FORMS_AVAILABLE:
        return render_under_construction(request, 'إنشاء فترة راتب')

    if request.method == 'POST':
        form = PayrollPeriodForm(request.POST)
        if form.is_valid():
            try:
                period = form.save()
                messages.success(request, f'تم إنشاء فترة الراتب "{period.name}" بنجاح')
                return redirect('Hr:salaries:payroll_period_list')
            except Exception as e:
                messages.error(request, f'حدث خطأ في إنشاء فترة الراتب: {str(e)}')
    else:
        form = PayrollPeriodForm()

    context = {
        'form': form,
        'title': 'إنشاء فترة راتب جديدة',
        'is_edit': False
    }

    return render(request, 'Hr/salary/period_form.html', context)


@login_required
def payroll_period_edit(request, period_id):
    """تعديل فترة راتب"""
    if not SALARY_MODELS_AVAILABLE or not SALARY_FORMS_AVAILABLE:
        return render_under_construction(request, 'تعديل فترة راتب')

    period = get_object_or_404(PayrollPeriod, pk=period_id)

    if request.method == 'POST':
        form = PayrollPeriodForm(request.POST, instance=period)
        if form.is_valid():
            try:
                period = form.save()
                messages.success(request, f'تم تحديث فترة الراتب "{period.name}" بنجاح')
                return redirect('Hr:salaries:payroll_period_list')
            except Exception as e:
                messages.error(request, f'حدث خطأ في تحديث فترة الراتب: {str(e)}')
    else:
        form = PayrollPeriodForm(instance=period)

    context = {
        'form': form,
        'period': period,
        'title': f'تعديل فترة الراتب: {period.name}',
        'is_edit': True
    }

    return render(request, 'Hr/salary/period_form.html', context)


@login_required
def payroll_period_delete(request, period_id):
    """حذف فترة راتب"""
    if not SALARY_MODELS_AVAILABLE:
        return render_under_construction(request, 'حذف فترة راتب')

    period = get_object_or_404(PayrollPeriod, pk=period_id)

    if request.method == 'POST':
        try:
            # Check if period has entries
            if PayrollEntry and PayrollEntry.objects.filter(period=period).exists():
                messages.error(request, 'لا يمكن حذف فترة الراتب لأنها تحتوي على قيود')
                return redirect('Hr:salaries:payroll_period_list')

            period_name = period.name
            period.delete()
            messages.success(request, f'تم حذف فترة الراتب "{period_name}" بنجاح')
            return redirect('Hr:salaries:payroll_period_list')

        except Exception as e:
            messages.error(request, f'حدث خطأ في حذف فترة الراتب: {str(e)}')
            return redirect('Hr:salaries:payroll_period_list')

    context = {
        'period': period,
        'title': f'حذف فترة الراتب: {period.name}'
    }

    return render(request, 'Hr/salary/period_delete.html', context)


# =============================================================================
# PAYROLL ENTRY VIEWS
# =============================================================================

@login_required
def payroll_entry_list(request):
    """عرض قائمة قيود الرواتب"""
    if not SALARY_MODELS_AVAILABLE:
        return render_under_construction(request, 'قيود الرواتب')

    try:
        if PayrollEntry:
            entries = PayrollEntry.objects.select_related('period').order_by('-created_at')
        else:
            entries = []

        # Filter by period
        period_id = request.GET.get('period')
        if period_id and PayrollEntry:
            entries = entries.filter(period_id=period_id)

        # Pagination
        paginator = Paginator(entries, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get periods for filter
        periods = PayrollPeriod.objects.all().order_by('-start_date') if PayrollPeriod else []

        context = {
            'entries': page_obj,
            'periods': periods,
            'selected_period': period_id,
            'title': 'قيود الرواتب'
        }

        return render(request, 'Hr/salary/entry_list.html', context)

    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض قيود الرواتب: {str(e)}')
        return render(request, 'Hr/salary/entry_list.html', {
            'entries': [],
            'periods': [],
            'title': 'قيود الرواتب',
            'error': str(e)
        })


@login_required
def payroll_entry_detail(request, entry_id):
    """عرض تفاصيل قيد راتب"""
    if not SALARY_MODELS_AVAILABLE:
        return render_under_construction(request, 'تفاصيل قيد الراتب')

    try:
        entry = get_object_or_404(PayrollEntry, pk=entry_id)
        employee = get_object_or_404(Employee, emp_id=entry.employee_id)

        context = {
            'entry': entry,
            'employee': employee,
            'title': f'تفاصيل قيد راتب: {employee.emp_name}'
        }

        return render(request, 'Hr/salary/entry_detail.html', context)

    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض تفاصيل قيد الراتب: {str(e)}')
        return redirect('Hr:salaries:payroll_entry_list')


@login_required
def payroll_entry_approve(request, entry_id):
    """اعتماد قيد راتب"""
    if not SALARY_MODELS_AVAILABLE:
        messages.info(request, 'هذه الميزة قيد التطوير')
        return redirect('Hr:salaries:payroll_entry_list')

    try:
        entry = get_object_or_404(PayrollEntry, pk=entry_id)
        entry.status = 'approved'
        entry.save()

        messages.success(request, 'تم اعتماد قيد الراتب بنجاح')

    except Exception as e:
        messages.error(request, f'حدث خطأ في اعتماد قيد الراتب: {str(e)}')

    return redirect('Hr:salaries:payroll_entry_detail', entry_id=entry_id)


@login_required
def payroll_entry_reject(request, entry_id):
    """رفض قيد راتب"""
    if not SALARY_MODELS_AVAILABLE:
        messages.info(request, 'هذه الميزة قيد التطوير')
        return redirect('Hr:salaries:payroll_entry_list')

    try:
        entry = get_object_or_404(PayrollEntry, pk=entry_id)
        entry.status = 'rejected'
        entry.save()

        messages.success(request, 'تم رفض قيد الراتب')

    except Exception as e:
        messages.error(request, f'حدث خطأ في رفض قيد الراتب: {str(e)}')

    return redirect('Hr:salaries:payroll_entry_detail', entry_id=entry_id)
