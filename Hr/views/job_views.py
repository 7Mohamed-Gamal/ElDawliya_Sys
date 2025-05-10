from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from Hr.models.job_models import Job
from Hr.forms.employee_forms import JobForm
from Hr.decorators import hr_module_permission_required

@login_required
@hr_module_permission_required('jobs', 'view')
def job_list(request):
    """عرض قائمة الوظائف"""
    # Import Employee model
    from Hr.models.employee_model import Employee
    from django.db.models import Count

    # Get all jobs
    jobs = Job.objects.all()

    # Create a dictionary to store employee counts for each job
    # This is more efficient than making a separate query for each job
    employee_counts = {}
    for emp in Employee.objects.values('jop_code').annotate(count=Count('emp_id')):
        if emp['jop_code'] is not None:
            employee_counts[emp['jop_code']] = emp['count']

    # Add employee_count attribute to each job object
    for job in jobs:
        job.employee_count = employee_counts.get(job.jop_code, 0)

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
            try:
                # If job code is not provided, generate it automatically
                if not form.cleaned_data.get('jop_code'):
                    # Get the highest job code
                    max_job = Job.objects.all().order_by('-jop_code').first()
                    # If there are no jobs, start with 1, otherwise increment the highest code
                    next_code = 1 if not max_job else max_job.jop_code + 1
                    form.instance.jop_code = next_code
                    print(f"Auto-generated job code: {next_code}")
                else:
                    print(f"Using provided job code: {form.cleaned_data.get('jop_code')}")

                job = form.save()
                print(f"Job saved with code: {job.jop_code}")
                messages.success(request, f'تم إنشاء الوظيفة بنجاح برمز {job.jop_code}')
                return redirect('Hr:jobs:list')
            except Exception as e:
                print(f"Error saving job: {str(e)}")
                messages.error(request, f'حدث خطأ أثناء حفظ الوظيفة: {str(e)}')
    else:
        # عند تحميل الصفحة، قم بإنشاء نموذج فارغ
        form = JobForm()
        # احصل على الرمز التالي للوظيفة
        max_job = Job.objects.all().order_by('-jop_code').first()
        next_code = 1 if not max_job else max_job.jop_code + 1
        print(f"Initial job code for form: {next_code}")

    context = {
        'form': form,
        'title': 'إنشاء وظيفة جديدة',
        'next_job_code': next_code if 'next_code' in locals() else None
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

@login_required
def get_next_job_code(request):
    """Get the next available job code"""
    try:
        # Get the highest job code
        max_job = Job.objects.all().order_by('-jop_code').first()

        # If there are no jobs, start with 1, otherwise increment the highest code
        next_code = 1 if not max_job else max_job.jop_code + 1

        print(f"Generated next job code: {next_code}")
        return JsonResponse({'next_code': next_code})
    except Exception as e:
        print(f"Error generating job code: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
