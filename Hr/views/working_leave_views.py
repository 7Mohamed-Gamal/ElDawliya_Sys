"""
Working Leave Management Views
These views provide actual implementation for leave management system
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta

# Import models that exist
try:
    from Hr.models.leave_models import (
        HrLeaveType as LeaveType,
        HrEmployeeLeave as EmployeeLeave,
        HrLeaveBalance as LeaveBalance
    )
    LEAVE_MODELS_AVAILABLE = True
except ImportError:
    LEAVE_MODELS_AVAILABLE = False
    LeaveType = EmployeeLeave = LeaveBalance = None

# Import legacy employee model
from Hr.models.legacy_employee import LegacyEmployee as Employee

# Import forms
try:
    from Hr.forms.leave_forms import (
        LeaveTypeForm, EmployeeLeaveForm, LeaveBalanceForm,
        LeaveRequestForm, LeaveApprovalForm
    )
    LEAVE_FORMS_AVAILABLE = True
except ImportError:
    LEAVE_FORMS_AVAILABLE = False


def render_under_construction(request, title):
    """Helper function to render under construction page"""
    return render(request, 'Hr/under_construction.html', {'title': title})


# =============================================================================
# LEAVE TYPE VIEWS
# =============================================================================

@login_required
def leave_type_list(request):
    """عرض قائمة أنواع الإجازات"""
    if not LEAVE_MODELS_AVAILABLE:
        return render_under_construction(request, 'أنواع الإجازات')
    
    try:
        leave_types = LeaveType.objects.all().order_by('name')
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            leave_types = leave_types.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(leave_types, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'leave_types': page_obj,
            'search_query': search_query,
            'title': 'أنواع الإجازات',
            'total_types': leave_types.count()
        }
        
        return render(request, 'Hr/leave/type_list.html', context)
        
    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض أنواع الإجازات: {str(e)}')
        return render(request, 'Hr/leave/type_list.html', {
            'leave_types': [],
            'title': 'أنواع الإجازات',
            'error': str(e)
        })


@login_required
def leave_type_create(request):
    """إنشاء نوع إجازة جديد"""
    if not LEAVE_MODELS_AVAILABLE or not LEAVE_FORMS_AVAILABLE:
        return render_under_construction(request, 'إنشاء نوع إجازة')
    
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            try:
                leave_type = form.save()
                messages.success(request, f'تم إنشاء نوع الإجازة "{leave_type.name}" بنجاح')
                return redirect('Hr:leaves:leave_type_list')
            except Exception as e:
                messages.error(request, f'حدث خطأ في إنشاء نوع الإجازة: {str(e)}')
    else:
        form = LeaveTypeForm()
    
    context = {
        'form': form,
        'title': 'إنشاء نوع إجازة جديد',
        'is_edit': False
    }
    
    return render(request, 'Hr/leave/type_form.html', context)


@login_required
def leave_type_edit(request, pk):
    """تعديل نوع إجازة"""
    if not LEAVE_MODELS_AVAILABLE or not LEAVE_FORMS_AVAILABLE:
        return render_under_construction(request, 'تعديل نوع إجازة')
    
    leave_type = get_object_or_404(LeaveType, pk=pk)
    
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=leave_type)
        if form.is_valid():
            try:
                leave_type = form.save()
                messages.success(request, f'تم تحديث نوع الإجازة "{leave_type.name}" بنجاح')
                return redirect('Hr:leaves:leave_type_list')
            except Exception as e:
                messages.error(request, f'حدث خطأ في تحديث نوع الإجازة: {str(e)}')
    else:
        form = LeaveTypeForm(instance=leave_type)
    
    context = {
        'form': form,
        'leave_type': leave_type,
        'title': f'تعديل نوع الإجازة: {leave_type.name}',
        'is_edit': True
    }
    
    return render(request, 'Hr/leave/type_form.html', context)


@login_required
def leave_type_delete(request, pk):
    """حذف نوع إجازة"""
    if not LEAVE_MODELS_AVAILABLE:
        return render_under_construction(request, 'حذف نوع إجازة')
    
    leave_type = get_object_or_404(LeaveType, pk=pk)
    
    if request.method == 'POST':
        try:
            # Check if type is used by employees
            if EmployeeLeave and EmployeeLeave.objects.filter(leave_type=leave_type).exists():
                messages.error(request, 'لا يمكن حذف نوع الإجازة لأنه مرتبط بطلبات إجازة')
                return redirect('Hr:leaves:leave_type_list')
            
            type_name = leave_type.name
            leave_type.delete()
            messages.success(request, f'تم حذف نوع الإجازة "{type_name}" بنجاح')
            return redirect('Hr:leaves:leave_type_list')
            
        except Exception as e:
            messages.error(request, f'حدث خطأ في حذف نوع الإجازة: {str(e)}')
            return redirect('Hr:leaves:leave_type_list')
    
    context = {
        'leave_type': leave_type,
        'title': f'حذف نوع الإجازة: {leave_type.name}'
    }
    
    return render(request, 'Hr/leave/type_delete.html', context)


# =============================================================================
# EMPLOYEE LEAVE VIEWS
# =============================================================================

@login_required
def employee_leave_list(request):
    """عرض قائمة طلبات الإجازات"""
    if not LEAVE_MODELS_AVAILABLE:
        return render_under_construction(request, 'طلبات الإجازات')
    
    try:
        if EmployeeLeave:
            leaves = EmployeeLeave.objects.select_related('leave_type').order_by('-created_at')
        else:
            leaves = []
        
        # Filter by employee
        employee_id = request.GET.get('employee')
        if employee_id and EmployeeLeave:
            leaves = leaves.filter(employee_id=employee_id)
        
        # Filter by status
        status = request.GET.get('status')
        if status and EmployeeLeave:
            leaves = leaves.filter(status=status)
        
        # Filter by leave type
        leave_type_id = request.GET.get('leave_type')
        if leave_type_id and EmployeeLeave:
            leaves = leaves.filter(leave_type_id=leave_type_id)
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query and EmployeeLeave:
            leaves = leaves.filter(
                Q(employee__emp_name__icontains=search_query) |
                Q(reason__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(leaves, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get filter options
        employees = Employee.objects.filter(working_condition='سارى').order_by('emp_name')
        leave_types = LeaveType.objects.all().order_by('name') if LeaveType else []
        
        context = {
            'leaves': page_obj,
            'employees': employees,
            'leave_types': leave_types,
            'search_query': search_query,
            'selected_employee': employee_id,
            'selected_status': status,
            'selected_leave_type': leave_type_id,
            'title': 'طلبات الإجازات',
            'total_leaves': leaves.count() if leaves else 0
        }
        
        return render(request, 'Hr/leave/leave_list.html', context)
        
    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض طلبات الإجازات: {str(e)}')
        return render(request, 'Hr/leave/leave_list.html', {
            'leaves': [],
            'employees': [],
            'leave_types': [],
            'title': 'طلبات الإجازات',
            'error': str(e)
        })


@login_required
def employee_leave_create(request):
    """إنشاء طلب إجازة جديد"""
    if not LEAVE_MODELS_AVAILABLE or not LEAVE_FORMS_AVAILABLE:
        return render_under_construction(request, 'طلب إجازة جديد')
    
    if request.method == 'POST':
        form = EmployeeLeaveForm(request.POST)
        if form.is_valid():
            try:
                leave = form.save(commit=False)
                leave.requested_by = request.user
                leave.save()
                messages.success(request, 'تم إنشاء طلب الإجازة بنجاح')
                return redirect('Hr:leaves:employee_leave_detail', pk=leave.pk)
            except Exception as e:
                messages.error(request, f'حدث خطأ في إنشاء طلب الإجازة: {str(e)}')
    else:
        form = EmployeeLeaveForm()
    
    context = {
        'form': form,
        'title': 'طلب إجازة جديد',
        'is_edit': False
    }
    
    return render(request, 'Hr/leave/leave_form.html', context)


@login_required
def employee_leave_detail(request, pk):
    """عرض تفاصيل طلب الإجازة"""
    if not LEAVE_MODELS_AVAILABLE:
        return render_under_construction(request, 'تفاصيل طلب الإجازة')
    
    try:
        leave = get_object_or_404(EmployeeLeave, pk=pk)
        employee = get_object_or_404(Employee, emp_id=leave.employee_id)
        
        # Calculate leave duration
        if leave.start_date and leave.end_date:
            duration = (leave.end_date - leave.start_date).days + 1
        else:
            duration = 0
        
        # Get employee leave balance if available
        leave_balance = None
        if LeaveBalance:
            try:
                leave_balance = LeaveBalance.objects.get(
                    employee_id=leave.employee_id,
                    leave_type=leave.leave_type
                )
            except LeaveBalance.DoesNotExist:
                pass
        
        context = {
            'leave': leave,
            'employee': employee,
            'duration': duration,
            'leave_balance': leave_balance,
            'title': f'تفاصيل طلب الإجازة: {employee.emp_name}'
        }
        
        return render(request, 'Hr/leave/leave_detail.html', context)
        
    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض تفاصيل طلب الإجازة: {str(e)}')
        return redirect('Hr:leaves:employee_leave_list')


@login_required
def employee_leave_edit(request, pk):
    """تعديل طلب إجازة"""
    if not LEAVE_MODELS_AVAILABLE or not LEAVE_FORMS_AVAILABLE:
        return render_under_construction(request, 'تعديل طلب إجازة')
    
    leave = get_object_or_404(EmployeeLeave, pk=pk)
    employee = get_object_or_404(Employee, emp_id=leave.employee_id)
    
    # Check if leave can be edited
    if leave.status not in ['pending', 'draft']:
        messages.error(request, 'لا يمكن تعديل طلب الإجازة بعد الموافقة أو الرفض')
        return redirect('Hr:leaves:employee_leave_detail', pk=pk)
    
    if request.method == 'POST':
        form = EmployeeLeaveForm(request.POST, instance=leave)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'تم تحديث طلب الإجازة بنجاح')
                return redirect('Hr:leaves:employee_leave_detail', pk=pk)
            except Exception as e:
                messages.error(request, f'حدث خطأ في تحديث طلب الإجازة: {str(e)}')
    else:
        form = EmployeeLeaveForm(instance=leave)
    
    context = {
        'form': form,
        'leave': leave,
        'employee': employee,
        'title': f'تعديل طلب إجازة: {employee.emp_name}',
        'is_edit': True
    }
    
    return render(request, 'Hr/leave/leave_form.html', context)


@login_required
def employee_leave_approve(request, pk):
    """الموافقة على طلب إجازة"""
    if not LEAVE_MODELS_AVAILABLE:
        return render_under_construction(request, 'الموافقة على طلب الإجازة')

    leave = get_object_or_404(EmployeeLeave, pk=pk)
    employee = get_object_or_404(Employee, emp_id=leave.employee_id)

    if leave.status != 'pending':
        messages.error(request, 'لا يمكن الموافقة على طلب إجازة غير معلق')
        return redirect('Hr:leaves:employee_leave_detail', pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')

        try:
            if action == 'approve':
                leave.status = 'approved'
                leave.approved_by = request.user
                leave.approval_date = timezone.now()
                leave.approval_comments = comments

                # Update leave balance if available
                if LeaveBalance:
                    try:
                        balance = LeaveBalance.objects.get(
                            employee_id=leave.employee_id,
                            leave_type=leave.leave_type
                        )
                        duration = (leave.end_date - leave.start_date).days + 1
                        balance.used_days += duration
                        balance.remaining_days = max(0, balance.total_days - balance.used_days)
                        balance.save()
                    except LeaveBalance.DoesNotExist:
                        pass

                messages.success(request, f'تم الموافقة على طلب إجازة {employee.emp_name}')

            elif action == 'reject':
                leave.status = 'rejected'
                leave.approved_by = request.user
                leave.approval_date = timezone.now()
                leave.approval_comments = comments

                messages.success(request, f'تم رفض طلب إجازة {employee.emp_name}')

            leave.save()
            return redirect('Hr:leaves:employee_leave_detail', pk=pk)

        except Exception as e:
            messages.error(request, f'حدث خطأ في معالجة طلب الإجازة: {str(e)}')

    # Calculate leave duration
    duration = 0
    if leave.start_date and leave.end_date:
        duration = (leave.end_date - leave.start_date).days + 1

    # Get employee leave balance
    leave_balance = None
    if LeaveBalance:
        try:
            leave_balance = LeaveBalance.objects.get(
                employee_id=leave.employee_id,
                leave_type=leave.leave_type
            )
        except LeaveBalance.DoesNotExist:
            pass

    context = {
        'leave': leave,
        'employee': employee,
        'duration': duration,
        'leave_balance': leave_balance,
        'title': f'الموافقة على طلب إجازة: {employee.emp_name}'
    }

    return render(request, 'Hr/leave/leave_approve.html', context)


@login_required
def leave_reports(request):
    """تقارير الإجازات"""
    if not LEAVE_MODELS_AVAILABLE:
        return render_under_construction(request, 'تقارير الإجازات')

    try:
        # Get date range from request
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')

        # Default to current year if no dates provided
        if not from_date or not to_date:
            current_year = timezone.now().year
            from_date = f'{current_year}-01-01'
            to_date = f'{current_year}-12-31'

        # Convert to datetime objects
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()

        # Get leave statistics
        if EmployeeLeave:
            leaves_in_period = EmployeeLeave.objects.filter(
                start_date__gte=from_date_obj,
                end_date__lte=to_date_obj
            )

            # Statistics by status
            approved_leaves = leaves_in_period.filter(status='approved').count()
            pending_leaves = leaves_in_period.filter(status='pending').count()
            rejected_leaves = leaves_in_period.filter(status='rejected').count()

            # Statistics by leave type
            leave_type_stats = []
            if LeaveType:
                for leave_type in LeaveType.objects.all():
                    count = leaves_in_period.filter(leave_type=leave_type).count()
                    if count > 0:
                        leave_type_stats.append({
                            'name': leave_type.name,
                            'count': count
                        })
        else:
            approved_leaves = pending_leaves = rejected_leaves = 0
            leave_type_stats = []

        context = {
            'from_date': from_date,
            'to_date': to_date,
            'approved_leaves': approved_leaves,
            'pending_leaves': pending_leaves,
            'rejected_leaves': rejected_leaves,
            'leave_type_stats': leave_type_stats,
            'title': 'تقارير الإجازات'
        }

        return render(request, 'Hr/leave/reports.html', context)

    except Exception as e:
        messages.error(request, f'حدث خطأ في عرض تقارير الإجازات: {str(e)}')
        return render(request, 'Hr/leave/reports.html', {
            'title': 'تقارير الإجازات',
            'error': str(e)
        })
