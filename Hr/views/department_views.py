from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from Hr.models.department_models import Department
from Hr.models.employee_model import Employee
from Hr.forms.employee_forms import DepartmentForm


@login_required
def department_list(request):
    """عرض قائمة الأقسام"""
    departments = Department.objects.annotate(employee_count=Count('employees')).order_by('dept_name')

    context = {
        'departments': departments,
        'title': 'قائمة الأقسام'
    }

    return render(request, 'Hr/departments/department_list.html', context)


@login_required
def department_detail(request, dept_code):
    """عرض تفاصيل قسم"""
    department = get_object_or_404(Department, dept_code=dept_code)
    
    # Get employees in this department
    employees = Employee.objects.filter(department=department)
    employee_count = employees.count()
    
    # Calculate employee statuses
    active_count = employees.filter(working_condition='سارى').count()
    on_leave_count = employees.filter(working_condition='إجازة').count()
    resigned_count = employees.filter(working_condition='استقالة').count()
    other_count = employee_count - (active_count + on_leave_count + resigned_count)
    
    # Get limited employees for display in department detail page
    employees = employees[:10]  # Limit to 10 employees
    
    context = {
        'department': department,
        'employees': employees,
        'employee_count': employee_count,
        'active_count': active_count,
        'on_leave_count': on_leave_count,
        'resigned_count': resigned_count,
        'other_count': other_count,
        'title': f'قسم {department.dept_name}'
    }

    return render(request, 'Hr/departments/department_detail.html', context)
