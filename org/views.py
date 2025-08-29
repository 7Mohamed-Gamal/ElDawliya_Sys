from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Department, Job, Branch


@login_required
def index(request):
    """الصفحة الرئيسية للتنظيم"""
    context = {
        'total_departments': Department.objects.filter(is_active=True).count(),
        'total_jobs': Job.objects.filter(is_active=True).count(),
        'total_branches': Branch.objects.filter(is_active=True).count(),
    }
    return render(request, 'org/index.html', context)


@login_required
def departments(request):
    """قائمة الأقسام"""
    departments_list = Department.objects.select_related('branch', 'parent_dept').filter(is_active=True)

    # البحث
    search = request.GET.get('search')
    if search:
        departments_list = departments_list.filter(
            Q(dept_name__icontains=search) |
            Q(branch__branch_name__icontains=search)
        )

    # التصفح
    paginator = Paginator(departments_list, 20)
    page_number = request.GET.get('page')
    departments_page = paginator.get_page(page_number)

    context = {
        'departments': departments_page,
        'search': search,
        'title': 'الأقسام'
    }
    return render(request, 'org/departments.html', context)


@login_required
def department_detail(request, dept_id):
    """تفاصيل القسم"""
    department = get_object_or_404(Department, dept_id=dept_id)

    # الأقسام الفرعية
    sub_departments = Department.objects.filter(parent_dept=department, is_active=True)

    # عدد الموظفين في القسم
    employees_count = department.employee_set.filter(is_active=True).count()

    context = {
        'department': department,
        'sub_departments': sub_departments,
        'employees_count': employees_count,
        'title': f'تفاصيل القسم - {department.dept_name}'
    }
    return render(request, 'org/department_detail.html', context)


@login_required
def jobs(request):
    """قائمة الوظائف"""
    jobs_list = Job.objects.filter(is_active=True).order_by('job_title')

    # البحث
    search = request.GET.get('search')
    if search:
        jobs_list = jobs_list.filter(
            Q(job_title__icontains=search) |
            Q(description__icontains=search)
        )

    # التصفح
    paginator = Paginator(jobs_list, 20)
    page_number = request.GET.get('page')
    jobs_page = paginator.get_page(page_number)

    context = {
        'jobs': jobs_page,
        'search': search,
        'title': 'الوظائف'
    }
    return render(request, 'org/jobs.html', context)


@login_required
def job_detail(request, job_id):
    """تفاصيل الوظيفة"""
    job = get_object_or_404(Job, job_id=job_id)

    # عدد الموظفين في هذه الوظيفة
    employees_count = job.employee_set.filter(is_active=True).count()

    context = {
        'job': job,
        'employees_count': employees_count,
        'title': f'تفاصيل الوظيفة - {job.job_title}'
    }
    return render(request, 'org/job_detail.html', context)


@login_required
def branches(request):
    """قائمة الأفرع"""
    branches_list = Branch.objects.select_related('company').filter(is_active=True)

    # البحث
    search = request.GET.get('search')
    if search:
        branches_list = branches_list.filter(
            Q(branch_name__icontains=search) |
            Q(branch_address__icontains=search)
        )

    # التصفح
    paginator = Paginator(branches_list, 20)
    page_number = request.GET.get('page')
    branches_page = paginator.get_page(page_number)

    context = {
        'branches': branches_page,
        'search': search,
        'title': 'الأفرع'
    }
    return render(request, 'org/branches.html', context)
