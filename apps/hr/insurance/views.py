from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import date, datetime, timedelta
from .models import HealthInsuranceProvider, EmployeeHealthInsurance, EmployeeSocialInsurance
from apps.hr.employees.models import Employee
from org.models import Department
from .forms import HealthInsuranceProviderForm, EmployeeHealthInsuranceForm, EmployeeSocialInsuranceForm


@login_required
def dashboard(request):
    """لوحة تحكم التأمينات"""
    today = date.today()

    # إحصائيات عامة
    total_providers = HealthInsuranceProvider.objects.count()
    total_health_insurance = EmployeeHealthInsurance.objects.count()
    total_social_insurance = EmployeeSocialInsurance.objects.count()
    active_health_policies = EmployeeHealthInsurance.objects.filter(
        end_date__gte=today
    ).count()

    # التأمينات المنتهية الصلاحية قريباً (خلال 30 يوم)
    expiring_soon = EmployeeHealthInsurance.objects.filter(
        end_date__gte=today,
        end_date__lte=today + timedelta(days=30)
    ).select_related('emp', 'provider').order_by('end_date')

    # التأمينات المنتهية الصلاحية
    expired_insurance = EmployeeHealthInsurance.objects.filter(
        end_date__lt=today
    ).select_related('emp', 'provider').order_by('-end_date')[:5]

    # إحصائيات مزودي التأمين
    provider_stats = HealthInsuranceProvider.objects.annotate(
        policy_count=Count('employeehealthinsurance'),
        total_premium=Sum('employeehealthinsurance__premium'),
        active_policies=Count('employeehealthinsurance',
                            filter=Q(employeehealthinsurance__end_date__gte=today))
    ).order_by('-policy_count')

    # إجمالي الأقساط الشهرية
    monthly_premiums = EmployeeHealthInsurance.objects.filter(
        end_date__gte=today
    ).aggregate(
        total_premium=Sum('premium')
    )['total_premium'] or 0

    # إحصائيات الأقسام
    department_stats = Department.objects.annotate(
        health_insurance_count=Count('employee__employeehealthinsurance'),
        social_insurance_count=Count('employee__employeesocialinsurance'),
        total_premium=Sum('employee__employeehealthinsurance__premium')
    ).filter(
        Q(health_insurance_count__gt=0) | Q(social_insurance_count__gt=0)
    ).order_by('-total_premium')[:5]

    context = {
        'total_providers': total_providers,
        'total_health_insurance': total_health_insurance,
        'total_social_insurance': total_social_insurance,
        'active_health_policies': active_health_policies,
        'expiring_soon': expiring_soon,
        'expired_insurance': expired_insurance,
        'provider_stats': provider_stats,
        'monthly_premiums': monthly_premiums,
        'department_stats': department_stats,
    }

    return render(request, 'insurance/dashboard.html', context)


# إدارة مزودي التأمين الصحي
@login_required
def provider_list(request):
    """قائمة مزودي التأمين الصحي"""
    providers = HealthInsuranceProvider.objects.annotate(
        policy_count=Count('employeehealthinsurance'),
        total_premium=Sum('employeehealthinsurance__premium')
    ).order_by('provider_name')

    # البحث
    search = request.GET.get('search')
    if search:
        providers = providers.filter(
            Q(provider_name__icontains=search) |
            Q(contact_no__icontains=search)
        )

    context = {
        'providers': providers,
    }

    return render(request, 'insurance/provider_list.html', context)


@login_required
def add_provider(request):
    """إضافة مزود تأمين صحي جديد"""
    if request.method == 'POST':
        form = HealthInsuranceProviderForm(request.POST)
        if form.is_valid():
            provider = form.save()
            messages.success(request, f'تم إضافة مزود التأمين {provider.provider_name} بنجاح.')
            return redirect('insurance:provider_list')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = HealthInsuranceProviderForm()

    context = {
        'form': form,
        'title': 'إضافة مزود تأمين صحي جديد'
    }

    return render(request, 'insurance/provider_form.html', context)


@login_required
def provider_detail(request, provider_id):
    """تفاصيل مزود التأمين الصحي"""
    provider = get_object_or_404(HealthInsuranceProvider, provider_id=provider_id)

    # بوالص التأمين الخاصة بهذا المزود
    policies = EmployeeHealthInsurance.objects.filter(
        provider=provider
    ).select_related('emp').order_by('-start_date')

    # إحصائيات المزود
    provider_stats = policies.aggregate(
        total_policies=Count('ins_id'),
        active_policies=Count('ins_id', filter=Q(end_date__gte=date.today())),
        total_premium=Sum('premium'),
        total_dependents=Sum('dependents')
    )

    context = {
        'provider': provider,
        'policies': policies,
        'provider_stats': provider_stats,
    }

    return render(request, 'insurance/provider_detail.html', context)


@login_required
def edit_provider(request, provider_id):
    """تعديل مزود التأمين الصحي"""
    provider = get_object_or_404(HealthInsuranceProvider, provider_id=provider_id)

    if request.method == 'POST':
        form = HealthInsuranceProviderForm(request.POST, instance=provider)
        if form.is_valid():
            provider = form.save()
            messages.success(request, f'تم تحديث مزود التأمين {provider.provider_name} بنجاح.')
            return redirect('insurance:provider_detail', provider_id=provider.provider_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = HealthInsuranceProviderForm(instance=provider)

    context = {
        'form': form,
        'provider': provider,
        'title': 'تعديل مزود التأمين الصحي'
    }

    return render(request, 'insurance/provider_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_provider(request, provider_id):
    """حذف مزود التأمين الصحي"""
    provider = get_object_or_404(HealthInsuranceProvider, provider_id=provider_id)

    try:
        # التحقق من وجود بوالص مرتبطة
        if EmployeeHealthInsurance.objects.filter(provider=provider).exists():
            messages.error(request, f'لا يمكن حذف مزود التأمين {provider.provider_name} لأنه مرتبط ببوالص تأمين.')
        else:
            provider.delete()
            messages.success(request, f'تم حذف مزود التأمين {provider.provider_name} بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف مزود التأمين: {str(e)}')

    return redirect('insurance:provider_list')


# إدارة التأمين الصحي للموظفين
@login_required
def health_insurance_list(request):
    """قائمة التأمينات الصحية للموظفين"""
    insurances = EmployeeHealthInsurance.objects.select_related('emp', 'provider').all()

    # البحث والفلترة
    search = request.GET.get('search')
    if search:
        insurances = insurances.filter(
            Q(emp__first_name__icontains=search) |
            Q(emp__last_name__icontains=search) |
            Q(emp__emp_code__icontains=search) |
            Q(policy_no__icontains=search)
        )

    # فلترة حسب المزود
    provider = request.GET.get('provider')
    if provider:
        insurances = insurances.filter(provider_id=provider)

    # فلترة حسب الحالة
    status = request.GET.get('status')
    today = date.today()
    if status == 'active':
        insurances = insurances.filter(end_date__gte=today)
    elif status == 'expired':
        insurances = insurances.filter(end_date__lt=today)
    elif status == 'expiring_soon':
        insurances = insurances.filter(
            end_date__gte=today,
            end_date__lte=today + timedelta(days=30)
        )

    # ترتيب النتائج
    insurances = insurances.order_by('-start_date')

    # التقسيم إلى صفحات
    paginator = Paginator(insurances, 20)
    page_number = request.GET.get('page')
    insurances = paginator.get_page(page_number)

    # قوائم للفلترة
    providers = HealthInsuranceProvider.objects.all().order_by('provider_name')

    context = {
        'insurances': insurances,
        'providers': providers,
    }

    return render(request, 'insurance/health_insurance_list.html', context)


@login_required
def add_health_insurance(request):
    """إضافة تأمين صحي جديد"""
    if request.method == 'POST':
        form = EmployeeHealthInsuranceForm(request.POST)
        if form.is_valid():
            insurance = form.save()
            messages.success(request, f'تم إضافة التأمين الصحي للموظف {insurance.emp.first_name} {insurance.emp.last_name} بنجاح.')
            return redirect('insurance:health_insurance_detail', insurance_id=insurance.ins_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeHealthInsuranceForm()

    context = {
        'form': form,
        'title': 'إضافة تأمين صحي جديد'
    }

    return render(request, 'insurance/health_insurance_form.html', context)


@login_required
def health_insurance_detail(request, insurance_id):
    """تفاصيل التأمين الصحي"""
    insurance = get_object_or_404(EmployeeHealthInsurance, ins_id=insurance_id)

    # حساب المدة المتبقية
    days_remaining = None
    if insurance.end_date:
        days_remaining = (insurance.end_date - date.today()).days

    # حساب إجمالي التكلفة
    total_cost = 0
    if insurance.premium and insurance.start_date and insurance.end_date:
        months = ((insurance.end_date.year - insurance.start_date.year) * 12 +
                 insurance.end_date.month - insurance.start_date.month)
        total_cost = insurance.premium * months

    context = {
        'insurance': insurance,
        'days_remaining': days_remaining,
        'total_cost': total_cost,
    }

    return render(request, 'insurance/health_insurance_detail.html', context)


@login_required
def edit_health_insurance(request, insurance_id):
    """تعديل التأمين الصحي"""
    insurance = get_object_or_404(EmployeeHealthInsurance, ins_id=insurance_id)

    if request.method == 'POST':
        form = EmployeeHealthInsuranceForm(request.POST, instance=insurance)
        if form.is_valid():
            insurance = form.save()
            messages.success(request, f'تم تحديث التأمين الصحي للموظف {insurance.emp.first_name} {insurance.emp.last_name} بنجاح.')
            return redirect('insurance:health_insurance_detail', insurance_id=insurance.ins_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeHealthInsuranceForm(instance=insurance)

    context = {
        'form': form,
        'insurance': insurance,
        'title': 'تعديل التأمين الصحي'
    }

    return render(request, 'insurance/health_insurance_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_health_insurance(request, insurance_id):
    """حذف التأمين الصحي"""
    insurance = get_object_or_404(EmployeeHealthInsurance, ins_id=insurance_id)

    try:
        insurance.delete()
        messages.success(request, f'تم حذف التأمين الصحي للموظف {insurance.emp.first_name} {insurance.emp.last_name} بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف التأمين الصحي: {str(e)}')

    return redirect('insurance:health_insurance_list')


# إدارة التأمين الاجتماعي (GOSI)
@login_required
def social_insurance_list(request):
    """قائمة التأمينات الاجتماعية للموظفين"""
    insurances = EmployeeSocialInsurance.objects.select_related('emp').all()

    # البحث والفلترة
    search = request.GET.get('search')
    if search:
        insurances = insurances.filter(
            Q(emp__first_name__icontains=search) |
            Q(emp__last_name__icontains=search) |
            Q(emp__emp_code__icontains=search) |
            Q(gosi_no__icontains=search)
        )

    # فلترة حسب الحالة
    status = request.GET.get('status')
    today = date.today()
    if status == 'active':
        insurances = insurances.filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        )
    elif status == 'expired':
        insurances = insurances.filter(end_date__lt=today)

    # ترتيب النتائج
    insurances = insurances.order_by('-start_date')

    # التقسيم إلى صفحات
    paginator = Paginator(insurances, 20)
    page_number = request.GET.get('page')
    insurances = paginator.get_page(page_number)

    context = {
        'insurances': insurances,
    }

    return render(request, 'insurance/social_insurance_list.html', context)


@login_required
def add_social_insurance(request):
    """إضافة تأمين اجتماعي جديد"""
    if request.method == 'POST':
        form = EmployeeSocialInsuranceForm(request.POST)
        if form.is_valid():
            insurance = form.save()
            messages.success(request, f'تم إضافة التأمين الاجتماعي للموظف {insurance.emp.first_name} {insurance.emp.last_name} بنجاح.')
            return redirect('insurance:social_insurance_detail', insurance_id=insurance.social_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeSocialInsuranceForm()

    context = {
        'form': form,
        'title': 'إضافة تأمين اجتماعي جديد'
    }

    return render(request, 'insurance/social_insurance_form.html', context)


@login_required
def social_insurance_detail(request, insurance_id):
    """تفاصيل التأمين الاجتماعي"""
    insurance = get_object_or_404(EmployeeSocialInsurance, social_id=insurance_id)

    # حساب إجمالي المساهمات
    total_contribution = 0
    if insurance.contribution and insurance.start_date:
        end_date = insurance.end_date or date.today()
        months = ((end_date.year - insurance.start_date.year) * 12 +
                 end_date.month - insurance.start_date.month)
        total_contribution = insurance.contribution * months

    context = {
        'insurance': insurance,
        'total_contribution': total_contribution,
    }

    return render(request, 'insurance/social_insurance_detail.html', context)


@login_required
def edit_social_insurance(request, insurance_id):
    """تعديل التأمين الاجتماعي"""
    insurance = get_object_or_404(EmployeeSocialInsurance, social_id=insurance_id)

    if request.method == 'POST':
        form = EmployeeSocialInsuranceForm(request.POST, instance=insurance)
        if form.is_valid():
            insurance = form.save()
            messages.success(request, f'تم تحديث التأمين الاجتماعي للموظف {insurance.emp.first_name} {insurance.emp.last_name} بنجاح.')
            return redirect('insurance:social_insurance_detail', insurance_id=insurance.social_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeSocialInsuranceForm(instance=insurance)

    context = {
        'form': form,
        'insurance': insurance,
        'title': 'تعديل التأمين الاجتماعي'
    }

    return render(request, 'insurance/social_insurance_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_social_insurance(request, insurance_id):
    """حذف التأمين الاجتماعي"""
    insurance = get_object_or_404(EmployeeSocialInsurance, social_id=insurance_id)

    try:
        insurance.delete()
        messages.success(request, f'تم حذف التأمين الاجتماعي للموظف {insurance.emp.first_name} {insurance.emp.last_name} بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف التأمين الاجتماعي: {str(e)}')

    return redirect('insurance:social_insurance_list')


# التقارير
@login_required
def reports(request):
    """تقارير التأمينات"""
    today = date.today()

    # إحصائيات عامة
    total_health_insurance = EmployeeHealthInsurance.objects.count()
    active_health_insurance = EmployeeHealthInsurance.objects.filter(
        end_date__gte=today
    ).count()
    total_social_insurance = EmployeeSocialInsurance.objects.count()

    # إجمالي الأقساط والمساهمات
    health_premiums = EmployeeHealthInsurance.objects.filter(
        end_date__gte=today
    ).aggregate(
        total_premium=Sum('premium')
    )['total_premium'] or 0

    social_contributions = EmployeeSocialInsurance.objects.filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    ).aggregate(
        total_contribution=Sum('contribution')
    )['total_contribution'] or 0

    # إحصائيات مزودي التأمين
    provider_stats = HealthInsuranceProvider.objects.annotate(
        policy_count=Count('employeehealthinsurance'),
        active_policies=Count('employeehealthinsurance',
                            filter=Q(employeehealthinsurance__end_date__gte=today)),
        total_premium=Sum('employeehealthinsurance__premium')
    ).order_by('-policy_count')

    # التأمينات المنتهية الصلاحية قريباً
    expiring_soon = EmployeeHealthInsurance.objects.filter(
        end_date__gte=today,
        end_date__lte=today + timedelta(days=30)
    ).count()

    # إحصائيات الأقسام
    department_stats = Department.objects.annotate(
        health_count=Count('employee__employeehealthinsurance'),
        social_count=Count('employee__employeesocialinsurance'),
        total_premium=Sum('employee__employeehealthinsurance__premium')
    ).filter(
        Q(health_count__gt=0) | Q(social_count__gt=0)
    ).order_by('-total_premium')

    context = {
        'total_health_insurance': total_health_insurance,
        'active_health_insurance': active_health_insurance,
        'total_social_insurance': total_social_insurance,
        'health_premiums': health_premiums,
        'social_contributions': social_contributions,
        'provider_stats': provider_stats,
        'expiring_soon': expiring_soon,
        'department_stats': department_stats,
    }

    return render(request, 'insurance/reports.html', context)


@login_required
def export_insurance(request):
    """تصدير بيانات التأمينات"""
    import csv

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="insurance.csv"'

    writer = csv.writer(response)
    writer.writerow(['الموظف', 'نوع التأمين', 'المزود/رقم GOSI', 'رقم البوليصة', 'تاريخ البداية', 'تاريخ النهاية', 'القسط/المساهمة'])

    # التأمين الصحي
    health_insurances = EmployeeHealthInsurance.objects.select_related('emp', 'provider').all()
    for insurance in health_insurances:
        writer.writerow([
            f"{insurance.emp.first_name} {insurance.emp.last_name}",
            'تأمين صحي',
            insurance.provider.provider_name if insurance.provider else '',
            insurance.policy_no or '',
            insurance.start_date or '',
            insurance.end_date or '',
            insurance.premium or 0
        ])

    # التأمين الاجتماعي
    social_insurances = EmployeeSocialInsurance.objects.select_related('emp').all()
    for insurance in social_insurances:
        writer.writerow([
            f"{insurance.emp.first_name} {insurance.emp.last_name}",
            'تأمين اجتماعي (GOSI)',
            insurance.gosi_no or '',
            '',
            insurance.start_date or '',
            insurance.end_date or '',
            insurance.contribution or 0
        ])

    return response


# بوابة الموظف
@login_required
def my_insurance(request):
    """تأميناتي الشخصية"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'لا يمكن الوصول لهذه الصفحة.')
        return redirect('insurance:dashboard')

    employee = request.user.employee

    # التأمين الصحي
    health_insurance = EmployeeHealthInsurance.objects.filter(
        emp=employee
    ).select_related('provider').order_by('-start_date').first()

    # التأمين الاجتماعي
    social_insurance = EmployeeSocialInsurance.objects.filter(
        emp=employee
    ).order_by('-start_date').first()

    context = {
        'employee': employee,
        'health_insurance': health_insurance,
        'social_insurance': social_insurance,
    }

    return render(request, 'insurance/my_insurance.html', context)


# AJAX Views
@login_required
def check_insurance_status(request, emp_id):
    """فحص حالة تأمين الموظف عبر AJAX"""
    try:
        employee = Employee.objects.get(emp_id=emp_id)
        today = date.today()

        # التأمين الصحي
        health_insurance = EmployeeHealthInsurance.objects.filter(
            emp=employee
        ).order_by('-start_date').first()

        health_status = 'غير مؤمن'
        if health_insurance:
            if health_insurance.end_date and health_insurance.end_date >= today:
                health_status = 'نشط'
            elif health_insurance.end_date and health_insurance.end_date < today:
                health_status = 'منتهي الصلاحية'
            else:
                health_status = 'نشط'

        # التأمين الاجتماعي
        social_insurance = EmployeeSocialInsurance.objects.filter(
            emp=employee
        ).order_by('-start_date').first()

        social_status = 'غير مؤمن'
        if social_insurance:
            if social_insurance.end_date and social_insurance.end_date >= today:
                social_status = 'نشط'
            elif social_insurance.end_date and social_insurance.end_date < today:
                social_status = 'منتهي الصلاحية'
            else:
                social_status = 'نشط'

        data = {
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'health_status': health_status,
            'social_status': social_status,
            'health_provider': health_insurance.provider.provider_name if health_insurance and health_insurance.provider else None,
            'health_policy': health_insurance.policy_no if health_insurance else None,
            'gosi_number': social_insurance.gosi_no if social_insurance else None
        }

        return JsonResponse(data)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'الموظف غير موجود'}, status=404)


@login_required
def insurance_expiry_alerts(request):
    """تنبيهات انتهاء صلاحية التأمين"""
    today = date.today()

    # التأمينات المنتهية الصلاحية خلال فترات مختلفة
    alerts = {
        'expired': EmployeeHealthInsurance.objects.filter(
            end_date__lt=today
        ).select_related('emp', 'provider').order_by('end_date'),

        'expiring_week': EmployeeHealthInsurance.objects.filter(
            end_date__gte=today,
            end_date__lte=today + timedelta(days=7)
        ).select_related('emp', 'provider').order_by('end_date'),

        'expiring_month': EmployeeHealthInsurance.objects.filter(
            end_date__gte=today + timedelta(days=8),
            end_date__lte=today + timedelta(days=30)
        ).select_related('emp', 'provider').order_by('end_date'),

        'expiring_quarter': EmployeeHealthInsurance.objects.filter(
            end_date__gte=today + timedelta(days=31),
            end_date__lte=today + timedelta(days=90)
        ).select_related('emp', 'provider').order_by('end_date')
    }

    context = {
        'alerts': alerts,
        'today': today,
    }

    return render(request, 'insurance/expiry_alerts.html', context)


# Bulk Operations
@login_required
def bulk_renew_insurance(request):
    """تجديد التأمينات بالجملة"""
    if request.method == 'POST':
        insurance_ids = request.POST.getlist('insurance_ids')
        renewal_months = int(request.POST.get('renewal_months', 12))

        if insurance_ids:
            renewed_count = 0
            for ins_id in insurance_ids:
                try:
                    insurance = EmployeeHealthInsurance.objects.get(ins_id=ins_id)
                    # تجديد التأمين
                    new_start_date = insurance.end_date + timedelta(days=1) if insurance.end_date else date.today()
                    new_end_date = new_start_date + timedelta(days=renewal_months * 30)

                    EmployeeHealthInsurance.objects.create(
                        emp=insurance.emp,
                        provider=insurance.provider,
                        policy_no=insurance.policy_no,
                        start_date=new_start_date,
                        end_date=new_end_date,
                        premium=insurance.premium,
                        dependents=insurance.dependents
                    )
                    renewed_count += 1
                except EmployeeHealthInsurance.DoesNotExist:
                    continue

            messages.success(request, f'تم تجديد {renewed_count} تأمين بنجاح.')
        else:
            messages.warning(request, 'لم يتم تحديد أي تأمينات.')

    return redirect('insurance:health_insurance_list')


@login_required
def bulk_import_insurance(request):
    """استيراد التأمينات بالجملة"""
    if request.method == 'POST':
        # معالجة ملف الاستيراد
        pass

    return render(request, 'insurance/bulk_import.html')


# Analytics
@login_required
def insurance_analytics(request):
    """تحليلات التأمينات"""
    today = date.today()

    # توزيع التأمينات حسب المزودين
    provider_distribution = HealthInsuranceProvider.objects.annotate(
        policy_count=Count('employeehealthinsurance'),
        active_policies=Count('employeehealthinsurance',
                            filter=Q(employeehealthinsurance__end_date__gte=today)),
        total_premium=Sum('employeehealthinsurance__premium')
    ).order_by('-policy_count')

    # اتجاهات التكلفة الشهرية
    monthly_costs = EmployeeHealthInsurance.objects.filter(
        end_date__gte=today
    ).extra(
        select={'month': "MONTH(start_date)", 'year': "YEAR(start_date)"}
    ).values('month', 'year').annotate(
        total_premium=Sum('premium'),
        policy_count=Count('ins_id')
    ).order_by('year', 'month')

    # توزيع التأمينات حسب الأقسام
    department_distribution = Department.objects.annotate(
        health_insurance_count=Count('employee__employeehealthinsurance'),
        social_insurance_count=Count('employee__employeesocialinsurance'),
        total_premium=Sum('employee__employeehealthinsurance__premium')
    ).filter(
        Q(health_insurance_count__gt=0) | Q(social_insurance_count__gt=0)
    ).order_by('-total_premium')

    context = {
        'provider_distribution': provider_distribution,
        'monthly_costs': monthly_costs,
        'department_distribution': department_distribution,
    }

    return render(request, 'insurance/insurance_analytics.html', context)
