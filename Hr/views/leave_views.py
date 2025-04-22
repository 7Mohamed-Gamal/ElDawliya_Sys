from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from Hr.models.leave_models import LeaveType, EmployeeLeave
from Hr.forms.leave_forms import LeaveTypeForm, EmployeeLeaveForm

# Leave Type Views
@login_required
def leave_type_list(request):
    """عرض قائمة أنواع الإجازات"""
    leave_types = LeaveType.objects.all().order_by('name')
    
    context = {
        'leave_types': leave_types,
        'title': 'أنواع الإجازات'
    }
    
    return render(request, 'Hr/leave_types/list.html', context)

@login_required
def leave_type_create(request):
    """إنشاء نوع إجازة جديد"""
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء نوع الإجازة بنجاح')
            return redirect('Hr:leave_types:list')
    else:
        form = LeaveTypeForm()
    
    context = {
        'form': form,
        'title': 'إنشاء نوع إجازة جديد'
    }
    
    return render(request, 'Hr/leave_types/create.html', context)

@login_required
def leave_type_detail(request, pk):
    """عرض تفاصيل نوع إجازة"""
    leave_type = get_object_or_404(LeaveType, pk=pk)
    
    # Get leaves of this type
    leaves = EmployeeLeave.objects.filter(leave_type=leave_type).order_by('-start_date')
    
    context = {
        'leave_type': leave_type,
        'leaves': leaves,
        'title': f'تفاصيل نوع الإجازة: {leave_type.name}'
    }
    
    return render(request, 'Hr/leave_types/detail.html', context)

@login_required
def leave_type_edit(request, pk):
    """تعديل نوع إجازة"""
    leave_type = get_object_or_404(LeaveType, pk=pk)
    
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=leave_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل نوع الإجازة بنجاح')
            return redirect('Hr:leave_types:detail', pk=leave_type.pk)
    else:
        form = LeaveTypeForm(instance=leave_type)
    
    context = {
        'form': form,
        'leave_type': leave_type,
        'title': f'تعديل نوع الإجازة: {leave_type.name}'
    }
    
    return render(request, 'Hr/leave_types/edit.html', context)

@login_required
def leave_type_delete(request, pk):
    """حذف نوع إجازة"""
    leave_type = get_object_or_404(LeaveType, pk=pk)
    
    if request.method == 'POST':
        # Check if there are any leaves of this type
        if EmployeeLeave.objects.filter(leave_type=leave_type).exists():
            messages.error(request, 'لا يمكن حذف نوع الإجازة لأنه مستخدم في إجازات الموظفين')
            return redirect('Hr:leave_types:detail', pk=leave_type.pk)
        
        leave_type.delete()
        messages.success(request, 'تم حذف نوع الإجازة بنجاح')
        return redirect('Hr:leave_types:list')
    
    context = {
        'leave_type': leave_type,
        'title': f'حذف نوع الإجازة: {leave_type.name}'
    }
    
    return render(request, 'Hr/leave_types/delete.html', context)

# Employee Leave Views
@login_required
def employee_leave_list(request):
    """عرض قائمة إجازات الموظفين"""
    # Filter leaves based on query parameters
    employee_id = request.GET.get('employee')
    leave_type_id = request.GET.get('leave_type')
    status = request.GET.get('status')
    
    leaves = EmployeeLeave.objects.all()
    
    if employee_id:
        leaves = leaves.filter(employee_id=employee_id)
    
    if leave_type_id:
        leaves = leaves.filter(leave_type_id=leave_type_id)
    
    if status:
        leaves = leaves.filter(status=status)
    
    # Default ordering
    leaves = leaves.order_by('-start_date')
    
    # Stats
    pending_leaves = EmployeeLeave.objects.filter(status='pending').count()
    approved_leaves = EmployeeLeave.objects.filter(status='approved').count()
    rejected_leaves = EmployeeLeave.objects.filter(status='rejected').count()

    leave_types = LeaveType.objects.all().order_by('name')
    
    context = {
        'leaves': leaves,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,
        'leave_types': leave_types,
        'title': 'إجازات الموظفين'
    }
    
    return render(request, 'Hr/leaves/list.html', context)

@login_required
def employee_leave_create(request):
    """إنشاء إجازة جديدة للموظف"""
    if request.method == 'POST':
        form = EmployeeLeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            
            # Calculate days count if not provided
            if not leave.days_count:
                delta = leave.end_date - leave.start_date
                leave.days_count = delta.days + 1  # Include both start and end dates
            
            leave.save()
            messages.success(request, 'تم إنشاء الإجازة بنجاح')
            return redirect('Hr:leaves:list')
    else:
        # Pre-fill employee if provided in query string
        employee_id = request.GET.get('employee')
        initial_data = {}
        if employee_id:
            initial_data['employee'] = employee_id
        
        form = EmployeeLeaveForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'إنشاء إجازة جديدة'
    }
    
    return render(request, 'Hr/leaves/create.html', context)

@login_required
def employee_leave_detail(request, pk):
    """عرض تفاصيل إجازة"""
    leave = get_object_or_404(EmployeeLeave, pk=pk)
    
    context = {
        'leave': leave,
        'title': f'تفاصيل الإجازة: {leave.employee} - {leave.leave_type}'
    }
    
    return render(request, 'Hr/leaves/detail.html', context)

@login_required
def employee_leave_edit(request, pk):
    """تعديل إجازة"""
    leave = get_object_or_404(EmployeeLeave, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeLeaveForm(request.POST, instance=leave)
        if form.is_valid():
            leave = form.save(commit=False)
            
            # Calculate days count if dates changed
            delta = leave.end_date - leave.start_date
            leave.days_count = delta.days + 1  # Include both start and end dates
            
            leave.save()
            messages.success(request, 'تم تعديل الإجازة بنجاح')
            return redirect('Hr:leaves:detail', pk=leave.pk)
    else:
        form = EmployeeLeaveForm(instance=leave)
    
    context = {
        'form': form,
        'leave': leave,
        'title': f'تعديل الإجازة: {leave.employee} - {leave.leave_type}'
    }
    
    return render(request, 'Hr/leaves/edit.html', context)

@login_required
def employee_leave_delete(request, pk):
    """حذف إجازة"""
    leave = get_object_or_404(EmployeeLeave, pk=pk)
    
    if request.method == 'POST':
        leave.delete()
        messages.success(request, 'تم حذف الإجازة بنجاح')
        return redirect('Hr:leaves:list')
    
    context = {
        'leave': leave,
        'title': f'حذف الإجازة: {leave.employee} - {leave.leave_type}'
    }
    
    return render(request, 'Hr/leaves/delete.html', context)

@login_required
def employee_leave_approve(request, pk):
    """الموافقة على إجازة"""
    leave = get_object_or_404(EmployeeLeave, pk=pk)
    
    if leave.status != 'pending':
        messages.error(request, 'لا يمكن الموافقة على إجازة غير معلقة')
        return redirect('Hr:leaves:detail', pk=leave.pk)
    
    leave.status = 'approved'
    leave.approved_by = request.user
    leave.approval_date = timezone.now()
    leave.save()
    
    messages.success(request, 'تمت الموافقة على الإجازة بنجاح')
    return redirect('Hr:leaves:detail', pk=leave.pk)

@login_required
def employee_leave_reject(request, pk):
    """رفض إجازة"""
    leave = get_object_or_404(EmployeeLeave, pk=pk)
    
    if leave.status != 'pending':
        messages.error(request, 'لا يمكن رفض إجازة غير معلقة')
        return redirect('Hr:leaves:detail', pk=leave.pk)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason')
        
        leave.status = 'rejected'
        leave.rejection_reason = rejection_reason
        leave.approved_by = request.user  # Using the same field for the person who rejected
        leave.approval_date = timezone.now()
        leave.save()
        
        messages.success(request, 'تم رفض الإجازة بنجاح')
        return redirect('Hr:leaves:detail', pk=leave.pk)
    
    context = {
        'leave': leave,
        'title': f'رفض الإجازة: {leave.employee} - {leave.leave_type}'
    }
    
    return render(request, 'Hr/leaves/reject.html', context)
