"""
عروض (Views) نظام الإجراءات الانضباطية
Disciplinary Actions Management Views
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.http import HttpResponse
from datetime import date, timedelta
from decimal import Decimal

from .models import DisciplinaryAction
from employees.models import Employee
from .forms import DisciplinaryActionForm, DisciplinaryActionSearchForm


# ================================================================
# DASHBOARD & HOME
# ================================================================

@login_required
def disciplinary_dashboard(request):
    """لوحة معلومات نظام الإجراءات الانضباطية"""

    # Statistics
    total_actions = DisciplinaryAction.objects.count()

    # Actions by type
    actions_by_type = DisciplinaryAction.objects.values('action_type').annotate(
        count=Count('action_id')
    ).order_by('-count')

    # Actions by severity
    actions_by_severity = DisciplinaryAction.objects.values('severity_level').annotate(
        count=Count('action_id')
    ).order_by('severity_level')

    # Recent actions (last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    recent_actions_count = DisciplinaryAction.objects.filter(
        action_date__gte=thirty_days_ago
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()

    # Active warnings (valid_until in future or null)
    active_warnings = DisciplinaryAction.objects.filter(
        Q(valid_until__gte=date.today().prefetch_related()  # TODO: Add appropriate prefetch_related fields) | Q(valid_until__isnull=True)
    ).count()

    # Recent disciplinary actions
    recent_actions = DisciplinaryAction.objects.select_related('emp').order_by('-action_date')[:10]

    # Employees with most actions
    employees_with_actions = Employee.objects.annotate(
        action_count=Count('disciplinaryaction')
    ).filter(action_count__gt=0).order_by('-action_count')[:10]

    # Average severity level
    avg_severity = DisciplinaryAction.objects.aggregate(
        avg=Avg('severity_level')
    )['avg'] or 0

    context = {
        'total_actions': total_actions,
        'actions_by_type': actions_by_type,
        'actions_by_severity': actions_by_severity,
        'recent_actions_count': recent_actions_count,
        'active_warnings': active_warnings,
        'recent_actions': recent_actions,
        'employees_with_actions': employees_with_actions,
        'avg_severity': round(avg_severity, 2),
    }

    return render(request, 'disciplinary/dashboard.html', context)


# ================================================================
# DISCIPLINARY ACTIONS CRUD
# ================================================================

@login_required
def action_list(request):
    """قائمة الإجراءات الانضباطية"""
    form = DisciplinaryActionSearchForm(request.GET or None)

    actions = DisciplinaryAction.objects.select_related('emp')

    # Apply filters
    if form.is_valid():
        if form.cleaned_data.get('employee'):
            actions = actions.filter(emp=form.cleaned_data['employee'])

        if form.cleaned_data.get('action_type'):
            actions = actions.filter(action_type=form.cleaned_data['action_type'])

        if form.cleaned_data.get('severity_level'):
            actions = actions.filter(severity_level=form.cleaned_data['severity_level'])

        if form.cleaned_data.get('date_from'):
            actions = actions.filter(action_date__gte=form.cleaned_data['date_from'])

        if form.cleaned_data.get('date_to'):
            actions = actions.filter(action_date__lte=form.cleaned_data['date_to'])

        if form.cleaned_data.get('search'):
            search = form.cleaned_data['search']
            actions = actions.filter(
                Q(reason__icontains=search) | Q(notes__icontains=search)
            )

    actions = actions.order_by('-action_date')

    # Pagination
    paginator = Paginator(actions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,
    }

    return render(request, 'disciplinary/action_list.html', context)


@login_required
def action_detail(request, action_id):
    """تفاصيل إجراء انضباطي"""
    action = get_object_or_404(
        DisciplinaryAction.objects.select_related('emp'),
        action_id=action_id
    )

    # Get other actions for the same employee
    employee_actions = DisciplinaryAction.objects.filter(
        emp=action.emp
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.exclude(action_id=action_id).order_by('-action_date')[:5]

    # Check if action is still valid
    is_valid = True
    if action.valid_until:
        is_valid = action.valid_until >= date.today()

    context = {
        'action': action,
        'employee_actions': employee_actions,
        'is_valid': is_valid,
    }

    return render(request, 'disciplinary/action_detail.html', context)


@login_required
def action_create(request):
    """إضافة إجراء انضباطي جديد"""
    if request.method == 'POST':
        form = DisciplinaryActionForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            # Set decision_by to current user ID
            action.decision_by = request.user.id
            action.save()
            messages.success(
                request,
                f'تم إضافة الإجراء الانضباطي للموظف "{action.emp.first_name} {action.emp.last_name}" بنجاح'
            )
            return redirect('disciplinary:action_detail', action_id=action.action_id)
    else:
        form = DisciplinaryActionForm()

    context = {
        'form': form,
        'title': 'إضافة إجراء انضباطي جديد',
    }

    return render(request, 'disciplinary/action_form.html', context)


@login_required
def action_update(request, action_id):
    """تعديل إجراء انضباطي"""
    action = get_object_or_404(DisciplinaryAction, action_id=action_id)

    if request.method == 'POST':
        form = DisciplinaryActionForm(request.POST, instance=action)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الإجراء الانضباطي بنجاح')
            return redirect('disciplinary:action_detail', action_id=action.action_id)
    else:
        form = DisciplinaryActionForm(instance=action)

    context = {
        'form': form,
        'action': action,
        'title': f'تعديل الإجراء الانضباطي: {action.action_type}',
    }

    return render(request, 'disciplinary/action_form.html', context)


@login_required
def action_delete(request, action_id):
    """حذف إجراء انضباطي"""
    action = get_object_or_404(DisciplinaryAction, action_id=action_id)

    if request.method == 'POST':
        emp_name = f"{action.emp.first_name} {action.emp.last_name}"
        action_type = action.action_type
        action.delete()
        messages.success(request, f'تم حذف الإجراء الانضباطي "{action_type}" للموظف "{emp_name}" بنجاح')
        return redirect('disciplinary:action_list')

    context = {
        'action': action,
    }

    return render(request, 'disciplinary/action_confirm_delete.html', context)


# ================================================================
# EMPLOYEE DISCIPLINARY HISTORY
# ================================================================

@login_required
def employee_history(request, emp_id):
    """سجل الإجراءات الانضباطية لموظف معين"""
    employee = get_object_or_404(Employee, emp_id=emp_id)

    actions = DisciplinaryAction.objects.filter(
        emp=employee
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('-action_date')

    # Statistics
    total_actions = actions.count()

    actions_by_type = actions.values('action_type').annotate(
        count=Count('action_id')
    ).order_by('-count')

    actions_by_severity = actions.values('severity_level').annotate(
        count=Count('action_id')
    ).order_by('severity_level')

    # Active warnings
    active_warnings = actions.filter(
        Q(valid_until__gte=date.today()) | Q(valid_until__isnull=True)
    ).count()

    # Recent actions (last 6 months)
    six_months_ago = date.today() - timedelta(days=180)
    recent_actions_count = actions.filter(action_date__gte=six_months_ago).count()

    # Average severity
    avg_severity = actions.aggregate(avg=Avg('severity_level'))['avg'] or 0

    context = {
        'employee': employee,
        'actions': actions,
        'total_actions': total_actions,
        'actions_by_type': actions_by_type,
        'actions_by_severity': actions_by_severity,
        'active_warnings': active_warnings,
        'recent_actions_count': recent_actions_count,
        'avg_severity': round(avg_severity, 2),
    }

    return render(request, 'disciplinary/employee_history.html', context)


# ================================================================
# REPORTS & EXPORT
# ================================================================

@login_required
def reports(request):
    """تقارير الإجراءات الانضباطية"""

    # Overall statistics
    total_actions = DisciplinaryAction.objects.count()

    # Actions by type
    actions_by_type = DisciplinaryAction.objects.values('action_type').annotate(
        count=Count('action_id')
    ).order_by('-count')

    # Actions by severity
    actions_by_severity = DisciplinaryAction.objects.values('severity_level').annotate(
        count=Count('action_id')
    ).order_by('severity_level')

    # Monthly trends (last 12 months)
    twelve_months_ago = date.today() - timedelta(days=365)
    monthly_actions = DisciplinaryAction.objects.filter(
        action_date__gte=twelve_months_ago
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.extra(
        select={'month': "MONTH(action_date)", 'year': "YEAR(action_date)"}
    ).values('month', 'year').annotate(
        count=Count('action_id')
    ).order_by('year', 'month')

    # Top employees with most actions
    top_employees = Employee.objects.annotate(
        action_count=Count('disciplinaryaction')
    ).filter(action_count__gt=0).order_by('-action_count')[:10]

    # Average severity by action type
    severity_by_type = DisciplinaryAction.objects.values('action_type').annotate(
        avg_severity=Avg('severity_level'),
        count=Count('action_id')
    ).order_by('-avg_severity')

    context = {
        'total_actions': total_actions,
        'actions_by_type': actions_by_type,
        'actions_by_severity': actions_by_severity,
        'monthly_actions': monthly_actions,
        'top_employees': top_employees,
        'severity_by_type': severity_by_type,
    }

    return render(request, 'disciplinary/reports.html', context)


@login_required
def export_actions(request):
    """تصدير الإجراءات الانضباطية إلى CSV"""
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="disciplinary_actions.csv"'

    # Add BOM for Excel to recognize UTF-8
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([
        'رقم الإجراء', 'الموظف', 'كود الموظف', 'نوع الإجراء',
        'تاريخ الإجراء', 'السبب', 'مستوى الخطورة',
        'صالح حتى', 'ملاحظات'
    ])

    actions = DisciplinaryAction.objects.select_related('emp').all().order_by('-action_date')

    for action in actions:
        writer.writerow([
            action.action_id,
            f"{action.emp.first_name} {action.emp.last_name}",
            action.emp.emp_code,
            action.action_type,
            action.action_date.strftime('%Y-%m-%d') if action.action_date else '',
            action.reason or '',
            action.severity_level or '',
            action.valid_until.strftime('%Y-%m-%d') if action.valid_until else '',
            action.notes or ''
        ])

    return response
