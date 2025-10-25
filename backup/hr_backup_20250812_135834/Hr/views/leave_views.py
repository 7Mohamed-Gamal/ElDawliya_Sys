from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth

# Modern model and form imports
from Hr.models.leave.leave_type_models import LeaveType
from Hr.models.leave.employee_leave_models import EmployeeLeave
from Hr.models.employee.employee_models import Employee
from Hr.forms.leave_forms import LeaveTypeForm, EmployeeLeaveForm
from Hr.forms.filter_forms import LeaveFilterForm

# --- Leave Type Views (No major changes needed) ---

@login_required
def leave_type_list(request):
    leave_types = LeaveType.objects.all().order_by('name')
    context = {'leave_types': leave_types, 'title': 'أنواع الإجازات'}
    return render(request, 'Hr/leaves/leave_type_list.html', context)

@login_required
def leave_type_create(request):
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء نوع الإجازة بنجاح')
            return redirect('Hr:leave_type_list')
    else:
        form = LeaveTypeForm()
    context = {'form': form, 'title': 'إنشاء نوع إجازة جديد'}
    return render(request, 'Hr/leaves/leave_type_form.html', context)

@login_required
def leave_type_detail(request, pk):
    leave_type = get_object_or_404(LeaveType, pk=pk)
    leaves = EmployeeLeave.objects.filter(leave_type=leave_type).order_by('-start_date')
    context = {'leave_type': leave_type, 'leaves': leaves, 'title': f'تفاصيل: {leave_type.name}'}
    return render(request, 'Hr/leaves/leave_type_detail.html', context)

@login_required
def leave_type_edit(request, pk):
    leave_type = get_object_or_404(LeaveType, pk=pk)
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=leave_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل نوع الإجازة بنجاح')
            return redirect('Hr:leave_type_detail', pk=leave_type.pk)
    else:
        form = LeaveTypeForm(instance=leave_type)
    context = {'form': form, 'leave_type': leave_type, 'title': f'تعديل: {leave_type.name}'}
    return render(request, 'Hr/leaves/leave_type_form.html', context)

@login_required
def leave_type_delete(request, pk):
    leave_type = get_object_or_404(LeaveType, pk=pk)
    if request.method == 'POST':
        if EmployeeLeave.objects.filter(leave_type=leave_type).exists():
            messages.error(request, 'لا يمكن حذف هذا النوع لأنه مستخدم في طلبات إجازة.')
            return redirect('Hr:leave_type_detail', pk=leave_type.pk)
        leave_type.delete()
        messages.success(request, 'تم حذف نوع الإجازة بنجاح')
        return redirect('Hr:leave_type_list')
    context = {'leave_type': leave_type, 'title': f'حذف: {leave_type.name}'}
    return render(request, 'Hr/leaves/leave_type_confirm_delete.html', context)


# --- Employee Leave Views (Refactored) ---

@login_required
def employee_leave_list(request):
    form = LeaveFilterForm(request.GET or None)
    leaves_qs = EmployeeLeave.objects.select_related('employee', 'leave_type').all()
    
    if form.is_valid():
        if form.cleaned_data.get('employee'):
            leaves_qs = leaves_qs.filter(employee=form.cleaned_data['employee'])
        if form.cleaned_data.get('leave_type'):
            leaves_qs = leaves_qs.filter(leave_type=form.cleaned_data['leave_type'])
        if form.cleaned_data.get('status'):
            leaves_qs = leaves_qs.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('date_from'):
            leaves_qs = leaves_qs.filter(start_date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            leaves_qs = leaves_qs.filter(end_date__lte=form.cleaned_data['date_to'])
    
    leaves = leaves_qs.order_by('-start_date')
    
    # Use constants for status
    pending_leaves = EmployeeLeave.objects.filter(status=EmployeeLeave.PENDING_APPROVAL).count()
    approved_leaves = EmployeeLeave.objects.filter(status=EmployeeLeave.APPROVED).count()
    rejected_leaves = EmployeeLeave.objects.filter(status=EmployeeLeave.REJECTED).count()

    context = {
        'form': form,
        'leaves': leaves,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,
        'title': 'إجازات الموظفين'
    }
    return render(request, 'Hr/leaves/employee_leave_list.html', context)

@login_required
def employee_leave_create(request):
    if request.method == 'POST':
        form = EmployeeLeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.requested_by = request.user
            leave.save()
            messages.success(request, 'تم إنشاء طلب الإجازة بنجاح.')
            return redirect('Hr:employee_leave_list')
    else:
        initial_data = {}
        employee_id = request.GET.get('employee')
        if employee_id:
            try:
                # Ensure employee exists before passing to form
                initial_data['employee'] = Employee.objects.get(pk=employee_id)
            except Employee.DoesNotExist:
                messages.error(request, "Employee not found.")
        form = EmployeeLeaveForm(initial=initial_data)
    
    context = {'form': form, 'title': 'طلب إجازة جديد'}
    return render(request, 'Hr/leaves/employee_leave_form.html', context)

@login_required
def employee_leave_detail(request, pk):
    leave = get_object_or_404(EmployeeLeave.objects.select_related('employee', 'leave_type', 'approved_by'), pk=pk)
    context = {'leave': leave, 'title': f'تفاصيل الإجازة: {leave.employee.full_name}'}
    return render(request, 'Hr/leaves/employee_leave_detail.html', context)

@login_required
def employee_leave_edit(request, pk):
    leave = get_object_or_404(EmployeeLeave, pk=pk)
    if request.method == 'POST':
        form = EmployeeLeaveForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الإجازة بنجاح.')
            return redirect('Hr:employee_leave_detail', pk=leave.pk)
    else:
        form = EmployeeLeaveForm(instance=leave)
    context = {'form': form, 'leave': leave, 'title': 'تعديل الإجازة'}
    return render(request, 'Hr/leaves/employee_leave_form.html', context)

@login_required
def employee_leave_delete(request, pk):
    leave = get_object_or_404(EmployeeLeave, pk=pk)
    if request.method == 'POST':
        leave.delete()
        messages.success(request, 'تم حذف الإجازة بنجاح.')
        return redirect('Hr:employee_leave_list')
    context = {'leave': leave, 'title': 'حذف الإجازة'}
    return render(request, 'Hr/leaves/employee_leave_confirm_delete.html', context)

@login_required
def employee_leave_approve(request, pk):
    leave = get_object_or_404(EmployeeLeave, pk=pk)
    if leave.status != EmployeeLeave.PENDING_APPROVAL:
        messages.error(request, 'يمكن فقط الموافقة على الطلبات قيد الانتظار.')
    else:
        leave.status = EmployeeLeave.APPROVED
        leave.approved_by = request.user
        leave.action_date = timezone.now()
        leave.save()
        messages.success(request, 'تمت الموافقة على الإجازة.')
    return redirect('Hr:employee_leave_detail', pk=leave.pk)

@login_required
def employee_leave_reject(request, pk):
    leave = get_object_or_404(EmployeeLeave, pk=pk)
    if leave.status != EmployeeLeave.PENDING_APPROVAL:
        messages.error(request, 'يمكن فقط رفض الطلبات قيد الانتظAR.')
        return redirect('Hr:employee_leave_detail', pk=leave.pk)

    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        leave.status = EmployeeLeave.REJECTED
        leave.approved_by = request.user
        leave.action_date = timezone.now()
        leave.rejection_reason = rejection_reason
        leave.save()
        messages.success(request, 'تم رفض الإجازة.')
        return redirect('Hr:employee_leave_detail', pk=leave.pk)

    context = {'leave': leave, 'title': 'رفض الإجازة'}
    return render(request, 'Hr/leaves/employee_leave_reject_form.html', context)


@login_required
def leave_analytics(request):
    today = timezone.now().date()
    current_year = today.year

    # Use constants for status
    approved_leaves = EmployeeLeave.objects.filter(status=EmployeeLeave.APPROVED, start_date__year=current_year)

    leave_by_type = approved_leaves.values('leave_type__name').annotate(
        count=Count('id'),
        total_days=Sum('duration_days')
    ).order_by('-total_days')

    leaves_by_month = approved_leaves.annotate(month=TruncMonth('start_date')).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    status_counts = EmployeeLeave.objects.values('status').annotate(count=Count('id'))
    status_map = {s['status']: s['count'] for s in status_counts}

    total_count = EmployeeLeave.objects.count()
    status_percentages = {k: (v / total_count * 100) if total_count > 0 else 0 for k, v in status_map.items()}

    context = {
        'leave_by_type_data': {
            'labels': [lt['leave_type__name'] for lt in leave_by_type],
            'days': [float(lt['total_days']) for lt in leave_by_type],
        },
        'leaves_by_month_data': {
            'labels': [lm['month'].strftime('%b %Y') for lm in leaves_by_month],
            'counts': [lm['count'] for lm in leaves_by_month],
        },
        'status_counts': status_map,
        'status_percentages': status_percentages,
        'title': 'تحليلات الإجازات'
    }
    
    return render(request, 'Hr/leaves/leave_analytics.html', context)
