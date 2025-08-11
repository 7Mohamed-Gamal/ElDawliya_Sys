from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Company
from .forms import CompanyForm


@login_required
def company_list(request):
    companies = Company.objects.all().order_by('name')
    return render(request, 'companies/company_list.html', {'companies': companies})


@login_required
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    return render(request, 'companies/company_detail.html', {'company': company})


@login_required
def company_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            messages.success(request, 'تم إنشاء الشركة بنجاح')
            return redirect('companies:detail', company.pk)
    else:
        form = CompanyForm()
    return render(request, 'companies/company_form.html', {'form': form})


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
