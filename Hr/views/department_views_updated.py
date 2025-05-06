from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from Hr.models.department_models import Department
from Hr.models.employee_model import Employee
from Hr.forms.employee_forms import DepartmentForm
from Hr.decorators import hr_module_permission_required


@login_required
@hr_module_permission_required('departments', 'view')
def department_list(request):
    """عرض قائمة الأقسام"""
    departments = Department.objects.annotate(employee_count=Count('employees')).order_by('dept_name')

    # إضافة معلومات مدير القسم لكل قسم
    departments_with_managers = []
    for department in departments:
        dept_info = {
            'dept_code': department.dept_code,
            'dept_name': department.dept_name,
            'employee_count': department.employee_count,
            'is_active': department.is_active,
            'note': department.note,
            'manager': None
        }

        # البحث عن مدير القسم إذا كان موجودًا
        if department.manager_id:
            try:
                manager = Employee.objects.get(emp_id=department.manager_id)
                dept_info['manager'] = manager
            except Employee.DoesNotExist:
                pass

        departments_with_managers.append(dept_info)

    context = {
        'departments': departments_with_managers,
        'title': 'قائمة الأقسام'
    }

    return render(request, 'Hr/departments/department_list.html', context)


@login_required
@hr_module_permission_required('departments', 'view')
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

    # Get department manager if exists
    manager = None
    if department.manager_id:
        try:
            manager = Employee.objects.get(emp_id=department.manager_id)
        except Employee.DoesNotExist:
            pass

    context = {
        'department': department,
        'employees': employees,
        'employee_count': employee_count,
        'active_count': active_count,
        'on_leave_count': on_leave_count,
        'resigned_count': resigned_count,
        'other_count': other_count,
        'title': f'قسم {department.dept_name}',
        'manager': manager  # إضافة مدير القسم إلى السياق
    }

    return render(request, 'Hr/departments/department_detail.html', context)


@login_required
@hr_module_permission_required('departments', 'add')
def department_create(request):
    """إنشاء قسم جديد"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            # إنشاء كود تلقائي للقسم
            if not form.cleaned_data.get('dept_code'):
                # الحصول على أعلى كود قسم موجود وإضافة 1 إليه
                max_code = Department.objects.all().order_by('-dept_code').first()
                next_code = 1 if not max_code else max_code.dept_code + 1
                form.instance.dept_code = next_code

            # حفظ القسم (سيتم حفظ مدير القسم تلقائيًا في وظيفة save المخصصة)
            department = form.save()

            messages.success(request, f'تم إنشاء القسم "{department.dept_name}" بنجاح. كود القسم: {department.dept_code}')
            return redirect('Hr:departments:list')
    else:
        # إنشاء نموذج جديد
        form = DepartmentForm()

    context = {
        'form': form,
        'title': 'إنشاء قسم جديد',
        'is_edit': False
    }

    return render(request, 'Hr/departments/department_form.html', context)


@login_required
@hr_module_permission_required('departments', 'edit')
def department_edit(request, dept_code):
    """تعديل قسم"""
    department = get_object_or_404(Department, dept_code=dept_code)

    # Get some employees for the department (limited to 5 for display)
    employee_list = Employee.objects.filter(department=department)[:5]
    employee_count = Employee.objects.filter(department=department).count()

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            # حفظ القسم (سيتم حفظ مدير القسم تلقائيًا في وظيفة save المخصصة)
            department = form.save()

            messages.success(request, f'تم تعديل القسم "{department.dept_name}" بنجاح')
            return redirect('Hr:departments:detail', dept_code=department.dept_code)
    else:
        # تعيين القيم الافتراضية للحقول الجديدة
        form = DepartmentForm(instance=department)

    context = {
        'form': form,
        'department': department,
        'employee_list': employee_list,
        'employee_count': employee_count,
        'title': f'تعديل القسم: {department.dept_name}',
        'is_edit': True
    }

    return render(request, 'Hr/departments/department_form.html', context)


@login_required
@hr_module_permission_required('departments', 'delete')
def department_delete(request, dept_code):
    """حذف قسم"""
    department = get_object_or_404(Department, dept_code=dept_code)

    if request.method == 'POST':
        # Check if there are any employees in this department
        if department.employees.exists():
            messages.error(request, 'لا يمكن حذف القسم لأنه يحتوي على موظفين')
            return redirect('Hr:departments:detail', dept_code=department.dept_code)

        department.delete()
        messages.success(request, 'تم حذف القسم بنجاح')
        return redirect('Hr:departments:list')

    context = {
        'department': department,
        'title': f'حذف القسم: {department.dept_name}'
    }

    return render(request, 'Hr/departments/department_confirm_delete.html', context)


@login_required
@hr_module_permission_required('departments', 'view')
def department_employee_list(request, dept_code):
    """عرض قائمة موظفي قسم معين"""
    department = get_object_or_404(Department, dept_code=dept_code)
    employees = Employee.objects.filter(department=department).order_by('emp_id')

    context = {
        'department': department,
        'employees': employees,
        'title': f'موظفي قسم {department.dept_name}'
    }

    return render(request, 'Hr/departments/department_employees.html', context)


@login_required
@hr_module_permission_required('departments', 'view')
def department_performance(request, dept_code):
    """تقييم أداء القسم"""
    department = get_object_or_404(Department, dept_code=dept_code)

    # Get all employees in this department
    employees = Employee.objects.filter(department=department)

    # Placeholder metrics (these should be calculated based on your actual data)
    attendance_rate = 95  # Example: 95% attendance rate
    task_completion_rate = 85  # Example: 85% of tasks completed on time
    evaluation_average = 4.2  # Example: average evaluation score out of 5

    context = {
        'department': department,
        'employees': employees,
        'attendance_rate': attendance_rate,
        'task_completion_rate': task_completion_rate,
        'evaluation_average': evaluation_average,
        'title': f'أداء قسم {department.dept_name}'
    }

    return render(request, 'Hr/departments/department_performance.html', context)
