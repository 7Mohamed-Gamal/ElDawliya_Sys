# =============================================================================
# ElDawliya HR Management System - Payroll Calculation Views
# =============================================================================
# Views for payroll calculation and processing
# Integrates with modern payroll system and attendance data
# =============================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, date

from Hr.models import PayrollPeriod, PayrollEntry, Employee, Department
from Hr.forms.new_payroll_forms import PayrollCalculationForm
from Hr.services.payroll_service import payroll_service


# =============================================================================
# PAYROLL CALCULATION VIEWS
# =============================================================================

@login_required
def payroll_calculation_dashboard(request):
    """لوحة تحكم حساب الرواتب"""
    
    # إحصائيات سريعة
    stats = {
        'total_periods': PayrollPeriod.objects.count(),
        'active_periods': PayrollPeriod.objects.filter(status='active').count(),
        'pending_calculations': PayrollPeriod.objects.filter(status='draft').count(),
        'total_employees': Employee.objects.filter(is_active=True).count(),
    }
    
    # آخر فترات الرواتب
    recent_periods = PayrollPeriod.objects.order_by('-created_at')[:5]
    
    # فترات تحتاج حساب
    pending_periods = PayrollPeriod.objects.filter(
        status__in=['draft', 'processing']
    ).order_by('-start_date')[:3]
    
    context = {
        'stats': stats,
        'recent_periods': recent_periods,
        'pending_periods': pending_periods,
        'title': _('لوحة تحكم حساب الرواتب'),
    }
    
    return render(request, 'Hr/payroll/payroll_calculation_dashboard.html', context)


@login_required
def payroll_calculation_wizard(request):
    """معالج حساب الرواتب"""
    
    if request.method == 'POST':
        form = PayrollCalculationForm(request.POST)
        if form.is_valid():
            # استخراج البيانات من النموذج
            payroll_period = form.cleaned_data['payroll_period']
            employees = form.cleaned_data.get('employees', [])
            include_attendance = form.cleaned_data.get('include_attendance', True)
            include_overtime = form.cleaned_data.get('include_overtime', True)
            include_leaves = form.cleaned_data.get('include_leaves', True)
            
            # تحديد معرفات الموظفين
            employee_ids = [emp.id for emp in employees] if employees else None
            
            try:
                # تنفيذ حساب الرواتب
                result = payroll_service.calculate_payroll_for_period(
                    payroll_period=payroll_period,
                    employee_ids=employee_ids,
                    user=request.user
                )
                
                if result['success']:
                    messages.success(
                        request, 
                        f"تم حساب رواتب {result['count']} موظف بنجاح"
                    )
                    
                    # عرض التحذيرات إن وجدت
                    if result.get('warnings'):
                        for warning in result['warnings']:
                            messages.warning(request, warning)
                    
                    return redirect(
                        'Hr:payroll_periods_new:detail', 
                        period_id=payroll_period.id
                    )
                else:
                    messages.error(
                        request, 
                        f"حدث خطأ في حساب الرواتب: {result['error']}"
                    )
                    
                    # عرض الأخطاء التفصيلية
                    if result.get('errors'):
                        for error in result['errors']:
                            messages.error(request, error)
                            
            except Exception as e:
                messages.error(request, f"خطأ غير متوقع: {str(e)}")
                
    else:
        form = PayrollCalculationForm()
    
    # بيانات إضافية للنموذج
    departments = Department.objects.filter(is_active=True).order_by('name')
    active_periods = PayrollPeriod.objects.filter(
        status__in=['draft', 'active']
    ).order_by('-start_date')
    
    context = {
        'form': form,
        'departments': departments,
        'active_periods': active_periods,
        'title': _('معالج حساب الرواتب'),
    }
    
    return render(request, 'Hr/payroll/payroll_calculation_wizard.html', context)


@login_required
def payroll_calculation_preview(request):
    """معاينة حساب الرواتب قبل التنفيذ"""
    
    if request.method == 'POST':
        period_id = request.POST.get('period_id')
        employee_ids = request.POST.getlist('employee_ids')
        
        if not period_id:
            return JsonResponse({
                'success': False,
                'error': 'معرف فترة الراتب مطلوب'
            })
        
        try:
            payroll_period = get_object_or_404(PayrollPeriod, id=period_id)
            
            # الحصول على الموظفين
            employees = Employee.objects.filter(is_active=True)
            if employee_ids:
                employees = employees.filter(id__in=employee_ids)
            
            # حساب المعاينة
            preview_data = []
            total_amount = 0
            
            for employee in employees:
                # حساب تقديري للراتب (يمكن تحسينه)
                salary_structure = employee.salary_structures.filter(
                    is_active=True
                ).first()
                
                if salary_structure:
                    estimated_earnings = salary_structure.total_earnings
                    estimated_deductions = salary_structure.total_deductions
                    estimated_net = estimated_earnings - estimated_deductions
                    
                    preview_data.append({
                        'employee_id': employee.id,
                        'employee_name': employee.full_name,
                        'department': employee.department.name if employee.department else '',
                        'basic_salary': float(salary_structure.basic_salary),
                        'estimated_earnings': float(estimated_earnings),
                        'estimated_deductions': float(estimated_deductions),
                        'estimated_net': float(estimated_net),
                    })
                    
                    total_amount += estimated_net
            
            return JsonResponse({
                'success': True,
                'preview_data': preview_data,
                'total_employees': len(preview_data),
                'total_amount': float(total_amount),
                'period_name': payroll_period.name
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'طريقة غير مسموحة'
    })


@login_required
def payroll_calculation_status(request, period_id):
    """حالة حساب الرواتب"""
    
    payroll_period = get_object_or_404(PayrollPeriod, id=period_id)
    
    # إحصائيات الحساب
    entries = payroll_period.payroll_entries.all()
    stats = {
        'total_entries': entries.count(),
        'calculated_entries': entries.filter(status='calculated').count(),
        'approved_entries': entries.filter(status='approved').count(),
        'paid_entries': entries.filter(status='paid').count(),
        'total_amount': entries.aggregate(
            total=Sum('net_salary')
        )['total'] or 0,
    }
    
    # تفاصيل الحساب
    calculation_details = []
    for entry in entries.select_related('employee'):
        calculation_details.append({
            'employee_name': entry.employee.full_name,
            'employee_id': entry.employee.employee_id,
            'basic_salary': entry.basic_salary,
            'total_earnings': entry.total_earnings,
            'total_deductions': entry.total_deductions,
            'net_salary': entry.net_salary,
            'status': entry.get_status_display(),
            'status_code': entry.status,
        })
    
    context = {
        'payroll_period': payroll_period,
        'stats': stats,
        'calculation_details': calculation_details,
        'title': f"حالة حساب الرواتب - {payroll_period.name}",
    }
    
    return render(request, 'Hr/payroll/payroll_calculation_status.html', context)


@login_required
def recalculate_payroll_entry(request, entry_id):
    """إعادة حساب سجل راتب محدد"""
    
    if request.method == 'POST':
        try:
            entry = get_object_or_404(PayrollEntry, id=entry_id)
            
            # التحقق من إمكانية إعادة الحساب
            if entry.status in ['approved', 'paid']:
                return JsonResponse({
                    'success': False,
                    'error': 'لا يمكن إعادة حساب سجل راتب معتمد أو مدفوع'
                })
            
            # إعادة حساب السجل
            updated_entry = payroll_service._calculate_employee_payroll(
                entry.employee,
                entry.payroll_period,
                request.user
            )
            
            if updated_entry:
                messages.success(
                    request,
                    f'تم إعادة حساب راتب {entry.employee.full_name} بنجاح'
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'تم إعادة الحساب بنجاح',
                    'new_net_salary': float(updated_entry.net_salary)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'فشل في إعادة الحساب'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'طريقة غير مسموحة'
    })
