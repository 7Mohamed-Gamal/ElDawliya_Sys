"""
Extended Employee Views for Comprehensive HR Management
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import Employee
from .models_extended import (
    ExtendedHealthInsuranceProvider, ExtendedEmployeeHealthInsurance,
    SocialInsuranceJobTitle, ExtendedEmployeeSocialInsurance,
    SalaryComponent, EmployeeSalaryComponent,
    EmployeeLeaveBalance, Vehicle, PickupPoint, EmployeeTransport,
    EvaluationCriteria, EmployeePerformanceEvaluation, EvaluationScore,
    WorkSchedule, EmployeeWorkSetup
)
from .forms_extended import (
    EmployeeHealthInsuranceForm, EmployeeSocialInsuranceForm,
    SalaryComponentForm, EmployeeSalaryComponentForm,
    EmployeeTransportForm, EmployeePerformanceEvaluationForm,
    EmployeeWorkSetupForm, HealthInsuranceProviderForm,
    SocialInsuranceJobTitleForm, VehicleForm, PickupPointForm,
    WorkScheduleForm, EvaluationCriteriaForm,
    EmployeeSalaryComponentFormSet, EvaluationScoreFormSet
)
from leaves.models import LeaveType
from loans.models import EmployeeLoan


@login_required
def comprehensive_employee_edit(request, emp_id):
    """عرض شامل لتعديل بيانات الموظف"""
    employee = get_object_or_404(Employee, emp_id=emp_id)
    
    # Get or create related records
    health_insurance, _ = ExtendedEmployeeHealthInsurance.objects.get_or_create(
        emp=employee,
        defaults={
            'insurance_status': 'inactive',
            'insurance_type': 'basic',
            'insurance_number': f'HI-{employee.emp_id}',
            'start_date': date.today(),
            'expiry_date': date.today() + timedelta(days=365),
            'num_dependents': 0,
        }
    )

    social_insurance, _ = ExtendedEmployeeSocialInsurance.objects.get_or_create(
        emp=employee,
        defaults={
            'insurance_status': 'inactive',
            'start_date': date.today(),
            'subscription_confirmed': False,
            'monthly_wage': Decimal('0.00'),
        }
    )
    
    transport_record = EmployeeTransport.objects.filter(
        emp=employee, is_active=True
    ).first()
    
    work_setup, _ = EmployeeWorkSetup.objects.get_or_create(
        emp=employee,
        is_active=True,
        defaults={
            'effective_date': date.today(),
            'overtime_rate': Decimal('1.5'),
            'late_deduction_rate': Decimal('0.0'),
            'absence_deduction_rate': Decimal('1.0'),
        }
    )
    
    if request.method == 'POST':
        tab = request.POST.get('active_tab', 'health_insurance')
        
        if tab == 'health_insurance':
            form = EmployeeHealthInsuranceForm(request.POST, instance=health_insurance)
            if form.is_valid():
                form.save()
                messages.success(request, 'تم حفظ بيانات التأمين الصحي بنجاح')
                return redirect('employees:comprehensive_edit', emp_id=emp_id)
        
        elif tab == 'social_insurance':
            form = EmployeeSocialInsuranceForm(request.POST, instance=social_insurance)
            if form.is_valid():
                form.save()
                messages.success(request, 'تم حفظ بيانات التأمينات الاجتماعية بنجاح')
                return redirect('employees:comprehensive_edit', emp_id=emp_id)
        
        elif tab == 'payroll_components':
            formset = EmployeeSalaryComponentFormSet(request.POST, instance=employee)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'تم حفظ مكونات الراتب بنجاح')
                return redirect('employees:comprehensive_edit', emp_id=emp_id)
        
        elif tab == 'transport':
            if transport_record:
                form = EmployeeTransportForm(request.POST, instance=transport_record)
            else:
                form = EmployeeTransportForm(request.POST)
                form.instance.emp = employee
            
            if form.is_valid():
                form.save()
                messages.success(request, 'تم حفظ بيانات النقل بنجاح')
                return redirect('employees:comprehensive_edit', emp_id=emp_id)
        
        elif tab == 'work_setup':
            form = EmployeeWorkSetupForm(request.POST, instance=work_setup)
            if form.is_valid():
                form.save()
                messages.success(request, 'تم حفظ إعدادات العمل بنجاح')
                return redirect('employees:comprehensive_edit', emp_id=emp_id)
    
    # Prepare forms for GET request
    health_insurance_form = EmployeeHealthInsuranceForm(instance=health_insurance)
    social_insurance_form = EmployeeSocialInsuranceForm(instance=social_insurance)
    salary_components_formset = EmployeeSalaryComponentFormSet(instance=employee)
    transport_form = EmployeeTransportForm(instance=transport_record)
    work_setup_form = EmployeeWorkSetupForm(instance=work_setup)
    
    # Get leave balances
    leave_balances = EmployeeLeaveBalance.objects.filter(
        emp=employee, year=date.today().year
    ).select_related('leave_type')
    
    # Get active loans
    active_loans = EmployeeLoan.objects.filter(
        emp=employee, status__in=['Approved', 'Active']
    ).select_related('loan_type')
    
    # Get recent evaluations
    recent_evaluations = EmployeePerformanceEvaluation.objects.filter(
        emp=employee
    ).order_by('-evaluation_date')[:5]
    
    context = {
        'employee': employee,
        'health_insurance_form': health_insurance_form,
        'social_insurance_form': social_insurance_form,
        'salary_components_formset': salary_components_formset,
        'transport_form': transport_form,
        'work_setup_form': work_setup_form,
        'leave_balances': leave_balances,
        'active_loans': active_loans,
        'recent_evaluations': recent_evaluations,
        'active_tab': request.GET.get('tab', 'health_insurance'),
    }
    
    return render(request, 'employees/comprehensive_edit.html', context)


@login_required
def get_vehicle_details(request, vehicle_id):
    """الحصول على تفاصيل المركبة عبر AJAX"""
    try:
        vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)
        data = {
            'supervisor_name': vehicle.supervisor_name,
            'supervisor_phone': vehicle.supervisor_phone,
            'driver_name': vehicle.driver_name,
            'driver_phone': vehicle.driver_phone,
            'capacity': vehicle.capacity,
            'route_info': vehicle.route_info,
        }
        return JsonResponse(data)
    except Vehicle.DoesNotExist:
        return JsonResponse({'error': 'المركبة غير موجودة'}, status=404)


@login_required
def calculate_salary_deductions(request, emp_id):
    """حساب الخصومات التلقائية للراتب"""
    employee = get_object_or_404(Employee, emp_id=emp_id)
    
    # Get social insurance data
    try:
        social_insurance = ExtendedEmployeeSocialInsurance.objects.get(emp=employee)
        insurance_deduction = social_insurance.employee_deduction
    except ExtendedEmployeeSocialInsurance.DoesNotExist:
        insurance_deduction = Decimal('0.00')
    
    # Calculate tax (simplified calculation - should be based on tax brackets)
    salary_components = EmployeeSalaryComponent.objects.filter(
        emp=employee,
        component__component_type='allowance',
        is_active=True
    )
    
    total_taxable_income = sum(
        comp.amount for comp in salary_components 
        if comp.component.is_taxable
    )
    
    # Simple tax calculation (you should implement proper tax brackets)
    tax_deduction = total_taxable_income * Decimal('0.05')  # 5% tax rate
    
    # Get active loan installments
    active_loans = EmployeeLoan.objects.filter(
        emp=employee, status__in=['Approved', 'Active']
    )
    
    loan_deductions = sum(loan.installment_amt or Decimal('0.00') for loan in active_loans)
    
    data = {
        'insurance_deduction': float(insurance_deduction),
        'tax_deduction': float(tax_deduction),
        'loan_deductions': float(loan_deductions),
        'total_deductions': float(insurance_deduction + tax_deduction + loan_deductions),
    }
    
    return JsonResponse(data)


# =============================================================================
# MANAGEMENT VIEWS FOR LOOKUP TABLES
# =============================================================================

@login_required
def health_insurance_providers_list(request):
    """قائمة مقدمي خدمات التأمين الصحي"""
    providers = ExtendedHealthInsuranceProvider.objects.all().order_by('provider_name')
    paginator = Paginator(providers, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'مقدمي خدمات التأمين الصحي',
    }
    return render(request, 'employees/health_insurance_providers_list.html', context)


@login_required
def health_insurance_provider_create(request):
    """إضافة مقدم خدمة تأمين صحي جديد"""
    if request.method == 'POST':
        form = HealthInsuranceProviderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة مقدم الخدمة بنجاح')
            return redirect('employees:health_insurance_providers_list')
    else:
        form = HealthInsuranceProviderForm()
    
    context = {
        'form': form,
        'title': 'إضافة مقدم خدمة تأمين صحي',
        'submit_text': 'إضافة',
    }
    return render(request, 'employees/health_insurance_provider_form.html', context)


@login_required
def social_insurance_job_titles_list(request):
    """قائمة مسميات الوظائف في التأمينات الاجتماعية"""
    job_titles = SocialInsuranceJobTitle.objects.all().order_by('job_code')
    paginator = Paginator(job_titles, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'مسميات الوظائف في التأمينات الاجتماعية',
    }
    return render(request, 'employees/social_insurance_job_titles_list.html', context)


@login_required
def social_insurance_job_title_create(request):
    """إضافة مسمى وظيفة جديد في التأمينات الاجتماعية"""
    if request.method == 'POST':
        form = SocialInsuranceJobTitleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة المسمى الوظيفي بنجاح')
            return redirect('employees:social_insurance_job_titles_list')
    else:
        form = SocialInsuranceJobTitleForm()
    
    context = {
        'form': form,
        'title': 'إضافة مسمى وظيفي في التأمينات الاجتماعية',
        'submit_text': 'إضافة',
    }
    return render(request, 'employees/social_insurance_job_title_form.html', context)


@login_required
def health_insurance_provider_edit(request, provider_id):
    """تعديل مقدم خدمة التأمين الصحي"""
    provider = get_object_or_404(ExtendedHealthInsuranceProvider, provider_id=provider_id)

    if request.method == 'POST':
        form = HealthInsuranceProviderForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث مقدم الخدمة بنجاح')
            return redirect('employees:health_insurance_providers_list')
    else:
        form = HealthInsuranceProviderForm(instance=provider)

    context = {
        'form': form,
        'provider': provider,
        'title': 'تعديل مقدم خدمة التأمين الصحي',
        'submit_text': 'حفظ التغييرات',
    }
    return render(request, 'employees/health_insurance_provider_form.html', context)


@login_required
def social_insurance_job_title_edit(request, job_title_id):
    """تعديل مسمى وظيفة في التأمينات الاجتماعية"""
    job_title = get_object_or_404(SocialInsuranceJobTitle, job_title_id=job_title_id)

    if request.method == 'POST':
        form = SocialInsuranceJobTitleForm(request.POST, instance=job_title)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المسمى الوظيفي بنجاح')
            return redirect('employees:social_insurance_job_titles_list')
    else:
        form = SocialInsuranceJobTitleForm(instance=job_title)

    context = {
        'form': form,
        'job_title': job_title,
        'title': 'تعديل مسمى وظيفي في التأمينات الاجتماعية',
        'submit_text': 'حفظ التغييرات',
    }
    return render(request, 'employees/social_insurance_job_title_form.html', context)


@login_required
def salary_components_list(request):
    """قائمة مكونات الراتب"""
    components = SalaryComponent.objects.all().order_by('component_type', 'sort_order', 'component_name')
    paginator = Paginator(components, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'مكونات الراتب',
    }
    return render(request, 'employees/salary_components_list.html', context)


@login_required
def salary_component_create(request):
    """إضافة مكون راتب جديد"""
    if request.method == 'POST':
        form = SalaryComponentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة مكون الراتب بنجاح')
            return redirect('employees:salary_components_list')
    else:
        form = SalaryComponentForm()

    context = {
        'form': form,
        'title': 'إضافة مكون راتب جديد',
        'submit_text': 'إضافة',
    }
    return render(request, 'employees/salary_component_form.html', context)


@login_required
def salary_component_edit(request, component_id):
    """تعديل مكون الراتب"""
    component = get_object_or_404(SalaryComponent, component_id=component_id)

    if request.method == 'POST':
        form = SalaryComponentForm(request.POST, instance=component)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث مكون الراتب بنجاح')
            return redirect('employees:salary_components_list')
    else:
        form = SalaryComponentForm(instance=component)

    context = {
        'form': form,
        'component': component,
        'title': 'تعديل مكون الراتب',
        'submit_text': 'حفظ التغييرات',
    }
    return render(request, 'employees/salary_component_form.html', context)


@login_required
def vehicles_list(request):
    """قائمة المركبات"""
    vehicles = Vehicle.objects.all().order_by('vehicle_number')
    paginator = Paginator(vehicles, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'إدارة المركبات',
    }
    return render(request, 'employees/vehicles_list.html', context)


@login_required
def vehicle_create(request):
    """إضافة مركبة جديدة"""
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة المركبة بنجاح')
            return redirect('employees:vehicles_list')
    else:
        form = VehicleForm()

    context = {
        'form': form,
        'title': 'إضافة مركبة جديدة',
        'submit_text': 'إضافة',
    }
    return render(request, 'employees/vehicle_form.html', context)


@login_required
def vehicle_edit(request, vehicle_id):
    """تعديل المركبة"""
    vehicle = get_object_or_404(Vehicle, vehicle_id=vehicle_id)

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المركبة بنجاح')
            return redirect('employees:vehicles_list')
    else:
        form = VehicleForm(instance=vehicle)

    context = {
        'form': form,
        'vehicle': vehicle,
        'title': 'تعديل المركبة',
        'submit_text': 'حفظ التغييرات',
    }
    return render(request, 'employees/vehicle_form.html', context)


@login_required
def pickup_points_list(request):
    """قائمة نقاط التجميع"""
    pickup_points = PickupPoint.objects.all().order_by('point_code')
    paginator = Paginator(pickup_points, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'إدارة نقاط التجميع',
    }
    return render(request, 'employees/pickup_points_list.html', context)


@login_required
def pickup_point_create(request):
    """إضافة نقطة تجميع جديدة"""
    if request.method == 'POST':
        form = PickupPointForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة نقطة التجميع بنجاح')
            return redirect('employees:pickup_points_list')
    else:
        form = PickupPointForm()

    context = {
        'form': form,
        'title': 'إضافة نقطة تجميع جديدة',
        'submit_text': 'إضافة',
    }
    return render(request, 'employees/pickup_point_form.html', context)


@login_required
def pickup_point_edit(request, pickup_point_id):
    """تعديل نقطة التجميع"""
    pickup_point = get_object_or_404(PickupPoint, pickup_point_id=pickup_point_id)

    if request.method == 'POST':
        form = PickupPointForm(request.POST, instance=pickup_point)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث نقطة التجميع بنجاح')
            return redirect('employees:pickup_points_list')
    else:
        form = PickupPointForm(instance=pickup_point)

    context = {
        'form': form,
        'pickup_point': pickup_point,
        'title': 'تعديل نقطة التجميع',
        'submit_text': 'حفظ التغييرات',
    }
    return render(request, 'employees/pickup_point_form.html', context)


@login_required
def work_schedules_list(request):
    """قائمة جداول العمل"""
    schedules = WorkSchedule.objects.all().order_by('schedule_name')
    paginator = Paginator(schedules, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'إدارة جداول العمل',
    }
    return render(request, 'employees/work_schedules_list.html', context)


@login_required
def work_schedule_create(request):
    """إضافة جدول عمل جديد"""
    if request.method == 'POST':
        form = WorkScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة جدول العمل بنجاح')
            return redirect('employees:work_schedules_list')
    else:
        form = WorkScheduleForm()

    context = {
        'form': form,
        'title': 'إضافة جدول عمل جديد',
        'submit_text': 'إضافة',
    }
    return render(request, 'employees/work_schedule_form.html', context)


@login_required
def work_schedule_edit(request, schedule_id):
    """تعديل جدول العمل"""
    schedule = get_object_or_404(WorkSchedule, schedule_id=schedule_id)

    if request.method == 'POST':
        form = WorkScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث جدول العمل بنجاح')
            return redirect('employees:work_schedules_list')
    else:
        form = WorkScheduleForm(instance=schedule)

    context = {
        'form': form,
        'schedule': schedule,
        'title': 'تعديل جدول العمل',
        'submit_text': 'حفظ التغييرات',
    }
    return render(request, 'employees/work_schedule_form.html', context)


@login_required
def evaluation_criteria_list(request):
    """قائمة معايير التقييم"""
    criteria = EvaluationCriteria.objects.all().order_by('sort_order', 'criteria_name')
    paginator = Paginator(criteria, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'إدارة معايير التقييم',
    }
    return render(request, 'employees/evaluation_criteria_list.html', context)


@login_required
def evaluation_criteria_create(request):
    """إضافة معيار تقييم جديد"""
    if request.method == 'POST':
        form = EvaluationCriteriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة معيار التقييم بنجاح')
            return redirect('employees:evaluation_criteria_list')
    else:
        form = EvaluationCriteriaForm()

    context = {
        'form': form,
        'title': 'إضافة معيار تقييم جديد',
        'submit_text': 'إضافة',
    }
    return render(request, 'employees/evaluation_criteria_form.html', context)


@login_required
def evaluation_criteria_edit(request, criteria_id):
    """تعديل معيار التقييم"""
    criteria = get_object_or_404(EvaluationCriteria, criteria_id=criteria_id)

    if request.method == 'POST':
        form = EvaluationCriteriaForm(request.POST, instance=criteria)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث معيار التقييم بنجاح')
            return redirect('employees:evaluation_criteria_list')
    else:
        form = EvaluationCriteriaForm(instance=criteria)

    context = {
        'form': form,
        'criteria': criteria,
        'title': 'تعديل معيار التقييم',
        'submit_text': 'حفظ التغييرات',
    }
    return render(request, 'employees/evaluation_criteria_form.html', context)


@login_required
def performance_evaluation_create(request, emp_id):
    """إنشاء تقييم أداء جديد"""
    employee = get_object_or_404(Employee, emp_id=emp_id)

    if request.method == 'POST':
        form = EmployeePerformanceEvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.emp = employee
            evaluation.save()

            # Create evaluation scores for all active criteria
            criteria = EvaluationCriteria.objects.filter(is_active=True)
            for criterion in criteria:
                EvaluationScore.objects.create(
                    evaluation=evaluation,
                    criteria=criterion,
                    score=0
                )

            messages.success(request, 'تم إنشاء التقييم بنجاح')
            return redirect('employees:performance_evaluation_edit', evaluation_id=evaluation.evaluation_id)
    else:
        form = EmployeePerformanceEvaluationForm(initial={
            'evaluation_date': date.today(),
            'evaluation_period_start': date.today().replace(day=1),
            'evaluation_period_end': date.today(),
        })

    context = {
        'form': form,
        'employee': employee,
        'title': f'إنشاء تقييم أداء - {employee.get_full_name()}',
        'submit_text': 'إنشاء التقييم',
    }
    return render(request, 'employees/performance_evaluation_form.html', context)


@login_required
def performance_evaluation_detail(request, evaluation_id):
    """عرض تفاصيل تقييم الأداء"""
    evaluation = get_object_or_404(EmployeePerformanceEvaluation, evaluation_id=evaluation_id)
    scores = EvaluationScore.objects.filter(evaluation=evaluation).select_related('criteria')

    context = {
        'evaluation': evaluation,
        'scores': scores,
        'title': f'تقييم الأداء - {evaluation.emp.get_full_name()}',
    }
    return render(request, 'employees/performance_evaluation_detail.html', context)


@login_required
def performance_evaluation_edit(request, evaluation_id):
    """تعديل تقييم الأداء"""
    evaluation = get_object_or_404(EmployeePerformanceEvaluation, evaluation_id=evaluation_id)

    if request.method == 'POST':
        form = EmployeePerformanceEvaluationForm(request.POST, instance=evaluation)
        formset = EvaluationScoreFormSet(request.POST, instance=evaluation)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                evaluation = form.save()
                formset.save()

                # Calculate overall score
                scores = EvaluationScore.objects.filter(evaluation=evaluation)
                total_weighted_score = sum(
                    score.score * score.criteria.weight for score in scores
                )
                total_weight = sum(score.criteria.weight for score in scores)

                if total_weight > 0:
                    evaluation.overall_score = total_weighted_score / total_weight
                    evaluation.save()

            messages.success(request, 'تم تحديث التقييم بنجاح')
            return redirect('employees:performance_evaluation_detail', evaluation_id=evaluation_id)
    else:
        form = EmployeePerformanceEvaluationForm(instance=evaluation)
        formset = EvaluationScoreFormSet(instance=evaluation)

    context = {
        'form': form,
        'formset': formset,
        'evaluation': evaluation,
        'title': f'تعديل تقييم الأداء - {evaluation.emp.get_full_name()}',
        'submit_text': 'حفظ التغييرات',
    }
    return render(request, 'employees/performance_evaluation_edit.html', context)
