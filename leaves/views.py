from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from django.db import models
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django import forms
from datetime import date, datetime, timedelta
from .models import LeaveType, EmployeeLeave, PublicHoliday
from employees.models import Employee
from .forms import LeaveTypeForm, EmployeeLeaveForm, PublicHolidayForm


@login_required
def dashboard(request):
    """لوحة تحكم الإجازات"""
    today = date.today()

    # إحصائيات عامة
    total_leave_types = LeaveType.objects.count()
    total_leaves = EmployeeLeave.objects.count()
    pending_leaves = EmployeeLeave.objects.filter(status='Pending').count()
    approved_leaves = EmployeeLeave.objects.filter(status='Approved').count()

    # إجازات اليوم
    today_leaves = EmployeeLeave.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        status='Approved'
    ).select_related('emp', 'leave_type')

    # الإجازات المعلقة للمراجعة
    pending_requests = EmployeeLeave.objects.filter(
        status='Pending'
    ).select_related('emp', 'leave_type').order_by('-start_date')[:5]

    # إحصائيات أنواع الإجازات
    leave_type_stats = LeaveType.objects.annotate(
        usage_count=Count('employeeleave')
    ).order_by('-usage_count')[:5]

    # العطلات الرسمية القادمة
    upcoming_holidays = PublicHoliday.objects.filter(
        holiday_date__gte=today
    ).order_by('holiday_date')[:5]

    context = {
        'total_leave_types': total_leave_types,
        'total_leaves': total_leaves,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'today_leaves': today_leaves,
        'pending_requests': pending_requests,
        'leave_type_stats': leave_type_stats,
        'upcoming_holidays': upcoming_holidays,
    }

    return render(request, 'leaves/dashboard.html', context)


@login_required
def leave_list(request):
    """قائمة طلبات الإجازات"""
    leaves = EmployeeLeave.objects.select_related('emp', 'leave_type').all()

    # البحث والفلترة
    search = request.GET.get('search')
    if search:
        leaves = leaves.filter(
            Q(emp__first_name__icontains=search) |
            Q(emp__last_name__icontains=search) |
            Q(emp__emp_code__icontains=search) |
            Q(reason__icontains=search)
        )

    # فلترة حسب نوع الإجازة
    leave_type = request.GET.get('leave_type')
    if leave_type:
        leaves = leaves.filter(leave_type_id=leave_type)

    # فلترة حسب الحالة
    status = request.GET.get('status')
    if status:
        leaves = leaves.filter(status=status)

    # فلترة حسب التاريخ
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        leaves = leaves.filter(start_date__gte=date_from)
    if date_to:
        leaves = leaves.filter(end_date__lte=date_to)

    # ترتيب النتائج
    leaves = leaves.order_by('-start_date')

    # التقسيم إلى صفحات
    paginator = Paginator(leaves, 20)
    page_number = request.GET.get('page')
    leaves = paginator.get_page(page_number)

    # قوائم للفلترة
    leave_types = LeaveType.objects.all().order_by('leave_name')

    context = {
        'leaves': leaves,
        'leave_types': leave_types,
    }

    return render(request, 'leaves/leave_list.html', context)


@login_required
def create_request(request):
    """إنشاء طلب إجازة جديد"""
    if request.method == 'POST':
        form = EmployeeLeaveForm(request.POST)
        if form.is_valid():
            leave = form.save()
            messages.success(request, f'تم إنشاء طلب الإجازة بنجاح.')
            return redirect('leaves:leave_detail', leave_id=leave.leave_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeLeaveForm()

    context = {
        'form': form,
        'title': 'طلب إجازة جديد'
    }

    return render(request, 'leaves/leave_form.html', context)


@login_required
def leave_detail(request, leave_id):
    """تفاصيل طلب الإجازة"""
    leave = get_object_or_404(EmployeeLeave, leave_id=leave_id)

    # حساب عدد الأيام
    if leave.start_date and leave.end_date:
        days_count = (leave.end_date - leave.start_date).days + 1
    else:
        days_count = 0

    context = {
        'leave': leave,
        'days_count': days_count,
    }

    return render(request, 'leaves/leave_detail.html', context)


@login_required
def edit_leave(request, leave_id):
    """تعديل طلب إجازة"""
    leave = get_object_or_404(EmployeeLeave, leave_id=leave_id)

    if request.method == 'POST':
        form = EmployeeLeaveForm(request.POST, instance=leave)
        if form.is_valid():
            leave = form.save()
            messages.success(request, 'تم تحديث طلب الإجازة بنجاح.')
            return redirect('leaves:leave_detail', leave_id=leave.leave_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeLeaveForm(instance=leave)

    context = {
        'form': form,
        'leave': leave,
        'title': 'تعديل طلب الإجازة'
    }

    return render(request, 'leaves/leave_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_leave(request, leave_id):
    """حذف طلب إجازة"""
    leave = get_object_or_404(EmployeeLeave, leave_id=leave_id)

    try:
        leave.delete()
        messages.success(request, 'تم حذف طلب الإجازة بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف طلب الإجازة: {str(e)}')

    return redirect('leaves:leave_list')


@login_required
@require_http_methods(["POST"])
def approve_leave(request, leave_id):
    """اعتماد طلب إجازة"""
    leave = get_object_or_404(EmployeeLeave, leave_id=leave_id)

    leave.status = 'Approved'
    leave.approved_date = timezone.now()
    # يمكن إضافة معرف المعتمد هنا
    leave.save()

    messages.success(request, f'تم اعتماد طلب الإجازة للموظف {leave.emp.first_name} {leave.emp.last_name}.')
    return redirect('leaves:leave_detail', leave_id=leave_id)


@login_required
@require_http_methods(["POST"])
def reject_leave(request, leave_id):
    """رفض طلب إجازة"""
    leave = get_object_or_404(EmployeeLeave, leave_id=leave_id)

    leave.status = 'Rejected'
    leave.approved_date = timezone.now()
    leave.save()

    messages.success(request, f'تم رفض طلب الإجازة للموظف {leave.emp.first_name} {leave.emp.last_name}.')
    return redirect('leaves:leave_detail', leave_id=leave_id)


# إدارة أنواع الإجازات
@login_required
def leave_types(request):
    """قائمة أنواع الإجازات"""
    types = LeaveType.objects.annotate(
        usage_count=Count('employeeleave')
    ).order_by('leave_name')

    context = {
        'types': types,
    }

    return render(request, 'leaves/leave_types.html', context)


@login_required
def add_leave_type(request):
    """إضافة نوع إجازة جديد"""
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            leave_type = form.save()
            messages.success(request, f'تم إضافة نوع الإجازة {leave_type.leave_name} بنجاح.')
            return redirect('leaves:leave_types')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = LeaveTypeForm()

    context = {
        'form': form,
        'title': 'إضافة نوع إجازة جديد'
    }

    return render(request, 'leaves/leave_type_form.html', context)


@login_required
def get_leave_type(request, type_id):
    """عرض تفاصيل نوع الإجازة"""
    leave_type = get_object_or_404(LeaveType, leave_type_id=type_id)

    # إحصائيات الاستخدام
    usage_stats = EmployeeLeave.objects.filter(leave_type=leave_type).aggregate(
        total_requests=Count('leave_id'),
        approved_requests=Count('leave_id', filter=Q(status='Approved')),
        pending_requests=Count('leave_id', filter=Q(status='Pending')),
        rejected_requests=Count('leave_id', filter=Q(status='Rejected'))
    )

    context = {
        'leave_type': leave_type,
        'usage_stats': usage_stats,
    }

    return render(request, 'leaves/leave_type_detail.html', context)


@login_required
def update_leave_type(request, type_id):
    """تحديث نوع الإجازة"""
    leave_type = get_object_or_404(LeaveType, leave_type_id=type_id)

    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=leave_type)
        if form.is_valid():
            leave_type = form.save()
            messages.success(request, f'تم تحديث نوع الإجازة {leave_type.leave_name} بنجاح.')
            return redirect('leaves:get_leave_type', type_id=type_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = LeaveTypeForm(instance=leave_type)

    context = {
        'form': form,
        'leave_type': leave_type,
        'title': 'تعديل نوع الإجازة'
    }

    return render(request, 'leaves/leave_type_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_leave_type(request, type_id):
    """حذف نوع الإجازة"""
    leave_type = get_object_or_404(LeaveType, leave_type_id=type_id)

    try:
        # التحقق من وجود إجازات مرتبطة
        if EmployeeLeave.objects.filter(leave_type=leave_type).exists():
            messages.error(request, f'لا يمكن حذف نوع الإجازة {leave_type.leave_name} لأنه مرتبط بطلبات إجازات.')
        else:
            leave_type.delete()
            messages.success(request, f'تم حذف نوع الإجازة {leave_type.leave_name} بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف نوع الإجازة: {str(e)}')

    return redirect('leaves:leave_types')


@login_required
def leave_type_stats(request, type_id):
    """إحصائيات نوع الإجازة"""
    leave_type = get_object_or_404(LeaveType, leave_type_id=type_id)

    # إحصائيات شهرية
    monthly_stats = EmployeeLeave.objects.filter(
        leave_type=leave_type
    ).extra(
        select={'month': "MONTH(start_date)", 'year': "YEAR(start_date)"}
    ).values('month', 'year').annotate(
        count=Count('leave_id')
    ).order_by('year', 'month')

    context = {
        'leave_type': leave_type,
        'monthly_stats': monthly_stats,
    }

    return render(request, 'leaves/leave_type_stats.html', context)


# تقارير أرصدة الإجازات
@login_required
def balance_report(request):
    """تقرير أرصدة الإجازات"""
    employees = Employee.objects.filter(emp_status='Active').select_related('dept', 'job')

    # فلترة حسب القسم
    department = request.GET.get('department')
    if department:
        employees = employees.filter(dept_id=department)

    # حساب أرصدة الإجازات لكل موظف
    employee_balances = []
    for emp in employees:
        # هنا يمكن إضافة منطق حساب الأرصدة الفعلي
        # Calculate used days using Python instead of database aggregation for SQL Server compatibility
        approved_leaves = EmployeeLeave.objects.filter(
            emp=emp,
            status='Approved',
            start_date__year=date.today().year
        )

        used_days = sum(
            (leave.end_date - leave.start_date).days + 1
            for leave in approved_leaves
        )

        employee_balances.append({
            'employee': emp,
            'used_days': used_days,
            'remaining_days': 30 - used_days,  # افتراض 30 يوم سنوياً
        })

    context = {
        'employee_balances': employee_balances,
    }

    return render(request, 'leaves/balance_report.html', context)


@login_required
def employee_balance(request, emp_id):
    """رصيد إجازات موظف محدد"""
    employee = get_object_or_404(Employee, emp_id=emp_id)

    # إجازات الموظف هذا العام
    current_year = date.today().year
    employee_leaves = EmployeeLeave.objects.filter(
        emp=employee,
        start_date__year=current_year
    ).select_related('leave_type')

    # تجميع حسب نوع الإجازة
    leave_summary = {}
    for leave in employee_leaves:
        leave_type_name = leave.leave_type.leave_name
        if leave_type_name not in leave_summary:
            leave_summary[leave_type_name] = {
                'total_requests': 0,
                'approved_days': 0,
                'pending_days': 0,
            }

        leave_summary[leave_type_name]['total_requests'] += 1
        if leave.status == 'Approved':
            days = (leave.end_date - leave.start_date).days + 1
            leave_summary[leave_type_name]['approved_days'] += days
        elif leave.status == 'Pending':
            days = (leave.end_date - leave.start_date).days + 1
            leave_summary[leave_type_name]['pending_days'] += days

    context = {
        'employee': employee,
        'employee_leaves': employee_leaves,
        'leave_summary': leave_summary,
        'current_year': current_year,
    }

    return render(request, 'leaves/employee_balance.html', context)


# العطلات الرسمية
@login_required
def holidays(request):
    """قائمة العطلات الرسمية"""
    holidays = PublicHoliday.objects.all().order_by('holiday_date')

    context = {
        'holidays': holidays,
    }

    return render(request, 'leaves/holidays.html', context)


@login_required
def add_holiday(request):
    """إضافة عطلة رسمية جديدة"""
    if request.method == 'POST':
        form = PublicHolidayForm(request.POST)
        if form.is_valid():
            holiday = form.save()
            messages.success(request, f'تم إضافة العطلة الرسمية بنجاح.')
            return redirect('leaves:holidays')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = PublicHolidayForm()

    context = {
        'form': form,
        'title': 'إضافة عطلة رسمية جديدة'
    }

    return render(request, 'leaves/holiday_form.html', context)


# بوابة الموظف
@login_required
def my_leaves(request):
    """إجازاتي الشخصية"""
    # هذه الدالة للموظف لعرض إجازاته الشخصية
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'لا يمكن الوصول لهذه الصفحة.')
        return redirect('leaves:dashboard')

    employee = request.user.employee

    # إجازات الموظف
    my_leaves = EmployeeLeave.objects.filter(
        emp=employee
    ).select_related('leave_type').order_by('-start_date')

    context = {
        'my_leaves': my_leaves,
        'employee': employee,
    }

    return render(request, 'leaves/my_leaves.html', context)


@login_required
def my_balance(request):
    """رصيد إجازاتي"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'لا يمكن الوصول لهذه الصفحة.')
        return redirect('leaves:dashboard')

    return employee_balance(request, request.user.employee.emp_id)


@login_required
def request_leave(request):
    """طلب إجازة جديدة (للموظف)"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'لا يمكن الوصول لهذه الصفحة.')
        return redirect('leaves:dashboard')

    if request.method == 'POST':
        form = EmployeeLeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.emp = request.user.employee
            leave.save()
            messages.success(request, 'تم إرسال طلب الإجازة بنجاح.')
            return redirect('leaves:my_leaves')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeLeaveForm()
        # إخفاء حقل الموظف لأنه سيتم تعيينه تلقائياً
        form.fields['emp'].widget = forms.HiddenInput()
        form.fields['emp'].initial = request.user.employee

    context = {
        'form': form,
        'title': 'طلب إجازة جديدة'
    }

    return render(request, 'leaves/request_leave.html', context)


# التقارير
@login_required
def leave_reports(request):
    """تقارير الإجازات"""
    today = date.today()

    # إحصائيات عامة
    total_leaves = EmployeeLeave.objects.count()
    this_month_leaves = EmployeeLeave.objects.filter(
        start_date__year=today.year,
        start_date__month=today.month
    ).count()

    # إحصائيات حسب النوع
    leave_type_stats = LeaveType.objects.annotate(
        total_requests=Count('employeeleave'),
        approved_requests=Count('employeeleave', filter=Q(employeeleave__status='Approved'))
    ).order_by('-total_requests')

    # إحصائيات حسب الحالة
    status_stats = EmployeeLeave.objects.aggregate(
        pending=Count('leave_id', filter=Q(status='Pending')),
        approved=Count('leave_id', filter=Q(status='Approved')),
        rejected=Count('leave_id', filter=Q(status='Rejected'))
    )

    context = {
        'total_leaves': total_leaves,
        'this_month_leaves': this_month_leaves,
        'leave_type_stats': leave_type_stats,
        'status_stats': status_stats,
    }

    return render(request, 'leaves/reports.html', context)


@login_required
def export_leaves(request):
    """تصدير بيانات الإجازات"""
    import csv

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leaves.csv"'

    writer = csv.writer(response)
    writer.writerow(['الموظف', 'نوع الإجازة', 'تاريخ البداية', 'تاريخ النهاية', 'السبب', 'الحالة'])

    leaves = EmployeeLeave.objects.select_related('emp', 'leave_type').all()
    for leave in leaves:
        writer.writerow([
            f"{leave.emp.first_name} {leave.emp.last_name}",
            leave.leave_type.leave_name,
            leave.start_date,
            leave.end_date,
            leave.reason,
            leave.status
        ])

    return response


# AJAX Views
@login_required
def check_leave_balance(request, emp_id, type_id):
    """فحص رصيد الإجازة عبر AJAX"""
    try:
        employee = Employee.objects.get(emp_id=emp_id)
        leave_type = LeaveType.objects.get(leave_type_id=type_id)

        # حساب الأيام المستخدمة هذا العام
        current_year = date.today().year
        # Calculate used days using Python instead of database aggregation for SQL Server compatibility
        approved_leaves = EmployeeLeave.objects.filter(
            emp=employee,
            leave_type=leave_type,
            status='Approved',
            start_date__year=current_year
        )

        used_days = sum(
            (leave.end_date - leave.start_date).days + 1
            for leave in approved_leaves
        )

        remaining_days = leave_type.max_days_per_year - used_days if leave_type.max_days_per_year else float('inf')

        data = {
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'leave_type_name': leave_type.leave_name,
            'max_days': leave_type.max_days_per_year,
            'used_days': used_days,
            'remaining_days': remaining_days,
            'can_request': remaining_days > 0
        }

        return JsonResponse(data)
    except (Employee.DoesNotExist, LeaveType.DoesNotExist):
        return JsonResponse({'error': 'البيانات غير موجودة'}, status=404)


@login_required
def calculate_leave_days(request):
    """حساب أيام الإجازة عبر AJAX"""
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not start_date_str or not end_date_str:
        return JsonResponse({'error': 'بيانات ناقصة'}, status=400)

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if end_date < start_date:
            return JsonResponse({'error': 'تاريخ النهاية يجب أن يكون بعد تاريخ البداية'}, status=400)

        # حساب عدد الأيام
        total_days = (end_date - start_date).days + 1

        # استبعاد العطلات الرسمية
        holidays = PublicHoliday.objects.filter(
            holiday_date__range=[start_date, end_date]
        ).count()

        working_days = total_days - holidays

        data = {
            'total_days': total_days,
            'holidays': holidays,
            'working_days': working_days,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }

        return JsonResponse(data)
    except ValueError:
        return JsonResponse({'error': 'تنسيق التاريخ غير صحيح'}, status=400)


# Bulk Operations
@login_required
def bulk_approve_leaves(request):
    """اعتماد طلبات الإجازات بالجملة"""
    if request.method == 'POST':
        leave_ids = request.POST.getlist('leave_ids')
        if leave_ids:
            EmployeeLeave.objects.filter(
                leave_id__in=leave_ids,
                status='Pending'
            ).update(
                status='Approved',
                approved_date=timezone.now()
            )

            messages.success(request, f'تم اعتماد {len(leave_ids)} طلب إجازة.')
        else:
            messages.warning(request, 'لم يتم تحديد أي طلبات.')

    return redirect('leaves:leave_list')


@login_required
def bulk_reject_leaves(request):
    """رفض طلبات الإجازات بالجملة"""
    if request.method == 'POST':
        leave_ids = request.POST.getlist('leave_ids')
        if leave_ids:
            EmployeeLeave.objects.filter(
                leave_id__in=leave_ids,
                status='Pending'
            ).update(
                status='Rejected',
                approved_date=timezone.now()
            )

            messages.success(request, f'تم رفض {len(leave_ids)} طلب إجازة.')
        else:
            messages.warning(request, 'لم يتم تحديد أي طلبات.')

    return redirect('leaves:leave_list')
