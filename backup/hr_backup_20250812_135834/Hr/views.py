from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

# Use the modern, refactored models
from Hr.models.core.department_models import Department
from Hr.models.employee.employee_models import Employee
from Hr.forms.employee_forms import DepartmentForm


@login_required
def department_list(request):
    """Display a list of departments with employee counts."""
    # The related_name on Employee.department is 'employees', so this works.
    departments = Department.objects.annotate(employee_count=Count('employees')).order_by('dept_name')

    context = {
        'departments': departments,
        'title': 'قائمة الأقسام'
    }

    return render(request, 'Hr/departments/department_list.html', context)


@login_required
def department_detail(request, dept_code):
    """Display details for a specific department."""
    department = get_object_or_404(Department, dept_code=dept_code)
    
    employees = Employee.objects.filter(department=department)
    employee_count = employees.count()
    
    # Calculate employee statuses using the new status field
    active_count = employees.filter(status=Employee.ACTIVE).count()
    terminated_count = employees.filter(status=Employee.TERMINATED).count()
    suspended_count = employees.filter(status=Employee.SUSPENDED).count()
    
    # Get limited employees for display
    employees_preview = employees[:10]
    
    context = {
        'department': department,
        'employees': employees_preview,
        'employee_count': employee_count,
        'active_count': active_count,
        'terminated_count': terminated_count,
        'suspended_count': suspended_count,
        'title': f'قسم {department.dept_name}'
    }

    return render(request, 'Hr/departments/department_detail.html', context)


@login_required
def department_create(request):
    """Create a new department."""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء القسم بنجاح')
            return redirect('Hr:department_list') # Corrected URL name
    else:
        form = DepartmentForm()
    
    context = {
        'form': form,
        'title': 'إنشاء قسم جديد',
        'is_edit': False
    }
    
    return render(request, 'Hr/departments/department_form.html', context)


@login_required
def department_edit(request, dept_code):
    """Edit an existing department."""
    department = get_object_or_404(Department, dept_code=dept_code)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل القسم بنجاح')
            return redirect('Hr:department_detail', dept_code=department.dept_code) # Corrected URL name
    else:
        form = DepartmentForm(instance=department)
    
    context = {
        'form': form,
        'department': department,
        'employee_count': department.employees.count(),
        'title': f'تعديل القسم: {department.dept_name}',
        'is_edit': True
    }
    
    return render(request, 'Hr/departments/department_form.html', context)


@login_required
def department_delete(request, dept_code):
    """Delete a department."""
    department = get_object_or_404(Department, dept_code=dept_code)
    
    if request.method == 'POST':
        if department.employees.exists():
            messages.error(request, 'لا يمكن حذف القسم لأنه يحتوي على موظفين')
            return redirect('Hr:department_detail', dept_code=department.dept_code) # Corrected URL name
        
        department.delete()
        messages.success(request, 'تم حذف القسم بنجاح')
        return redirect('Hr:department_list') # Corrected URL name
    
    context = {
        'department': department,
        'title': f'حذف القسم: {department.dept_name}'
    }
    
    return render(request, 'Hr/departments/department_confirm_delete.html', context)


@login_required
def department_employee_list(request, dept_code):
    """Display a list of all employees in a specific department."""
    department = get_object_or_404(Department, dept_code=dept_code)
    # Use the new field name for ordering
    employees = Employee.objects.filter(department=department).order_by('employee_id')
    
    context = {
        'department': department,
        'employees': employees,
        'title': f'موظفي قسم {department.dept_name}'
    }
    
    return render(request, 'Hr/departments/department_employees.html', context)


# This view seems to be for a placeholder page, no changes needed.
def update_data(request):
    return render(request, 'Hr/update_data.html', {
        'page_title': 'تحديث البيانات',
    })
