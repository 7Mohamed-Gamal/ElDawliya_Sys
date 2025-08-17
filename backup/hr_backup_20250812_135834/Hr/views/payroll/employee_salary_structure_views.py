# =============================================================================
# ElDawliya HR Management System - Employee Salary Structure Views
# =============================================================================
# Views for employee salary structure management
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, date

from Hr.models import EmployeeSalaryStructure, EmployeeSalaryComponent, Employee, SalaryComponent
from Hr.forms.new_payroll_forms import EmployeeSalaryStructureForm


# =============================================================================
# EMPLOYEE SALARY STRUCTURE VIEWS
# =============================================================================

@login_required
def structure_list(request):
    """عرض قائمة هياكل رواتب الموظفين"""
    structures = EmployeeSalaryStructure.objects.select_related(
        'employee', 'employee__department'
    ).order_by('-effective_date', 'employee__full_name')
    
    # البحث والتصفية
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    active_filter = request.GET.get('active', '')
    
    if search_query:
        structures = structures.filter(
            Q(employee__full_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )
    
    if department_filter:
        structures = structures.filter(employee__department_id=department_filter)
    
    if active_filter:
        is_active = active_filter == 'true'
        structures = structures.filter(is_active=is_active)
    
    # الترقيم
    paginator = Paginator(structures, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # إحصائيات سريعة
    stats = {
        'total_structures': EmployeeSalaryStructure.objects.count(),
        'active_structures': EmployeeSalaryStructure.objects.filter(is_active=True).count(),
        'employees_with_salary': Employee.objects.filter(
            salary_structures__isnull=False
        ).distinct().count(),
        'employees_without_salary': Employee.objects.filter(
            salary_structures__isnull=True
        ).count(),
    }
    
    context = {
        'structures': page_obj,
        'search_query': search_query,
        'department_filter': department_filter,
        'active_filter': active_filter,
        'stats': stats,
        'title': _('هياكل رواتب الموظفين'),
    }
    
    return render(request, 'Hr/payroll/employee_salary_structure_list.html', context)


@login_required
def structure_detail(request, structure_id):
    """عرض تفاصيل هيكل راتب الموظف"""
    structure = get_object_or_404(
        EmployeeSalaryStructure.objects.select_related('employee'), 
        id=structure_id
    )
    
    # مكونات الراتب
    salary_components = structure.salary_components.select_related(
        'salary_component'
    ).order_by('salary_component__display_order')
    
    # تجميع المكونات حسب الفئة
    earnings = salary_components.filter(salary_component__category='earning')
    deductions = salary_components.filter(salary_component__category='deduction')
    employer_contributions = salary_components.filter(
        salary_component__category='employer_contribution'
    )
    
    # حساب المجاميع
    totals = {
        'total_earnings': earnings.aggregate(total=Sum('amount'))['total'] or 0,
        'total_deductions': deductions.aggregate(total=Sum('amount'))['total'] or 0,
        'total_employer_contributions': employer_contributions.aggregate(
            total=Sum('amount')
        )['total'] or 0,
    }
    totals['net_salary'] = totals['total_earnings'] - totals['total_deductions']
    
    context = {
        'structure': structure,
        'earnings': earnings,
        'deductions': deductions,
        'employer_contributions': employer_contributions,
        'totals': totals,
        'title': f"هيكل راتب {structure.employee.full_name}",
    }
    
    return render(request, 'Hr/payroll/employee_salary_structure_detail.html', context)


@login_required
def structure_create(request):
    """إنشاء هيكل راتب جديد للموظف"""
    employee_id = request.GET.get('employee_id')
    employee = None
    
    if employee_id:
        employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        form = EmployeeSalaryStructureForm(request.POST)
        if form.is_valid():
            structure = form.save(commit=False)
            structure.created_by = request.user
            
            # إلغاء تفعيل الهياكل السابقة للموظف
            if structure.is_active:
                EmployeeSalaryStructure.objects.filter(
                    employee=structure.employee,
                    is_active=True
                ).update(is_active=False)
            
            structure.save()
            
            messages.success(request, _('تم إنشاء هيكل الراتب بنجاح'))
            return redirect('Hr:employee_salary_structures:detail', structure_id=structure.id)
    else:
        initial_data = {}
        if employee:
            initial_data['employee'] = employee
        form = EmployeeSalaryStructureForm(initial=initial_data)
    
    context = {
        'form': form,
        'employee': employee,
        'title': _('إنشاء هيكل راتب جديد'),
        'action': 'create',
    }
    
    return render(request, 'Hr/payroll/employee_salary_structure_form.html', context)


@login_required
def structure_edit(request, structure_id):
    """تحديث هيكل راتب الموظف"""
    structure = get_object_or_404(EmployeeSalaryStructure, id=structure_id)
    
    if request.method == 'POST':
        form = EmployeeSalaryStructureForm(request.POST, instance=structure)
        if form.is_valid():
            updated_structure = form.save(commit=False)
            
            # إلغاء تفعيل الهياكل السابقة للموظف إذا تم تفعيل هذا الهيكل
            if updated_structure.is_active and not structure.is_active:
                EmployeeSalaryStructure.objects.filter(
                    employee=updated_structure.employee,
                    is_active=True
                ).exclude(id=structure.id).update(is_active=False)
            
            updated_structure.save()
            
            messages.success(request, _('تم تحديث هيكل الراتب بنجاح'))
            return redirect('Hr:employee_salary_structures:detail', structure_id=structure.id)
    else:
        form = EmployeeSalaryStructureForm(instance=structure)
    
    context = {
        'form': form,
        'structure': structure,
        'title': f"تحديث هيكل راتب {structure.employee.full_name}",
        'action': 'edit',
    }
    
    return render(request, 'Hr/payroll/employee_salary_structure_form.html', context)


@login_required
def structure_delete(request, structure_id):
    """حذف هيكل راتب الموظف"""
    structure = get_object_or_404(EmployeeSalaryStructure, id=structure_id)
    
    if request.method == 'POST':
        employee_name = structure.employee.full_name
        structure.delete()
        messages.success(request, f'تم حذف هيكل راتب {employee_name} بنجاح')
        return redirect('Hr:employee_salary_structures:list')
    
    context = {
        'structure': structure,
        'title': f"حذف هيكل راتب {structure.employee.full_name}",
    }
    
    return render(request, 'Hr/payroll/employee_salary_structure_delete.html', context)


@login_required
def structure_activate(request, structure_id):
    """تفعيل هيكل راتب الموظف"""
    structure = get_object_or_404(EmployeeSalaryStructure, id=structure_id)
    
    if request.method == 'POST':
        # إلغاء تفعيل الهياكل السابقة للموظف
        EmployeeSalaryStructure.objects.filter(
            employee=structure.employee,
            is_active=True
        ).update(is_active=False)
        
        # تفعيل الهيكل الحالي
        structure.is_active = True
        structure.save()
        
        messages.success(
            request, 
            f'تم تفعيل هيكل راتب {structure.employee.full_name} بنجاح'
        )
        return redirect('Hr:employee_salary_structures:detail', structure_id=structure.id)
    
    context = {
        'structure': structure,
        'title': f"تفعيل هيكل راتب {structure.employee.full_name}",
    }
    
    return render(request, 'Hr/payroll/employee_salary_structure_activate.html', context)


@login_required
def structure_copy(request, structure_id):
    """نسخ هيكل راتب الموظف"""
    original_structure = get_object_or_404(EmployeeSalaryStructure, id=structure_id)
    
    if request.method == 'POST':
        target_employee_id = request.POST.get('target_employee')
        
        if not target_employee_id:
            messages.error(request, _('يجب اختيار الموظف المستهدف'))
            return redirect('Hr:employee_salary_structures:detail', structure_id=structure_id)
        
        target_employee = get_object_or_404(Employee, id=target_employee_id)
        
        # إنشاء هيكل راتب جديد
        new_structure = EmployeeSalaryStructure.objects.create(
            employee=target_employee,
            basic_salary=original_structure.basic_salary,
            currency=original_structure.currency,
            effective_date=timezone.now().date(),
            is_active=False,  # يتم تفعيله يدوياً
            created_by=request.user
        )
        
        # نسخ مكونات الراتب
        for component in original_structure.salary_components.all():
            EmployeeSalaryComponent.objects.create(
                salary_structure=new_structure,
                salary_component=component.salary_component,
                amount=component.amount,
                is_active=component.is_active
            )
        
        # إعادة حساب المجاميع
        new_structure.calculate_totals()
        
        messages.success(
            request, 
            f'تم نسخ هيكل الراتب إلى {target_employee.full_name} بنجاح'
        )
        return redirect('Hr:employee_salary_structures:detail', structure_id=new_structure.id)
    
    # قائمة الموظفين المتاحين للنسخ
    available_employees = Employee.objects.filter(is_active=True).exclude(
        id=original_structure.employee.id
    ).order_by('full_name')
    
    context = {
        'structure': original_structure,
        'available_employees': available_employees,
        'title': f"نسخ هيكل راتب {original_structure.employee.full_name}",
    }
    
    return render(request, 'Hr/payroll/employee_salary_structure_copy.html', context)
