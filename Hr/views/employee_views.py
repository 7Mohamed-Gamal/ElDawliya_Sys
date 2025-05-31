from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Count

from Hr.models import Department, Job, Car, Employee
from Hr.forms import EmployeeForm, EmployeeFilterForm, DepartmentForm, JobForm, CarForm, EmployeeSearchForm
from administrator.utils import has_permission


@login_required
def dashboard(request):
    """لوحة معلومات الموظفين"""
    # إحصائيات الموظفين
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(working_condition='سارى').count()
    insured_employees = Employee.objects.filter(insurance_status='مؤمن عليه').count()
    inactive_insured_employees = Employee.objects.filter(insurance_status='غير مؤمن عليه').count()

    # الموظفين حسب القسم
    dept_queryset = Department.objects.annotate(
        employee_count=Count('employees')
    )

    departments = []
    for dept in dept_queryset:
        try:
            percentage = (dept.employee_count / total_employees * 100) if total_employees > 0 else 0
        except (ZeroDivisionError, TypeError):
            percentage = 0
            
        departments.append({
            'dept_code': dept.dept_code,
            'dept_name': dept.dept_name,
            'employee_count': dept.employee_count,
            'percentage': percentage,
            'percentage_str': min(percentage, 100)  # Ensure it doesn't exceed 100%
        })

    # توزيع التأمين
    insurance_distribution = [
        {'name': 'مؤمن عليه', 'count': insured_employees},
        {'name': 'غير مؤمن عليه', 'count': inactive_insured_employees}
    ]

    # البطاقات الصحية التي على وشك الانتهاء
    expiring_health_cards = Employee.objects.filter(
        health_card_renewal_date__isnull=False,
    ).order_by('health_card_renewal_date')[:10]

    # تجديد العقود الوشيكة
    upcoming_contract_renewals = Employee.objects.filter(
        contract_renewal_date__isnull=False,
    ).order_by('contract_renewal_date')[:10]

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'insured_employees': insured_employees,
        'departments': departments,
        'insurance_distribution': insurance_distribution,
        'expiring_health_cards': expiring_health_cards,
        'upcoming_contract_renewals': upcoming_contract_renewals,
    }

    # Add department and job counts for template
    departments_count = Department.objects.count()
    jobs_count = Job.objects.count()
    context['departments_count'] = departments_count
    context['jobs_count'] = jobs_count

    return render(request, 'Hr/dashboard.html', context)


@login_required
def employee_list(request):
    """عرض قائمة الموظفين مع إمكانية البحث والتصفية"""

    # إعداد عامل التصفية
    filter_form = EmployeeFilterForm(request.GET or None)
    total_employees = Employee.objects.all()

    # التحقق من حالة التبديل (نشط/غير نشط)
    status = request.GET.get('status', 'active')

    # تحديد الموظفين بناءً على الحالة
    if status == 'inactive':
        # عرض الموظفين غير النشطين (المستقيلين)
        employees = Employee.objects.filter(working_condition='استقالة').order_by('emp_id')
    else:
        # عرض الموظفين النشطين (الافتراضي)
        employees = Employee.objects.filter(working_condition__in=['سارى']).order_by('emp_id')

    # تطبيق التصفية إذا تم تقديم النموذج
    if filter_form.is_valid():
        # تصفية حسب الاسم أو الرقم
        search_query = filter_form.cleaned_data.get('search')
        if search_query:
            employees = employees.filter(
                Q(emp_full_name__icontains=search_query) |
                Q(emp_id__icontains=search_query)
            )

        # تصفية حسب القسم
        department = filter_form.cleaned_data.get('department')
        if department:
            employees = employees.filter(department=department)

        # تصفية حسب الوظيفة
        job = filter_form.cleaned_data.get('job')
        if job:
            employees = employees.filter(jop_code=job)

        # تصفية حسب حالة العمل
        working_condition = filter_form.cleaned_data.get('working_condition')
        if working_condition:
            employees = employees.filter(working_condition=working_condition)

        # تصفية حسب حالة التأمين
        insurance_status = filter_form.cleaned_data.get('insurance_status')
        if insurance_status:
            employees = employees.filter(insurance_status=insurance_status)

    # إحصائيات الموظفين
    total_employees = employees.count()
    active_employees = employees.filter(working_condition='سارى').count()
    on_leave_employees = employees.filter(working_condition='إجازة').count()
    resigned_employees = employees.filter(working_condition='استقالة').count()

    # الموظفين حسب القسم
    employees_by_department = Department.objects.annotate(
        count=Count('employees')
    ).filter(count__gt=0)

    context = {
        'employees': employees,
        'filter_form': filter_form,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'on_leave_employees': on_leave_employees,
        'resigned_employees': resigned_employees,
        'employees_by_department': employees_by_department,
        'status': status,  # إضافة حالة التبديل للقالب
    }

    return render(request, 'Hr/employees/employee_list.html', context)


@login_required
def employee_detail(request, emp_id):
    """عرض تفاصيل موظف محدد"""
    employee = get_object_or_404(Employee, emp_id=emp_id)

    context = {
        'employee': employee,
    }

    return render(request, 'Hr/employees/employee_detail.html', context)


@login_required
def employee_create(request):
    """إنشاء موظف جديد"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                employee = form.save()
                messages.success(request, f'تم إنشاء الموظف {employee.emp_full_name} بنجاح')
                return redirect('Hr:employees:detail', emp_id=employee.emp_id)
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء حفظ الموظف: {str(e)}')
    else:
        form = EmployeeForm()

    context = {
        'form': form,
        'title': 'إضافة موظف جديد',
        'button_text': 'إنشاء'
    }

    return render(request, 'Hr/employees/employee_form_new.html', context)


@login_required
def employee_edit(request, emp_id):
    """تعديل بيانات موظف"""
    employee = get_object_or_404(Employee, emp_id=emp_id)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث بيانات الموظف {employee.emp_full_name} بنجاح')
            return redirect('Hr:employees:detail', emp_id=employee.emp_id)
    else:
        form = EmployeeForm(instance=employee)

    context = {
        'form': form,
        'employee': employee,
        'title': 'تعديل بيانات الموظف',
        'button_text': 'حفظ التغييرات',
    }

    return render(request, 'Hr/employees/employee_form.html', context)


@login_required
def employee_delete(request, emp_id):
    """حذف موظف"""
    employee = get_object_or_404(Employee, emp_id=emp_id)

    if request.method == 'POST':
        employee.delete()
        messages.success(request, f'تم حذف الموظف {employee.emp_full_name} بنجاح')
        return redirect('Hr:employees:list')

    context = {
        'employee': employee,
    }

    return render(request, 'Hr/employees/employee_confirm_delete.html', context)


# Move employee_search view to this file from Hr/views.py
@login_required
def employee_print(request, emp_id):
    """طباعة بيانات موظف"""
    employee = get_object_or_404(Employee, emp_id=emp_id)

    context = {
        'employee': employee,
        'title': f'طباعة بيانات الموظف: {employee.emp_full_name}',
        'print_mode': True,
    }

    return render(request, 'Hr/employees/employee_print.html', context)


@login_required
def employee_search(request):
    """صفحة البحث عن الموظف وعرض بياناته وتحليلاته"""
    form = EmployeeSearchForm(request.GET or None)
    employees = Employee.objects.none()
    selected_employee = None
    analytics = {}

    if form.is_valid():
        employee_code = form.cleaned_data.get('employee_code')
        name = form.cleaned_data.get('name')
        national_id = form.cleaned_data.get('national_id')
        insurance_number = form.cleaned_data.get('insurance_number')

        # Build query filters
        filters = Q()
        if employee_code:
            filters &= Q(emp_id__icontains=employee_code)
        if name:
            filters &= (Q(emp_first_name__icontains=name) | Q(emp_second_name__icontains=name) | Q(emp_full_name__icontains=name))
        if national_id:
            filters &= Q(national_id__icontains=national_id)
        if insurance_number:
            filters &= Q(insurance_number__icontains=insurance_number)

        employees = Employee.objects.filter(filters)

        # If exactly one employee found, select for detailed view
        if employees.count() == 1:
            selected_employee = employees.first()

            # Example analytics - customize as needed
            analytics = {
                'attendance_rate': 95,  # Placeholder
                'task_completion_rate': 90,  # Placeholder
                'evaluation_score': 4.5,  # Placeholder
            }

    context = {
        'form': form,
        'employees': employees,
        'selected_employee': selected_employee,
        'analytics': analytics,
        'title': 'بحث الموظفين',
    }
    return render(request, 'Hr/employees/employee_search.html', context)


@login_required
def employee_detail_view(request):
    """عرض معلومات الموظف بشكل تفصيلي"""
    employee = None
    emp_id = request.GET.get('emp_id')
    national_id = request.GET.get('national_id')

    if emp_id:
        employee = Employee.objects.filter(emp_id=emp_id).first()
    elif national_id:
        employee = Employee.objects.filter(national_id=national_id).first()

    context = {
        'employee': employee,
        'title': 'بيانات الموظف تفصيلي'
    }

    return render(request, 'Hr/employees/employee_detail_view.html', context)
