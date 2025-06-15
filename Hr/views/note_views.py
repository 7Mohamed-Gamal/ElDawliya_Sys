from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta
import json

from Hr.models.note_models import EmployeeNote, EmployeeNoteHistory
from Hr.models.employee_model import Employee
from Hr.models.base_models import Department
from Hr.forms.note_forms import (
    EmployeeNoteForm, EmployeeSearchForm, EmployeeNoteFilterForm,
    EmployeeNoteReportForm
)


@login_required
def employee_notes_dashboard(request):
    """لوحة معلومات ملاحظات الموظفين الرئيسية"""

    # إحصائيات عامة
    total_notes = EmployeeNote.objects.filter(is_active=True).count()
    positive_notes = EmployeeNote.objects.filter(
        is_active=True, note_type='positive'
    ).count()
    negative_notes = EmployeeNote.objects.filter(
        is_active=True, note_type='negative'
    ).count()
    general_notes = EmployeeNote.objects.filter(
        is_active=True, note_type='general'
    ).count()

    # ملاحظات تتطلب متابعة
    follow_up_notes = EmployeeNote.objects.filter(
        is_active=True,
        follow_up_required=True,
        follow_up_date__lte=timezone.now().date()
    ).count()

    # الملاحظات الحديثة
    recent_notes = EmployeeNote.objects.filter(
        is_active=True
    ).select_related('employee', 'created_by').order_by('-created_at')[:10]

    # إحصائيات حسب القسم
    department_stats = Department.objects.annotate(
        notes_count=Count('employees__notes', filter=Q(employees__notes__is_active=True))
    ).filter(notes_count__gt=0).order_by('-notes_count')[:5]

    # إحصائيات شهرية (آخر 6 أشهر)
    six_months_ago = timezone.now() - timedelta(days=180)
    try:
        # Try to get monthly stats, but handle database-specific issues
        monthly_stats = EmployeeNote.objects.filter(
            is_active=True,
            created_at__gte=six_months_ago
        ).values('created_at__year', 'created_at__month').annotate(
            count=Count('id')
        ).order_by('created_at__year', 'created_at__month')

        # Convert to the expected format
        monthly_stats = [
            {
                'month': f"{item['created_at__year']}-{item['created_at__month']:02d}",
                'count': item['count']
            }
            for item in monthly_stats
        ]
    except Exception as e:
        # Fallback to empty list if there's a database issue
        monthly_stats = []

    context = {
        'total_notes': total_notes,
        'positive_notes': positive_notes,
        'negative_notes': negative_notes,
        'general_notes': general_notes,
        'follow_up_notes': follow_up_notes,
        'recent_notes': recent_notes,
        'department_stats': department_stats,
        'monthly_stats': monthly_stats,
        'title': 'لوحة معلومات ملاحظات الموظفين'
    }

    return render(request, 'Hr/notes/dashboard.html', context)


@login_required
def employee_notes_create(request):
    """صفحة إنشاء ملاحظة جديدة للموظف"""

    search_form = EmployeeSearchForm()
    note_form = EmployeeNoteForm()
    selected_employee = None

    # التحقق من وجود موظف محدد في الرابط
    employee_id = request.GET.get('employee_id')
    if employee_id:
        try:
            selected_employee = Employee.objects.get(emp_id=employee_id)
        except Employee.DoesNotExist:
            messages.error(request, 'الموظف المحدد غير موجود')

    if request.method == 'POST':
        if 'search_employee' in request.POST:
            # البحث عن موظف
            search_form = EmployeeSearchForm(request.POST)
            if search_form.is_valid():
                # تنفيذ البحث
                return redirect('Hr:notes:employee_search_ajax')

        elif 'create_note' in request.POST:
            # إنشاء ملاحظة جديدة
            note_form = EmployeeNoteForm(request.POST)
            employee_id = request.POST.get('employee_id')

            if employee_id and note_form.is_valid():
                try:
                    selected_employee = Employee.objects.get(emp_id=employee_id)
                    note = note_form.save(commit=False)
                    note.employee = selected_employee
                    note.created_by = request.user
                    note.save()

                    # إنشاء سجل في التاريخ
                    EmployeeNoteHistory.objects.create(
                        note=note,
                        action='created',
                        changed_by=request.user,
                        new_values={
                            'title': note.title,
                            'content': note.content,
                            'note_type': note.note_type,
                            'priority': note.priority
                        }
                    )

                    messages.success(
                        request,
                        f'تم إنشاء الملاحظة "{note.title}" للموظف {selected_employee.emp_full_name} بنجاح'
                    )
                    return redirect('Hr:notes:employee_notes', employee_id=selected_employee.emp_id)

                except Employee.DoesNotExist:
                    messages.error(request, 'الموظف المحدد غير موجود')
            else:
                if not employee_id:
                    messages.error(request, 'يجب اختيار موظف أولاً')

    context = {
        'search_form': search_form,
        'note_form': note_form,
        'selected_employee': selected_employee,
        'title': 'إضافة ملاحظة جديدة'
    }

    return render(request, 'Hr/notes/create.html', context)


@login_required
@require_http_methods(["GET"])
def employee_search_ajax(request):
    """البحث عن الموظفين عبر AJAX"""

    search_form = EmployeeSearchForm(request.GET)
    employees = Employee.objects.none()

    if search_form.is_valid():
        employees_query = Employee.objects.select_related('department')

        # البحث السريع
        quick_search = search_form.cleaned_data.get('quick_search')
        if quick_search:
            employees_query = employees_query.filter(
                Q(emp_id__icontains=quick_search) |
                Q(emp_full_name__icontains=quick_search) |
                Q(emp_first_name__icontains=quick_search) |
                Q(emp_second_name__icontains=quick_search) |
                Q(national_id__icontains=quick_search) |
                Q(emp_phone1__icontains=quick_search) |
                Q(emp_phone2__icontains=quick_search)
            )

        # البحث المتقدم
        employee_id = search_form.cleaned_data.get('employee_id')
        if employee_id:
            employees_query = employees_query.filter(emp_id__icontains=employee_id)

        full_name = search_form.cleaned_data.get('full_name')
        if full_name:
            employees_query = employees_query.filter(
                Q(emp_full_name__icontains=full_name) |
                Q(emp_first_name__icontains=full_name) |
                Q(emp_second_name__icontains=full_name)
            )

        national_id = search_form.cleaned_data.get('national_id')
        if national_id:
            employees_query = employees_query.filter(national_id__icontains=national_id)

        phone = search_form.cleaned_data.get('phone')
        if phone:
            employees_query = employees_query.filter(
                Q(emp_phone1__icontains=phone) |
                Q(emp_phone2__icontains=phone)
            )

        department = search_form.cleaned_data.get('department')
        if department:
            employees_query = employees_query.filter(department=department)

        car = search_form.cleaned_data.get('car')
        if car:
            employees_query = employees_query.filter(emp_car=car.car_id)

        employees = employees_query.order_by('emp_full_name')[:20]  # حد أقصى 20 نتيجة

    # إعداد البيانات للإرجاع
    employees_data = []
    for employee in employees:
        employees_data.append({
            'emp_id': employee.emp_id,
            'emp_full_name': employee.emp_full_name or employee.emp_first_name,
            'emp_first_name': employee.emp_first_name,
            'national_id': employee.national_id,
            'department_name': employee.department.dept_name if employee.department else '',
            'phone': employee.emp_phone1,
            'working_condition': employee.working_condition,
            'notes_count': employee.notes.filter(is_active=True).count()
        })

    return JsonResponse({
        'success': True,
        'employees': employees_data,
        'count': len(employees_data)
    })


@login_required
def employee_notes_list(request, employee_id):
    """عرض قائمة ملاحظات موظف محدد"""

    employee = get_object_or_404(Employee, emp_id=employee_id)

    # تطبيق الفلاتر
    filter_form = EmployeeNoteFilterForm(request.GET or None)
    notes_query = employee.notes.filter(is_active=True).select_related('created_by', 'last_modified_by')

    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        if search:
            notes_query = notes_query.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__icontains=search)
            )

        note_type = filter_form.cleaned_data.get('note_type')
        if note_type:
            notes_query = notes_query.filter(note_type=note_type)

        priority = filter_form.cleaned_data.get('priority')
        if priority:
            notes_query = notes_query.filter(priority=priority)

        is_important = filter_form.cleaned_data.get('is_important')
        if is_important:
            notes_query = notes_query.filter(is_important=True)

        is_confidential = filter_form.cleaned_data.get('is_confidential')
        if is_confidential:
            notes_query = notes_query.filter(is_confidential=True)

        follow_up_required = filter_form.cleaned_data.get('follow_up_required')
        if follow_up_required:
            notes_query = notes_query.filter(follow_up_required=True)

        date_from = filter_form.cleaned_data.get('date_from')
        if date_from:
            notes_query = notes_query.filter(created_at__date__gte=date_from)

        date_to = filter_form.cleaned_data.get('date_to')
        if date_to:
            notes_query = notes_query.filter(created_at__date__lte=date_to)

        created_by = filter_form.cleaned_data.get('created_by')
        if created_by:
            notes_query = notes_query.filter(created_by=created_by)

    # ترتيب النتائج
    notes_query = notes_query.order_by('-created_at')

    # تقسيم الصفحات
    paginator = Paginator(notes_query, 10)  # 10 ملاحظات في كل صفحة
    page_number = request.GET.get('page')
    notes = paginator.get_page(page_number)

    # إحصائيات الموظف
    employee_stats = {
        'total_notes': employee.notes.filter(is_active=True).count(),
        'positive_notes': employee.notes.filter(is_active=True, note_type='positive').count(),
        'negative_notes': employee.notes.filter(is_active=True, note_type='negative').count(),
        'general_notes': employee.notes.filter(is_active=True, note_type='general').count(),
        'important_notes': employee.notes.filter(is_active=True, is_important=True).count(),
        'follow_up_notes': employee.notes.filter(
            is_active=True,
            follow_up_required=True,
            follow_up_date__lte=timezone.now().date()
        ).count(),
    }

    context = {
        'employee': employee,
        'notes': notes,
        'filter_form': filter_form,
        'employee_stats': employee_stats,
        'title': f'ملاحظات الموظف - {employee.emp_full_name or employee.emp_first_name}'
    }

    return render(request, 'Hr/notes/employee_notes.html', context)


@login_required
def employee_note_detail(request, note_id):
    """عرض تفاصيل ملاحظة محددة"""

    note = get_object_or_404(EmployeeNote, id=note_id, is_active=True)

    # التحقق من الصلاحيات للملاحظات السرية
    if note.is_confidential and not request.user.has_perm('Hr.view_confidential_notes'):
        if note.created_by != request.user:
            messages.error(request, 'ليس لديك صلاحية لعرض هذه الملاحظة السرية')
            return redirect('Hr:notes:dashboard')

    # تاريخ التعديلات
    history = note.history.select_related('changed_by').order_by('-changed_at')

    context = {
        'note': note,
        'history': history,
        'title': f'تفاصيل الملاحظة - {note.title}'
    }

    return render(request, 'Hr/notes/detail.html', context)


@login_required
def employee_note_edit(request, note_id):
    """تعديل ملاحظة موظف"""

    note = get_object_or_404(EmployeeNote, id=note_id, is_active=True)

    # التحقق من الصلاحيات
    if not request.user.has_perm('Hr.manage_all_notes') and note.created_by != request.user:
        messages.error(request, 'ليس لديك صلاحية لتعديل هذه الملاحظة')
        return redirect('Hr:notes:detail', note_id=note.id)

    # حفظ القيم القديمة للمقارنة
    old_values = {
        'title': note.title,
        'content': note.content,
        'note_type': note.note_type,
        'priority': note.priority,
        'evaluation_link': note.evaluation_link,
        'evaluation_score': note.evaluation_score,
        'tags': note.tags,
        'is_important': note.is_important,
        'is_confidential': note.is_confidential,
        'follow_up_required': note.follow_up_required,
        'follow_up_date': note.follow_up_date,
    }

    if request.method == 'POST':
        form = EmployeeNoteForm(request.POST, instance=note)
        if form.is_valid():
            # حفظ التعديلات
            updated_note = form.save(commit=False)
            updated_note.last_modified_by = request.user
            updated_note.save()

            # تسجيل التغييرات في التاريخ
            new_values = {
                'title': updated_note.title,
                'content': updated_note.content,
                'note_type': updated_note.note_type,
                'priority': updated_note.priority,
                'evaluation_link': updated_note.evaluation_link,
                'evaluation_score': updated_note.evaluation_score,
                'tags': updated_note.tags,
                'is_important': updated_note.is_important,
                'is_confidential': updated_note.is_confidential,
                'follow_up_required': updated_note.follow_up_required,
                'follow_up_date': str(updated_note.follow_up_date) if updated_note.follow_up_date else None,
            }

            # التحقق من وجود تغييرات
            changes_detected = False
            for key, new_value in new_values.items():
                old_value = old_values.get(key)
                if str(old_value) != str(new_value):
                    changes_detected = True
                    break

            if changes_detected:
                EmployeeNoteHistory.objects.create(
                    note=updated_note,
                    action='updated',
                    changed_by=request.user,
                    old_values=old_values,
                    new_values=new_values
                )

            messages.success(request, f'تم تحديث الملاحظة "{updated_note.title}" بنجاح')
            return redirect('Hr:notes:detail', note_id=updated_note.id)
    else:
        form = EmployeeNoteForm(instance=note)

    context = {
        'form': form,
        'note': note,
        'employee': note.employee,
        'title': f'تعديل الملاحظة - {note.title}'
    }

    return render(request, 'Hr/notes/edit.html', context)


@login_required
def employee_note_delete(request, note_id):
    """حذف ملاحظة موظف (حذف منطقي)"""

    note = get_object_or_404(EmployeeNote, id=note_id, is_active=True)

    # التحقق من الصلاحيات
    if not request.user.has_perm('Hr.manage_all_notes') and note.created_by != request.user:
        messages.error(request, 'ليس لديك صلاحية لحذف هذه الملاحظة')
        return redirect('Hr:notes:detail', note_id=note.id)

    if request.method == 'POST':
        # حذف منطقي
        note.is_active = False
        note.last_modified_by = request.user
        note.save()

        # تسجيل الحذف في التاريخ
        EmployeeNoteHistory.objects.create(
            note=note,
            action='deleted',
            changed_by=request.user,
            notes=f'تم حذف الملاحظة: {note.title}'
        )

        messages.success(request, f'تم حذف الملاحظة "{note.title}" بنجاح')
        return redirect('Hr:notes:employee_notes', employee_id=note.employee.emp_id)

    context = {
        'note': note,
        'title': f'حذف الملاحظة - {note.title}'
    }

    return render(request, 'Hr/notes/delete_confirm.html', context)


@login_required
def employee_notes_reports(request):
    """صفحة تقارير ملاحظات الموظفين"""

    form = EmployeeNoteReportForm()
    report_data = None

    if request.method == 'POST':
        form = EmployeeNoteReportForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data['report_type']
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            department = form.cleaned_data.get('department')
            employee = form.cleaned_data.get('employee')
            include_confidential = form.cleaned_data.get('include_confidential', False)

            # بناء الاستعلام الأساسي
            base_query = EmployeeNote.objects.filter(
                is_active=True,
                created_at__date__gte=date_from,
                created_at__date__lte=date_to
            )

            # تطبيق فلاتر إضافية
            if department:
                base_query = base_query.filter(employee__department=department)

            if employee:
                base_query = base_query.filter(employee=employee)

            if not include_confidential:
                base_query = base_query.filter(is_confidential=False)

            # إنشاء التقرير حسب النوع
            if report_type == 'employee_summary':
                report_data = generate_employee_summary_report(base_query)
            elif report_type == 'department_summary':
                report_data = generate_department_summary_report(base_query)
            elif report_type == 'type_summary':
                report_data = generate_type_summary_report(base_query)
            elif report_type == 'date_range':
                report_data = generate_date_range_report(base_query, date_from, date_to)
            elif report_type == 'performance_trends':
                report_data = generate_performance_trends_report(base_query)

            # التصدير إذا طُلب
            export_format = form.cleaned_data.get('export_format')
            if export_format and report_data:
                return export_report(report_data, export_format, report_type)

    context = {
        'form': form,
        'report_data': report_data,
        'title': 'تقارير ملاحظات الموظفين'
    }

    return render(request, 'Hr/notes/reports.html', context)


# Helper functions for report generation

def generate_employee_summary_report(query):
    """إنشاء تقرير ملخص حسب الموظف"""

    employee_stats = query.values(
        'employee__emp_id',
        'employee__emp_full_name',
        'employee__emp_first_name',
        'employee__department__dept_name'
    ).annotate(
        total_notes=Count('id'),
        positive_notes=Count('id', filter=Q(note_type='positive')),
        negative_notes=Count('id', filter=Q(note_type='negative')),
        general_notes=Count('id', filter=Q(note_type='general')),
        important_notes=Count('id', filter=Q(is_important=True)),
        avg_evaluation_score=Avg('evaluation_score')
    ).order_by('-total_notes')

    return {
        'type': 'employee_summary',
        'data': list(employee_stats),
        'total_employees': employee_stats.count(),
        'total_notes': query.count()
    }


def generate_department_summary_report(query):
    """إنشاء تقرير ملخص حسب القسم"""

    department_stats = query.values(
        'employee__department__dept_name'
    ).annotate(
        total_notes=Count('id'),
        positive_notes=Count('id', filter=Q(note_type='positive')),
        negative_notes=Count('id', filter=Q(note_type='negative')),
        general_notes=Count('id', filter=Q(note_type='general')),
        employees_count=Count('employee', distinct=True),
        avg_evaluation_score=Avg('evaluation_score')
    ).order_by('-total_notes')

    return {
        'type': 'department_summary',
        'data': list(department_stats),
        'total_departments': department_stats.count(),
        'total_notes': query.count()
    }


def generate_type_summary_report(query):
    """إنشاء تقرير ملخص حسب نوع الملاحظة"""

    type_stats = query.values('note_type').annotate(
        count=Count('id'),
        percentage=Count('id') * 100.0 / query.count()
    ).order_by('-count')

    priority_stats = query.values('priority').annotate(
        count=Count('id'),
        percentage=Count('id') * 100.0 / query.count()
    ).order_by('-count')

    return {
        'type': 'type_summary',
        'type_stats': list(type_stats),
        'priority_stats': list(priority_stats),
        'total_notes': query.count()
    }


def generate_date_range_report(query, date_from, date_to):
    """إنشاء تقرير حسب الفترة الزمنية"""

    # إحصائيات يومية
    daily_stats = query.extra(
        select={'date': "date(created_at)"}
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    # إحصائيات أسبوعية
    weekly_stats = query.extra(
        select={'week': "strftime('%%Y-%%W', created_at)"}
    ).values('week').annotate(
        count=Count('id')
    ).order_by('week')

    # إحصائيات شهرية
    monthly_stats = query.extra(
        select={'month': "strftime('%%Y-%%m', created_at)"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    return {
        'type': 'date_range',
        'daily_stats': list(daily_stats),
        'weekly_stats': list(weekly_stats),
        'monthly_stats': list(monthly_stats),
        'date_from': date_from,
        'date_to': date_to,
        'total_notes': query.count()
    }


def generate_performance_trends_report(query):
    """إنشاء تقرير اتجاهات الأداء"""

    # اتجاهات الأداء حسب الشهر
    performance_trends = query.filter(
        evaluation_score__isnull=False
    ).extra(
        select={'month': "strftime('%%Y-%%m', created_at)"}
    ).values('month').annotate(
        avg_score=Avg('evaluation_score'),
        positive_count=Count('id', filter=Q(note_type='positive')),
        negative_count=Count('id', filter=Q(note_type='negative')),
        total_count=Count('id')
    ).order_by('month')

    # أفضل وأسوأ الموظفين من ناحية الأداء
    employee_performance = query.filter(
        evaluation_score__isnull=False
    ).values(
        'employee__emp_id',
        'employee__emp_full_name',
        'employee__emp_first_name'
    ).annotate(
        avg_score=Avg('evaluation_score'),
        total_notes=Count('id'),
        positive_notes=Count('id', filter=Q(note_type='positive')),
        negative_notes=Count('id', filter=Q(note_type='negative'))
    ).order_by('-avg_score')

    return {
        'type': 'performance_trends',
        'trends': list(performance_trends),
        'top_performers': list(employee_performance[:10]),
        'bottom_performers': list(employee_performance.order_by('avg_score')[:10]),
        'total_notes': query.count()
    }


def export_report(report_data, export_format, report_type):
    """تصدير التقرير بالتنسيق المطلوب"""

    if export_format == 'pdf':
        return export_pdf_report(report_data, report_type)
    elif export_format == 'excel':
        return export_excel_report(report_data, report_type)
    elif export_format == 'csv':
        return export_csv_report(report_data, report_type)


def export_pdf_report(report_data, report_type):
    """تصدير التقرير كملف PDF"""
    from django.template.loader import get_template
    from weasyprint import HTML, CSS
    from django.conf import settings
    import os

    template = get_template(f'Hr/notes/reports/pdf_{report_type}.html')
    html_content = template.render({'report_data': report_data})

    # إنشاء PDF
    pdf_file = HTML(string=html_content).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="employee_notes_report_{report_type}.pdf"'

    return response


def export_excel_report(report_data, report_type):
    """تصدير التقرير كملف Excel"""
    import openpyxl
    from openpyxl.styles import Font, Alignment
    from io import BytesIO

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"تقرير ملاحظات الموظفين - {report_type}"

    # إعداد الخط والمحاذاة للعربية
    arabic_font = Font(name='Arial Unicode MS', size=12)
    center_alignment = Alignment(horizontal='center', vertical='center')

    # إضافة البيانات حسب نوع التقرير
    if report_type == 'employee_summary':
        headers = ['رقم الموظف', 'اسم الموظف', 'القسم', 'إجمالي الملاحظات', 'إيجابية', 'سلبية', 'عامة', 'مهمة', 'متوسط التقييم']
        ws.append(headers)

        for item in report_data['data']:
            ws.append([
                item['employee__emp_id'],
                item['employee__emp_full_name'] or item['employee__emp_first_name'],
                item['employee__department__dept_name'] or '',
                item['total_notes'],
                item['positive_notes'],
                item['negative_notes'],
                item['general_notes'],
                item['important_notes'],
                round(item['avg_evaluation_score'] or 0, 2)
            ])

    # تطبيق التنسيق
    for row in ws.iter_rows():
        for cell in row:
            cell.font = arabic_font
            cell.alignment = center_alignment

    # حفظ الملف
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="employee_notes_report_{report_type}.xlsx"'

    return response


def export_csv_report(report_data, report_type):
    """تصدير التقرير كملف CSV"""
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # إضافة BOM للدعم العربي
    output.write('\ufeff')

    if report_type == 'employee_summary':
        writer.writerow(['رقم الموظف', 'اسم الموظف', 'القسم', 'إجمالي الملاحظات', 'إيجابية', 'سلبية', 'عامة', 'مهمة', 'متوسط التقييم'])

        for item in report_data['data']:
            writer.writerow([
                item['employee__emp_id'],
                item['employee__emp_full_name'] or item['employee__emp_first_name'],
                item['employee__department__dept_name'] or '',
                item['total_notes'],
                item['positive_notes'],
                item['negative_notes'],
                item['general_notes'],
                item['important_notes'],
                round(item['avg_evaluation_score'] or 0, 2)
            ])

    response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="employee_notes_report_{report_type}.csv"'

    return response

@login_required
def employee_note_list(request):
    """عرض قائمة ملاحظات الموظفين"""
    # Filter notes based on query parameters
    employee_id = request.GET.get('employee')
    important_only = request.GET.get('important') == 'true'
    
    notes = EmployeeNote.objects.all()
    
    if employee_id:
        notes = notes.filter(employee_id=employee_id)
    
    if important_only:
        notes = notes.filter(is_important=True)
    
    # Default ordering
    notes = notes.order_by('-created_at')
    
    context = {
        'notes': notes,
        'title': 'ملاحظات الموظفين'
    }
    
    return render(request, 'Hr/notes/list.html', context)

@login_required
def employee_note_create(request):
    """إنشاء ملاحظة جديدة للموظف"""
    if request.method == 'POST':
        form = EmployeeNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.created_by = request.user
            note.save()
            messages.success(request, 'تم إنشاء الملاحظة بنجاح')
            return redirect('Hr:notes:list')
    else:
        # Pre-fill employee if provided in query string
        employee_id = request.GET.get('employee')
        initial_data = {}
        if employee_id:
            initial_data['employee'] = employee_id
        
        form = EmployeeNoteForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'إنشاء ملاحظة جديدة'
    }
    
    return render(request, 'Hr/notes/create.html', context)

@login_required
def employee_note_detail(request, pk):
    """عرض تفاصيل ملاحظة"""
    note = get_object_or_404(EmployeeNote, pk=pk)
    
    context = {
        'note': note,
        'title': f'تفاصيل الملاحظة: {note.title}'
    }
    
    return render(request, 'Hr/notes/detail.html', context)

@login_required
def employee_note_edit(request, pk):
    """تعديل ملاحظة"""
    note = get_object_or_404(EmployeeNote, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الملاحظة بنجاح')
            return redirect('Hr:notes:detail', pk=note.pk)
    else:
        form = EmployeeNoteForm(instance=note)
    
    context = {
        'form': form,
        'note': note,
        'title': f'تعديل الملاحظة: {note.title}'
    }
    
    return render(request, 'Hr/notes/edit.html', context)

@login_required
def employee_note_delete(request, pk):
    """حذف ملاحظة"""
    note = get_object_or_404(EmployeeNote, pk=pk)
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'تم حذف الملاحظة بنجاح')
        return redirect('Hr:notes:list')
    
    context = {
        'note': note,
        'title': f'حذف الملاحظة: {note.title}'
    }
    
    return render(request, 'Hr/notes/delete.html', context)
