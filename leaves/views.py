from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LeaveType, EmployeeLeave, PublicHoliday
from .forms import LeaveTypeForm, EmployeeLeaveForm, PublicHolidayForm


@login_required
def leave_type_list(request):
    items = LeaveType.objects.all().order_by('leave_name')
    return render(request, 'leaves/leave_type_list.html', {'items': items})

@login_required
def leave_type_create(request):
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء نوع الإجازة بنجاح')
            return redirect('leaves:leave_types')
    else:
        form = LeaveTypeForm()
    return render(request, 'leaves/leave_type_form.html', {'form': form, 'title': 'إضافة نوع إجازة'})

@login_required
def leave_type_edit(request, pk):
    item = get_object_or_404(LeaveType, pk=pk)
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل نوع الإجازة بنجاح')
            return redirect('leaves:leave_types')
    else:
        form = LeaveTypeForm(instance=item)
    return render(request, 'leaves/leave_type_form.html', {'form': form, 'title': 'تعديل نوع إجازة'})

@login_required
def leave_type_delete(request, pk):
    item = get_object_or_404(LeaveType, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'تم حذف نوع الإجازة')
        return redirect('leaves:leave_types')
    return render(request, 'leaves/leave_type_confirm_delete.html', {'item': item})


@login_required
def employee_leave_list(request):
    items = EmployeeLeave.objects.select_related('emp', 'leave_type').order_by('-start_date')
    return render(request, 'leaves/employee_leave_list.html', {'items': items})

@login_required
def employee_leave_create(request):
    if request.method == 'POST':
        form = EmployeeLeaveForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء إجازة للموظف')
            return redirect('leaves:employee_leaves')
    else:
        form = EmployeeLeaveForm()
    return render(request, 'leaves/employee_leave_form.html', {'form': form, 'title': 'إضافة إجازة'})

@login_required
def employee_leave_edit(request, pk):
    item = get_object_or_404(EmployeeLeave, pk=pk)
    if request.method == 'POST':
        form = EmployeeLeaveForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الإجازة')
            return redirect('leaves:employee_leaves')
    else:
        form = EmployeeLeaveForm(instance=item)
    return render(request, 'leaves/employee_leave_form.html', {'form': form, 'title': 'تعديل إجازة'})

@login_required
def employee_leave_delete(request, pk):
    item = get_object_or_404(EmployeeLeave, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'تم حذف الإجازة')
        return redirect('leaves:employee_leaves')
    return render(request, 'leaves/employee_leave_confirm_delete.html', {'item': item})


@login_required
def public_holiday_list(request):
    items = PublicHoliday.objects.all().order_by('-holiday_date')
    return render(request, 'leaves/public_holiday_list.html', {'items': items})

@login_required
def public_holiday_create(request):
    if request.method == 'POST':
        form = PublicHolidayForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة عطلة رسمية')
            return redirect('leaves:holidays')
    else:
        form = PublicHolidayForm()
    return render(request, 'leaves/public_holiday_form.html', {'form': form, 'title': 'إضافة عطلة'})

@login_required
def public_holiday_edit(request, pk):
    item = get_object_or_404(PublicHoliday, pk=pk)
    if request.method == 'POST':
        form = PublicHolidayForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل العطلة')
            return redirect('leaves:holidays')
    else:
        form = PublicHolidayForm(instance=item)
    return render(request, 'leaves/public_holiday_form.html', {'form': form, 'title': 'تعديل عطلة'})

@login_required
def public_holiday_delete(request, pk):
    item = get_object_or_404(PublicHoliday, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'تم حذف العطلة')
        return redirect('leaves:holidays')
    return render(request, 'leaves/public_holiday_confirm_delete.html', {'item': item})
