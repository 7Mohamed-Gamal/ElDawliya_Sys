from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from Hr.models.insurance_models import JobInsurance
from Hr.forms.insurance_forms import JobInsuranceForm

@login_required
def insurance_job_list(request):
    """عرض قائمة وظائف التأمين"""
    insurance_jobs = JobInsurance.objects.all().order_by('job_name_insurance')
    
    context = {
        'insurance_jobs': insurance_jobs,
        'title': 'وظائف التأمين'
    }
    
    return render(request, 'Hr/insurance_jobs/list.html', context)

@login_required
def insurance_job_create(request):
    """إنشاء وظيفة تأمين جديدة"""
    if request.method == 'POST':
        form = JobInsuranceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء وظيفة التأمين بنجاح')
            return redirect('Hr:insurance_jobs:list')
    else:
        form = JobInsuranceForm()
    
    context = {
        'form': form,
        'title': 'إنشاء وظيفة تأمين جديدة'
    }
    
    return render(request, 'Hr/insurance_jobs/create.html', context)

@login_required
def insurance_job_detail(request, job_code_insurance):
    """عرض تفاصيل وظيفة تأمين"""
    insurance_job = get_object_or_404(JobInsurance, job_code_insurance=job_code_insurance)
    
    # Get employees with this insurance job
    employees = insurance_job.employee_set.all()
    
    context = {
        'insurance_job': insurance_job,
        'employees': employees,
        'title': f'تفاصيل وظيفة التأمين: {insurance_job.job_name_insurance}'
    }
    
    return render(request, 'Hr/insurance_jobs/detail.html', context)

@login_required
def insurance_job_edit(request, job_code_insurance):
    """تعديل وظيفة تأمين"""
    insurance_job = get_object_or_404(JobInsurance, job_code_insurance=job_code_insurance)
    
    if request.method == 'POST':
        form = JobInsuranceForm(request.POST, instance=insurance_job)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل وظيفة التأمين بنجاح')
            return redirect('Hr:insurance_jobs:detail', job_code_insurance=insurance_job.job_code_insurance)
    else:
        form = JobInsuranceForm(instance=insurance_job)
    
    context = {
        'form': form,
        'insurance_job': insurance_job,
        'title': f'تعديل وظيفة التأمين: {insurance_job.job_name_insurance}'
    }
    
    return render(request, 'Hr/insurance_jobs/edit.html', context)

@login_required
def insurance_job_delete(request, job_code_insurance):
    """حذف وظيفة تأمين"""
    insurance_job = get_object_or_404(JobInsurance, job_code_insurance=job_code_insurance)
    
    if request.method == 'POST':
        insurance_job.delete()
        messages.success(request, 'تم حذف وظيفة التأمين بنجاح')
        return redirect('Hr:insurance_jobs:list')
    
    context = {
        'insurance_job': insurance_job,
        'title': f'حذف وظيفة التأمين: {insurance_job.job_name_insurance}'
    }
    
    return render(request, 'Hr/insurance_jobs/delete.html', context)
