"""
Function-based views for Company management
These views provide the actual implementation for company, branch, department, and job position management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _

# Import models - use what's available
try:
    from Hr.models import Company, Branch, Department as NewDepartment, JobPosition
    MODELS_AVAILABLE = True
except ImportError:
    # If new models aren't available, create placeholder functions
    MODELS_AVAILABLE = False
    Company = Branch = NewDepartment = JobPosition = None

# Use legacy models for compatibility
from Hr.models.legacy.legacy_models import LegacyDepartment as Department
from Hr.models.legacy_employee import LegacyEmployee as Employee

# Import forms - only import what works
try:
    from Hr.forms.company_forms import CompanyForm, BranchForm
    FORMS_AVAILABLE = True
except ImportError:
    FORMS_AVAILABLE = False
    CompanyForm = BranchForm = None

# For now, we'll use simple forms for Department and JobPosition
from django import forms

class SimpleDepartmentForm(forms.Form):
    """Simple form for department - placeholder"""
    name = forms.CharField(max_length=200, label='اسم القسم')

class SimpleJobPositionForm(forms.Form):
    """Simple form for job position - placeholder"""
    title = forms.CharField(max_length=200, label='المسمى الوظيفي')


def render_under_construction(request, title):
    """Helper function to render under construction page"""
    return render(request, 'Hr/under_construction.html', {'title': title})


# =============================================================================
# COMPANY VIEWS
# =============================================================================

@login_required
def company_list(request):
    """عرض قائمة الشركات"""
    if not MODELS_AVAILABLE:
        return render_under_construction(request, 'قائمة الشركات')
    
    try:
        # Get all companies with related data
        companies = Company.objects.annotate(
            branch_count=Count('branches', distinct=True),
            employee_count=Count('employees', distinct=True)
        ).order_by('name')
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            companies = companies.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(companies, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'companies': page_obj,
            'search_query': search_query,
            'title': 'قائمة الشركات',
            'total_companies': companies.count()
        }
        
        return render(request, 'Hr/company/company_list.html', context)
        
    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض قائمة الشركات: {str(e)}')
        return render(request, 'Hr/company/company_list.html', {
            'companies': [],
            'title': 'قائمة الشركات',
            'error': str(e)
        })


@login_required
def company_create(request):
    """إنشاء شركة جديدة"""
    if not MODELS_AVAILABLE or not FORMS_AVAILABLE:
        return render_under_construction(request, 'إضافة شركة جديدة')
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                company = form.save()
                messages.success(request, f'تم إنشاء الشركة "{company.name}" بنجاح')
                return redirect('companies:detail', company.id)
            except Exception as e:
                messages.error(request, f'حدث خطأ في إنشاء الشركة: {str(e)}')
    else:
        form = CompanyForm()
    
    context = {
        'form': form,
        'title': 'إضافة شركة جديدة',
        'is_edit': False
    }
    
    return render(request, 'Hr/company/company_form.html', context)


@login_required
def company_detail(request, company_id):
    """عرض تفاصيل الشركة"""
    if not MODELS_AVAILABLE:
        return render_under_construction(request, 'تفاصيل الشركة')
    
    try:
        company = get_object_or_404(Company, id=company_id)
        
        # Get company statistics
        branches = company.branches.all()
        departments = NewDepartment.objects.filter(company=company) if NewDepartment else []
        employees = company.employees.all()
        
        # Get recent employees (last 30 days)
        from datetime import datetime, timedelta
        recent_employees = employees.filter(
            created_at__gte=datetime.now() - timedelta(days=30)
        ).order_by('-created_at')[:5]
        
        context = {
            'company': company,
            'branches': branches,
            'departments': departments,
            'employees': employees,
            'recent_employees': recent_employees,
            'branch_count': branches.count(),
            'department_count': len(departments),
            'employee_count': employees.count(),
            'active_employee_count': employees.filter(status='active').count(),
            'title': f'تفاصيل الشركة: {company.name}'
        }
        
        return render(request, 'Hr/company/company_detail.html', context)
        
    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض تفاصيل الشركة: {str(e)}')
        return redirect('Hr:companies:list')


@login_required
def company_edit(request, company_id):
    """تعديل الشركة"""
    if not MODELS_AVAILABLE or not FORMS_AVAILABLE:
        return render_under_construction(request, 'تعديل الشركة')
    
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            try:
                company = form.save()
                messages.success(request, f'تم تحديث الشركة "{company.name}" بنجاح')
                return redirect('companies:detail', company.id)
            except Exception as e:
                messages.error(request, f'حدث خطأ في تحديث الشركة: {str(e)}')
    else:
        form = CompanyForm(instance=company)
    
    context = {
        'form': form,
        'company': company,
        'title': f'تعديل الشركة: {company.name}',
        'is_edit': True
    }
    
    return render(request, 'Hr/company/company_form.html', context)


@login_required
def company_delete(request, company_id):
    """حذف الشركة"""
    if not MODELS_AVAILABLE:
        return render_under_construction(request, 'حذف الشركة')
    
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        try:
            # Check if company has employees
            if company.employees.exists():
                messages.error(request, 'لا يمكن حذف الشركة لأنها تحتوي على موظفين')
                return redirect('companies:detail', company.id)
            
            company_name = company.name
            company.delete()
            messages.success(request, f'تم حذف الشركة "{company_name}" بنجاح')
            return redirect('companies:list')
            
        except Exception as e:
            messages.error(request, f'حدث خطأ في حذف الشركة: {str(e)}')
            return redirect('companies:detail', company.id)
    
    context = {
        'company': company,
        'title': f'حذف الشركة: {company.name}'
    }
    
    return render(request, 'Hr/company/company_delete.html', context)


@login_required
def company_toggle_status(request, company_id):
    """تغيير حالة الشركة (نشط/غير نشط)"""
    if not MODELS_AVAILABLE:
        messages.info(request, 'هذه الميزة قيد التطوير')
        return redirect('Hr:dashboard')
    
    company = get_object_or_404(Company, id=company_id)
    
    try:
        company.is_active = not company.is_active
        company.save()
        
        status_text = 'نشطة' if company.is_active else 'غير نشطة'
        messages.success(request, f'تم تغيير حالة الشركة إلى {status_text}')
        
    except Exception as e:
        messages.error(request, f'حدث خطأ في تغيير حالة الشركة: {str(e)}')
    
    return redirect('companies:detail', company.id)


@login_required
def company_dashboard(request, company_id):
    """لوحة تحكم الشركة"""
    if not MODELS_AVAILABLE:
        return render_under_construction(request, 'لوحة تحكم الشركة')
    
    # This is a placeholder for now - can be expanded later
    return redirect('companies:list')


@login_required
def company_export(request):
    """تصدير قائمة الشركات"""
    # Placeholder for export functionality
    messages.info(request, 'ميزة التصدير قيد التطوير')
    return redirect('companies:list')


@require_http_methods(["GET"])
def company_search_ajax(request):
    """البحث في الشركات عبر AJAX"""
    if not MODELS_AVAILABLE:
        return JsonResponse({'results': []})
    
    search_term = request.GET.get('term', '')
    
    companies = Company.objects.filter(
        Q(name__icontains=search_term) |
        Q(code__icontains=search_term)
    )[:10]
    
    results = [
        {
            'id': str(company.id),
            'text': company.name,
            'code': company.code
        }
        for company in companies
    ]
    
    return JsonResponse({'results': results})


@require_http_methods(["GET"])
def company_stats_ajax(request, company_id):
    """إحصائيات الشركة عبر AJAX"""
    if not MODELS_AVAILABLE:
        return JsonResponse({'success': False, 'error': 'Models not available'})
    
    try:
        company = get_object_or_404(Company, id=company_id)
        
        stats = {
            'branches': company.branches.count(),
            'departments': NewDepartment.objects.filter(company=company).count() if NewDepartment else 0,
            'employees': company.employees.count(),
            'active_employees': company.employees.filter(status='active').count()
        }
        
        return JsonResponse({'success': True, 'stats': stats})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# =============================================================================
# BRANCH VIEWS
# =============================================================================

@login_required
def branch_list(request):
    """عرض قائمة الفروع"""
    if not MODELS_AVAILABLE:
        return render_under_construction(request, 'قائمة الفروع')

    try:
        branches = Branch.objects.select_related('company').annotate(
            employee_count=Count('employees', distinct=True),
            department_count=Count('departments', distinct=True)
        ).order_by('company__name', 'name')

        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            branches = branches.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(company__name__icontains=search_query)
            )

        # Filter by company
        company_id = request.GET.get('company')
        if company_id:
            branches = branches.filter(company_id=company_id)

        # Pagination
        paginator = Paginator(branches, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get companies for filter dropdown
        companies = Company.objects.filter(is_active=True).order_by('name')

        context = {
            'branches': page_obj,
            'companies': companies,
            'search_query': search_query,
            'selected_company': company_id,
            'title': 'قائمة الفروع',
            'total_branches': branches.count()
        }

        return render(request, 'Hr/company/branch_list.html', context)

    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض قائمة الفروع: {str(e)}')
        return render(request, 'Hr/company/branch_list.html', {
            'branches': [],
            'companies': [],
            'title': 'قائمة الفروع',
            'error': str(e)
        })


@login_required
def branch_create(request):
    """إنشاء فرع جديد"""
    if not MODELS_AVAILABLE or not FORMS_AVAILABLE:
        return render_under_construction(request, 'إضافة فرع جديد')

    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            try:
                branch = form.save()
                messages.success(request, f'تم إنشاء الفرع "{branch.name}" بنجاح')
                return redirect('Hr:branches:detail', branch_id=branch.id)
            except Exception as e:
                messages.error(request, f'حدث خطأ في إنشاء الفرع: {str(e)}')
    else:
        form = BranchForm()

    context = {
        'form': form,
        'title': 'إضافة فرع جديد',
        'is_edit': False
    }

    return render(request, 'Hr/company/branch_form.html', context)


@login_required
def branch_detail(request, branch_id):
    """عرض تفاصيل الفرع"""
    if not MODELS_AVAILABLE:
        return render_under_construction(request, 'تفاصيل الفرع')

    try:
        branch = get_object_or_404(Branch, id=branch_id)

        # Get branch statistics
        departments = branch.departments.all()
        employees = branch.employees.all()

        context = {
            'branch': branch,
            'departments': departments,
            'employees': employees,
            'department_count': departments.count(),
            'employee_count': employees.count(),
            'active_employee_count': employees.filter(status='active').count(),
            'title': f'تفاصيل الفرع: {branch.name}'
        }

        return render(request, 'Hr/company/branch_detail.html', context)

    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض تفاصيل الفرع: {str(e)}')
        return redirect('Hr:branches:list')


@login_required
def branch_edit(request, branch_id):
    """تعديل الفرع"""
    if not MODELS_AVAILABLE or not FORMS_AVAILABLE:
        return render_under_construction(request, 'تعديل الفرع')

    branch = get_object_or_404(Branch, id=branch_id)

    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            try:
                branch = form.save()
                messages.success(request, f'تم تحديث الفرع "{branch.name}" بنجاح')
                return redirect('Hr:branches:detail', branch_id=branch.id)
            except Exception as e:
                messages.error(request, f'حدث خطأ في تحديث الفرع: {str(e)}')
    else:
        form = BranchForm(instance=branch)

    context = {
        'form': form,
        'branch': branch,
        'title': f'تعديل الفرع: {branch.name}',
        'is_edit': True
    }

    return render(request, 'Hr/company/branch_form.html', context)


@login_required
def branch_delete(request, branch_id):
    """حذف الفرع"""
    if not MODELS_AVAILABLE:
        return render_under_construction(request, 'حذف الفرع')

    branch = get_object_or_404(Branch, id=branch_id)

    if request.method == 'POST':
        try:
            # Check if branch has employees
            if branch.employees.exists():
                messages.error(request, 'لا يمكن حذف الفرع لأنه يحتوي على موظفين')
                return redirect('Hr:branches:detail', branch_id=branch.id)

            branch_name = branch.name
            company_id = branch.company.id
            branch.delete()
            messages.success(request, f'تم حذف الفرع "{branch_name}" بنجاح')
            return redirect('Hr:companies:detail', company_id=company_id)

        except Exception as e:
            messages.error(request, f'حدث خطأ في حذف الفرع: {str(e)}')
            return redirect('Hr:branches:detail', branch_id=branch.id)

    context = {
        'branch': branch,
        'title': f'حذف الفرع: {branch.name}'
    }

    return render(request, 'Hr/company/branch_delete.html', context)


@login_required
def branch_toggle_status(request, branch_id):
    """تغيير حالة الفرع (نشط/غير نشط)"""
    if not MODELS_AVAILABLE:
        messages.info(request, 'هذه الميزة قيد التطوير')
        return redirect('Hr:dashboard')

    branch = get_object_or_404(Branch, id=branch_id)

    try:
        branch.is_active = not branch.is_active
        branch.save()

        status_text = 'نشط' if branch.is_active else 'غير نشط'
        messages.success(request, f'تم تغيير حالة الفرع إلى {status_text}')

    except Exception as e:
        messages.error(request, f'حدث خطأ في تغيير حالة الفرع: {str(e)}')

    return redirect('Hr:branches:detail', branch_id=branch.id)


@login_required
def branches_by_company(request, company_id):
    """عرض فروع شركة معينة"""
    if not MODELS_AVAILABLE:
        return render_under_construction(request, 'فروع الشركة')

    try:
        company = get_object_or_404(Company, id=company_id)
        branches = company.branches.all().order_by('name')

        context = {
            'company': company,
            'branches': branches,
            'title': f'فروع شركة {company.name}'
        }

        return render(request, 'Hr/company/company_branches.html', context)

    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض فروع الشركة: {str(e)}')
        return redirect('Hr:companies:list')


@require_http_methods(["GET"])
def branch_search_ajax(request):
    """البحث في الفروع عبر AJAX"""
    if not MODELS_AVAILABLE:
        return JsonResponse({'results': []})

    search_term = request.GET.get('term', '')
    company_id = request.GET.get('company_id')

    branches = Branch.objects.select_related('company')

    if company_id:
        branches = branches.filter(company_id=company_id)

    if search_term:
        branches = branches.filter(
            Q(name__icontains=search_term) |
            Q(code__icontains=search_term)
        )

    branches = branches[:10]

    results = [
        {
            'id': str(branch.id),
            'text': f"{branch.company.name} - {branch.name}",
            'code': branch.code
        }
        for branch in branches
    ]

    return JsonResponse({'results': results})
