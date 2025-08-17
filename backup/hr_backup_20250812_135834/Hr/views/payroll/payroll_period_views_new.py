# =============================================================================
# ElDawliya HR Management System - Payroll Period Views
# =============================================================================
# Views for payroll period management
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, date

from Hr.models import PayrollPeriod, PayrollEntry, Employee, Company
from Hr.forms.new_payroll_forms import PayrollPeriodForm


# =============================================================================
# PAYROLL PERIOD VIEWS
# =============================================================================

@login_required
def period_list(request):
    """عرض قائمة فترات الرواتب"""
    periods = PayrollPeriod.objects.all().order_by('-start_date')
    
    # البحث والتصفية
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    year_filter = request.GET.get('year', '')
    
    if search_query:
        periods = periods.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if status_filter:
        periods = periods.filter(status=status_filter)
    
    if year_filter:
        periods = periods.filter(start_date__year=year_filter)
    
    # الترقيم
    paginator = Paginator(periods, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # إحصائيات سريعة
    stats = {
        'total_periods': PayrollPeriod.objects.count(),
        'active_periods': PayrollPeriod.objects.filter(status='active').count(),
        'completed_periods': PayrollPeriod.objects.filter(status='completed').count(),
        'current_year_periods': PayrollPeriod.objects.filter(
            start_date__year=timezone.now().year
        ).count(),
    }
    
    # سنوات متاحة للتصفية
    available_years = PayrollPeriod.objects.dates('start_date', 'year', order='DESC')
    
    context = {
        'periods': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'year_filter': year_filter,
        'stats': stats,
        'available_years': available_years,
        'title': _('فترات الرواتب'),
        'status_choices': PayrollPeriod.STATUS_CHOICES,
    }
    
    return render(request, 'Hr/payroll/payroll_period_list.html', context)


@login_required
def period_detail(request, period_id):
    """عرض تفاصيل فترة الراتب"""
    period = get_object_or_404(PayrollPeriod, id=period_id)
    
    # إحصائيات الفترة
    entries = period.payroll_entries.all()
    stats = {
        'total_entries': entries.count(),
        'draft_entries': entries.filter(status='draft').count(),
        'calculated_entries': entries.filter(status='calculated').count(),
        'approved_entries': entries.filter(status='approved').count(),
        'paid_entries': entries.filter(status='paid').count(),
        'total_amount': entries.aggregate(
            total=Sum('net_salary')
        )['total'] or 0,
    }
    
    # سجلات الرواتب مع التصفية
    status_filter = request.GET.get('status', '')
    department_filter = request.GET.get('department', '')
    
    filtered_entries = entries.select_related('employee', 'employee__department')
    
    if status_filter:
        filtered_entries = filtered_entries.filter(status=status_filter)
    
    if department_filter:
        filtered_entries = filtered_entries.filter(
            employee__department_id=department_filter
        )
    
    # الترقيم
    paginator = Paginator(filtered_entries, 20)
    page_number = request.GET.get('page')
    entries_page = paginator.get_page(page_number)
    
    context = {
        'period': period,
        'stats': stats,
        'entries': entries_page,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'title': f"تفاصيل فترة الراتب - {period.name}",
        'status_choices': PayrollEntry.STATUS_CHOICES,
    }
    
    return render(request, 'Hr/payroll/payroll_period_detail.html', context)


@login_required
def period_create(request):
    """إنشاء فترة راتب جديدة"""
    if request.method == 'POST':
        form = PayrollPeriodForm(request.POST)
        if form.is_valid():
            period = form.save(commit=False)
            period.created_by = request.user
            period.save()
            
            messages.success(request, _('تم إنشاء فترة الراتب بنجاح'))
            return redirect('Hr:payroll_periods_new:detail', period_id=period.id)
    else:
        form = PayrollPeriodForm()
    
    context = {
        'form': form,
        'title': _('إنشاء فترة راتب جديدة'),
        'action': 'create',
    }
    
    return render(request, 'Hr/payroll/payroll_period_form.html', context)


@login_required
def period_edit(request, period_id):
    """تحديث فترة الراتب"""
    period = get_object_or_404(PayrollPeriod, id=period_id)
    
    # التحقق من إمكانية التعديل
    if period.status in ['completed', 'closed']:
        messages.error(request, _('لا يمكن تعديل فترة راتب مكتملة أو مغلقة'))
        return redirect('Hr:payroll_periods_new:detail', period_id=period.id)
    
    if request.method == 'POST':
        form = PayrollPeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث فترة الراتب بنجاح'))
            return redirect('Hr:payroll_periods_new:detail', period_id=period.id)
    else:
        form = PayrollPeriodForm(instance=period)
    
    context = {
        'form': form,
        'period': period,
        'title': f"تحديث فترة الراتب - {period.name}",
        'action': 'edit',
    }
    
    return render(request, 'Hr/payroll/payroll_period_form.html', context)


@login_required
def period_delete(request, period_id):
    """حذف فترة الراتب"""
    period = get_object_or_404(PayrollPeriod, id=period_id)
    
    # التحقق من إمكانية الحذف
    if period.payroll_entries.exists():
        messages.error(
            request, 
            _('لا يمكن حذف فترة الراتب لأنها تحتوي على سجلات رواتب')
        )
        return redirect('Hr:payroll_periods_new:detail', period_id=period.id)
    
    if request.method == 'POST':
        period_name = period.name
        period.delete()
        messages.success(request, f'تم حذف فترة الراتب "{period_name}" بنجاح')
        return redirect('Hr:payroll_periods_new:list')
    
    context = {
        'period': period,
        'title': f"حذف فترة الراتب - {period.name}",
    }
    
    return render(request, 'Hr/payroll/payroll_period_delete.html', context)


@login_required
def period_close(request, period_id):
    """إغلاق فترة الراتب"""
    period = get_object_or_404(PayrollPeriod, id=period_id)
    
    if request.method == 'POST':
        if period.status != 'completed':
            messages.error(request, _('يجب أن تكون فترة الراتب مكتملة قبل الإغلاق'))
            return redirect('Hr:payroll_periods_new:detail', period_id=period.id)
        
        period.status = 'closed'
        period.closed_at = timezone.now()
        period.closed_by = request.user
        period.save()
        
        messages.success(request, f'تم إغلاق فترة الراتب "{period.name}" بنجاح')
        return redirect('Hr:payroll_periods_new:detail', period_id=period.id)
    
    context = {
        'period': period,
        'title': f"إغلاق فترة الراتب - {period.name}",
    }
    
    return render(request, 'Hr/payroll/payroll_period_close.html', context)


@login_required
def period_reopen(request, period_id):
    """إعادة فتح فترة الراتب"""
    period = get_object_or_404(PayrollPeriod, id=period_id)
    
    if request.method == 'POST':
        if period.status != 'closed':
            messages.error(request, _('فترة الراتب ليست مغلقة'))
            return redirect('Hr:payroll_periods_new:detail', period_id=period.id)
        
        period.status = 'completed'
        period.closed_at = None
        period.closed_by = None
        period.save()
        
        messages.success(request, f'تم إعادة فتح فترة الراتب "{period.name}" بنجاح')
        return redirect('Hr:payroll_periods_new:detail', period_id=period.id)
    
    context = {
        'period': period,
        'title': f"إعادة فتح فترة الراتب - {period.name}",
    }
    
    return render(request, 'Hr/payroll/payroll_period_reopen.html', context)


@login_required
def period_summary_ajax(request, period_id):
    """ملخص فترة الراتب - AJAX"""
    period = get_object_or_404(PayrollPeriod, id=period_id)
    
    entries = period.payroll_entries.all()
    summary = {
        'period_name': period.name,
        'status': period.get_status_display(),
        'total_entries': entries.count(),
        'total_amount': float(entries.aggregate(
            total=Sum('net_salary')
        )['total'] or 0),
        'status_breakdown': {},
    }
    
    # تفصيل حسب الحالة
    for status_code, status_name in PayrollEntry.STATUS_CHOICES:
        count = entries.filter(status=status_code).count()
        amount = entries.filter(status=status_code).aggregate(
            total=Sum('net_salary')
        )['total'] or 0
        
        summary['status_breakdown'][status_code] = {
            'name': status_name,
            'count': count,
            'amount': float(amount),
        }
    
    return JsonResponse(summary)
