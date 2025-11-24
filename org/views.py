from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django import forms
from .models import Department, Job, Branch
from companies.models import Company


class DepartmentForm(forms.ModelForm):
    """DepartmentForm class"""
    class Meta:
        """Meta class"""
        model = Department
        fields = ['dept_name', 'parent_dept', 'branch', 'manager_id']
        widgets = {
            'dept_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم القسم'
            }),
            'parent_dept': forms.Select(attrs={
                'class': 'form-control'
            }),
            'branch': forms.Select(attrs={
                'class': 'form-control'
            }),
            'manager_id': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'معرف المدير (اختياري)'
            }),
        }
        labels = {
            'dept_name': 'اسم القسم',
            'parent_dept': 'القسم الأب',
            'branch': 'الفرع',
            'manager_id': 'معرف المدير',
        }


class JobForm(forms.ModelForm):
    """JobForm class"""
    class Meta:
        """Meta class"""
        model = Job
        fields = ['job_title', 'job_level', 'basic_salary', 'description']
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان الوظيفة'
            }),
            'job_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مستوى الوظيفة (اختياري)'
            }),
            'basic_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'الراتب الأساسي (اختياري)',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'وصف الوظيفة (اختياري)',
                'rows': 3
            }),
        }
        labels = {
            'job_title': 'عنوان الوظيفة',
            'job_level': 'مستوى الوظيفة',
            'basic_salary': 'الراتب الأساسي',
            'description': 'الوصف',
        }


class BranchForm(forms.ModelForm):
    """BranchForm class"""
    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)
        # Only show active companies in the dropdown
        self.fields['company'].queryset = Company.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('name')
        # Make company field required
        self.fields['company'].required = True
        # Add empty label for company dropdown
        self.fields['company'].empty_label = "اختر الشركة"

    class Meta:
        """Meta class"""
        model = Branch
        fields = ['branch_name', 'branch_address', 'phone', 'company', 'manager_id']
        widgets = {
            'branch_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الفرع',
                'required': True
            }),
            'branch_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان الفرع',
                'rows': 3
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف'
            }),
            'company': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'manager_id': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'معرف المدير (اختياري)'
            }),
        }
        labels = {
            'branch_name': 'اسم الفرع',
            'branch_address': 'العنوان',
            'phone': 'رقم الهاتف',
            'company': 'الشركة',
            'manager_id': 'معرف المدير',
        }

    def clean_branch_name(self):
        """clean_branch_name function"""
        branch_name = self.cleaned_data.get('branch_name', '').strip()
        if not branch_name:
            raise forms.ValidationError('اسم الفرع مطلوب')
        return branch_name

    def clean_company(self):
        """clean_company function"""
        company = self.cleaned_data.get('company')
        if not company:
            raise forms.ValidationError('يجب اختيار شركة')
        if not company.is_active:
            raise forms.ValidationError('الشركة المختارة غير نشطة')
        return company


@login_required
def index(request):
    """الصفحة الرئيسية للتنظيم"""
    context = {
        'total_departments': Department.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count(),
        'total_jobs': Job.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count(),
        'total_branches': Branch.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count(),
    }
    return render(request, 'org/index.html', context)


@login_required
def departments(request):
    """قائمة الأقسام"""
    # Optimize query with select_related and annotate for employee count
    departments_list = Department.objects.select_related(
        'branch', 'parent_dept'
    ).annotate(
        employee_count=Count('employee', filter=Q(employee__emp_status='Active'), distinct=True)
    ).filter(is_active=True)

    # البحث
    search = request.GET.get('search')
    if search:
        departments_list = departments_list.filter(
            Q(dept_name__icontains=search) |
            Q(branch__branch_name__icontains=search)
        )

    # ترتيب النتائج
    departments_list = departments_list.order_by('dept_name')

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
def department_add(request):
    """إضافة قسم جديد"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'تم إضافة القسم "{department.dept_name}" بنجاح.')
            return redirect('org:departments')
    else:
        form = DepartmentForm()

    context = {
        'form': form,
        'title': 'إضافة قسم جديد'
    }
    return render(request, 'org/department_add.html', context)


@login_required
def department_edit(request, dept_id):
    """تعديل القسم"""
    department = get_object_or_404(Department, dept_id=dept_id)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'تم تعديل القسم "{department.dept_name}" بنجاح.')
            return redirect('org:department_detail', dept_id=department.dept_id)
    else:
        form = DepartmentForm(instance=department)

    context = {
        'form': form,
        'department': department,
        'title': f'تعديل القسم - {department.dept_name}'
    }
    return render(request, 'org/department_edit.html', context)


@login_required
def department_detail(request, dept_id):
    """تفاصيل القسم"""
    department = get_object_or_404(Department, dept_id=dept_id)

    # الأقسام الفرعية
    sub_departments = Department.objects.filter(parent_dept=department, is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields

    # عدد الموظفين في القسم
    employees_count = department.employee_set.filter(emp_status='Active').count()

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
    # Optimize query with annotate for employee count
    jobs_list = Job.objects.annotate(
        employee_count=Count('employee', filter=Q(employee__emp_status='Active'), distinct=True)
    ).filter(is_active=True).order_by('job_title')

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
def job_add(request):
    """إضافة وظيفة جديدة"""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save()
            messages.success(request, f'تم إضافة الوظيفة "{job.job_title}" بنجاح.')
            return redirect('org:jobs')
    else:
        form = JobForm()

    context = {
        'form': form,
        'title': 'إضافة وظيفة جديدة'
    }
    return render(request, 'org/job_add.html', context)


@login_required
def job_detail(request, job_id):
    """تفاصيل الوظيفة"""
    job = get_object_or_404(Job, job_id=job_id)

    # عدد الموظفين في هذه الوظيفة
    employees_count = job.employee_set.filter(emp_status='Active').count()

    context = {
        'job': job,
        'employees_count': employees_count,
        'title': f'تفاصيل الوظيفة - {job.job_title}'
    }
    return render(request, 'org/job_detail.html', context)


@login_required
def branches(request):
    """قائمة الأفرع"""
    branches_list = Branch.objects.select_related('company').annotate(
        department_count=Count('department', distinct=True)
    ).filter(is_active=True)

    # البحث
    search = request.GET.get('search')
    if search:
        branches_list = branches_list.filter(
            Q(branch_name__icontains=search) |
            Q(branch_address__icontains=search)
        )

    # ترتيب النتائج
    branches_list = branches_list.order_by('branch_name')

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


@login_required
def branch_add(request):
    """إضافة فرع جديد"""
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            branch = form.save()
            messages.success(request, f'تم إضافة الفرع "{branch.branch_name}" بنجاح.')
            return redirect('org:branches')
    else:
        form = BranchForm()

    context = {
        'form': form,
        'title': 'إضافة فرع جديد'
    }
    return render(request, 'org/branch_add.html', context)


@login_required
def branch_detail(request, branch_id):
    """تفاصيل الفرع"""
    branch = get_object_or_404(Branch, branch_id=branch_id)

    # الأقسام التابعة للفرع
    departments = Department.objects.filter(branch=branch, is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields

    context = {
        'branch': branch,
        'departments': departments,
        'title': f'تفاصيل الفرع - {branch.branch_name}'
    }
    return render(request, 'org/branch_detail.html', context)
