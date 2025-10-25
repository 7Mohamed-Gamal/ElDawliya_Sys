from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import csv

# Modern model and form imports
from Hr.models.core.department_models import Department
from Hr.models.employee.employee_models import Employee
from Hr.models.core.job_models import Job
from Hr.forms.employee_forms import EmployeeForm, EmployeeFilterForm, EmployeeSearchForm

# Note: The dashboard view from the original file was removed as it duplicates
# functionality from dashboard_views.py and is not the primary dashboard.

@login_required
def employee_list(request):
    """Display a list of employees with search and filtering."""
    try:
        filter_form = EmployeeFilterForm(request.GET or None)
        status_filter = request.GET.get('status', 'active')

        if status_filter == 'inactive':
            employees_qs = Employee.objects.filter(status=Employee.TERMINATED)
        else:
            employees_qs = Employee.objects.filter(status=Employee.ACTIVE)

        employees_qs = employees_qs.select_related('department', 'position').order_by('employee_id')

        if filter_form.is_valid():
            search_query = filter_form.cleaned_data.get('search')
            if search_query:
                employees_qs = employees_qs.filter(
                    Q(full_name__icontains=search_query) |
                    Q(employee_id__icontains=search_query) |
                    Q(national_id__icontains=search_query)
                )
            
            department = filter_form.cleaned_data.get('department')
            if department:
                employees_qs = employees_qs.filter(department=department)

            position = filter_form.cleaned_data.get('position')
            if position:
                employees_qs = employees_qs.filter(position=position)

            status = filter_form.cleaned_data.get('status')
            if status:
                employees_qs = employees_qs.filter(status=status)

    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        employees_qs = Employee.objects.none()
        filter_form = EmployeeFilterForm()

    # Statistics (calculated on the filtered queryset)
    total_employees = employees_qs.count()
    
    context = {
        'employees': employees_qs,
        'filter_form': filter_form,
        'total_employees': total_employees,
        'active_employees': employees_qs.filter(status=Employee.ACTIVE).count(),
        'terminated_employees': employees_qs.filter(status=Employee.TERMINATED).count(),
        'status': status_filter,
    }

    return render(request, 'Hr/employees/employee_list.html', context)


@login_required
def employee_detail(request, employee_id):
    """Display details for a specific employee."""
    employee = get_object_or_404(Employee.objects.select_related('department', 'position'), employee_id=employee_id)
    context = {'employee': employee}
    return render(request, 'Hr/employees/employee_detail.html', context)


@login_required
def employee_create(request):
    """Create a new employee."""
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                employee = form.save()
                messages.success(request, f'Employee {employee.full_name} created successfully.')
                return redirect('Hr:employee_detail', employee_id=employee.employee_id)
            except Exception as e:
                messages.error(request, f'Error saving employee: {str(e)}')
    else:
        form = EmployeeForm()

    context = {
        'form': form,
        'title': 'Add New Employee',
        'button_text': 'Create'
    }
    return render(request, 'Hr/employees/employee_form.html', context)


@login_required
def employee_edit(request, employee_id):
    """Edit an existing employee."""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Employee {employee.full_name} updated successfully.')
            return redirect('Hr:employee_detail', employee_id=employee.employee_id)
    else:
        form = EmployeeForm(instance=employee)

    context = {
        'form': form,
        'employee': employee,
        'title': 'Edit Employee',
        'button_text': 'Save Changes',
    }
    return render(request, 'Hr/employees/employee_form.html', context)


@login_required
def employee_delete(request, employee_id):
    """Delete an employee."""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, f'Employee {employee.full_name} deleted successfully.')
        return redirect('Hr:employee_list')

    context = {'employee': employee}
    return render(request, 'Hr/employees/employee_confirm_delete.html', context)


@login_required
def employee_search(request):
    """Advanced employee search page."""
    form = EmployeeSearchForm(request.GET or None)
    employees_qs = Employee.objects.none()
    
    if form.is_valid() and any(form.cleaned_data.values()):
        filters = Q()
        
        if form.cleaned_data.get('quick_search'):
            query = form.cleaned_data['quick_search']
            filters &= (
                Q(employee_id__icontains=query) |
                Q(full_name__icontains=query) |
                Q(national_id__icontains=query) |
                Q(mobile_phone__icontains=query) |
                Q(department__name__icontains=query) |
                Q(position__name__icontains=query)
            )

        # Apply other specific filters from the refactored EmployeeSearchForm
        if form.cleaned_data.get('employee_id'):
            filters &= Q(employee_id__icontains=form.cleaned_data['employee_id'])
        if form.cleaned_data.get('full_name'):
            filters &= Q(full_name__icontains=form.cleaned_data['full_name'])
        if form.cleaned_data.get('national_id'):
            filters &= Q(national_id__icontains=form.cleaned_data['national_id'])
        if form.cleaned_data.get('department'):
            filters &= Q(department=form.cleaned_data['department'])
        if form.cleaned_data.get('position'):
            filters &= Q(position=form.cleaned_data['position'])
        if form.cleaned_data.get('status'):
            filters &= Q(status=form.cleaned_data['status'])
        if form.cleaned_data.get('join_date_from'):
            filters &= Q(join_date__gte=form.cleaned_data['join_date_from'])
        if form.cleaned_data.get('join_date_to'):
            filters &= Q(join_date__lte=form.cleaned_data['join_date_to'])

        employees_qs = Employee.objects.filter(filters).select_related('department', 'position').order_by('full_name')

    paginator = Paginator(employees_qs, 20)
    page_number = request.GET.get('page')
    employees_page = paginator.get_page(page_number)

    context = {
        'form': form,
        'employees': employees_page,
        'title': 'Employee Search',
        'total_results': paginator.count,
    }
    return render(request, 'Hr/employees/employee_search.html', context)

@login_required
def employee_export(request):
    """Export employee data to CSV format based on current filters."""
    try:
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="employees_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        response.write('\ufeff')  # BOM for UTF-8 in Excel

        writer = csv.writer(response)
        writer.writerow([
            'Employee ID', 'Full Name', 'Department', 'Position', 'Mobile Phone',
            'National ID', 'Join Date', 'Status'
        ])

        # Reuse filtering logic from employee_list
        employees = Employee.objects.select_related('department', 'position').all()
        filter_form = EmployeeFilterForm(request.GET or None)

        if filter_form.is_valid():
            # This is a simplified version of the filtering logic for export
            status = request.GET.get('status', 'active')
            if status == 'inactive':
                 employees = employees.filter(status=Employee.TERMINATED)
            else:
                 employees = employees.filter(status=Employee.ACTIVE)

            search_query = filter_form.cleaned_data.get('search')
            if search_query:
                employees = employees.filter(
                    Q(full_name__icontains=search_query) |
                    Q(employee_id__icontains=search_query) |
                    Q(national_id__icontains=search_query)
                )
            if filter_form.cleaned_data.get('department'):
                employees = employees.filter(department=filter_form.cleaned_data['department'])
            if filter_form.cleaned_data.get('position'):
                employees = employees.filter(position=filter_form.cleaned_data['position'])

        for emp in employees:
            writer.writerow([
                emp.employee_id,
                emp.full_name,
                emp.department.name if emp.department else '',
                emp.position.name if emp.position else '',
                emp.mobile_phone,
                emp.national_id,
                emp.join_date.strftime('%Y-%m-%d') if emp.join_date else '',
                emp.get_status_display(),
            ])

        return response
    except Exception as e:
        messages.error(request, f'An error occurred during export: {str(e)}')
        return redirect('Hr:employee_list')
