from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string

from Hr.models import Department, Job, Employee
from Hr.forms import EmployeeForm, EmployeeFilterForm, EmployeeSearchForm


@login_required
def dashboard(request):
    """لوحة معلومات الموظفين المحسنة"""
    from datetime import datetime, timedelta

    # إحصائيات الموظفين الأساسية
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(working_condition='سارى').count()
    insured_employees = Employee.objects.filter(insurance_status='مؤمن عليه').count()
    inactive_insured_employees = Employee.objects.filter(insurance_status='غير مؤمن عليه').count()
    resigned_employees = Employee.objects.filter(working_condition='استقالة').count()

    # إحصائيات إضافية للوحة المحسنة
    today = datetime.now().date()

    # الموظفين الجدد (آخر 30 يوم)
    recent_employees = Employee.objects.filter(
        emp_date_hiring__gte=today - timedelta(days=30)
    ).select_related('department').order_by('-emp_date_hiring')

    # أعياد الميلاد اليوم (تقدير - يحتاج تاريخ الميلاد)
    birthdays_today = Employee.objects.filter(
        date_birth__month=today.month,
        date_birth__day=today.day
    ).count() if hasattr(Employee, 'date_birth') else 0

    # الموظفين في إجازة اليوم (تقدير)
    on_leave_today = Employee.objects.filter(
        working_condition='إجازة'
    ).count()

    # حضور اليوم (تقدير - يحتاج نظام حضور)
    today_attendance = active_employees  # placeholder

    # الموظفين حسب القسم
    dept_queryset = Department.objects.annotate(
        employee_count=Count('employees')
    ).filter(employee_count__gt=0)

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
        health_card_renewal_date__lte=today + timedelta(days=30)
    ).order_by('health_card_renewal_date')[:10]

    # تجديد العقود الوشيكة
    upcoming_contract_renewals = Employee.objects.filter(
        contract_renewal_date__isnull=False,
        contract_renewal_date__lte=today + timedelta(days=30)
    ).order_by('contract_renewal_date')[:10]

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'insured_employees': insured_employees,
        'resigned_employees': resigned_employees,
        'departments': departments,
        'insurance_distribution': insurance_distribution,
        'expiring_health_cards': expiring_health_cards,
        'upcoming_contract_renewals': upcoming_contract_renewals,
        # بيانات إضافية للوحة المحسنة
        'recent_employees': recent_employees,
        'today_attendance': today_attendance,
        'on_leave_today': on_leave_today,
        'birthdays_today': birthdays_today,
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
    try:
        # إعداد عامل التصفية
        filter_form = EmployeeFilterForm(request.GET or None)

        # التحقق من حالة التبديل (نشط/غير نشط)
        status = request.GET.get('status', 'active')

        # تحديد الموظفين بناءً على الحالة مع تحسين الاستعلام
        if status == 'inactive':
            # عرض الموظفين غير النشطين (المستقيلين)
            employees = Employee.objects.select_related('department').filter(
                working_condition='استقالة'
            ).order_by('emp_id')
        else:
            # عرض الموظفين النشطين (الافتراضي)
            employees = Employee.objects.select_related('department').filter(
                working_condition__in=['سارى']
            ).order_by('emp_id')

        # تطبيق التصفية إذا تم تقديم النموذج
        if filter_form.is_valid():
            # تصفية حسب البحث السريع
            search_query = filter_form.cleaned_data.get('search')
            if search_query:
                employees = employees.filter(
                    Q(emp_full_name__icontains=search_query) |
                    Q(emp_first_name__icontains=search_query) |
                    Q(emp_second_name__icontains=search_query) |
                    Q(emp_id__icontains=search_query) |
                    Q(national_id__icontains=search_query)
                )

            # تصفية حسب الاسم
            name = filter_form.cleaned_data.get('name')
            if name:
                employees = employees.filter(
                    Q(emp_full_name__icontains=name) |
                    Q(emp_first_name__icontains=name) |
                    Q(emp_second_name__icontains=name)
                )

            # تصفية حسب القسم
            department = filter_form.cleaned_data.get('department')
            if department:
                employees = employees.filter(department=department)

            # تصفية حسب الوظيفة
            job = filter_form.cleaned_data.get('job')
            if job:
                employees = employees.filter(jop_code=job.jop_code)

            # تصفية حسب حالة العمل
            working_condition = filter_form.cleaned_data.get('working_condition')
            if working_condition:
                employees = employees.filter(working_condition=working_condition)

            # تصفية حسب حالة التأمين
            insurance_status = filter_form.cleaned_data.get('insurance_status')
            if insurance_status:
                employees = employees.filter(insurance_status=insurance_status)

    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء تحميل قائمة الموظفين: {str(e)}')
        employees = Employee.objects.none()
        filter_form = EmployeeFilterForm()

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

    if form.is_valid() and any(form.cleaned_data.values()):
        # Build search filters
        filters = Q()

        # البحث السريع العام
        if form.cleaned_data.get('quick_search'):
            quick_search = form.cleaned_data['quick_search']
            quick_filters = (
                Q(emp_id__icontains=quick_search) |
                Q(emp_full_name__icontains=quick_search) |
                Q(emp_first_name__icontains=quick_search) |
                Q(emp_second_name__icontains=quick_search) |
                Q(national_id__icontains=quick_search) |
                Q(emp_phone1__icontains=quick_search) |
                Q(emp_phone2__icontains=quick_search) |
                Q(emp_address__icontains=quick_search) |
                Q(governorate__icontains=quick_search) |
                Q(jop_name__icontains=quick_search) |
                Q(department__dept_name__icontains=quick_search) |
                Q(emp_car__icontains=quick_search)
            )
            filters &= quick_filters

        # معلومات الهوية
        if form.cleaned_data.get('employee_code'):
            filters &= Q(emp_id__icontains=form.cleaned_data['employee_code'])

        if form.cleaned_data.get('name'):
            name = form.cleaned_data['name']
            filters &= (
                Q(emp_full_name__icontains=name) |
                Q(emp_first_name__icontains=name) |
                Q(emp_second_name__icontains=name)
            )

        if form.cleaned_data.get('national_id'):
            filters &= Q(national_id__icontains=form.cleaned_data['national_id'])

        # معلومات الاتصال
        if form.cleaned_data.get('phone'):
            phone = form.cleaned_data['phone']
            filters &= (
                Q(emp_phone1__icontains=phone) |
                Q(emp_phone2__icontains=phone)
            )

        if form.cleaned_data.get('address'):
            address = form.cleaned_data['address']
            filters &= (
                Q(emp_address__icontains=address) |
                Q(governorate__icontains=address)
            )

        # معلومات العمل
        if form.cleaned_data.get('department'):
            filters &= Q(department=form.cleaned_data['department'])

        if form.cleaned_data.get('job_name'):
            filters &= Q(jop_name=form.cleaned_data['job_name'].jop_name)

        if form.cleaned_data.get('working_condition'):
            filters &= Q(working_condition=form.cleaned_data['working_condition'])

        # معلومات السيارة
        if form.cleaned_data.get('car'):
            filters &= Q(emp_car=form.cleaned_data['car'].car_id)

        if form.cleaned_data.get('shift_type'):
            filters &= Q(shift_type=form.cleaned_data['shift_type'])

        # معلومات التأمين
        if form.cleaned_data.get('insurance_status'):
            filters &= Q(insurance_status=form.cleaned_data['insurance_status'])

        if form.cleaned_data.get('insurance_number'):
            filters &= Q(insurance_number__icontains=form.cleaned_data['insurance_number'])

        if form.cleaned_data.get('health_card'):
            filters &= Q(health_card=form.cleaned_data['health_card'])

        # معلومات شخصية
        if form.cleaned_data.get('emp_type'):
            filters &= Q(emp_type=form.cleaned_data['emp_type'])

        if form.cleaned_data.get('marital_status'):
            filters &= Q(emp_marital_status=form.cleaned_data['marital_status'])

        # تواريخ التعيين
        if form.cleaned_data.get('hire_date_from'):
            filters &= Q(emp_date_hiring__gte=form.cleaned_data['hire_date_from'])

        if form.cleaned_data.get('hire_date_to'):
            filters &= Q(emp_date_hiring__lte=form.cleaned_data['hire_date_to'])

        # تواريخ الميلاد
        if form.cleaned_data.get('birth_date_from'):
            filters &= Q(date_birth__gte=form.cleaned_data['birth_date_from'])

        if form.cleaned_data.get('birth_date_to'):
            filters &= Q(date_birth__lte=form.cleaned_data['birth_date_to'])

        # تطبيق الفلاتر والحصول على النتائج
        employees = Employee.objects.filter(filters).select_related('department').order_by('emp_full_name')

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
        'total_results': employees.count() if employees else 0,
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


@login_required
def employee_dashboard_simple(request):
    """عرض لوحة معلومات مبسطة للموظفين"""
    # إحصائيات أساسية للموظفين
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(working_condition='سارى').count()
    departments_count = Department.objects.count()
    
    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'departments_count': departments_count,
    }
    
    return render(request, 'Hr/dashboard_simple.html', context)
@login_required
def employee_export(request):
    """Export employee data to CSV format"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime

    try:
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="employees_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        # Add BOM for proper UTF-8 encoding in Excel
        response.write('\ufeff')

        writer = csv.writer(response)

        # Write CSV header
        writer.writerow([
            'رقم الموظف', 'الاسم الكامل', 'الاسم الأول', 'الاسم الثاني',
            'القسم', 'الوظيفة', 'الهاتف', 'العنوان', 'الرقم القومي',
            'تاريخ التعيين', 'حالة العمل', 'حالة التأمين'
        ])

        # Get employees with related data
        employees = Employee.objects.select_related('department').all()

        # Apply filters if provided
        filter_form = EmployeeFilterForm(request.GET or None)
        if filter_form.is_valid():
            search_query = filter_form.cleaned_data.get('search')
            if search_query:
                employees = employees.filter(
                    Q(emp_full_name__icontains=search_query) |
                    Q(emp_id__icontains=search_query) |
                    Q(national_id__icontains=search_query)
                )

            department = filter_form.cleaned_data.get('department')
            if department:
                employees = employees.filter(department=department)

            working_condition = filter_form.cleaned_data.get('working_condition')
            if working_condition:
                employees = employees.filter(working_condition=working_condition)

        # Write employee data
        for employee in employees:
            writer.writerow([
                employee.emp_id or '',
                employee.emp_full_name or '',
                employee.emp_first_name or '',
                employee.emp_second_name or '',
                employee.department.dept_name if employee.department else '',
                employee.jop_name or '',
                employee.emp_phone1 or '',
                employee.emp_address or '',
                employee.national_id or '',
                employee.emp_date_hiring.strftime('%Y-%m-%d') if employee.emp_date_hiring else '',
                employee.working_condition or '',
                employee.insurance_status or ''
            ])

        return response

    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء تصدير البيانات: {str(e)}')
        return redirect('Hr:employees:list')


@login_required
@require_http_methods(["GET"])
def employee_list_ajax(request):
    """AJAX endpoint for dynamic employee filtering"""
    try:
        # Get status parameter
        status = request.GET.get('status', 'active')

        # Calculate all statistics first (for the entire system)
        all_employees = Employee.objects.select_related('department')
        total_employees_system = all_employees.count()
        active_employees_system = all_employees.filter(working_condition='سارى').count()
        on_leave_employees_system = all_employees.filter(working_condition='إجازة').count()
        resigned_employees_system = all_employees.filter(working_condition='استقالة').count()

        # Filter employees based on status
        if status == 'inactive':
            employees = all_employees.filter(working_condition='استقالة').order_by('emp_id')
        else:
            employees = all_employees.filter(working_condition__in=['سارى']).order_by('emp_id')

        # Apply additional filters if provided
        filter_form = EmployeeFilterForm(request.GET or None)
        if filter_form.is_valid():
            # Apply search filters
            search_query = filter_form.cleaned_data.get('search')
            if search_query:
                employees = employees.filter(
                    Q(emp_full_name__icontains=search_query) |
                    Q(emp_first_name__icontains=search_query) |
                    Q(emp_second_name__icontains=search_query) |
                    Q(emp_id__icontains=search_query) |
                    Q(national_id__icontains=search_query)
                )

            # Apply other filters
            department = filter_form.cleaned_data.get('department')
            if department:
                employees = employees.filter(department=department)

            job = filter_form.cleaned_data.get('job')
            if job:
                employees = employees.filter(jop_code=job.jop_code)

            working_condition = filter_form.cleaned_data.get('working_condition')
            if working_condition:
                employees = employees.filter(working_condition=working_condition)

            insurance_status = filter_form.cleaned_data.get('insurance_status')
            if insurance_status:
                employees = employees.filter(insurance_status=insurance_status)

        # Calculate filtered statistics
        filtered_count = employees.count()

        # Prepare response data
        response_data = {
            'success': True,
            'status': status,
            'statistics': {
                'total_employees': total_employees_system,
                'active_employees': active_employees_system,
                'on_leave_employees': on_leave_employees_system,
                'resigned_employees': resigned_employees_system,
                'filtered_count': filtered_count,
                'active_percentage': round((active_employees_system / total_employees_system * 100) if total_employees_system > 0 else 0, 1),
                'resigned_percentage': round((resigned_employees_system / total_employees_system * 100) if total_employees_system > 0 else 0, 1),
            },
            'employees_count': filtered_count,
        }

        # Render employee list HTML
        context = {
            'employees': employees,
            'status': status,
            'total_employees': total_employees_system,
            'active_employees': active_employees_system,
            'on_leave_employees': on_leave_employees_system,
            'resigned_employees': resigned_employees_system,
        }

        # Render both table and card views
        table_html = render_to_string('Hr/employees/partials/employee_table.html', context, request=request)
        card_html = render_to_string('Hr/employees/partials/employee_cards.html', context, request=request)

        response_data['table_html'] = table_html
        response_data['card_html'] = card_html

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'حدث خطأ أثناء تحميل البيانات: {str(e)}'
        }, status=500)
