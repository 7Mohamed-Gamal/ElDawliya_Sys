"""
Company Views for HRMS
Handles company management operations
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _

try:
    from Hr.models.core.company_models import Company
    from Hr.forms.core.company_forms import CompanyForm
except ImportError:
    # Placeholder for development
    Company = None
    CompanyForm = None


@login_required
def company_list(request):
    """List all companies with search and pagination"""
    companies = Company.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        companies = companies.filter(
            Q(name__icontains=search_query) |
            Q(legal_name__icontains=search_query) |
            Q(tax_id__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        companies = companies.filter(is_active=(status_filter == 'active'))
    
    # Annotate with counts
    companies = companies.annotate(
        employees_count=Count('employees'),
        branches_count=Count('branches'),
        departments_count=Count('departments')
    )
    
    # Pagination
    paginator = Paginator(companies, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'title': _('إدارة الشركات'),
    }
    
    return render(request, 'Hr/core/company/list.html', context)


@login_required
def company_detail(request, company_id):
    """Display company details"""
    company = get_object_or_404(Company, id=company_id)
    
    # Get related statistics
    stats = {
        'employees_count': company.employees.filter(status='active').count(),
        'branches_count': company.branches.filter(is_active=True).count(),
        'departments_count': company.departments.filter(is_active=True).count(),
    }
    
    # Get recent employees
    recent_employees = company.employees.filter(status='active').order_by('-created_at')[:5]
    
    context = {
        'company': company,
        'stats': stats,
        'recent_employees': recent_employees,
        'title': f'{company.name} - تفاصيل الشركة',
    }
    
    return render(request, 'Hr/core/company/detail.html', context)


@login_required
def company_create(request):
    """Create a new company"""
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            messages.success(request, _('تم إنشاء الشركة بنجاح'))
            return redirect('Hr:companies:detail', company_id=company.id)
    else:
        form = CompanyForm()
    
    context = {
        'form': form,
        'title': _('إضافة شركة جديدة'),
        'submit_text': _('إنشاء الشركة'),
    }
    
    return render(request, 'Hr/core/company/form.html', context)


@login_required
def company_edit(request, company_id):
    """Edit an existing company"""
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث بيانات الشركة بنجاح'))
            return redirect('Hr:companies:detail', company_id=company.id)
    else:
        form = CompanyForm(instance=company)
    
    context = {
        'form': form,
        'company': company,
        'title': f'تعديل {company.name}',
        'submit_text': _('حفظ التغييرات'),
    }
    
    return render(request, 'Hr/core/company/form.html', context)


@login_required
@require_http_methods(["POST"])
def company_delete(request, company_id):
    """Delete a company"""
    company = get_object_or_404(Company, id=company_id)
    
    # Check if company has employees
    if company.employees.exists():
        messages.error(request, _('لا يمكن حذف الشركة لوجود موظفين مرتبطين بها'))
        return redirect('Hr:companies:detail', company_id=company.id)
    
    company_name = company.name
    company.delete()
    messages.success(request, f'تم حذف الشركة "{company_name}" بنجاح')
    return redirect('Hr:companies:list')


@login_required
def company_toggle_status(request, company_id):
    """Toggle company active status"""
    company = get_object_or_404(Company, id=company_id)
    company.is_active = not company.is_active
    company.save()
    
    status_text = 'تم تفعيل' if company.is_active else 'تم إلغاء تفعيل'
    messages.success(request, f'{status_text} الشركة "{company.name}" بنجاح')
    
    return redirect('Hr:companies:detail', company_id=company.id)


@login_required
def company_dashboard(request, company_id):
    """Company dashboard with analytics"""
    company = get_object_or_404(Company, id=company_id)
    
    # Get comprehensive statistics
    stats = {
        'total_employees': company.employees.count(),
        'active_employees': company.employees.filter(status='active').count(),
        'total_branches': company.branches.count(),
        'active_branches': company.branches.filter(is_active=True).count(),
        'total_departments': company.departments.count(),
        'active_departments': company.departments.filter(is_active=True).count(),
    }
    
    # Get department statistics
    department_stats = company.departments.filter(is_active=True).annotate(
        employee_count=Count('employees')
    ).order_by('-employee_count')[:10]
    
    # Get recent activities (this would need to be implemented)
    recent_activities = []
    
    context = {
        'company': company,
        'stats': stats,
        'department_stats': department_stats,
        'recent_activities': recent_activities,
        'title': f'{company.name} - لوحة التحكم',
    }
    
    return render(request, 'Hr/core/company/dashboard.html', context)


@login_required
def company_export(request):
    """Export companies data"""
    # This would implement export functionality
    # For now, return a simple response
    companies = Company.objects.all()
    
    # Implementation would depend on export format (Excel, PDF, etc.)
    messages.info(request, _('سيتم تنفيذ وظيفة التصدير قريباً'))
    return redirect('Hr:companies:list')


# AJAX Views
@login_required
def company_search_ajax(request):
    """AJAX search for companies"""
    query = request.GET.get('q', '')
    companies = Company.objects.filter(
        Q(name__icontains=query) | Q(legal_name__icontains=query)
    ).filter(is_active=True)[:10]
    
    results = [
        {
            'id': company.id,
            'name': company.name,
            'legal_name': company.legal_name,
            'tax_id': company.tax_id,
        }
        for company in companies
    ]
    
    return JsonResponse({'results': results})


@login_required
def company_stats_ajax(request, company_id):
    """Get company statistics via AJAX"""
    company = get_object_or_404(Company, id=company_id)
    
    stats = {
        'employees': {
            'total': company.employees.count(),
            'active': company.employees.filter(status='active').count(),
            'inactive': company.employees.filter(status='inactive').count(),
        },
        'branches': {
            'total': company.branches.count(),
            'active': company.branches.filter(is_active=True).count(),
        },
        'departments': {
            'total': company.departments.count(),
            'active': company.departments.filter(is_active=True).count(),
        }
    }
    
    return JsonResponse(stats)
