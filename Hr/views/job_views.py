from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from Hr.models.job_models import Job
from Hr.forms.employee_forms import JobForm
from Hr.decorators import hr_module_permission_required

@login_required
@hr_module_permission_required('jobs', 'view')
def job_list(request):
    """عرض قائمة الوظائف"""
    jobs = Job.objects.all()

    context = {
        'jobs': jobs,
        'title': 'قائمة الوظائف'
    }

    return render(request, 'Hr/jobs/job_list.html', context)

@login_required
@hr_module_permission_required('jobs', 'add')
def job_create(request):
    """إنشاء وظيفة جديدة"""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء الوظيفة بنجاح')
            return redirect('Hr:jobs:list')
    else:
        form = JobForm()

    context = {
        'form': form,
        'title': 'إنشاء وظيفة جديدة'
    }

    return render(request, 'Hr/jobs/create.html', context)

@login_required
@hr_module_permission_required('jobs', 'view')
def job_detail(request, jop_code):
    """عرض تفاصيل وظيفة"""
    job = get_object_or_404(Job, jop_code=jop_code)

    # Get employees with this job code
    from Hr.models.employee_model import Employee
    employees = Employee.objects.filter(jop_code=jop_code)

    context = {
        'job': job,
        'employees': employees,
        'title': f'تفاصيل الوظيفة: {job.jop_name}'
    }

    return render(request, 'Hr/jobs/detail.html', context)

@login_required
@hr_module_permission_required('jobs', 'edit')
def job_edit(request, jop_code):
    """تعديل وظيفة"""
    job = get_object_or_404(Job, jop_code=jop_code)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الوظيفة بنجاح')
            return redirect('Hr:jobs:detail', jop_code=job.jop_code)
    else:
        form = JobForm(instance=job)

    context = {
        'form': form,
        'job': job,
        'title': f'تعديل الوظيفة: {job.jop_name}'
    }

    return render(request, 'Hr/jobs/edit.html', context)

@login_required
@hr_module_permission_required('jobs', 'delete')
def job_delete(request, jop_code):
    """حذف وظيفة"""
    job = get_object_or_404(Job, jop_code=jop_code)

    # Import Employee model
    from Hr.models.employee_model import Employee

    if request.method == 'POST':
        # Check if there are any employees with this job
        if Employee.objects.filter(jop_code=jop_code).exists():
            messages.error(request, 'لا يمكن حذف الوظيفة لأنها مرتبطة بموظفين')
            return redirect('Hr:jobs:detail', jop_code=job.jop_code)

        job.delete()
        messages.success(request, 'تم حذف الوظيفة بنجاح')
        return redirect('Hr:jobs:list')

    # Get employees with this job for the template
    employees = Employee.objects.filter(jop_code=jop_code)

    context = {
        'job': job,
        'employees': employees,
        'title': f'حذف الوظيفة: {job.jop_name}'
    }

    return render(request, 'Hr/jobs/delete.html', context)
