"""
Extended Employee Views for Comprehensive HR Management
"""
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)

from .models import Employee
from .models_extended import (
    ExtendedHealthInsuranceProvider, ExtendedEmployeeHealthInsurance,
    SocialInsuranceJobTitle, ExtendedEmployeeSocialInsurance,
    SalaryComponent, EmployeeSalaryComponent,
    EmployeeLeaveBalance, Vehicle, PickupPoint, EmployeeTransport,
    EvaluationCriteria, EmployeePerformanceEvaluation, EvaluationScore,
    WorkSchedule, EmployeeWorkSetup, ExtendedEmployeeDocument, EmployeeDocumentCategory
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
    # First, ensure we have a default health insurance provider
    default_provider, created = ExtendedHealthInsuranceProvider.objects.get_or_create(
        provider_code='DEFAULT',
        defaults={
            'provider_name': 'مقدم خدمة افتراضي',
            'contact_person': 'غير محدد',
            'phone': '',
            'email': '',
            'address': '',
            'is_active': True,
        }
    )

    if created:
        logger.info(f"Created default health insurance provider: {default_provider.provider_name}")

    # Now create or get the health insurance record with the provider
    try:
        health_insurance, created = ExtendedEmployeeHealthInsurance.objects.get_or_create(
            emp=employee,
            defaults={
                'provider': default_provider,
                'insurance_status': 'inactive',
                'insurance_type': 'basic',
                'insurance_number': f'HI-{employee.emp_id}-{timezone.now().strftime("%Y%m%d")}',
                'start_date': date.today(),
                'expiry_date': date.today() + timedelta(days=365),
                'num_dependents': 0,
                'monthly_premium': Decimal('0.00'),
                'employee_contribution': Decimal('0.00'),
                'company_contribution': Decimal('0.00'),
            }
        )

        if created:
            logger.info(f"Created health insurance record for employee {employee.emp_code}")

    except Exception as e:
        logger.error(f"Error creating health insurance record for employee {employee.emp_code}: {str(e)}")
        # If we can't create the record, we'll handle it gracefully
        health_insurance = None

    # Ensure we have a default social insurance job title
    default_job_title, created = SocialInsuranceJobTitle.objects.get_or_create(
        job_code='DEFAULT',
        defaults={
            'job_title': 'مسمى وظيفي افتراضي',
            'insurable_wage_amount': Decimal('0.00'),
            'employee_deduction_percentage': Decimal('9.00'),  # Standard Saudi rate
            'company_contribution_percentage': Decimal('12.00'),  # Standard Saudi rate
        }
    )

    if created:
        logger.info(f"Created default social insurance job title: {default_job_title.job_title}")

    # Now create or get the social insurance record
    try:
        social_insurance, created = ExtendedEmployeeSocialInsurance.objects.get_or_create(
            emp=employee,
            defaults={
                'insurance_status': 'inactive',
                'start_date': date.today(),
                'subscription_confirmed': False,
                'job_title_id': default_job_title.id,  # Use job_title_id instead of job_title
                'social_insurance_number': f'SI-{employee.emp_id}-{timezone.now().strftime("%Y%m%d")}',
                'monthly_wage': Decimal('0.00'),
                'deduction_percentage': Decimal('9.0'),  # Add default deduction percentage
                'employee_deduction': Decimal('0.00'),
                'company_contribution': Decimal('0.00'),
            }
        )

        if created:
            logger.info(f"Created social insurance record for employee {employee.emp_code}")

    except Exception as e:
        logger.error(f"Error creating social insurance record for employee {employee.emp_code}: {str(e)}")
        # If we can't create the record, we'll handle it gracefully
        social_insurance = None

    transport_record = EmployeeTransport.objects.filter(
        emp=employee, is_active=True
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

    # Ensure we have a default work schedule
    from datetime import time
    default_work_schedule, created = WorkSchedule.objects.get_or_create(
        schedule_code='DEFAULT',
        defaults={
            'schedule_name': 'جدول عمل افتراضي',
            'daily_hours': Decimal('8.00'),
            'weekly_hours': Decimal('40.00'),
            'start_time': time(8, 0),  # 8:00 AM
            'end_time': time(16, 0),   # 4:00 PM
            'break_duration': 60,      # 60 minutes break
            'is_flexible': False,
            'overtime_applicable': True,
            'is_active': True,
            'description': 'جدول العمل الافتراضي للنظام - 8 ساعات يومياً من 8 صباحاً إلى 4 عصراً',
        }
    )

    if created:
        logger.info(f"Created default work schedule: {default_work_schedule.schedule_name}")

    # Now create or get the work setup record with the work schedule
    try:
        work_setup, created = EmployeeWorkSetup.objects.get_or_create(
            emp=employee,
            is_active=True,
            defaults={
                'work_schedule': default_work_schedule,
                'effective_date': date.today(),
                'overtime_rate': Decimal('1.5'),
                'late_deduction_rate': Decimal('0.0'),
                'absence_deduction_rate': Decimal('1.0'),
                'notes': 'إعدادات العمل الافتراضية',
            }
        )

        if created:
            logger.info(f"Created work setup record for employee {employee.emp_code}")

    except Exception as e:
        logger.error(f"Error creating work setup record for employee {employee.emp_code}: {str(e)}")
        # If we can't create the record, we'll handle it gracefully
        work_setup = None

    if request.method == 'POST':
        tab = request.POST.get('active_tab', 'basic_info')

        if tab == 'basic_info':
            # Handle basic employee information update
            employee.first_name = request.POST.get('first_name', employee.first_name)
            employee.second_name = request.POST.get('second_name', employee.second_name)
            employee.third_name = request.POST.get('third_name', employee.third_name)
            employee.last_name = request.POST.get('last_name', employee.last_name)
            employee.gender = request.POST.get('gender', employee.gender)
            employee.nationality = request.POST.get('nationality', employee.nationality)
            employee.national_id = request.POST.get('national_id', employee.national_id)
            employee.passport_no = request.POST.get('passport_no', employee.passport_no)
            employee.mobile = request.POST.get('mobile', employee.mobile)
            employee.email = request.POST.get('email', employee.email)
            employee.address = request.POST.get('address', employee.address)
            employee.emp_status = request.POST.get('emp_status', employee.emp_status)
            employee.notes = request.POST.get('notes', employee.notes)

            # Handle date fields
            birth_date = request.POST.get('birth_date')
            if birth_date:
                employee.birth_date = birth_date

            hire_date = request.POST.get('hire_date')
            if hire_date:
                employee.hire_date = hire_date

            join_date = request.POST.get('join_date')
            if join_date:
                employee.join_date = join_date

            probation_end = request.POST.get('probation_end')
            if probation_end:
                employee.probation_end = probation_end

            try:
                employee.save()
                messages.success(request, 'تم حفظ البيانات الأساسية بنجاح')
                return redirect('employees:comprehensive_edit', emp_id=emp_id)
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء حفظ البيانات: {str(e)}')

        elif tab == 'health_insurance':
            if health_insurance:
                form = EmployeeHealthInsuranceForm(request.POST, instance=health_insurance)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'تم حفظ بيانات التأمين الصحي بنجاح')
                    return redirect('employees:comprehensive_edit', emp_id=emp_id)
                else:
                    messages.error(request, 'يرجى تصحيح الأخطاء في نموذج التأمين الصحي')
            else:
                messages.error(request, 'لا يمكن حفظ بيانات التأمين الصحي. يرجى المحاولة مرة أخرى.')
                return redirect('employees:comprehensive_edit', emp_id=emp_id)

        elif tab == 'social_insurance':
            if social_insurance:
                form = EmployeeSocialInsuranceForm(request.POST, instance=social_insurance)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'تم حفظ بيانات التأمينات الاجتماعية بنجاح')
                    return redirect('employees:comprehensive_edit', emp_id=emp_id)
                else:
                    messages.error(request, 'يرجى تصحيح الأخطاء في نموذج التأمينات الاجتماعية')
            else:
                messages.error(request, 'لا يمكن حفظ بيانات التأمينات الاجتماعية. يرجى المحاولة مرة أخرى.')
                return redirect('employees:comprehensive_edit', emp_id=emp_id)

        elif tab == 'salary_components':
            # Handle salary components form submission
            try:
                action = request.POST.get('action')

                if action == 'add_component':
                    # Handle adding new salary component
                    component_id = request.POST.get('component_id')
                    amount = request.POST.get('amount')
                    calculation_type = request.POST.get('calculation_type', 'fixed')
                    notes = request.POST.get('notes', '')

                    if component_id and amount:
                        component = get_object_or_404(SalaryComponent, component_id=component_id)

                        # Check if this component already exists for this employee
                        existing_component = EmployeeSalaryComponent.objects.filter(
                            emp=employee, component=component
                        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

                        if existing_component:
                            # Update existing component
                            existing_component.amount = Decimal(amount)
                            existing_component.calculation_type = calculation_type
                            existing_component.notes = notes
                            existing_component.save()
                            messages.success(request, f'تم تحديث {component.component_name} بنجاح')
                        else:
                            # Create new component
                            EmployeeSalaryComponent.objects.create(
                                emp=employee,
                                component=component,
                                amount=Decimal(amount),
                                calculation_type=calculation_type,
                                notes=notes
                            )
                            messages.success(request, f'تم إضافة {component.component_name} بنجاح')
                    else:
                        messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')

                elif action == 'remove_component':
                    # Handle removing salary component
                    component_id = request.POST.get('component_id')
                    if component_id:
                        try:
                            component_to_remove = EmployeeSalaryComponent.objects.get(
                                emp_salary_component_id=component_id, emp=employee
                            )
                            component_name = component_to_remove.component.component_name
                            component_to_remove.delete()
                            messages.success(request, f'تم حذف {component_name} بنجاح')
                        except EmployeeSalaryComponent.DoesNotExist:
                            messages.error(request, 'المكون المطلوب حذفه غير موجود')
                    else:
                        messages.error(request, 'لم يتم تحديد المكون المطلوب حذفه')

            except Exception as e:
                logger.error(f"Error updating salary components for employee {emp_id}: {str(e)}")
                messages.error(request, f'حدث خطأ أثناء تحديث مكونات الراتب: {str(e)}')
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

        elif tab == 'leave_balances':
            # Handle leave balances update
            updated_count = 0
            for balance in EmployeeLeaveBalance.objects.filter(emp=employee, year=date.today().prefetch_related()  # TODO: Add appropriate prefetch_related fields.year):
                opening_balance = request.POST.get(f'opening_balance_{balance.id}')
                accrued_balance = request.POST.get(f'accrued_balance_{balance.id}')
                carried_forward = request.POST.get(f'carried_forward_{balance.id}')

                if opening_balance is not None:
                    balance.opening_balance = Decimal(opening_balance)
                if accrued_balance is not None:
                    balance.accrued_balance = Decimal(accrued_balance)
                if carried_forward is not None:
                    balance.carried_forward = Decimal(carried_forward)

                # Recalculate current balance
                balance.current_balance = balance.opening_balance + balance.accrued_balance + balance.carried_forward - balance.used_balance
                balance.save()
                updated_count += 1

            messages.success(request, f'تم تحديث {updated_count} رصيد إجازة بنجاح')
            return redirect('employees:comprehensive_edit', emp_id=emp_id)

        elif tab == 'work_setup':
            if work_setup:
                form = EmployeeWorkSetupForm(request.POST, instance=work_setup)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'تم حفظ إعدادات العمل بنجاح')
                    return redirect('employees:comprehensive_edit', emp_id=emp_id)
                else:
                    messages.error(request, 'يرجى تصحيح الأخطاء في نموذج إعدادات العمل')
            else:
                messages.error(request, 'لا يمكن حفظ إعدادات العمل. يرجى المحاولة مرة أخرى.')
                return redirect('employees:comprehensive_edit', emp_id=emp_id)

    # Prepare forms for GET request
    health_insurance_form = EmployeeHealthInsuranceForm(instance=health_insurance) if health_insurance else EmployeeHealthInsuranceForm()
    social_insurance_form = EmployeeSocialInsuranceForm(instance=social_insurance) if social_insurance else EmployeeSocialInsuranceForm()

    # Get salary components for this employee
    salary_components = EmployeeSalaryComponent.objects.filter(emp=employee).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('component')

    # Get available salary components
    available_allowances = SalaryComponent.objects.filter(component_type='allowance', is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields
    available_deductions = SalaryComponent.objects.filter(component_type='deduction', is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields

    transport_form = EmployeeTransportForm(instance=transport_record)
    work_setup_form = EmployeeWorkSetupForm(instance=work_setup) if work_setup else EmployeeWorkSetupForm()

    # Get leave balances
    leave_balances = EmployeeLeaveBalance.objects.filter(
        emp=employee, year=date.today().prefetch_related()  # TODO: Add appropriate prefetch_related fields.year
    ).select_related('leave_type')

    # Get active loans
    active_loans = EmployeeLoan.objects.filter(
        emp=employee, status__in=['Approved', 'Active']
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('loan_type')

    # Get recent evaluations
    recent_evaluations = EmployeePerformanceEvaluation.objects.filter(
        emp=employee
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('-evaluation_date')[:5]

    # Get employee documents
    employee_documents = ExtendedEmployeeDocument.objects.filter(
        emp=employee
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('-created_at')

    # Get document categories
    document_categories = EmployeeDocumentCategory.objects.filter(
        is_active=True
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('sort_order', 'category_name')

    context = {
        'employee': employee,
        'health_insurance_form': health_insurance_form,
        'social_insurance_form': social_insurance_form,
        'salary_components': salary_components,
        'available_allowances': available_allowances,
        'available_deductions': available_deductions,
        'transport_form': transport_form,
        'work_setup_form': work_setup_form,
        'leave_balances': leave_balances,
        'active_loans': active_loans,
        'recent_evaluations': recent_evaluations,
        'employee_documents': employee_documents,
        'document_categories': document_categories,
        'active_tab': request.GET.get('tab', 'basic_info'),
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
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields

    total_taxable_income = sum(
        comp.amount for comp in salary_components
        if comp.component.is_taxable
    )

    # Simple tax calculation (you should implement proper tax brackets)
    tax_deduction = total_taxable_income * Decimal('0.05')  # 5% tax rate

    # Get active loan installments
    active_loans = EmployeeLoan.objects.filter(
        emp=employee, status__in=['Approved', 'Active']
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields

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
    providers = ExtendedHealthInsuranceProvider.objects.all().select_related()  # TODO: Add appropriate select_related fields.order_by('provider_name')
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
    job_titles = SocialInsuranceJobTitle.objects.all().select_related()  # TODO: Add appropriate select_related fields

    # Search functionality
    search = request.GET.get('search')
    if search:
        job_titles = job_titles.filter(
            Q(job_code__icontains=search) |
            Q(job_title__icontains=search)
        )

    # Status filter
    status = request.GET.get('status')
    if status == 'active':
        job_titles = job_titles.filter(is_active=True)
    elif status == 'inactive':
        job_titles = job_titles.filter(is_active=False)

    # Order by job_code
    job_titles = job_titles.order_by('job_code')

    # Pagination
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
    components = SalaryComponent.objects.all().select_related()  # TODO: Add appropriate select_related fields.order_by('component_type', 'sort_order', 'component_name')
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
    vehicles = Vehicle.objects.all().select_related()  # TODO: Add appropriate select_related fields

    # Search functionality
    search = request.GET.get('search')
    if search:
        vehicles = vehicles.filter(
            Q(vehicle_number__icontains=search) |
            Q(vehicle_model__icontains=search) |
            Q(driver_name__icontains=search) |
            Q(supervisor_name__icontains=search)
        )

    # Status filter
    status = request.GET.get('status')
    if status:
        vehicles = vehicles.filter(vehicle_status=status)

    # Year filter
    year = request.GET.get('year')
    if year:
        vehicles = vehicles.filter(vehicle_year=year)

    # Order by vehicle_number
    vehicles = vehicles.order_by('vehicle_number')

    # Get unique years for filter dropdown
    years = Vehicle.objects.values_list('vehicle_year', flat=True).distinct().order_by('-vehicle_year')

    # Pagination
    paginator = Paginator(vehicles, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'إدارة المركبات',
        'years': years,
        'status_choices': Vehicle.VEHICLE_STATUS_CHOICES,
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
    pickup_points = PickupPoint.objects.all().select_related()  # TODO: Add appropriate select_related fields

    # Search functionality
    search = request.GET.get('search')
    if search:
        pickup_points = pickup_points.filter(
            Q(point_name__icontains=search) |
            Q(point_code__icontains=search) |
            Q(address__icontains=search)
        )

    # Status filter
    status = request.GET.get('status')
    if status == 'active':
        pickup_points = pickup_points.filter(is_active=True)
    elif status == 'inactive':
        pickup_points = pickup_points.filter(is_active=False)

    # Order by point_code
    pickup_points = pickup_points.order_by('point_code')

    # Pagination
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
    schedules = WorkSchedule.objects.all().select_related()  # TODO: Add appropriate select_related fields.order_by('schedule_name')
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
    criteria = EvaluationCriteria.objects.all().select_related()  # TODO: Add appropriate select_related fields.order_by('sort_order', 'criteria_name')
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
            criteria = EvaluationCriteria.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields
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
    scores = EvaluationScore.objects.filter(evaluation=evaluation).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('criteria')

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
                scores = EvaluationScore.objects.filter(evaluation=evaluation).prefetch_related()  # TODO: Add appropriate prefetch_related fields
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


@login_required
def initialize_leave_balances(request, emp_id):
    """تهيئة أرصدة الإجازات للموظف"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'طريقة الطلب غير صحيحة'})

    try:
        employee = get_object_or_404(Employee, emp_id=emp_id)
        current_year = date.today().year

        # Check if employee already has leave balances for current year
        existing_balances = EmployeeLeaveBalance.objects.filter(
            emp=employee, year=current_year
        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()

        if existing_balances > 0:
            return JsonResponse({
                'success': False,
                'message': f'الموظف لديه بالفعل {existing_balances} رصيد إجازة لعام {current_year}'
            })

        # Get all active leave types
        try:
            from leaves.models import LeaveType
            leave_types = LeaveType.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields
        except ImportError:
            return JsonResponse({
                'success': False,
                'message': 'تطبيق الإجازات غير متوفر في النظام.'
            })

        if not leave_types.exists():
            return JsonResponse({
                'success': False,
                'message': 'لا توجد أنواع إجازات نشطة في النظام. يرجى إضافة أنواع الإجازات أولاً من قسم إدارة الإجازات.'
            })

        created_balances = []

        # Create default leave balances for each leave type
        for leave_type in leave_types:
            # Set default balances based on leave type
            if 'سنوية' in leave_type.leave_name or 'Annual' in leave_type.leave_name:
                opening_balance = Decimal('21.0')  # 21 days annual leave (Saudi standard)
                accrued_balance = Decimal('21.0')
            elif 'مرضية' in leave_type.leave_name or 'Sick' in leave_type.leave_name:
                opening_balance = Decimal('30.0')  # 30 days sick leave (Saudi standard)
                accrued_balance = Decimal('30.0')
            elif 'طارئة' in leave_type.leave_name or 'Emergency' in leave_type.leave_name:
                opening_balance = Decimal('5.0')   # 5 days emergency leave
                accrued_balance = Decimal('5.0')
            elif 'أمومة' in leave_type.leave_name or 'Maternity' in leave_type.leave_name:
                opening_balance = Decimal('70.0')  # 70 days maternity leave (Saudi standard)
                accrued_balance = Decimal('70.0')
            elif 'أبوة' in leave_type.leave_name or 'Paternity' in leave_type.leave_name:
                opening_balance = Decimal('3.0')   # 3 days paternity leave (Saudi standard)
                accrued_balance = Decimal('3.0')
            else:
                # Default for other leave types
                opening_balance = Decimal('10.0')
                accrued_balance = Decimal('10.0')

            # Create the leave balance record
            leave_balance = EmployeeLeaveBalance.objects.create(
                emp=employee,
                leave_type=leave_type,
                year=current_year,
                opening_balance=opening_balance,
                accrued_balance=accrued_balance,
                used_balance=Decimal('0.0'),
                carried_forward=Decimal('0.0'),
                current_balance=opening_balance + accrued_balance,
                notes=f'تم إنشاء الرصيد تلقائياً في {timezone.now().strftime("%Y-%m-%d %H:%M")}'
            )

            created_balances.append({
                'leave_type': leave_type.leave_name,
                'balance': float(leave_balance.current_balance)
            })

        # Log the action
        logger.info(f"Initialized {len(created_balances)} leave balances for employee {employee.emp_code}")

        return JsonResponse({
            'success': True,
            'message': f'تم إنشاء {len(created_balances)} رصيد إجازة بنجاح',
            'created_balances': created_balances
        })

    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'الموظف غير موجود'})
    except Exception as e:
        logger.error(f"Error initializing leave balances for employee {emp_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'حدث خطأ أثناء تهيئة أرصدة الإجازات: {str(e)}'
        })


@login_required
def upload_document(request):
    """رفع وثيقة جديدة للموظف"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'طريقة الطلب غير صحيحة'})

    try:
        emp_id = request.POST.get('emp_id')
        employee = get_object_or_404(Employee, emp_id=emp_id)

        # Get form data
        category_id = request.POST.get('document_category')
        document_name = request.POST.get('document_name')
        document_file = request.FILES.get('document_file')
        document_date = request.POST.get('document_date')
        expiry_date = request.POST.get('expiry_date')
        notes = request.POST.get('document_notes')

        # Validate required fields
        if not all([category_id, document_name, document_file]):
            return JsonResponse({
                'success': False,
                'message': 'يرجى ملء جميع الحقول المطلوبة'
            })

        # Get category
        category = get_object_or_404(EmployeeDocumentCategory, category_id=category_id)

        # Validate file
        file_extension = document_file.name.split('.')[-1].lower()
        allowed_extensions = category.get_allowed_extensions_list()

        if file_extension not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'message': f'نوع الملف غير مسموح. الأنواع المسموحة: {", ".join(allowed_extensions)}'
            })

        # Check file size
        max_size_mb = category.max_file_size_mb
        if document_file.size > max_size_mb * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'message': f'حجم الملف كبير جداً. الحد الأقصى المسموح: {max_size_mb} ميجابايت'
            })

        # Create document record
        document = ExtendedEmployeeDocument.objects.create(
            emp=employee,
            category=category,
            document_name=document_name,
            document_file=document_file,
            document_date=document_date if document_date else None,
            expiry_date=expiry_date if expiry_date else None,
            notes=notes,
            uploaded_by=request.user
        )

        logger.info(f"Document uploaded successfully: {document.document_name} for employee {employee.emp_code}")

        return JsonResponse({
            'success': True,
            'message': 'تم رفع الوثيقة بنجاح',
            'document_id': document.document_id
        })

    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'حدث خطأ أثناء رفع الوثيقة: {str(e)}'
        })


@login_required
def delete_document(request):
    """حذف وثيقة الموظف"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'طريقة الطلب غير صحيحة'})

    try:
        document_id = request.POST.get('document_id')
        document = get_object_or_404(ExtendedEmployeeDocument, document_id=document_id)

        # Check permissions (optional - you can add more sophisticated permission checking)
        # For now, any logged-in user can delete documents

        # Delete the file from storage
        if document.document_file:
            try:
                document.document_file.delete(save=False)
            except Exception as e:
                logger.warning(f"Could not delete file {document.document_file.name}: {str(e)}")

        # Delete the database record
        document_name = document.document_name
        employee_code = document.emp.emp_code
        document.delete()

        logger.info(f"Document deleted successfully: {document_name} for employee {employee_code}")

        return JsonResponse({
            'success': True,
            'message': 'تم حذف الوثيقة بنجاح'
        })

    except ExtendedEmployeeDocument.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'الوثيقة غير موجودة'})
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'حدث خطأ أثناء حذف الوثيقة: {str(e)}'
        })


@login_required
def add_salary_component(request):
    """إضافة مكون راتب جديد للموظف"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'طريقة الطلب غير صحيحة'})

    try:
        emp_id = request.POST.get('emp_id')
        component_id = request.POST.get('component_id')
        amount = request.POST.get('amount')
        calculation_type = request.POST.get('calculation_type', 'fixed')
        notes = request.POST.get('notes', '')

        # Validate required fields
        if not all([emp_id, component_id, amount]):
            return JsonResponse({
                'success': False,
                'message': 'يرجى ملء جميع الحقول المطلوبة'
            })

        employee = get_object_or_404(Employee, emp_id=emp_id)
        component = get_object_or_404(SalaryComponent, component_id=component_id)

        # Check if this component already exists for this employee
        existing_component = EmployeeSalaryComponent.objects.filter(
            emp=employee, component=component
        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

        if existing_component:
            # Update existing component
            existing_component.amount = Decimal(amount)
            existing_component.calculation_type = calculation_type
            existing_component.notes = notes
            existing_component.save()
            message = f'تم تحديث {component.component_name} بنجاح'
        else:
            # Create new component
            new_component = EmployeeSalaryComponent.objects.create(
                emp=employee,
                component=component,
                amount=Decimal(amount),
                calculation_type=calculation_type,
                notes=notes
            )
            message = f'تم إضافة {component.component_name} بنجاح'

        logger.info(f"Salary component updated: {component.component_name} for employee {employee.emp_code}")

        return JsonResponse({
            'success': True,
            'message': message,
            'component_name': component.component_name,
            'amount': float(amount)
        })

    except Exception as e:
        logger.error(f"Error adding salary component: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'حدث خطأ أثناء إضافة مكون الراتب: {str(e)}'
        })


@login_required
def remove_salary_component(request):
    """حذف مكون راتب للموظف"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'طريقة الطلب غير صحيحة'})

    try:
        component_id = request.POST.get('component_id')

        if not component_id:
            return JsonResponse({
                'success': False,
                'message': 'لم يتم تحديد المكون المطلوب حذفه'
            })

        component_to_remove = get_object_or_404(EmployeeSalaryComponent, emp_salary_component_id=component_id)

        # Check permissions (optional - you can add more sophisticated permission checking)
        # For now, any logged-in user can remove components

        component_name = component_to_remove.component.component_name
        employee_code = component_to_remove.emp.emp_code
        component_to_remove.delete()

        logger.info(f"Salary component removed: {component_name} for employee {employee_code}")

        return JsonResponse({
            'success': True,
            'message': f'تم حذف {component_name} بنجاح'
        })

    except EmployeeSalaryComponent.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'المكون المطلوب حذفه غير موجود'})
    except Exception as e:
        logger.error(f"Error removing salary component: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'حدث خطأ أثناء حذف مكون الراتب: {str(e)}'
        })
