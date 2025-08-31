from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Company
from .forms import CompanyForm


@login_required
def company_list(request):
    """قائمة الشركات مع البحث والتصفح"""
    companies_list = Company.objects.annotate(
        branch_count=Count('branch', distinct=True)
    ).filter(is_active=True)

    # البحث
    search = request.GET.get('search')
    if search:
        companies_list = companies_list.filter(
            Q(name__icontains=search) |
            Q(name_en__icontains=search) |
            Q(tax_number__icontains=search) |
            Q(commercial_register__icontains=search)
        )

    # ترتيب النتائج
    companies_list = companies_list.order_by('name')

    # التصفح
    paginator = Paginator(companies_list, 20)
    page_number = request.GET.get('page')
    companies_page = paginator.get_page(page_number)

    context = {
        'companies': companies_page,
        'search': search,
        'title': 'إدارة الشركات'
    }
    return render(request, 'companies/company_list.html', context)


@login_required
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    return render(request, 'companies/company_detail.html', {'company': company})


@login_required
def company_create(request):
    """إضافة شركة جديدة"""
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            # Ensure new companies are always active
            company.is_active = True
            company.save()
            messages.success(request, f'تم إنشاء الشركة "{company.name}" بنجاح')
            return redirect('companies:list')
    else:
        form = CompanyForm()

    context = {
        'form': form,
        'title': 'إضافة شركة جديدة'
    }
    return render(request, 'companies/company_add.html', context)


@login_required
def company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات الشركة')
            return redirect('companies:detail', company.pk)
    else:
        form = CompanyForm(instance=company)
    return render(request, 'companies/company_form.html', {'form': form, 'company': company})


@login_required
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.delete()
        messages.success(request, 'تم حذف الشركة')
        return redirect('companies:list')
    return render(request, 'companies/company_confirm_delete.html', {'company': company})

# Create your views here.
