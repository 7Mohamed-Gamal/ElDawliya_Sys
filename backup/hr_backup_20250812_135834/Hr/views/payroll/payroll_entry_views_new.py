# =============================================================================
# ElDawliya HR Management System - Payroll Entry Views
# =============================================================================
# Views for payroll entry management
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, date

from Hr.models import PayrollEntry, PayrollPeriod, Employee, EmployeeSalaryStructure
from Hr.forms.new_payroll_forms import PayrollEntryForm, PayrollCalculationForm


# =============================================================================
# PAYROLL ENTRY VIEWS
# =============================================================================

@login_required
def entry_list(request):
    """عرض قائمة سجلات الرواتب"""
    entries = PayrollEntry.objects.select_related(
        'employee', 'payroll_period', 'employee__department'
    ).order_by('-payroll_period__start_date', 'employee__full_name')
    
    # البحث والتصفية
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    period_filter = request.GET.get('period', '')
    department_filter = request.GET.get('department', '')
    
    if search_query:
        entries = entries.filter(
            Q(employee__full_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query) |
            Q(payroll_period__name__icontains=search_query)
        )
    
    if status_filter:
        entries = entries.filter(status=status_filter)
    
    if period_filter:
        entries = entries.filter(payroll_period_id=period_filter)
    
    if department_filter:
        entries = entries.filter(employee__department_id=department_filter)
    
    # الترقيم
    paginator = Paginator(entries, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # إحصائيات سريعة
    stats = {
        'total_entries': PayrollEntry.objects.count(),
        'pending_entries': PayrollEntry.objects.filter(status='draft').count(),
        'approved_entries': PayrollEntry.objects.filter(status='approved').count(),
        'paid_entries': PayrollEntry.objects.filter(status='paid').count(),
    }
    
    # فترات متاحة للتصفية
    available_periods = PayrollPeriod.objects.order_by('-start_date')[:12]
    
    context = {
        'entries': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'period_filter': period_filter,
        'department_filter': department_filter,
        'stats': stats,
        'available_periods': available_periods,
        'title': _('سجلات الرواتب'),
        'status_choices': PayrollEntry.STATUS_CHOICES,
    }
    
    return render(request, 'Hr/payroll/payroll_entry_list.html', context)


@login_required
def entry_detail(request, entry_id):
    """عرض تفاصيل سجل الراتب"""
    entry = get_object_or_404(
        PayrollEntry.objects.select_related(
            'employee', 'payroll_period', 'employee__department'
        ), 
        id=entry_id
    )
    
    # تفاصيل الراتب
    salary_details = entry.payroll_details.select_related('salary_component').order_by(
        'salary_component__display_order'
    )
    
    # تجميع التفاصيل حسب الفئة
    earnings = salary_details.filter(salary_component__category='earning')
    deductions = salary_details.filter(salary_component__category='deduction')
    employer_contributions = salary_details.filter(
        salary_component__category='employer_contribution'
    )
    
    # حساب المجاميع
    totals = {
        'total_earnings': earnings.aggregate(total=Sum('amount'))['total'] or 0,
        'total_deductions': deductions.aggregate(total=Sum('amount'))['total'] or 0,
        'total_employer_contributions': employer_contributions.aggregate(
            total=Sum('amount')
        )['total'] or 0,
    }
    
    context = {
        'entry': entry,
        'earnings': earnings,
        'deductions': deductions,
        'employer_contributions': employer_contributions,
        'totals': totals,
        'title': f"تفاصيل راتب {entry.employee.full_name} - {entry.payroll_period.name}",
    }
    
    return render(request, 'Hr/payroll/payroll_entry_detail.html', context)


@login_required
def entry_create(request):
    """إنشاء سجل راتب جديد"""
    if request.method == 'POST':
        form = PayrollEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = request.user
            entry.save()
            
            messages.success(request, _('تم إنشاء سجل الراتب بنجاح'))
            return redirect('Hr:payroll_entries_new:detail', entry_id=entry.id)
    else:
        form = PayrollEntryForm()
    
    context = {
        'form': form,
        'title': _('إنشاء سجل راتب جديد'),
        'action': 'create',
    }
    
    return render(request, 'Hr/payroll/payroll_entry_form.html', context)


@login_required
def entry_edit(request, entry_id):
    """تحديث سجل الراتب"""
    entry = get_object_or_404(PayrollEntry, id=entry_id)
    
    # التحقق من إمكانية التعديل
    if entry.status in ['approved', 'paid']:
        messages.error(request, _('لا يمكن تعديل سجل راتب معتمد أو مدفوع'))
        return redirect('Hr:payroll_entries_new:detail', entry_id=entry.id)
    
    if request.method == 'POST':
        form = PayrollEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث سجل الراتب بنجاح'))
            return redirect('Hr:payroll_entries_new:detail', entry_id=entry.id)
    else:
        form = PayrollEntryForm(instance=entry)
    
    context = {
        'form': form,
        'entry': entry,
        'title': f"تحديث راتب {entry.employee.full_name}",
        'action': 'edit',
    }
    
    return render(request, 'Hr/payroll/payroll_entry_form.html', context)


@login_required
def entry_approve(request, entry_id):
    """اعتماد سجل الراتب"""
    entry = get_object_or_404(PayrollEntry, id=entry_id)
    
    if request.method == 'POST':
        if entry.status != 'calculated':
            messages.error(request, _('يمكن اعتماد الرواتب المحسوبة فقط'))
            return redirect('Hr:payroll_entries_new:detail', entry_id=entry.id)
        
        entry.status = 'approved'
        entry.approved_by = request.user
        entry.approved_at = timezone.now()
        entry.save()
        
        messages.success(
            request, 
            f'تم اعتماد راتب {entry.employee.full_name} بنجاح'
        )
        return redirect('Hr:payroll_entries_new:detail', entry_id=entry.id)
    
    context = {
        'entry': entry,
        'title': f"اعتماد راتب {entry.employee.full_name}",
    }
    
    return render(request, 'Hr/payroll/payroll_entry_approve.html', context)


@login_required
def entry_reject(request, entry_id):
    """رفض سجل الراتب"""
    entry = get_object_or_404(PayrollEntry, id=entry_id)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if not rejection_reason:
            messages.error(request, _('يجب إدخال سبب الرفض'))
            return redirect('Hr:payroll_entries_new:detail', entry_id=entry.id)
        
        entry.status = 'rejected'
        entry.rejection_reason = rejection_reason
        entry.rejected_by = request.user
        entry.rejected_at = timezone.now()
        entry.save()
        
        messages.success(
            request, 
            f'تم رفض راتب {entry.employee.full_name}'
        )
        return redirect('Hr:payroll_entries_new:detail', entry_id=entry.id)
    
    context = {
        'entry': entry,
        'title': f"رفض راتب {entry.employee.full_name}",
    }
    
    return render(request, 'Hr/payroll/payroll_entry_reject.html', context)


@login_required
def entry_mark_paid(request, entry_id):
    """تسجيل سجل الراتب كمدفوع"""
    entry = get_object_or_404(PayrollEntry, id=entry_id)
    
    if request.method == 'POST':
        if entry.status != 'approved':
            messages.error(request, _('يمكن دفع الرواتب المعتمدة فقط'))
            return redirect('Hr:payroll_entries_new:detail', entry_id=entry.id)
        
        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method', 'bank_transfer')
        payment_reference = request.POST.get('payment_reference', '')
        
        entry.status = 'paid'
        entry.payment_date = payment_date or timezone.now().date()
        entry.payment_method = payment_method
        entry.payment_reference = payment_reference
        entry.paid_by = request.user
        entry.save()
        
        messages.success(
            request, 
            f'تم تسجيل راتب {entry.employee.full_name} كمدفوع'
        )
        return redirect('Hr:payroll_entries_new:detail', entry_id=entry.id)
    
    context = {
        'entry': entry,
        'title': f"تسجيل دفع راتب {entry.employee.full_name}",
    }
    
    return render(request, 'Hr/payroll/payroll_entry_mark_paid.html', context)


@login_required
def bulk_approve_entries(request):
    """اعتماد مجموعة من سجلات الرواتب"""
    if request.method == 'POST':
        entry_ids = request.POST.getlist('entry_ids')
        
        if not entry_ids:
            messages.error(request, _('يجب اختيار سجلات للاعتماد'))
            return redirect('Hr:payroll_entries_new:list')
        
        entries = PayrollEntry.objects.filter(
            id__in=entry_ids, 
            status='calculated'
        )
        
        approved_count = 0
        for entry in entries:
            entry.status = 'approved'
            entry.approved_by = request.user
            entry.approved_at = timezone.now()
            entry.save()
            approved_count += 1
        
        messages.success(
            request, 
            f'تم اعتماد {approved_count} سجل راتب بنجاح'
        )
        
        return redirect('Hr:payroll_entries_new:list')
    
    return redirect('Hr:payroll_entries_new:list')
